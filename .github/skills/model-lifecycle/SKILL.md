---
name: model-lifecycle
description: 'Extend or troubleshoot Hugging Face model registration, local downloads, reuse, deletion, and cache handling in this project. Use for model configuration changes, ModelManager fixes, or admin model-management workflows.'
---

# Model lifecycle

## Read first

Paths are relative to the repository root:
- `app/services/model_manager.py`
- `app/utils/config.py`
- `configs/models.yaml`
- `app/pages/1_Admin.py`
- `tests/test_model_manager.py`
- `.specify/memory/constitution.md`

## Workflow

1. Inspect the current model configuration schema and callers before adding a model or changing a service signature. Preserve existing entries unless removal is requested.
2. Trace `MODEL_DIR`, `HF_HOME`, and `TRANSFORMERS_CACHE` through the configuration utilities. Keep configuration environment-driven and credentials out of YAML and logs.
3. Review the relevant `ModelManager` methods: `get_model_path`, `model_exists`, `download_model`, `delete_model`, `clear_hf_cache`, and `refresh_local_models`.
4. Preserve completion-manifest and required-artifact checks before reuse. Test complete and partial directories, all indexed weight shards, and manifest size mismatches. Legacy directories without a manifest are intentionally not ready.
5. Preserve repository-ID validation, resolved-path containment, and symlink rejection before download or deletion. Replacing `/` with `__` alone is not a comprehensive traversal or symlink defense.
6. Trace the classification caller when changing model paths. Verify that inference actually uses local artifacts; a local availability check alone does not prevent a remote pipeline download.
7. If implementing revision support, carry the configured revision through downloads and prediction metadata; do not assume the existing downloader pins revisions.
8. Add focused unit tests and run `python -m pytest -q tests/test_model_manager.py` in the selected environment from the repository root.

## Safe test patterns

- Use pytest `tmp_path` for model and cache directories. Set cache environment variables before constructing the manager, or patch the configuration functions used by the service.
- Patch `app.services.model_manager.snapshot_download`, where the function is imported, rather than contacting Hugging Face.
- A successful fake download should write configuration, tokenizer artifacts, and nonempty placeholder weights into the provided staging directory and return that path. Fixtures test structural validation, not real weight loadability.
- Check that an existing valid model skips the downloader.
- Simulate downloader failure and verify only the request's staging directory is removed; pre-existing model directories must survive download and artifact-validation failures.
- Cover missing models, missing cache directories, filesystem errors, and boundary/path cases when modifying those behaviors.
- Never run deletion or cache-clearing checks against a user's real model directories or shared Hugging Face cache.

## Completion checklist

- Model IDs and any revision settings match the actual configuration contract.
- UI status and error messages reflect service results.
- No test downloads weights or depends on GPU availability.
- Documentation distinguishes implemented guarantees from remaining validation gaps.