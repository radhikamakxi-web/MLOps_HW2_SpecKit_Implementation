# Zero-Shot Text Classification Platform

## Purpose

This learning project provides a zero-shot text classification platform using PyTorch, Hugging Face Transformers, Streamlit, and MinIO. It separates model management, inference, configuration, and storage into dedicated layers and includes official Spec Kit v1.3.3 workflows for GitHub Copilot alongside the existing project specifications.

**Start here:** [Spec Kit workflows](#spec-kit-installation-and-project-status) ·
[Application quick start](#quick-start) · [Tests](#running-tests) ·
[Current tasks](specs/001-zero-shot-platform/tasks.md) ·
[Validation evidence](specs/001-zero-shot-platform/validation.md)

## Current Implementation Status

Model management has offline regression coverage, and the official Spec Kit workflows
are installed. Remediation R1 is **in progress**, not a completed release. Current gaps:


| Area             | Current behavior / limitation                                                                                                                                                     |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Labels           | YAML load/save helpers now exist, but the pages still hardcode options and Admin**Save labels** is not wired to persistence.                                                      |
| Inference        | Classification still passes a repository ID rather than the managed local path; offline reuse and explicit PyTorch loading remain pending.                                        |
| Storage          | `save_prediction()` still passes bytes rather than a readable stream. The new prediction validation module is not yet connected to the classifier/storage path.                   |
| Configuration    | The default bucket is now`zeroshot-learning-output`; storage credentials must be supplied through the environment. Existing environments using the old bucket name need updating. |
| Revision/logging | Revision metadata is still hardcoded as`main`. Structured logging support exists, but operation-wide integration and redaction tests remain pending.                              |
| Verification     | No CI or live MinIO integration suite exists yet. The earlier 64-test result predates the partial R1 code changes; it is not a current full-suite pass.                           |

The instructions below distinguish the implemented workflow from these remaining tasks. A displayed prediction alone is not proof that storage succeeded.

## Architecture Overview

The application is separated into several key layers:

- Streamlit pages: UI for administrators and users
- Model manager: local model lifecycle and configuration
- Classifier: zero-shot inference using Hugging Face `pipeline`
- MinIO storage: JSON persistence for predictions
- Configuration utilities: environment and YAML loading

```text
Streamlit Admin ──> ModelManager ──> Hugging Face / local model files
Streamlit Classify ──> ZeroShotClassifier ──> Transformers pipeline
                   └─> MinIOStorage ──> MinIO JSON object (upload fix pending)
Configuration utilities ──> environment settings and YAML configuration
```

## Project Structure

```text
MLOpsHomework2/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── .github/skills/             # Nine official speckit-* skills + three custom skills
├── .vscode/tasks.json         # Local launch task; interpreter path is machine-specific
├── configs/
│   ├── models.yaml
│   └── labels.yaml
├── app/
│   ├── streamlit_app.py
│   ├── pages/
│   │   ├── 1_Admin.py
│   │   └── 2_Classify_Text.py
│   ├── services/
│   │   ├── model_manager.py
│   │   ├── classifier.py
│   │   ├── minio_storage.py
│   │   └── prediction.py      # R1 contract helper; integration pending
│   └── utils/
│       ├── config.py
│       └── logging_config.py
├── models/                    # Runtime downloads; ignored by Git
├── tests/
│   ├── test_model_manager.py
│   ├── test_classifier.py
│   └── test_minio_storage.py
├── specs/
│   └── 001-zero-shot-platform/
│       ├── spec.md            # Canonical specification used by Spec Kit
│       ├── plan.md
│       ├── data-model.md
│       ├── tasks.md           # Task IDs, checkboxes, dependencies, and evidence
│       ├── validation.md      # Actual checks, historical baseline, and blockers
│       └── decisions/         # Explicit adoption/bucket decision
└── .specify/
    ├── init-options.json
    ├── integration.json
    ├── integrations/          # Official managed-file manifests
    ├── feature.json           # Machine-local active feature; ignored by Git
    ├── memory/constitution.md # Reviewed project principles and R1 amendments
    ├── scripts/bash/          # Official feature/setup/prerequisite scripts
    ├── templates/             # Official specification/plan/task templates
    └── workflows/speckit/workflow.yml
```

## Supported Models

The app includes at least two zero-shot models by default:

- `MoritzLaurer/deberta-v3-base-zeroshot-v2.0`
- `facebook/bart-large-mnli`

The model list is configured in [`configs/models.yaml`](configs/models.yaml). Add an entry with `id`, `name`, and `task: zeroshot-learning-output` to extend the list. Being configured does **not** mean a model has been downloaded.

## Model Management Workflow

1. Start the application.
2. Open the admin page.
3. Review the configured model list and local status.
4. Click Download for a model that is missing local files.
5. The model is stored under `MODEL_DIR` using an encoded model ID, as shown below.
6. Downloaded models are reused when already available.
7. Administrators can delete individual models or clear the Hugging Face cache.
8. Model identifiers are validated, literal underscores are escaped as `%5F` and `/` is replaced with `__` to avoid name collisions. Resolved model paths must remain direct children of `MODEL_DIR`. Model-directory symlinks are rejected.

```text
models/
├── MoritzLaurer__deberta-v3-base-zeroshot-v2.0/
│   └── .model-complete.json   # Alongside downloaded configuration/tokenizer/weights
└── facebook__bart-large-mnli/
    └── .model-complete.json
```

Statuses are `available` (validated local model), `missing` (absent or not ready), and `invalid` (unsafe identifier or path). Refresh the page after downloading or deleting to update the displayed status. **Only download one model initially** if you want to limit disk and network use.

## Candidate Labels

`configs/labels.yaml` contains a proposed default set, but the current pages use hardcoded options:

- sports
- politics
- technology
- finance
- health
- education

The classification page lets you select from these labels. The classifier trims whitespace, removes empty values and case-sensitive duplicates, and requires at least two unique labels. `app/utils/config.py` now provides `load_labels()` and atomic `save_labels()` helpers using `LABELS_CONFIG`; connecting those helpers to **Save labels** and the classification page remains unfinished.

## MinIO Bucket and Prediction Output

/constitutionThe application uses `MINIO_BUCKET`, defaulting to the S3-compatible name
`zeroshot-learning-output`. Invalid names are rejected rather than silently
rewritten. The naming exception to the homework example is documented in
[ADR-001](specs/001-zero-shot-platform/decisions/001-adoption-and-bucket.md) and
constitution 1.1.0. The storage service attempts to create the configured bucket
when missing; the upload fix remains pending.

The intended persistence contract is one JSON object per successful classification, using a path similar to:
`predictions/YYYY/MM/DD/{request_id}.json`

The classification page constructs a payload containing:

- `request_id`
- `timestamp`
- `input_text`
- `predicted_class`
- `confidence`
- `candidate_labels`
- `ranked_predictions`
- `model`
- `model_revision`
- `application_version`

The page displays classification results before attempting the write. Until the raw-bytes upload bug is fixed, do not treat this intended persistence contract as a verified feature.

## Required Software

- Python 3.10+ for the app; Python 3.10 was used for the last regression run. Dependency compatibility with newer Python releases must be checked separately.
- A virtual environment or Conda environment and pip.
- Docker Desktop or Docker Engine with Compose for local MinIO.
- Internet access for package/model downloads and sufficient memory/disk for large models, caches, and staging copies.
- For Spec Kit development tooling: Git, `uv`, and Python 3.11+. The installation below uses an isolated Python 3.12 tool environment rather than changing the app's Python version.

## Environment Configuration

Run commands from the repository root. Copy `.env.example` to `.env` if `.env` does not already exist; otherwise edit the existing file rather than overwriting it:

```bash
cp .env.example .env
```

For Streamlit running on your host and MinIO running in Compose, use:

```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=replace-me
MINIO_SECRET_KEY=replace-me
MINIO_SECURE=false
MINIO_BUCKET=zeroshot-learning-output
MODEL_DIR=./models
LABELS_CONFIG=./configs/labels.yaml
HF_HOME=./.cache/huggingface
TRANSFORMERS_CACHE=./.cache/huggingface/transformers
HF_TOKEN=
APP_VERSION=0.1.0
```

`.env.example` now targets a host-run app using `localhost:9000`. Use `minio:9000`
only when the app shares the MinIO Compose network. Endpoints contain a host and
port, not an `http://` prefix; `MINIO_SECURE` controls TLS.

`MODEL_DIR`, `LABELS_CONFIG`, `HF_HOME`, and `TRANSFORMERS_CACHE` are resolved
relative to the project root when given as relative paths. `HF_TOKEN` can be
consumed by Hugging Face tooling for authenticated downloads; never commit or
print it. Replace both credential placeholders before using storage. The current
Compose file uses `minioadmin` / `minioadmin` for local development; the client
credentials must match the server. Change both sides for a shared deployment.

## Quick Start

### 1. Create the environment

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\Activate.ps1` instead. You can also use an existing compatible Conda environment. Configure `.env` as described above before launching.

### 2. Start MinIO

```bash
docker compose up -d minio
```

Open the MinIO console at:

- http://localhost:9001

### 3. Start the Streamlit app

```bash
PYTHONPATH=. python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

This macOS/Linux command explicitly makes the project package importable. In PowerShell, set `$env:PYTHONPATH = "."` first, then run the same `python -m streamlit ...` command without the `PYTHONPATH=.` prefix.

Open **http://127.0.0.1:8501**. This is a local URL, not a public hosted deployment. The existing VS Code task **Run local Streamlit app** contains an absolute interpreter path specific to the development machine; adjust it before using the task on another machine.

### 4. Use the app

- Open http://localhost:8501
- Go to the Admin page
- Download a model
- Choose labels
- Go to the classification page
- Submit input text
- Review predicted class and confidence

Download a model successfully before using **Classify**. The UI warns when no local model is available, but the button is not disabled. Storage testing remains blocked by the upload issue described above.

## Model Download and Cache Behavior

- Models are checked against the local `MODEL_DIR` before download.
- A model is available only when its `.model-complete.json` manifest matches its ID and required files: a valid model configuration, tokenizer artifacts, and nonempty PyTorch weights (including all indexed shards). A separate `tokenizer_config.json` is validated when present but is optional for layouts that infer tokenizer settings from the model configuration.
- If a model is already available and its recorded artifact sizes still match, the app does not re-download it.
- Downloads use a unique `.download-*` staging directory under `MODEL_DIR`. Only a completed, structurally validated download is published to its final directory.
- On download or validation failure, staging data is removed and a pre-existing incomplete copy is preserved. Retrying a successful download replaces that incomplete copy.
- Empty folders, missing/empty artifacts, missing shards, malformed JSON, and unsafe paths are not treated as ready models.
- **Migration:** folders downloaded by the earlier implementation have no completion manifest. They appear as `missing`; use the Admin **Download** button to download and validate them again. Allow room for a temporary second copy. Do not create a manifest manually to bypass validation.
- These checks do not deserialize weights or detect same-size file corruption. A live inference smoke test is still needed to confirm model loadability.
- Abrupt process termination may leave a `.download-*` staging directory, but it is never reported as a ready model. Remove such leftovers only after confirming no download is running. Concurrent administration is not supported.
- **Delete [model]** removes that model's managed directory. **Clear Hugging Face cache** removes the configured `HF_HOME` directory and recreates it empty; it does not remove a separate `MODEL_DIR` or a `TRANSFORMERS_CACHE` configured outside `HF_HOME`. Only point these settings at dedicated application directories.
- Downloaded model artifacts are not committed to Git.

## Verifying Stored Predictions in MinIO

First fix the upload stream handling and configure a valid bucket name. Then:

1. Start MinIO and run a classification from the Streamlit page.
2. Confirm the success message includes the object path.
3. Open the MinIO console at http://localhost:9001.
4. Navigate to the bucket configured by `MINIO_BUCKET` (for the local example, `zeroshot-learning-output`).
5. Open the saved `predictions/YYYY/MM/DD/{request_id}.json` object.

Check that the JSON matches the input, selected model, labels, and displayed scores. This is a manual integration procedure, not a completed live verification.

## Docker Support

`docker-compose.yml` starts **MinIO only**, exposes the API on port 9000 and the console on port 9001, and persists data in the `minio_data` named volume. It does not launch Streamlit.

`Dockerfile` describes a Python 3.10 Streamlit image, but a complete app-and-MinIO container deployment has not been validated. Before building an image, add an appropriate `.dockerignore`: the current `COPY . .` would otherwise include local files such as `.env`, environments, model weights, and caches. Git ignore rules do not exclude files from a Docker build context. Do not publish an image containing credentials.

## Running Tests

```bash
python -m pytest -q tests/test_model_manager.py
python -m pytest -q
```

The last complete run **before R1 code changes** reported 60 model-manager tests
and 64 total tests passing. It used mocked downloads and temporary directories,
not live inference or MinIO. Do not treat that result as validation of the current
partial changes: tests still need to be adapted to required storage credentials
and the new contracts, then rerun.

[Validation evidence](specs/001-zero-shot-platform/validation.md) separates
historical results, workflow checks, and blocked or unexecuted checks. Dependencies
currently use minimum-version constraints, not a reproducible lockfile.

## Spec Kit Installation and Project Status

The official **Specify CLI v1.3.3** was installed and verified on the development machine on November 9, 2026, using `uv` and isolated Python 3.12.13. This machine-level installation is separate from the application dependencies and is not included in `requirements.txt`.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Git if needed. On a new development machine, install the pinned CLI release:

```bash
uv tool install specify-cli --python 3.12 --from git+https://github.com/github/spec-kit.git@v1.3.3
uv tool update-shell
```

The `--python 3.12` option keeps the CLI separate from the app's Python 3.10 environment. `uv` can provision that interpreter if needed. Restart your terminal if PATH was updated. For the current macOS/Linux shell, the typical tool location can also be enabled with:

```bash
export PATH="$HOME/.local/bin:$PATH"
specify version
specify check
```

`specify version` should report **1.3.3**. The prerequisite check may report optional agent CLIs as absent; GitHub Copilot does not require a separate CLI for this integration. VS Code still needs the appropriate agent available and authenticated.

**This workspace now contains the official workflows.** They were generated using
the installed v1.3.3 CLI with `--integration copilot --script sh` in a temporary
directory, reviewed, and merged without overwriting the existing constitution or
the three custom skills. Generated scripts/templates/skills are unmodified, and
their official manifests support later integrity checks and upgrades.

The existing feature is selected through `.specify/feature.json`. Its documents are:

- [Constitution](.specify/memory/constitution.md)
- [Canonical specification](specs/001-zero-shot-platform/spec.md)
- [Implementation plan](specs/001-zero-shot-platform/plan.md)
- [Data model](specs/001-zero-shot-platform/data-model.md)
- [Task breakdown](specs/001-zero-shot-platform/tasks.md)

`spec.md` is the single canonical specification, and `tasks.md` is the active
implementation checklist. Superseded compatibility documents and the duplicate
task archive have been removed; all current references use these canonical files.

The project adopted official Spec Kit workflows after initial application code
already existed. That historical ordering cannot be repaired retroactively.
For remediation R1, the constitution was reviewed and amended first, followed by
the specification, plan, data model, and tasks before code changes. See
[ADR-001](specs/001-zero-shot-platform/decisions/001-adoption-and-bucket.md).

### Required deliverable order


| Order | Deliverable              | Workflow / artifact                                                                                   |
| ----- | ------------------------ | ----------------------------------------------------------------------------------------------------- |
| 1     | Review the constitution  | `/speckit-constitution` and `.specify/memory/constitution.md`                                         |
| 2     | Specify the feature      | `/speckit-specify` → `spec.md`                                                                       |
| 3     | Plan implementation      | `/speckit-plan` → `plan.md`                                                                          |
| 4     | Review the data model    | Produced during`/speckit-plan` → `data-model.md`; there is no separate data-model skill              |
| 5     | Break down tasks         | `/speckit-tasks` → `tasks.md`                                                                        |
| 6     | Implement reviewed tasks | `/speckit-analyze` before scoped `/speckit-implement`; validate results before marking tasks complete |

Review constitution alignment at each step. Do not claim that generating files
or passing workflow prerequisites proves implementation completeness.

### Use the workflows in GitHub Copilot

Open this folder in VS Code with GitHub Copilot Chat available and authenticated.
Reload the window or start a new chat if the newly added skills are not discovered.
Enter these commands in **Copilot Chat**, not in the terminal:


| Skill                   | Purpose                                                                                              |
| ----------------------- | ---------------------------------------------------------------------------------------------------- |
| `/speckit-constitution` | Review or update project principles. Preserve existing decisions unless explicitly changing them.    |
| `/speckit-specify`      | Specify a new feature; creates/selects feature artifacts.                                            |
| `/speckit-clarify`      | Resolve ambiguity in the active specification.                                                       |
| `/speckit-plan`         | Develop or revise the implementation plan and design artifacts.                                      |
| `/speckit-tasks`        | Generate or revise an actionable task checklist.                                                     |
| `/speckit-analyze`      | Check consistency across the specification, plan, and tasks without implementing changes.            |
| `/speckit-checklist`    | Create requirements-quality review checklists.                                                       |
| `/speckit-implement`    | Execute the task checklist; give a task scope if you do not want the whole backlog attempted.        |
| `/speckit-converge`     | Assess remaining gaps and append necessary work; it is not evidence of completion until checks pass. |

**Recommended next step for the existing feature:** run `/speckit-analyze`.
Review its findings before choosing a pending task in
`specs/001-zero-shot-platform/tasks.md`. Do not rerun `/speckit-specify` merely to
resume existing work, since that starts the specification workflow for a feature.
Planning/task-generation commands may revise documents, so back up or review
changes before accepting regeneration.

For a new feature, review the constitution first, then specify → clarify
(optional) → plan and data model → tasks → analyze → implement → converge,
with human review between stages. For the current feature, continue from the
pending task IDs rather than regenerate all artifacts.

### Check setup and select the existing feature

From the repository root:

```bash
specify integration status
specify workflow list
specify workflow info speckit
bash .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
```

Expected: Copilot integration status `OK`, no missing/modified managed files, a
`Full SDD Cycle (speckit)` workflow, and prerequisite output pointing to
`specs/001-zero-shot-platform`. These checks validate installation and file
availability, not application acceptance criteria.

During adoption, all six Bash scripts passed syntax validation; plan/task template
resolution and a new-feature dry-run also passed without overwriting documents.
These are workflow checks, not a current application test result. Scripts use
Bash; on Windows, use a compatible environment such as WSL rather than PowerShell.

The generated `.specify/.gitignore` excludes `feature.json` because feature
selection is local state. On a fresh copy, or to switch back to this feature, use:

```bash
SPECIFY_FEATURE_DIRECTORY=specs/001-zero-shot-platform bash .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
```

This command also records the selection for later agent invocations. The current
workspace had no Git metadata when workflows were added; Spec Kit supports this
mode. No Git repository, branch, commit, or remote was created by this setup.

The bundled workflow at `.specify/workflows/speckit/workflow.yml` describes
specify → review gate → plan → review gate → tasks → implement. It is a Spec Kit
workflow, **not a GitHub Actions CI workflow**. Agent execution of the entire
cycle has not been performed as part of installation; use the individual chat
skills and review outputs. Read-only workflow inspection does not run those steps.

Do not rerun `specify init --here --force` as a routine launch step. For future
upgrades, back up documents, review `specify integration upgrade --help`, and
inspect the resulting managed-file changes rather than blindly overwriting them.

Sources: [official release v1.3.3](https://github.com/github/spec-kit/releases/tag/v1.3.3) and [Spec Kit documentation](https://github.github.io/spec-kit/).

## AI Agent Skills

The three custom project skills remain alongside the nine official Spec Kit
skills in `.github/skills/`. Each contains a
`SKILL.md` with discovery metadata, relevant source files, and a focused workflow
for compatible coding agents:

- [Spec-driven development](.github/skills/spec-driven-development/SKILL.md):
  keep requirements, implementation, tests, and Spec Kit artifacts aligned.
- [Model lifecycle](.github/skills/model-lifecycle/SKILL.md):
  manage model configuration, downloads, local reuse, deletion, and cache safety.
- [Classification and storage testing](.github/skills/classification-storage-testing/SKILL.md):
  validate inference and MinIO persistence with offline mocks and opt-in live checks.

Ask your agent to use the relevant skill, for example: “Use the model-lifecycle
skill to add tests for failed downloads.” Agents without skill discovery can read
the linked files directly. These skills are development guidance, not runtime
dependencies, and do not download models or start services automatically.

## Troubleshooting


| Symptom                                    | What to check                                                                                                                                                   |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `specify: command not found`               | Check`uv tool list`, update the tool-bin PATH with `uv tool update-shell`, and restart the terminal.                                                            |
| `No module named streamlit` or `app`       | Activate the intended environment, install requirements, and launch from the repository root with the documented`PYTHONPATH` command.                           |
| Model status is`missing`                   | Download it in Admin. Empty, damaged, or legacy folders without a completion manifest are deliberately not considered ready. Refresh after success.             |
| Model status is`invalid`                   | Check the repository ID, directory containment, and symlinks. Do not bypass validation by creating a manifest manually.                                         |
| Download fails                             | Check connectivity, access permissions/token requirements, and free disk space. Retrying preserves existing folders on network or artifact-validation failures. |
| Tokenizer or pipeline initialization fails | Check the Transformers error and required tokenizer dependencies. Model readiness checks are structural and do not guarantee loadability.                       |
| MinIO connection fails                     | Check that Docker and MinIO are running; use`localhost:9000` from the host, not `minio:9000`. Ensure credentials match the server.                              |
| Storage credentials rejected               | Set`MINIO_ACCESS_KEY` and `MINIO_SECRET_KEY`; empty values and `replace-me` are not valid configuration.                                                        |
| Bucket name rejected                       | Set`MINIO_BUCKET` to an S3-compatible name such as `zeroshot-learning-output`.                                                                                  |
| Upload fails despite displayed results     | The binary-stream fix in`MinIOStorage.save_prediction()` is pending; displaying a result does not prove persistence.                                            |
| Label changes disappear                    | Persistence helpers exist, but the current Save button is not yet connected to them.                                                                            |

Do not clear caches as a first response to every error. The cache-clearing action deletes all contents of the configured `HF_HOME`.

## Security Note

This project does not implement authentication for the admin page. Keep it bound to localhost or a trusted environment; do not expose it publicly as-is. Deletion and cache cleanup are destructive administrator actions, and concurrent administration is unsupported.

Never commit `.env`, tokens, model directories, caches, or sensitive prediction records. Uploaded JSON includes the full input text: use synthetic data for testing. MinIO's Compose configuration exposes ports on the host and uses development credentials, so apply appropriate network restrictions and stronger credentials before any shared deployment.
