# Implementation Plan

**Feature**: `001-zero-shot-platform`  
**Specification**: [spec.md](spec.md)  
**Execution checklist**: [tasks.md](tasks.md)

This plan predates official workflow adoption and is preserved rather than
regenerated from a template. Run `/speckit-analyze` before choosing a pending task.
The scope below includes intended behavior, not a claim that every component is
complete; current gaps and verification status are recorded in `tasks.md` and the
repository README. Future planning should expand technical context, constitution
checks, and any needed research/contracts rather than silently discard this plan.

## 1. Architecture
The app is organized in a layered architecture:
- Streamlit pages for UI
- service modules for model management, inference, and persistence
- configuration utilities
- MinIO storage client

## 2. Components
- `app/streamlit_app.py`: app entrypoint and page navigation
- `app/pages/1_Admin.py`: model and label administration
- `app/pages/2_Classify_Text.py`: inference interface
- `app/services/model_manager.py`: model registry, download, cache, and delete logic
- `app/services/classifier.py`: pipeline creation and zero-shot inference
- `app/services/minio_storage.py`: bucket creation and object writing
- `app/utils/config.py`: environment and YAML loading
- `app/utils/logging_config.py`: logging utilities

## 3. Model Caching Strategy
- Use `MODEL_DIR` plus model ID to create a local path like `models/{model_id}`.
- Validate Hugging Face repository IDs, reject model-directory symlinks, and require resolved paths to remain direct children of the configured model root before downloading or deleting.
- Encode literal underscores as `%5F` before replacing `/` with `__`, so namespaced and unnamespaced IDs cannot map to the same directory.
- Check a completion manifest and required artifact sizes before reusing a directory; directory existence alone is insufficient.
- Use Hugging Face cache configuration via `HF_HOME` and `TRANSFORMERS_CACHE`.
- Download into a unique temporary directory beneath `MODEL_DIR`. Require configuration, tokenizer files, and nonempty PyTorch weights (including all shards referenced by a weight index).
- Accept BART vocabulary/merges and DeBERTa SentencePiece layouts as well as tokenizer JSON. Validate separate tokenizer configuration when present; it is not mandatory for models that infer tokenizer settings from `model_type`.
- After a successful download and structural validation, write `.model-complete.json` and rename the staging directory into the final model path. Remove staging data on failure; do not discard an existing incomplete copy on network or validation failure.
- Legacy directories without a manifest are not ready and must be re-downloaded. Validation checks presence, JSON structure, and sizes, not weight deserialization or cryptographic integrity. Concurrent administration is outside the v1 scope.

## 4. MinIO Strategy
- Connect using environment variables for endpoint, access key, secret key, and bucket.
- Create bucket automatically if missing.
- Save predictions as JSON to `predictions/YYYY/MM/DD/{request_id}.json`.

## 5. Testing Strategy
- Unit tests for model manager and classifier logic
- Integration tests for MinIO writes when MinIO is running
- Mocked or lightweight model fixtures for offline or CI runs

## 6. Deployment and Docker
- `docker-compose.yml` for MinIO
- `Dockerfile` for Streamlit service
- `.env.example` documents required environment variables

## 7. Quality Gates
- Run pytest
- Verify MinIO bucket creation
- Validate README instructions and quick-start flow

## 8. R1 technical plan (after constitution and specification review)

Python 3.10 remains the app runtime; Specify CLI uses its separate Python 3.12 tool
environment. Keep Python, PyTorch, Transformers, Streamlit, and MinIO. No alternate
storage or inference backend is introduced.

1. `config.py`: load/atomically save a single label list, provide shared label
	validation, validate S3 bucket names and required credentials from environment.
2. `model_manager.py`: resolve `revision` with `HfApi.model_info`, download by SHA,
	record selector/SHA in the existing manifest, expose ready-model metadata and
	a cache identity. Preserve existing path/readiness and staged-download checks.
3. `classifier.py`: accept an injected manager for tests, load local AutoTokenizer
	and AutoModelForSequenceClassification with offline flags, construct the PT
	pipeline, and cache only the currently selected artifact. Build the full
	prediction record in the service, not the UI; sort/validate pipeline results.
4. `minio_storage.py`: validate complete prediction records, use `BytesIO` and
	finite JSON, create the configured bucket, and raise sanitized storage errors.
	Client injection supports strict offline mocks and opt-in live round trips.
5. `logging_config.py`: JSON formatter and allowlisted event fields; no raw
	exceptions, tokens, inputs, or unreviewed dictionaries. Services emit success
	and failure metadata without exposing sensitive values.
6. Streamlit: session-local classifier reuse, persisted labels shared by pages,
	disabled invalid submits, model/timestamp/revision display, and separate
	inference versus persistence error handling. Clear session classifier on
	lifecycle changes. Retain a simple multipage entrypoint.
7. Add strict offline service/UI tests, opt-in live MinIO tests, lint and CI,
	a dependency lock, `.dockerignore`, placeholder environment settings, and
	documented service start/stop commands. Do not auto-download real model weights.

### Basic CI setup scope (2026-11-11)

Implement the offline portion of T018 first: GitHub Actions on pushes, pull requests,
and manual dispatch; Python 3.10; pinned Ruff/pytest-socket tooling; default Ruff
error checks; and pytest with sockets disabled and Hugging Face offline flags.
Install CPU PyTorch on the runner; package installation requires network access,
but test execution must not download models or contact storage. Isolate the storage
path test from developer credentials with synthetic test-only configuration.
Preserve the existing stream-upload fix while cleaning lint errors and replacing
Python 3.11-only datetime imports to retain Python 3.10 compatibility.

Add Docker build exclusions without building an image. Document GitHub activation
and required-status configuration. This is partial constitution v1.2.0 coverage:
the separate live MinIO job, automated secret/artifact checks, dependency lock,
image digest pinning, and verified branch enforcement remain outstanding. Do not
claim release compliance from the basic workflow or mark T018 complete before
its GitHub execution and build-exclusion verification are recorded.

## 9. Constitution compliance gate for R1

| Principle | Design / task mapping | Required evidence |
| --- | --- | --- |
| Python/PT/Transformers | FR-001, T009, T031 | Local-only load and explicit PT mock assertions |
| Controlled model lifecycle | FR-001/002, T021–T025, T031 | Existing safety tests plus revision/cache tests |
| MinIO system of record | FR-005/006, T010/011/013 | Strict SDK-stream tests; real round trip separately |
| Configuration/secrets | FR-003/006, T027/T033 | Atomic label persistence, invalid credential/config tests |
| Observability/privacy | FR-007, T029 | Parseable JSON events; secret/input redaction tests |
| Reproducibility | FR-002/009, T030/T031 | Locked versions and recorded resolved commit |
| Quality gates | FR-008, T015/016/018/020 | Lint, offline tests, opt-in integration, real-model evidence |
| Decision records | ADR-001, T032 | Explicit bucket exception and honest adoption chronology |

Gate status at planning: architecture is aligned; the bucket exception is explicit
in constitution 1.1.0. Runtime compliance remains pending until implementation and
tests pass. Docker daemon availability and large model downloads are external
verification prerequisites, not grounds for marking live acceptance complete.
