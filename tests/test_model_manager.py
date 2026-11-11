import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from app.services.model_manager import ModelManager


def write_model_artifacts(directory):
    """Tiny structural fixtures, not loadable model weights."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "config.json").write_text('{"model_type": "bart"}', encoding="utf-8")
    (directory / "tokenizer_config.json").write_text("{}", encoding="utf-8")
    (directory / "tokenizer.json").write_text('{"version": "1.0"}', encoding="utf-8")
    (directory / "model.safetensors").write_bytes(b"test-weight-bytes")


def write_completion(directory, model_id):
    files = {file.name: file.stat().st_size for file in directory.iterdir() if file.is_file()
             and file.name != ModelManager.COMPLETION_FILE}
    (directory / ModelManager.COMPLETION_FILE).write_text(
        json.dumps({"version": 1, "model_id": model_id, "files": files}), encoding="utf-8",
    )


@pytest.fixture
def manager(tmp_path, monkeypatch):
    """Keep every model and cache operation inside this test's directory."""
    monkeypatch.setenv("MODEL_DIR", str(tmp_path / "models"))
    monkeypatch.setenv("HF_HOME", str(tmp_path / "hf-cache"))
    monkeypatch.setenv("TRANSFORMERS_CACHE", str(tmp_path / "transformers-cache"))
    return ModelManager()


@pytest.fixture(autouse=True)
def downloader(monkeypatch):
    """Fail closed if a test accidentally tries to download real weights."""
    mocked = Mock(side_effect=AssertionError("Unexpected Hugging Face download"))
    monkeypatch.setattr("app.services.model_manager.snapshot_download", mocked)
    return mocked


def test_configured_model_path_uses_sanitized_name(manager):
    path = manager.get_model_path("MoritzLaurer/deberta-v3-base-zeroshot-v2.0")
    assert path.name == "MoritzLaurer__deberta-v3-base-zeroshot-v2.0"
    assert path.parent == manager.model_dir


def test_missing_model_is_detected(manager):
    assert manager.model_exists("nonexistent/model") is False


def test_clear_hf_cache_handles_missing_dir(manager, tmp_path):
    manager.hf_home = tmp_path / "does-not-exist-hf"
    ok, message = manager.clear_hf_cache()
    assert ok is True
    assert "does not exist" in message.lower()


def test_delete_model_reports_missing_file(manager):
    ok, message = manager.delete_model("missing/model")
    assert ok is False
    assert "not found" in message.lower()


@pytest.mark.parametrize("model_id", [
    "MoritzLaurer/deberta-v3-base-zeroshot-v2.0",
    "facebook/bart-large-mnli",
])
def test_existing_local_model_skips_download(manager, downloader, model_id):
    target = manager.get_model_path(model_id)
    write_model_artifacts(target)
    write_completion(target, model_id)
    marker = target / "config.json"

    assert manager.model_exists(model_id) is True
    ok, message, path = manager.download_model(model_id)

    assert ok is True
    assert "already available" in message.lower()
    assert path == target
    assert json.loads(marker.read_text(encoding="utf-8")) == {"model_type": "bart"}
    downloader.assert_not_called()


@pytest.mark.parametrize("model_id", [
    "MoritzLaurer/deberta-v3-base-zeroshot-v2.0",
    "facebook/bart-large-mnli",
])
def test_missing_model_downloads_once_into_controlled_directory(manager, downloader, model_id):
    target = manager.get_model_path(model_id)

    def fake_download(**kwargs):
        destination = Path(kwargs["local_dir"])
        assert destination.parent == manager.model_dir
        assert destination != target
        assert manager.model_exists(model_id) is False
        write_model_artifacts(destination)
        return str(destination)

    downloader.side_effect = fake_download
    assert manager.model_exists(model_id) is False

    ok, message, path = manager.download_model(model_id)

    assert ok is True
    assert "successfully" in message.lower()
    assert path == target
    assert target.resolve().parent == manager.model_dir.resolve()
    assert manager.model_exists(model_id) is True
    staging = Path(downloader.call_args.kwargs["local_dir"])
    downloader.assert_called_once_with(
        repo_id=model_id,
        cache_dir=str(manager.hf_home),
        local_dir=str(staging),
        local_dir_use_symlinks=False,
    )
    assert not staging.exists()
    assert (target / manager.COMPLETION_FILE).is_file()

    # A second request must reuse the first download, not call Hugging Face.
    second_ok, _, second_path = manager.download_model(model_id)
    assert second_ok is True
    assert second_path == target
    assert downloader.call_count == 1


def test_regular_file_is_not_a_local_model(manager):
    manager.get_model_path("example/model").write_text("not a directory", encoding="utf-8")
    assert manager.model_exists("example/model") is False


def test_model_directory_uses_environment_configuration(manager, tmp_path):
    assert manager.model_dir == tmp_path / "models"
    assert manager.model_dir.is_dir()


def test_failed_download_removes_only_partial_target(manager, downloader):
    target = manager.get_model_path("example/broken")
    other_model = manager.get_model_path("example/keep")
    other_model.mkdir()
    marker = other_model / "config.json"
    marker.write_text("{}", encoding="utf-8")

    def fail_download(**kwargs):
        (Path(kwargs["local_dir"]) / "partial.bin").write_bytes(b"partial")
        raise RuntimeError("Simulated network failure")

    downloader.side_effect = fail_download
    ok, message, path = manager.download_model("example/broken")

    assert ok is False
    assert "Simulated network failure" in message
    assert path is None
    assert not target.exists()
    assert marker.read_text(encoding="utf-8") == "{}"
    assert not list(manager.model_dir.glob(".download-*"))
    downloader.assert_called_once()


def test_empty_directory_is_not_a_ready_model(manager):
    manager.get_model_path("example/incomplete").mkdir()
    assert manager.model_exists("example/incomplete") is False


def test_parent_directory_identifier_cannot_escape_model_root(manager):
    with pytest.raises(ValueError):
        manager.get_model_path("..")


@pytest.mark.parametrize("model_id", ["", ".", "..", "../outside", "/tmp/outside", "a/b/c", "a\\b", "a/../b", None])
def test_invalid_identifiers_cannot_download_or_delete(manager, downloader, model_id):
    with pytest.raises(ValueError):
        manager.get_model_path(model_id)
    assert manager.model_exists(model_id) is False
    assert manager.download_model(model_id)[0] is False
    assert manager.delete_model(model_id)[0] is False
    downloader.assert_not_called()


def test_model_directory_symlink_is_rejected(manager, downloader, tmp_path):
    outside = tmp_path / "outside"
    write_model_artifacts(outside)
    write_completion(outside, "example/model")
    target = manager.get_model_path("example/model")
    target.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError):
        manager.get_model_path("example/model")
    assert manager.model_exists("example/model") is False
    assert manager.download_model("example/model")[0] is False
    assert manager.delete_model("example/model")[0] is False
    assert (outside / "model.safetensors").is_file()
    assert target.is_symlink()
    downloader.assert_not_called()


def test_legacy_directory_without_completion_is_not_ready(manager):
    write_model_artifacts(manager.get_model_path("example/model"))
    assert manager.model_exists("example/model") is False


@pytest.mark.parametrize("filename", ["config.json", "tokenizer_config.json", "tokenizer.json", "model.safetensors"])
@pytest.mark.parametrize("damage", ["missing", "empty", "truncated"])
def test_damaged_artifact_is_not_ready(manager, filename, damage):
    target = manager.get_model_path("example/model")
    write_model_artifacts(target)
    write_completion(target, "example/model")
    artifact = target / filename
    if damage == "missing":
        artifact.unlink()
    elif damage == "empty":
        artifact.write_bytes(b"")
    else:
        artifact.write_bytes(artifact.read_bytes()[:-1])
    assert manager.model_exists("example/model") is False


@pytest.mark.parametrize("marker", ["not json", "[]", "{}", '{"version": 1, "model_id": "wrong/model", "files": {}}'])
def test_invalid_completion_manifest_is_not_ready(manager, marker):
    target = manager.get_model_path("example/model")
    write_model_artifacts(target)
    (target / manager.COMPLETION_FILE).write_text(marker, encoding="utf-8")
    assert manager.model_exists("example/model") is False


def test_complete_weight_shards_are_required(manager):
    model_id = "example/sharded"
    target = manager.get_model_path(model_id)
    write_model_artifacts(target)
    (target / "model.safetensors").unlink()
    index = {"weight_map": {"layer.1": "model-00001.safetensors", "layer.2": "model-00002.safetensors"}}
    (target / "model.safetensors.index.json").write_text(json.dumps(index), encoding="utf-8")
    for shard in index["weight_map"].values():
        (target / shard).write_bytes(b"test shard")
    write_completion(target, model_id)
    assert manager.model_exists(model_id) is True
    (target / "model-00002.safetensors").unlink()
    assert manager.model_exists(model_id) is False


@pytest.mark.parametrize("shard", ["../outside.bin", "/tmp/outside.bin", "..\\outside.bin"])
def test_weight_index_cannot_reference_external_files(manager, shard):
    target = manager.get_model_path("example/sharded")
    write_model_artifacts(target)
    (target / "model.safetensors").unlink()
    (target / "model.safetensors.index.json").write_text(
        json.dumps({"weight_map": {"layer": shard}}), encoding="utf-8",
    )
    write_completion(target, "example/sharded")
    assert manager.model_exists("example/sharded") is False


@pytest.mark.parametrize("filename", ["model.safetensors", ModelManager.COMPLETION_FILE])
def test_artifact_symlinks_are_not_ready(manager, tmp_path, filename):
    target = manager.get_model_path("example/model")
    write_model_artifacts(target)
    write_completion(target, "example/model")
    outside = tmp_path / "external-artifact"
    (target / filename).rename(outside)
    (target / filename).symlink_to(outside)
    assert manager.model_exists("example/model") is False


def test_incomplete_download_is_not_published(manager, downloader):
    def incomplete(**kwargs):
        (Path(kwargs["local_dir"]) / "config.json").write_text("{}", encoding="utf-8")
        return kwargs["local_dir"]

    downloader.side_effect = incomplete
    ok, message, path = manager.download_model("example/model")
    assert ok is False
    assert "failed" in message.lower()
    assert path is None
    assert not manager.get_model_path("example/model").exists()
    assert not list(manager.model_dir.glob(".download-*"))


def test_successful_retry_replaces_incomplete_directory(manager, downloader):
    target = manager.get_model_path("example/model")
    target.mkdir()
    (target / "old-partial.bin").write_bytes(b"partial")

    def complete(**kwargs):
        write_model_artifacts(Path(kwargs["local_dir"]))
        return kwargs["local_dir"]

    downloader.side_effect = complete
    assert manager.download_model("example/model")[0] is True
    assert manager.model_exists("example/model") is True
    assert not (target / "old-partial.bin").exists()


def test_failed_retry_preserves_preexisting_directory(manager, downloader):
    target = manager.get_model_path("example/model")
    target.mkdir()
    marker = target / "existing.txt"
    marker.write_text("keep", encoding="utf-8")
    downloader.side_effect = RuntimeError("Simulated failure")
    assert manager.download_model("example/model")[0] is False
    assert marker.read_text(encoding="utf-8") == "keep"
    assert not list(manager.model_dir.glob(".download-*"))


def test_wrong_download_destination_is_rejected(manager, downloader, tmp_path):
    outside = tmp_path / "outside"
    write_model_artifacts(outside)
    downloader.side_effect = None
    downloader.return_value = str(outside)
    assert manager.download_model("example/model")[0] is False
    assert (outside / "model.safetensors").is_file()
    assert not manager.get_model_path("example/model").exists()


def test_regular_file_destination_is_preserved(manager, downloader):
    target = manager.get_model_path("example/model")
    target.write_text("keep", encoding="utf-8")
    assert manager.download_model("example/model")[0] is False
    assert target.read_text(encoding="utf-8") == "keep"
    downloader.assert_not_called()


def test_refresh_distinguishes_ready_incomplete_and_invalid(manager):
    manager.models = [{"id": "example/ready"}, {"id": "example/partial"}, {"id": ".."}]
    write_model_artifacts(manager.get_model_path("example/ready"))
    write_completion(manager.get_model_path("example/ready"), "example/ready")
    manager.get_model_path("example/partial").mkdir()
    entries = manager.refresh_local_models()
    assert [entry["status"] for entry in entries] == ["available", "missing", "invalid"]
    assert entries[-1]["local_path"] is None


def test_delete_removes_only_selected_model(manager):
    write_model_artifacts(manager.get_model_path("example/remove"))
    write_model_artifacts(manager.get_model_path("example/keep"))
    assert manager.delete_model("example/remove")[0] is True
    assert not manager.get_model_path("example/remove").exists()
    assert manager.get_model_path("example/keep").is_dir()


def test_repository_id_encoding_has_no_namespace_collision(manager):
    namespaced = manager.get_model_path("example/model")
    literal = manager.get_model_path("example__model")
    assert namespaced != literal
    write_model_artifacts(namespaced)
    write_model_artifacts(literal)
    assert manager.delete_model("example__model")[0] is True
    assert namespaced.is_dir()


@pytest.mark.parametrize("layout", ["bart", "deberta"])
def test_supported_tokenizer_and_weight_layouts(manager, downloader, layout):
    model_id = "facebook/bart-large-mnli" if layout == "bart" else "MoritzLaurer/deberta-v3-base-zeroshot-v2.0"

    def download_layout(**kwargs):
        directory = Path(kwargs["local_dir"])
        model_type = "bart" if layout == "bart" else "deberta-v2"
        (directory / "config.json").write_text(json.dumps({"model_type": model_type}), encoding="utf-8")
        (directory / "pytorch_model.bin").write_bytes(b"placeholder weights")
        if layout == "bart":
            # BART can derive tokenizer settings from model_type without tokenizer_config.json.
            (directory / "vocab.json").write_text('{"token": 0}', encoding="utf-8")
            (directory / "merges.txt").write_text("#version: 0.2\na b\n", encoding="utf-8")
        else:
            (directory / "tokenizer_config.json").write_text("{}", encoding="utf-8")
            (directory / "spm.model").write_bytes(b"placeholder sentencepiece")
        return kwargs["local_dir"]

    downloader.side_effect = download_layout
    assert manager.download_model(model_id)[0] is True
    assert manager.model_exists(model_id) is True


@pytest.mark.parametrize("filename", ["config.json", "tokenizer_config.json", "tokenizer.json"])
def test_download_with_malformed_json_is_rejected(manager, downloader, filename):
    def malformed(**kwargs):
        directory = Path(kwargs["local_dir"])
        write_model_artifacts(directory)
        (directory / filename).write_text("not json", encoding="utf-8")
        return kwargs["local_dir"]

    downloader.side_effect = malformed
    assert manager.download_model("example/model")[0] is False
    assert not manager.get_model_path("example/model").exists()


def test_download_cannot_overwrite_external_file_via_manifest_symlink(manager, downloader, tmp_path):
    outside = tmp_path / "external.txt"
    outside.write_text("keep", encoding="utf-8")

    def symlinked(**kwargs):
        directory = Path(kwargs["local_dir"])
        write_model_artifacts(directory)
        (directory / manager.COMPLETION_FILE).symlink_to(outside)
        return kwargs["local_dir"]

    downloader.side_effect = symlinked
    assert manager.download_model("example/model")[0] is False
    assert outside.read_text(encoding="utf-8") == "keep"
    assert not list(manager.model_dir.glob(".download-*"))
