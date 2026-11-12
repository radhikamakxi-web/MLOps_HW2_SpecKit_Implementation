# Validation evidence and current status

## Scope

The official Spec Kit v1.3.3 workflows are installed for GitHub Copilot. The
application's R1 remediation is partially implemented, not a completed release.
The original homework remains the source guideline; [ADR-001](decisions/001-adoption-and-bucket.md)
records the adoption chronology and explicit bucket-name exception.

## Historical baseline: workflow adoption

- Copilot integration reported OK with no missing or modified managed files.
- All six generated Bash scripts passed syntax checks.
- Feature prerequisites, plan/task template resolution, and new-feature dry-run passed.
- Application suite: 60 model-manager tests and 64 total tests passed using mocks
  and temporary directories. No real model download, real inference, or live MinIO
  upload was verified by that result.

These checks preceded R1 code changes. They must not be presented as a current
full-suite pass.

## R1 status at documentation cleanup

Completed planning sequence: constitution review/amendment → specification → plan
→ data model → task breakdown, before R1 application edits. This forward sequence
does not prove the original implementation followed that order.

Partial application changes exist in `app/utils/config.py`,
`app/utils/logging_config.py`, and `app/services/prediction.py`: label persistence
helpers, required storage configuration, structured logging support, and prediction
validation. They are not yet integrated throughout the UI and service flow or
validated by an updated full test suite. Required credentials also mean the old
MinIO test must be adapted rather than assumed to keep passing without setup.

The documentation cleanup updates the README and canonical references, removes
superseded compatibility/archive files, and aligns `.env.example` with the current
configuration helpers. It does not complete the remaining runtime tasks.

### Documentation-cleanup checks

- All 28 relative links/anchors checked across eight project documents resolve;
  code fences are balanced and no active reference to the deleted files remains.
- All 21 official managed-file hashes match; all nine official skills are intact.
- `specify integration status`: OK, zero missing or modified managed files.
- `specify workflow list`: bundled Full SDD Cycle is installed.
- Read-only feature prerequisites resolve the canonical spec, plan, and tasks.
- No application test suite or live service was run during this documentation cleanup.

## Basic CI setup validation (2026-11-11)

- Added a GitHub Actions workflow for Python 3.10 lint and offline tests on
  push/pull request/manual dispatch, plus pinned Ruff/pytest-socket tools and
  Docker build exclusions. No GitHub workflow run or image build was performed.
- Preserved the user's readable-stream upload fix. Removed duplicate/unused
  imports and used `timezone.utc` instead of the Python 3.11-only `datetime.UTC`
  to retain the declared Python 3.10 runtime compatibility.
- Isolated the storage-path test with synthetic environment settings; it still
  does not exercise real uploads or validate the complete persistence contract.
- Workflow YAML structure, triggers, permissions, and required commands passed
  static checks. Application/test files parsed using Python 3.10 syntax rules;
  this does not establish Python 3.10 runtime or dependency compatibility.
- Local environment: macOS, project virtual environment, Python 3.14.7.
  `python -m ruff check app tests`: **passed**.
  `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_TELEMETRY=1 python -m pytest -q --disable-socket`:
  **64 passed**, with network sockets disabled. No live services or models used.
- This is fresh local evidence, not a Python 3.10 GitHub-run result, end-to-end
  verification, or proof of full constitutional compliance. T018 remains open
  pending GitHub execution/build-exclusion verification. Required status checks
  must be configured and verified by a repository maintainer.

## Outstanding acceptance evidence

- Updated unit/UI tests and lint after completing R1 service/UI integration.
- Live MinIO round trip with a valid bucket and required credentials. Docker's
  daemon was unavailable at the start of R1; no live pass has been recorded.
- Real downloaded model → local PyTorch inference → persisted JSON demonstration.
- Dependency lock, CI execution, and safe image-building validation.

Consult [tasks.md](tasks.md) for pending work. Mark each task complete only after
its own acceptance checks run; do not infer runtime correctness from workflow setup.