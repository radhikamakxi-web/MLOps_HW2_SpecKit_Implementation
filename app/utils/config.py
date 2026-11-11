import os
import tempfile
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from minio.helpers import check_bucket_name

from app.utils.logging_config import log_event

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]


class ConfigurationError(ValueError):
    """Safe configuration message suitable for display to a user."""


def validate_labels(candidate_labels: list[str]) -> list[str]:
    if not isinstance(candidate_labels, list) or any(not isinstance(label, str) for label in candidate_labels):
        raise ValueError("Candidate labels must be a list of strings.")
    labels = list(dict.fromkeys(label.strip() for label in candidate_labels if label.strip()))
    if len(labels) < 2:
        raise ValueError("At least two unique candidate labels are required.")
    return labels


def get_labels_path() -> Path:
    path = Path(get_env("LABELS_CONFIG", "configs/labels.yaml")).expanduser()
    return path if path.is_absolute() else BASE_DIR / path


def load_labels() -> list[str]:
    try:
        config = load_yaml_config(get_labels_path())
        if not isinstance(config, dict):
            raise ValueError("Expected a YAML mapping")
        return validate_labels(config.get("labels"))
    except (OSError, ValueError, yaml.YAMLError):
        raise ConfigurationError("Label configuration is invalid or missing. Save at least two labels in Admin.") from None


def save_labels(labels: list[str]) -> list[str]:
    normalized = validate_labels(labels)
    destination = get_labels_path()
    temporary = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            yaml.safe_dump({"labels": normalized}, stream, allow_unicode=True, sort_keys=False)
        os.replace(temporary, destination)
    except OSError:
        log_event("labels_save_failed")
        raise ConfigurationError("Unable to save labels. Check configuration-directory permissions.") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    log_event("labels_saved", label_count=len(normalized))
    return normalized


def get_env(name: str, default: Any = None) -> Any:
    value = os.getenv(name, default)
    if value is None:
        return None
    return value


def get_model_dir() -> Path:
    model_dir = Path(get_env("MODEL_DIR", "./models")).expanduser()
    if not model_dir.is_absolute():
        model_dir = (BASE_DIR / model_dir).resolve()
    return model_dir


def get_hf_home() -> Path:
    hf_home = Path(get_env("HF_HOME", "./.cache/huggingface")).expanduser()
    if not hf_home.is_absolute():
        hf_home = (BASE_DIR / hf_home).resolve()
    return hf_home


def get_transformers_cache() -> Path:
    cache = Path(get_env("TRANSFORMERS_CACHE", "./.cache/huggingface/transformers")).expanduser()
    if not cache.is_absolute():
        cache = (BASE_DIR / cache).resolve()
    return cache


def load_yaml_config(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_absolute():
        file_path = BASE_DIR / file_path
    with file_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data


def get_app_version() -> str:
    return get_env("APP_VERSION", "0.1.0")


def get_minio_settings() -> dict[str, Any]:
    bucket = str(get_env("MINIO_BUCKET", "zeroshot_learning_output"))
    try:
        check_bucket_name(bucket, strict=True)
    except ValueError:
        raise ConfigurationError("MINIO_BUCKET must be an S3-compatible name; use zeroshot_learning_output.") from None
    access_key = get_env("MINIO_ACCESS_KEY")
    secret_key = get_env("MINIO_SECRET_KEY")
    if not access_key or not secret_key or access_key == "replace-me" or secret_key == "replace-me":
        raise ConfigurationError("Set MINIO_ACCESS_KEY and MINIO_SECRET_KEY in your local environment.")
    endpoint = str(get_env("MINIO_ENDPOINT", "localhost:9000"))
    if "://" in endpoint or "/" in endpoint or "@" in endpoint:
        raise ConfigurationError("MINIO_ENDPOINT must contain only a host and optional port.")
    secure = str(get_env("MINIO_SECURE", "false")).lower()
    if secure not in {"true", "false"}:
        raise ConfigurationError("MINIO_SECURE must be true or false.")
    return {
        "endpoint": endpoint,
        "access_key": access_key,
        "secret_key": secret_key,
        "secure": secure == "true",
        "bucket": bucket,
    }
