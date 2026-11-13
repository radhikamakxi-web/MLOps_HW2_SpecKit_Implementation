from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import yaml
from huggingface_hub import snapshot_download
from huggingface_hub.utils import HFValidationError, validate_repo_id

from app.utils.config import BASE_DIR, get_hf_home, get_model_dir, get_transformers_cache, load_yaml_config


class ModelManager:
    COMPLETION_FILE = ".model-complete.json"

    def __init__(self, model_dir: str | Path | None = None):
        self.model_dir = (Path(model_dir) if model_dir else get_model_dir()).expanduser().resolve()
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.hf_home = get_hf_home()
        self.hf_home.mkdir(parents=True, exist_ok=True)
        self.transformers_cache = get_transformers_cache()
        self.transformers_cache.mkdir(parents=True, exist_ok=True)
        self.config_path = BASE_DIR / "configs" / "models.yaml"
        self.models = self._load_models()

    def _load_models(self) -> list[dict[str, Any]]:
        config = load_yaml_config(self.config_path)
        items = config.get("models", [])
        return items if isinstance(items, list) else []

    def get_supported_models(self) -> list[dict[str, Any]]:
        self.models = self._load_models()
        return self.models

    def refresh_local_models(self) -> list[dict[str, Any]]:
        self.models = self._load_models()
        results: list[dict[str, Any]] = []
        for model in self.models:
            model_id = model.get("id", "")
            status = "available" if model_id and self.model_exists(model_id) else "missing"
            results.append({**model, "status": status})
        return results

    def add_model(
        self,
        model_id: str,
        name: str = "",
        task: str = "zero-shot-classification",
    ) -> tuple[bool, str]:
        clean_id = model_id.strip() if isinstance(model_id, str) else ""
        if not clean_id:
            return False, "Model identifier is required."

        try:
            validate_repo_id(clean_id)
        except HFValidationError as exc:
            return False, f"Invalid Hugging Face model ID: {exc}"

        clean_name = name.strip() if isinstance(name, str) and name.strip() else clean_id
        clean_task = task.strip() if isinstance(task, str) and task.strip() else "zero-shot-classification"

        current_models = self._load_models()
        if any(str(m.get("id", "")).lower() == clean_id.lower() for m in current_models):
            return False, f"Model '{clean_id}' is already configured."

        current_models.append(
            {
                "id": clean_id,
                "name": clean_name,
                "task": clean_task,
            }
        )

        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            serialized = yaml.safe_dump({"models": current_models}, sort_keys=False, allow_unicode=True)
            self.config_path.write_text(serialized, encoding="utf-8")
            self.models = current_models
            return True, f"Model '{clean_name}' ({clean_id}) added to configuration."
        except OSError as exc:
            return False, f"Failed to save model configuration: {exc}"

    def get_model_path(self, model_id: str) -> Path:
        if not isinstance(model_id, str) or not model_id:
            raise ValueError("Model identifier must be a nonempty string.")
        validate_repo_id(model_id)
        # Escape literal underscores so "org/model" and "org__model" cannot collide.
        sanitized = model_id.replace("_", "%5F").replace("/", "__")
        path = self.model_dir / sanitized
        if self.model_dir.resolve() != self.model_dir or path.is_symlink() or path.resolve().parent != self.model_dir:
            raise ValueError("Model path must be a direct, non-symlink child of MODEL_DIR.")
        return path

    @staticmethod
    def _file_size(directory: Path, name: str) -> int:
        """Validate artifact paths, including paths supplied by shard indexes."""
        relative = Path(name)
        if relative.is_absolute() or not relative.parts or ".." in relative.parts or "\\" in name:
            raise ValueError("Unsafe model artifact path.")
        path = directory
        for part in relative.parts:
            path = path / part
            if path.is_symlink():
                raise ValueError("Model artifacts must not be symlinks.")
        if not path.resolve().is_relative_to(directory.resolve()) or not path.is_file():
            raise ValueError(f"Missing model artifact: {name}")
        size = path.stat().st_size
        if size == 0:
            raise ValueError(f"Empty model artifact: {name}")
        return size

    @classmethod
    def _read_json(cls, directory: Path, name: str) -> dict:
        cls._file_size(directory, name)
        value = json.loads((directory / name).read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"Expected a JSON object in {name}.")
        return value

    @classmethod
    def _artifact_sizes(cls, directory: Path) -> dict[str, int]:
        """Check structural completeness without loading multi-gigabyte weights."""
        config = cls._read_json(directory, "config.json")
        if not isinstance(config.get("model_type"), str) or not config["model_type"]:
            raise ValueError("Model configuration must specify model_type.")
        names = ["config.json"]
        # Some repositories (including BART layouts) infer tokenizer settings
        # from model_type and do not include a separate tokenizer config.
        tokenizer_config = directory / "tokenizer_config.json"
        if tokenizer_config.exists() or tokenizer_config.is_symlink():
            cls._read_json(directory, "tokenizer_config.json")
            names.append("tokenizer_config.json")
        for tokenizer_files in (
            ("tokenizer.json",), ("spm.model",), ("sentencepiece.bpe.model",),
            ("vocab.txt",), ("vocab.json", "merges.txt"),
        ):
            if all((directory / name).exists() for name in tokenizer_files):
                names.extend(tokenizer_files)
                for name in tokenizer_files:
                    if name.endswith(".json"):
                        cls._read_json(directory, name)
                break
        else:
            raise ValueError("Missing tokenizer artifacts.")

        for weights in ("model.safetensors", "model.safetensors.index.json",
                        "pytorch_model.bin", "pytorch_model.bin.index.json"):
            if not (directory / weights).exists():
                continue
            names.append(weights)
            if weights.endswith(".index.json"):
                weight_map = cls._read_json(directory, weights).get("weight_map")
                if not isinstance(weight_map, dict) or not weight_map:
                    raise ValueError("Weight index must contain a nonempty weight_map.")
                shards = list(weight_map.values())
                if not all(isinstance(shard, str) and shard for shard in shards):
                    raise ValueError("Invalid weight shard names.")
                names.extend(shards)
            break
        else:
            raise ValueError("Missing PyTorch model weights.")
        return {name: cls._file_size(directory, name) for name in names}

    def model_exists(self, model_id: str) -> bool:
        try:
            path = self.get_model_path(model_id)
            if not path.is_dir():
                return False
            manifest = self._read_json(path, self.COMPLETION_FILE)
            return (manifest.get("version") == 1
                    and manifest.get("model_id") == model_id
                    and manifest.get("files") == self._artifact_sizes(path))
        except (OSError, ValueError, RuntimeError):
            return False

    def download_model(self, model_id: str) -> tuple[bool, str, Path | None]:
        if not model_id:
            return False, "Model identifier is required.", None

        staging = None
        try:
            target_dir = self.get_model_path(model_id)
            if self.model_exists(model_id):
                return True, "Model already available locally.", target_dir
            if target_dir.exists() and not target_dir.is_dir():
                raise ValueError("Model destination exists but is not a directory.")
            staging = Path(tempfile.mkdtemp(prefix=".download-", dir=self.model_dir))
            downloaded = snapshot_download(
                repo_id=model_id,
                cache_dir=str(self.hf_home),
                local_dir=str(staging),
                local_dir_use_symlinks=False,
            )
            if staging.is_symlink() or not staging.is_dir() or Path(downloaded).resolve() != staging.resolve():
                raise ValueError("Model download did not return its staging directory.")
            manifest = {"version": 1, "model_id": model_id, "files": self._artifact_sizes(staging)}
            marker = staging / self.COMPLETION_FILE
            # Do not follow a marker symlink supplied by a remote repository.
            if marker.is_symlink():
                raise ValueError("Completion manifest must not be a symlink.")
            marker.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            # Recheck containment immediately before replacing an incomplete copy.
            target_dir = self.get_model_path(model_id)
            if target_dir.exists():
                shutil.rmtree(target_dir)
            staging.rename(target_dir)
            return True, "Model downloaded successfully.", target_dir
        except Exception as exc:
            return False, f"Model download failed: {exc}", None
        finally:
            if staging is not None:
                if staging.is_symlink():
                    staging.unlink()
                elif staging.exists():
                    shutil.rmtree(staging, ignore_errors=True)

    def delete_model(self, model_id: str) -> tuple[bool, str]:
        try:
            path = self.get_model_path(model_id)
            if not path.exists():
                return False, "Model is not downloaded locally."
            shutil.rmtree(path)
            return True, f"Deleted local model '{model_id}'."
        except Exception as exc:
            return False, f"Failed to delete model: {exc}"

    def clear_hf_cache(self) -> tuple[bool, str]:
        
        try:
            if self.hf_home.exists():
                shutil.rmtree(self.hf_home)
            self.hf_home.mkdir(parents=True, exist_ok=True)
            return True, "Hugging Face cache cleared."
        except Exception as exc:
            return False, f"Failed to clear Hugging Face cache: {exc}"
