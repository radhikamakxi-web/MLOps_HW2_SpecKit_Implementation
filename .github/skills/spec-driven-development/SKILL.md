---
name: spec-driven-development
description: 'Implement or update features in this zero-shot MLOps project using its Spec Kit constitution, specification, plan, data model, and tasks. Use when changing requirements, planning features, or checking implementation against acceptance criteria.'
---

# Spec-driven development

## Project context

Run commands from the repository root. Paths below are repository-relative.

Read these artifacts before changing feature behavior:
- `.specify/memory/constitution.md` — project principles and quality gates.
- `specs/001-zero-shot-platform/spec.md` — canonical requirements and acceptance criteria.
- `specs/001-zero-shot-platform/plan.md` — implementation approach.
- `specs/001-zero-shot-platform/data-model.md` — configuration and prediction contracts.
- `specs/001-zero-shot-platform/tasks.md` — implementation checklist.

Official Spec Kit v1.3.3 scripts, templates, and nine Copilot skills are installed
in `.specify/` and `.github/skills/speckit-*/`. Check `specify integration status`
and the feature prerequisite script before using them on a new machine. CLI
installation is separate from project scaffolding; do not rerun forced init over
existing work. Read `specs/001-zero-shot-platform/validation.md` for actual evidence
and `decisions/001-adoption-and-bucket.md` within that feature for the adoption history.

## Workflow

1. Review the constitution first, then identify the requested change and applicable acceptance criteria. Distinguish intended behavior from implemented behavior.
2. Update the specification, plan, data model, and tasks in that order before implementation. The `/speckit-plan` workflow produces the data model; there is no separate data-model command. Add testable tasks without marking unfinished work complete.
3. Keep changes in the appropriate layer:
   - `app/pages/` and `app/streamlit_app.py`: Streamlit presentation and orchestration.
   - `app/services/model_manager.py`: model lifecycle.
   - `app/services/classifier.py`: validation and inference.
   - `app/services/minio_storage.py`: prediction persistence.
   - `app/utils/config.py`: environment and YAML configuration.
   - `configs/`: declarative model and label settings.
4. Add targeted tests under `tests/`. Mock model downloads and external storage for unit tests; use temporary directories for filesystem operations.
5. Run affected tests, then `python -m pytest -q` using the project's selected Python environment. Report unavailable dependencies or infrastructure as blockers, not passing checks.
6. Update README instructions when setup, configuration, or user workflows change. Mark tasks complete only after their acceptance criteria have been verified.

## Guardrails

- MinIO remains the system of record; do not silently fall back to local prediction files.
- Never commit `.env`, credentials, model weights, caches, or private prediction inputs.
- Do not download large models, delete existing models, or clear real caches as incidental validation.
- Admin functionality is intended for trusted/local use; do not represent it as authenticated or production-secure.
- Document deliberate constitution exceptions with their reason, impact, and mitigation.

## Completion report

Summarize changed requirements, implementation files, tests actually run and their results, and any remaining acceptance gaps. Do not claim full conformance based only on the current small unit-test suite.