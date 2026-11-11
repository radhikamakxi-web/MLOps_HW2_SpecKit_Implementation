# Constitution: Zero-Shot Text Classification Platform

**Version:** 1.1.0 (remediation iteration R1).
Reviewed before R1 specification, plan, data-model, task, and code changes.
This review does not establish the creation order of the original implementation.

## 1. Purpose

The project exists to build a reproducible Python-based zero-shot text classification platform using PyTorch, Hugging Face Transformers, Streamlit, and MinIO for learning and demonstrating MLOps practices.

## 2. Scope

In scope for v1:

- Local configuration-driven model registry
- Streamlit admin page and classification page
- Zero-shot text classification with candidate labels
- Model download, reuse, deletion, and cache cleanup
- JSON prediction persistence in MinIO
- Automated tests and documentation

Out of scope for v1:

- User authentication and authorization
- Multi-user admin workflows
- Large-scale production deployment orchestration
- Non-MinIO storage backends

## 3. Reproducibility

- Dependencies, Python version, model identifiers, and revisions must be documented.
- Model configuration must be declarative and versionable.
- All environment-specific settings must be loaded from environment variables or local config files.
- Download selectors must resolve to immutable Hugging Face commit hashes before download. Record the selector and resolved commit in the local manifest and prediction record. Unknown legacy revisions must be reported as unknown, never fabricated as `main`.

## 4. Configuration and Secrets

- Secrets are never committed to Git.
- Credentials must be supplied through `.env` or platform environment variables.
- No tokens, access keys, or `.env` files are committed.

## 5. Model Lifecycle Management

- Models are downloaded from Hugging Face and stored in a controlled local directory.
- Existing models are reused when available.
- Model deletion and cache cleanup are explicit administrator actions.
- Partially downloaded models are not treated as valid.

## 6. Data Persistence

- This S3-compatible default replaces the homework's underscore-containing name; see [ADR-001](../../specs/001-zero-shot-platform/decisions/001-adoption-and-bucket.md). `MINIO_BUCKET` remains configurable and invalid names are rejected rather than silently rewritten.
- A request is successful only after its classification is persisted as structured JSON in the configured MinIO bucket, defaulting to `zeroshot_learning_output`.
- MinIO is the mandatory object-store system of record for prediction outputs.
- Local files may be used for temporary processing or caches, but must not replace MinIO.

## 7. Separation of Concerns

- Streamlit UI code remains UI-only.
- Model management is handled by a dedicated service layer.
- Inference logic is isolated in a classifier service.
- MinIO storage logic is isolated in a storage service.
- Configuration is loaded through a utilities layer.

## 8. Testing Standards

- Unit tests cover each major service and data-validation flow.
- Integration tests cover MinIO interactions when MinIO is running.
- Large downloads are mocked or lightweight fixtures are used whenever practical.

## 9. Error Handling

- Invalid input, unavailable models, failed downloads, and MinIO failures must yield clear error messages.
- Secrets must never appear in logs.
- Application behavior must fail gracefully without exposing credentials.

## 10. Observability

- Model download, classification, cache cleanup, and MinIO writes are logged with useful metadata.
- Logs should not include sensitive input or credentials.
- Use structured JSON events with allowlisted metadata. Never log raw input, credential values, or raw external exception messages; user-facing errors must also omit these details.

## 11. Security and Privacy

- Admin access is intended for local development or trusted environments unless authentication is added.
- Sensitive credentials are never logged.
- Input payloads are sanitized and validated before inference.

## 12. Documentation

- Setup, quick start, model management flow, MinIO usage, testing, and troubleshooting must be documented.
- The README must explain the system clearly to a new developer.

## 13. Quality Gates

- Automated tests must pass before the project is considered complete.
- Formatting or lint checks should be run when available.
- Acceptance criteria must be satisfied.

## 14. Decision Record Process

Any deliberate exception to these principles must be documented in writing with the reason, impact, and mitigation plan.

## 15. Technology Consistency

- Application logic must be implemented in Python; shell/YAML/JSON may support tooling, configuration, and deployment.
- PyTorch is required for loading and running models.
- Inference must explicitly use the PyTorch backend and local-only model/tokenizer loading. Never silently switch frameworks or download during classification.
- Transformers is used for zero-shot classification pipeline support.
- Streamlit is used for UI.
- MinIO is used for prediction persistence.

## 16. Compliance Check

All pull requests or final submissions must verify:

- configuration is environment-driven;
- no model artifacts or credentials are committed;
- no `.env` file is tracked;
- automated tests pass; and
- the README contains reproduction instructions.
- revision provenance, structured logging, persisted labels, and MinIO error handling are covered by tests;
- lint and offline tests pass; live integration and live-model smoke checks are reported separately and never implied by mocked tests.
