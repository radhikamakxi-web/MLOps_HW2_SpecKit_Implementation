# Tasks: Zero-Shot Text Classification Platform

**Inputs**: [spec.md](spec.md), [plan.md](plan.md), [data-model.md](data-model.md),
and the [constitution](../../.specify/memory/constitution.md).

This checklist adapts the original task breakdown to the official Spec Kit format.
This file is the single active task list; superseded duplicate task documents have
been removed. Adoption history is recorded in [ADR-001](decisions/001-adoption-and-bucket.md).
Checked items describe implemented work with the evidence noted below, not proof
that the entire application is production-ready. Unfinished features stay unchecked.

## Phase 1: Setup and configuration

- [x] T001 Initialize the Python package and dependency/test configuration in `app/`, `pyproject.toml`, and `requirements.txt`.
- [x] T002 Configure both supported model IDs in `configs/models.yaml`.
- [x] T003 Create the candidate-label YAML seed in `configs/labels.yaml` (UI persistence is T027).
- [x] T004 Load environment settings and YAML through `app/utils/config.py`.

## Phase 2: Model management and offline tests

- [x] T005 Implement staged Hugging Face downloads in `app/services/model_manager.py`.
- [x] T006 Implement readiness checks and reuse of complete models in `app/services/model_manager.py`.
- [x] T007 Implement selected-model deletion in `app/services/model_manager.py`.
- [x] T008 Implement configured Hugging Face cache cleanup in `app/services/model_manager.py`.
- [x] T012 Create model download/delete/cache controls in `app/pages/1_Admin.py` (label saving is T027).
- [x] T015 Add offline unit tests in `tests/test_model_manager.py`, `tests/test_classifier.py`, and `tests/test_minio_storage.py`; live upload coverage remains T016.
- [x] T021 Reject unsafe model IDs, model-directory symlinks, and paths outside the model root in `app/services/model_manager.py`.
- [x] T022 Avoid namespace/underscore path collisions in `app/services/model_manager.py`.
- [x] T023 Require a completion manifest and structurally valid nonempty model/tokenizer files, including indexed shards, in `app/services/model_manager.py`.
- [x] T024 Clean up staging on download/validation failure while preserving pre-existing model directories in `app/services/model_manager.py`.
- [x] T025 Replace expected failures with regression coverage for artifact layouts, symlinks, retries, and deletion in `tests/test_model_manager.py`.
- [x] T026 Document legacy-download migration and structural-validation limits in `README.md`.

## Phase 3: Complete inference, labels, and persistence

These are existing application gaps, not work performed merely by installing Spec Kit.
For each task, add focused failing tests first, implement the fix, and then run regressions.

- [ ] T009 Complete managed-local inference in `app/services/classifier.py` and `app/pages/2_Classify_Text.py`; use the validated local model path rather than redownloading by repository ID, and test pipeline reuse/result shaping.
- [ ] T027 Implement add/remove/save label configuration via `app/utils/config.py`, `configs/labels.yaml`, and both Streamlit pages; add persistence and validation tests.
- [ ] T010 Complete bucket creation validation in `app/services/minio_storage.py` and `tests/test_minio_storage.py`; resolve the underscore-containing default bucket against S3 naming rules, documenting any necessary constitution/specification change before changing the default.
- [ ] T011 Fix `save_prediction()` in `app/services/minio_storage.py` to upload a readable binary stream; test Unicode JSON, byte length, request IDs, bucket behavior, and upload failures in `tests/test_minio_storage.py`.
- [ ] T013 Finish `app/pages/2_Classify_Text.py` integration: show model/timestamp metadata, use persisted labels, and distinguish inference success from successful storage.
- [ ] T014 Prevent classification without a ready model and test invalid-input/error handling across `app/pages/2_Classify_Text.py` and the service tests.

## Phase 4: Integration, documentation, and release checks

- [ ] T016 Add opt-in live MinIO integration tests under `tests/` using a dedicated test bucket and synthetic data; document configuration in `README.md`.
- [x] T017 Add MinIO service configuration in `docker-compose.yml` and the app `Dockerfile` (live container verification is T020).
- [ ] T018 Add a CI workflow in `.github/workflows/` for offline tests, and a `.dockerignore` before building images so credentials, environments, and model artifacts are excluded.
	- Basic CI scope (2026-11-11): add Python 3.10 Ruff/offline pytest checks on push/PR/manual runs, pinned test tools, network-disabled tests, isolated storage-test settings, and build exclusions. Fix only blocking imports/runtime compatibility; preserve the existing upload change. Keep this task open until GitHub execution and build exclusions are verified. Separate live MinIO CI, automated hygiene checks, and required-status enforcement remain outstanding.
- [x] T019 Document setup, architecture, model management, tests, and current limitations in `README.md`; keep it updated when pending tasks are implemented.
- [ ] T020 Validate and record the real model-download → inference → MinIO JSON flow in `README.md`; requires T009–T014, T016, and T027. Do not report this complete from mocked tests.
- [x] T028 Verify official Spec Kit integration, workflow discovery, feature prerequisites, and unchanged application regressions; document usage in `README.md`.

## R1 remediation tasks (recorded before application changes)

The constitution was reviewed first, then `spec.md`, `plan.md`, and
`data-model.md` were updated in that order before this task update. This is a
forward remediation iteration, not proof of the original creation order.

- [ ] T029 Implement allowlisted JSON lifecycle/inference/storage events in `app/utils/logging_config.py` and services; add privacy/redaction tests (FR-007).
- [ ] T030 Record Python/package versions and a repeatable dependency lock; align Docker/CI setup and reproduction instructions (FR-009).
- [ ] T031 Resolve model selectors to immutable commits, record provenance, cache local PT pipelines by artifact identity, and test these contracts (FR-001/002).
- [ ] T032 Apply ADR-001 consistently to the constitution/spec/configuration/docs and record honest chronology and actual test evidence in `validation.md`.
- [ ] T033 Require environment-supplied storage credentials, validate bucket configuration, and prevent secret-bearing exceptions from reaching logs/UI (FR-005/006).
- [ ] T034 Add Streamlit interaction tests for model/label gating, persisted labels, metadata, and storage failure semantics (FR-003/004/006).

Execute T032's decision/spec alignment first; shared config/logging next; then
T009/010/011/027/029/031/033 core contracts; T013/014/034 UI; T016/018/030 checks.
Do not mark T020 complete without a real model and live MinIO demonstration.

## Dependencies and execution rules

- Phase 1 precedes Phase 2. T027 and T009 are prerequisites for T013; T010 and T011 precede T016. Finish functional gaps before T020.
- Tasks touching the same files must run sequentially. No parallel `[P]` markers are assigned in this migrated backlog.
- Live model downloads, cache deletion, and shared-storage cleanup require explicit intent; offline tests use mocks and temporary directories.
- Work only on requested pending task IDs; `/speckit-implement` without a scope may attempt the entire remaining backlog.

## Validation evidence

Current validation status and blockers are recorded in [validation.md](validation.md).
The results below are historical workflow-adoption evidence, before partial R1
application changes; they do not certify the current implementation. R1 core/UI,
CI, and verification work remains pending while documentation cleanup is performed.

Before workflow adoption: 60 model-manager tests and 64 total tests passed using
mocked downloads and temporary directories. No live model download or inference
was performed. T020 remains incomplete until actual end-to-end verification.

Workflow-adoption validation: `specify integration status` reports OK with no
modified or missing managed files; the bundled workflow is discoverable; all six
Bash scripts pass syntax checks; feature prerequisites resolve `spec.md`,
`plan.md`, and `tasks.md`; plan/task template resolution and new-feature dry-run
succeed without overwriting project documents. Official file hashes, all three
custom skills, and the original constitution were checked. The full application
test suite was rerun: **64 passed**. No agent-driven full SDD cycle was executed.
