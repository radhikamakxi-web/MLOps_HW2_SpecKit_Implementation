# Specification: Zero-Shot Text Classification Platform

**R1 review:** Updated after constitution 1.1.0 review and before R1 planning/code.
The original requirements remain below, with the bucket exception recorded in
[ADR-001](decisions/001-adoption-and-bucket.md).

## 1. Purpose and Scope

The project provides a small MLOps-style zero-shot text classification platform using Streamlit, Hugging Face Transformers, PyTorch, and MinIO. The initial version supports model management, candidate-label configuration, text classification, and persistent JSON storage of prediction results.

## 2. Roles and Users

- Administrator: downloads and manages zero-shot models, configures labels, and inspects local cache state.
- End user: provides input text, selects model and labels, and views prediction results.

## 3. User Stories

- As an administrator, I can view the configured zero-shot models.
- As an administrator, I can download a model when it is missing.
- As an administrator, I can delete a downloaded model and clear the Hugging Face cache.
- As an administrator, I can define candidate labels and save them for later use.
- As a user, I can classify input text using a selected model and label set.
- As the system, I persist every successful classification in MinIO as JSON.

## 4. Functional Requirements

### Model management

- The app shall expose at least two configured zero-shot models.
- The app shall display model availability and local path status.
- The app shall download a model only when missing or explicitly requested.
- The app shall allow deletion of a local model directory.
- The app shall allow clearing the global Hugging Face cache.
- Local readiness shall require validated configuration, tokenizer artifacts, complete nonempty PyTorch weights (including every indexed shard), and a completion manifest written after a successful download. Empty folders and unverified legacy downloads are not ready.
- Model identifiers and resolved paths shall be validated before download or deletion; model-directory symlinks and paths outside `MODEL_DIR` shall be rejected.
- Downloads shall be staged beneath `MODEL_DIR` and published only after validation. Download or artifact-validation failures shall preserve previously existing directories and remove only their own staging directory.

### Candidate labels

- The app shall permit adding, removing, and saving a label set.
- Labels must be trimmed, deduplicated, and must not be empty.
- At least two labels must be provided before classification.

### Classification

- The app shall allow input text and candidate-label selection.
- The app shall validate input and available models before inference.
- The app shall show predicted class, confidence score, and ranked predictions.
- The app shall record the model identifier and timestamp.

### MinIO persistence

- Each successful prediction shall be saved to MinIO under the configured bucket.
- The default bucket is `zeroshot-learning-output`, configurable via `MINIO_BUCKET` and validated without silent name rewriting (ADR-001).
- The object path shall follow `predictions/YYYY/MM/DD/{request_id}.json`.

## 5. Non-Functional Requirements

- Python implementation only.
- PyTorch is used for inference.
- Environment variables are used for configuration.
- Secrets are not committed to Git.
- Structured logs should capture key operations.

## 6. Acceptance Criteria

- The app starts without code edits using documented commands.
- MinIO bucket creation is automatic.
- Models are downloadable and deletable from local storage.
- The user can classify text and view ranked results.
- Each prediction is stored as JSON in MinIO.
- Unit and integration tests pass with the documented setup.

## 7. R1 measurable contracts and edge cases

- **FR-001 Local inference:** Classify only a model with a valid managed completion manifest. Load model and tokenizer from its resolved local directory with `local_files_only=True`, `trust_remote_code=False`, and pipeline `framework="pt"`. Reject missing/incomplete models before pipeline creation. Cache only one pipeline per classifier, keyed by artifact identity, and invalidate UI session state after model deletion/download changes.
- **FR-002 Revisions:** Resolve each configured revision selector (default `main`) through Hugging Face metadata to an immutable SHA, download that exact SHA, and record selector/SHA. Availability must not reuse a manifest for a different requested selector. Legacy manifests may be reused for the default selector but must report an unknown resolved revision honestly.
- **FR-003 Labels:** Load one saved label set from configurable YAML. Trim whitespace, remove empty values and exact duplicates, preserve order, reject non-string labels and fewer than two unique labels. Admin add/remove/save operations persist atomically; classification reads the same file.
- **FR-004 Prediction:** Require nonblank string text and valid labels. Reject malformed pipeline output; sort all returned scores descending; highest score determines predicted class. Return UUID, UTC timestamp, input, candidate labels, ranking, confidence, model ID/name, actual revision or null, app version, and latency.
- **FR-005 Storage:** Validate payload and bucket configuration; serialize JSON once using finite numeric values, upload a readable binary stream with its exact byte length and JSON content type. Preserve request ID and use date-based object keys. Create missing buckets, including safe handling of an already-created bucket race.
- **FR-006 Failure semantics:** No ready model or invalid label set disables classification. A storage failure can display the inference result but must say it was NOT saved. Report sanitized actionable errors; do not leak raw exception strings or credentials. No local prediction fallback.
- **FR-007 Observability:** Emit structured allowlisted events for downloads/reuse/deletion/cache cleanup, label saves, inference, and storage. Never include input text, arbitrary exception messages, or credentials.
- **FR-008 Verification:** Offline tests cover local-only loading, pipeline reuse, ranking, labels, storage contracts/failures, revision metadata, logging redaction, and Streamlit validation. Opt-in MinIO tests create/read/delete only a unique test-owned bucket. CI runs lint/offline tests and a separate live MinIO job.
- **FR-009 Reproducibility:** Record Python/dependency versions and a repeatable dependency lock; pin/document model revisions and container image. Document separate outcomes for mocked tests, real storage tests, and real-model smoke checks.

Security boundary: no authentication or multi-admin concurrency in v1; bind local
services to loopback by default. Use synthetic input for tests. Sensitive inference
inputs are intentionally present in stored prediction JSON, never in logs.
