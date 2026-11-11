User: /speckit-constitution Review and confirm the project principles for a reproducible zero-shot text classification platform using Python, PyTorch, Hugging Face Transformers, Streamlit, and MinIO. Include config-driven model lifecycle management, secure secrets handling, no committed models or credentials, structured logging, and enforced automated testing.

GitHub Copilot: Optimizing tool selection...

Created 3 todos

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2)

Searched for files matching `**/*constitution*`, 3 matches

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.specify)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.github)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/README.md#1-1), lines 1 to 260

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/pyproject.toml)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.github/skills/speckit-constitution/SKILL.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.specify/memory/constitution.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.specify/templates)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/plan.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/tasks.md)

I’ll update only the project constitution, as required by this workflow. I’ll make the principles enforceable and distinguish them from implementation compliance, since CI and several runtime safeguards are still pending.

Ran terminal command:  .specify/scripts/bash/resolve-template.sh constitution-template --json && git log --follow --format='%ad %s' --date=short -- .specify/memory/constitution.md && git status --short

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/decisions/001-adoption-and-bucket.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/spec.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.gitignore)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/validation.md)

Starting: *Update enforceable project principles* (2/3)

The existing principles cover the requested stack, but testing gates need clearer enforcement. The constitution also names an invalid underscore-containing MinIO bucket. I’ll publish version 1.2.0 with stronger gates and the valid default, `zeroshot-learning-output`. The original ratification date is unverified, so I’ll flag it rather than invent one.

Using "Apply Patch"

Using "Apply Patch"


```

```


Starting: *Validate constitution and report outcome* (3/3)

Checked [](file:///Users/radhakarthikeyan/MLOpsHomework2/.specify/memory/constitution.md), no problems found

Ran terminal command:  git diff --check && git diff --stat && ruby -rdate -e 'p = ".specify/memory/constitution.md"; s = File.read(p); abort "Unresolved scaffold token" if s.match?(/\[[A-Z][A-Z0-9_]*\]/); abort "Version mismatch" unless s.include?("Version change: 1.1.0 → 1.2.0") && s.include?("**Version**: 1.2.0"); abort "Principle count mismatch" unless s.scan(/^### /).length == 8; headings = s.scan(/^## (.+)$/).flatten; abort "Scaffold mismatch" unless headings == ["Core Principles", "Scope and Operating Constraints", "Development Workflow and Quality Gates", "Governance"]; s.scan(/\b\d{4}-\d{2}-\d{2}\b/).each { |d| Date.iso8601(d) }; abort "Vague SHOULD wording" if s.match?(/\bshould\b/i); s.scan(/\]\(([^)]+)\)/).flatten.each { |link| abort "Broken link: #{link}" unless File.exist?(File.expand_path(link, File.dirname(p))) }; puts "PASS: scaffold, eight principles, version, dates, links, and normative wording"; puts "Expected manual TODO: original ratification date"' && if test -f /Users/radhakarthikeyan/MLOpsHomework2/.specify/extensions.yml; then printf 'Extension hooks file present; review required\n'; else printf 'No extension hooks registered\n'; fi && git status --short

Completed: *Validate constitution and report outcome* (3/3)

Updated constitution.md to **v1.2.0**, a minor revision strengthening enforceable requirements.

Confirmed principles:
- Required Python, PyTorch, Transformers, Streamlit, and MinIO stack.
- Locked dependencies and immutable model revisions.
- Config-driven model lifecycle, validated downloads, reuse, and safe cleanup.
- Environment-supplied secrets; no committed credentials or model artifacts.
- Structured JSON logging with privacy safeguards.
- Mandatory CI checks, offline tests, live MinIO integration, and separate real-model release evidence.
- MinIO persistence required before reporting a saved prediction.

**Validation:** Document checks passed; only the constitution changed. Application tests were not run, and CI enforcement remains pending.

**Follow-ups:** Confirm the original ratification date, align downstream documentation with `zeroshot-learning-output`, and remove the temporary Sync Impact Report before committing.

Suggested commit: `docs: amend constitution to v1.2.0 with enforceable reproducibility and testing principles`

Made changes.

User: why not constitution-template.md not updated

GitHub Copilot: That was intentional. The `/speckit-constitution` workflow explicitly requires updating **only** constitution.md, not template files.

- **constitution-template.md** is the reusable scaffold containing placeholders and structural guidance.
- **constitution.md** is the actual project constitution containing your confirmed principles.

The workflow reads the template, fills its structure with project-specific requirements, and writes the result to the constitution. Updating the template would change the scaffold for future generation—not the project’s governing principles.

User: is it valid to submit the template with placeholder for my data science course project submission

GitHub Copilot: Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/homework02-MLOps_Project_%20ZeroShot_TextClassification_SpecKit.md#1-1), lines 1 to 300

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/homework02-MLOps_Project_%20ZeroShot_TextClassification_SpecKit.md#340-340), lines 340 to 706

**Yes—as a supporting template, not as your completed constitution.**

Your homework02-MLOps_Project_ ZeroShot_TextClassification_SpecKit.md require a project-specific constitution defining actual engineering principles. They do not require replacing placeholders in the reusable template.

| File | Submission expectation |
|---|---|
| constitution-template.md | Can retain placeholders; it is Spec Kit scaffolding. |
| constitution.md | Must contain your reviewed, project-specific principles—not an unfilled template. |

**Before submitting your current constitution:**
- Resolve `TODO(RATIFICATION_DATE)` using a verified date, or explicitly state that the original date is unknown—do not invent one.
- Remove the temporary Sync Impact Report after reviewing it.
- Make sure specifications and implementation match the principles, and clearly disclose unfinished requirements.

Keeping a reusable template with placeholders is not itself an incomplete deliverable. **Submitting only that template instead of the completed constitution would be insufficient.** Final grading remains the instructor’s decision.

User: how to run and test this project in a speckit 

GitHub Copilot: 

User: how to run and test this project in a speckit

GitHub Copilot: Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/README.md#280-280), lines 280 to 483

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.specify/memory/constitution.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/docker-compose.yml)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/tests/test_minio_storage.py)

Using "Get Container Tools Configuration"
Completed with input: {}

**Spec Kit guides development; it does not run the application itself.** Use Spec Kit commands in **Copilot Chat**, and use **pytest, Streamlit, and Docker in the terminal**.

For this existing project, follow this sequence.

## 1. Verify Spec Kit setup

From your project’s root directory, run:

```bash
specify integration status
specify workflow list

SPECIFY_FEATURE_DIRECTORY=specs/001-zero-shot-platform \
bash .specify/scripts/bash/check-prerequisites.sh \
  --json --require-spec --require-tasks --include-tasks
```

These check workflow installation and required documents—not application correctness.

Do not rerun `specify init` or regenerate the existing feature just to launch it.

## 2. Review the project through Spec Kit

In **Copilot Chat**, enter:

```text
/speckit-analyze Review the existing zero-shot platform against constitution
v1.2.0. Identify inconsistencies, missing tests, and incomplete acceptance
criteria. Do not change application code.
```

Then address reviewed findings in small scopes:

```text
/speckit-implement Complete T032 only. Align the bucket-name decision and
related documents with the constitution. Preserve historical evidence.
```

For subsequent implementation, select pending IDs from tasks.md, rather than asking it to implement the entire backlog.

## 3. Prepare the Python environment

Your terminal shows that the project environment was activated. In a new terminal, use:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Configure an untracked local .env using .env.example. For a host-run Streamlit app, use:

- `MINIO_ENDPOINT=localhost:9000`
- `MINIO_BUCKET=zeroshot-learning-output`
- `MINIO_SECURE=false` for local HTTP only
- Credentials matching your local MinIO server

Never commit actual credentials.

## 4. Run automated tests first

```bash
python -m pytest -q tests/test_model_manager.py
python -m pytest -q
```

For detailed failure information:

```bash
python -m pytest -vv --tb=short
```

**Important:** The documented 64-test pass is historical. The current suite must be rerun; some tests need updates for the newer required-credentials configuration.

Existing mocked tests do **not** establish that a real model or live MinIO upload works.

## 5. Start MinIO and Streamlit

Start Docker Desktop, then run:

```bash
docker compose up -d minio
docker compose ps
```

Start Streamlit:

```bash
PYTHONPATH=. python -m streamlit run app/streamlit_app.py \
  --server.address 127.0.0.1 \
  --server.port 8501
```

Open:

- Application: http://127.0.0.1:8501
- MinIO console: http://127.0.0.1:9001

**Security:** The current Compose configuration uses development credentials and exposes MinIO ports on all host interfaces. Restrict it to local access before use on an untrusted network.

## 6. Perform the end-to-end test

1. Open **Admin** and download one configured model.
2. Confirm it becomes available.
3. Open **Classify Text**, select the model and at least two labels.
4. Submit synthetic text and inspect the ranking.
5. Open MinIO and verify the corresponding JSON object exists.
6. Compare its input, model, labels, scores, and request metadata with the result.

**Current blockers:** Managed-local inference, label persistence, the MinIO upload fix, live integration tests, and CI remain pending in the documented backlog. A displayed prediction is **not proof of successful storage**.

Record actual passes, failures, and blockers in validation.md. Mark tasks complete only after their checks pass.

To stop: press **Ctrl+C** for Streamlit, then run `docker compose stop minio`.

User: /speckit-analyze Review the existing zero-shot platform against constitution
v1.2.0. Identify inconsistencies, missing tests, and incomplete acceptance
criteria. Do not change application code.

GitHub Copilot: Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.github/skills/speckit-analyze/SKILL.md)

I’ll compare the specification, plan, and tasks with constitution v1.2.0, then inspect the implementation and tests for supporting evidence. This will be read-only; no files will be changed and no live services or model downloads will be started.

Created 3 todos

Ran terminal command:  if test -f .specify/extensions.yml; then cat .specify/extensions.yml; fi && git status --short && .specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.specify/memory/constitution.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/spec.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/plan.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/tasks.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/data-model.md)

Audit runtime and tests

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/spec.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.specify/memory/constitution.md)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.github)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/specs/001-zero-shot-platform/tasks.md)

Ran terminal command:  find app tests configs .github -type f ! -path '*/__pycache__/*' ! -name '.env' ! -name '.env.*' -print && find . -type d \( -name .git -o -name .venv -o -name .cache -o -name .pytest_cache -o -name models \) -prune -o -type f \( -name '*lock*' -o -name '.dockerignore' -o -name '.gitignore' -o -name '.gitattributes' -o -name 'MANIFEST.in' -o -name 'setup.cfg' -o -name 'setup.py' -o -name '*requirements*' \) -print

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/services/model_manager.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/services/classifier.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/services/prediction.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/services/minio_storage.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/utils/config.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/utils/logging_config.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/pages/1_Admin.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/pages/2_Classify_Text.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/streamlit_app.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/tests/test_model_manager.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/tests/test_classifier.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/tests/test_minio_storage.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.github/skills/speckit-analyze/SKILL.md#1-1), lines 1 to 250

Ran terminal command:  for f in configs/models.yaml configs/labels.yaml Dockerfile docker-compose.yml requirements.txt pyproject.toml .gitignore README.md specs/001-zero-shot-platform/plan.md specs/001-zero-shot-platform/data-model.md specs/001-zero-shot-platform/validation.md specs/001-zero-shot-platform/decisions/001-adoption-and-bucket.md; do printf '\n--- %s ---\n' "$f"; awk '{line=$0; if (line ~ /(MINIO_ROOT_USER|MINIO_ROOT_PASSWORD|MINIO_ACCESS_KEY|MINIO_SECRET_KEY)[=:]/) sub(/[:=].*$/, ": [REDACTED credential configuration]", line); printf "%5d %s\n", NR,line}' "$f"; done && printf '\n--- tracked paths (names only) ---\n' && git ls-files && printf '\n--- test function inventory ---\n' && grep -n '^def test_' tests/test_*.py

Ran terminal command:  for f in configs/models.yaml configs/labels.yaml Dockerfile docker-compose.yml requirements.txt pyproject.toml .gitignore .specify/.gitignore; do printf '\n--- %s ---\n' "$f"; awk '{line=$0; if (line ~ /(MINIO_ROOT_USER|MINIO_ROOT_PASSWORD|MINIO_ACCESS_KEY|MINIO_SECRET_KEY)[=:]/) {style=(line ~ /\$\{/ ? "environment interpolation" : "embedded literal"); sub(/[:=].*$/, ": [REDACTED; " style "]", line)}; printf "%4d %s\n", NR,line}' "$f"; done && printf '\n--- environment EXAMPLE only (redacted) ---\n' && awk '{line=$0; if (line ~ /^[A-Za-z_]*(KEY|PASSWORD|TOKEN|USER)=/) {value=substr(line,index(line,"=")+1); style=(value=="replace-me" || value=="" ? "placeholder or empty" : "non-placeholder"); sub(/=.*/, "=[REDACTED; " style "]",line)}; printf "%4d %s\n",NR,line}' .env.example && printf '\n--- source line counts ---\n' && wc -l app/services/*.py app/utils/*.py app/pages/*.py tests/*.py && printf '\n--- tests per file (function definitions) ---\n' && grep -c '^def test_' tests/test_*.py && printf '\n--- hooks configuration existence ---\n' && if test -f .specify/extensions.yml; then printf 'extensions.yml exists; not executed\n'; else printf 'No extensions.yml\n'; fi

Ran terminal command:  printf '\n--- README opening / examples ---\n' && awk 'NR<=198 {line=$0; if (tolower(line) ~ /(credential|password|secret|access.key|token)/) line="[credential-related documentation omitted]"; printf "%4d %s\n",NR,line}' README.md && for f in app/services/model_manager.py app/services/classifier.py app/services/minio_storage.py app/services/prediction.py app/utils/config.py app/utils/logging_config.py app/pages/1_Admin.py app/pages/2_Classify_Text.py; do printf '\n--- %s ---\n' "$f"; nl -ba "$f"; done

Ran terminal command:  printf '\n--- requirement and governance anchors ---\n' && grep -n -E 'FR-00|repeatable dependency|selectors MUST|Lifecycle changes|Credentials and tokens|Ignore rules|loopback|defaulting to|structured JSON|required CI|CI MUST|Version\*\*' specs/001-zero-shot-platform/spec.md .specify/memory/constitution.md && printf '\n--- pending task anchors ---\n' && grep -n -E 'T009|T010|T011|T013|T014|T016|T018|T020|T027|T029|T030|T031|T032|T033|T034' specs/001-zero-shot-platform/tasks.md && printf '\n--- application helper references ---\n' && grep -n -E 'validate_prediction|load_labels|save_labels|log_event|configure_logging|session_state|revision' app/services/*.py app/utils/*.py app/pages/*.py && printf '\n--- ignored path probes (nonexistent example paths; no file reads) ---\n' && git check-ignore --no-index .env .env.production models/example.bin .cache/example predictions/example.json || true

Starting: *Audit implementation and test coverage* (2/3)

Ran terminal command:  for file in app/services/classifier.py app/services/minio_storage.py app/utils/config.py app/utils/logging_config.py app/pages/1_Admin.py app/pages/2_Classify_Text.py configs/models.yaml .env.example Dockerfile docker-compose.yml pyproject.toml requirements.txt tests/test_classifier.py tests/test_minio_storage.py .gitignore; do printf '\n--- %s ---\n' "$file"; nl -ba "$file"; done

Ran terminal command:  for file in specs/001-zero-shot-platform/spec.md specs/001-zero-shot-platform/tasks.md specs/001-zero-shot-platform/data-model.md specs/001-zero-shot-platform/decisions/001-adoption-and-bucket.md specs/001-zero-shot-platform/validation.md; do printf '\n--- %s ---\n' "$file"; nl -ba "$file"; done && printf '\n--- lifecycle implementation ---\n' && nl -ba app/services/model_manager.py | sed -n '1,180p;300,480p' && printf '\n--- test definitions and assertions ---\n' && rg -n '^def test_|assert_called|Download failed|download failed|network|parametrize' tests && printf '\n--- workspace support files ---\n' && git ls-files .github .dockerignore '*lock*' '*requirements*' '.env*' 'models/**' '.cache/**' && printf '\n--- repository root ---\n' && ls -a

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/services/model_manager.py#175-175), lines 175 to 201

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/tests/test_model_manager.py#1-1), lines 1 to 180

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/app/services/prediction.py)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2/.github)

Read [](file:///Users/radhakarthikeyan/MLOpsHomework2)

Searched for regex `^def test_|log_event\(|validate_prediction\(` (`**/{tests,app}/**/*.py`), 38 results

The review found an invalid bucket default in both the specification and runtime configuration, plus missing work for the stricter v1.2.0 CI gates. It also found a wrong-model cache bug: after a failed switch, the classifier can reuse the previous model while reporting the newly requested one. Existing tests do not cover that case.

Ran terminal command:  printf '\n--- constitution references ---\n' && grep -nE '^### |^## |Ratified|original adoption|TODO|required CI|Required CI|MUST configure' .specify/memory/constitution.md && printf '\n--- plan gates ---\n' && nl -ba specs/001-zero-shot-platform/plan.md | sed -n '45,112p' && printf '\n--- static counts ---\n' && ruby -e 's=File.read("specs/001-zero-shot-platform/tasks.md"); puts "tasks=#{s.scan(/^- \[[ x]\] T\d+/).length}; checked=#{s.scan(/^- \[x\] T\d+/).length}; pending=#{s.scan(/^- \[ \] T\d+/).length}"; Dir.glob("tests/test_*.py").sort.each { |p| puts "#{p}: #{File.read(p).scan(/^def test_/).length} test functions" }' && printf '\n--- tracked artifact paths ---\n' && git ls-files '.env*' 'models/**' '.cache/**' '.github/workflows/**' '*lock*' '.dockerignore' && printf '\n--- final status ---\n' && git status --short && if test -f .specify/extensions.yml; then printf 'Extension hooks file present\n'; else printf 'No extension hooks file\n'; fi

Starting: *Report conflicts and acceptance gaps* (3/3)

Completed: *Report conflicts and acceptance gaps* (3/3)

## Specification Analysis Report

**Result: not yet compliant with constitution v1.2.0.** Resolve document conflicts and missing quality-gate requirements before further implementation.

The existing feature passed prerequisite discovery. This was a **read-only review**: no files changed, tests executed, services started, or models downloaded. Existing user edits were preserved.

### Findings

Constitution `MUST` violations are classified **CRITICAL**; this includes unfinished requirements, not just newly discovered defects.

| ID | Severity | Location | Finding and recommendation |
|---|---|---|---|
| C1 | **CRITICAL** | spec.md, config.py, 001-adoption-and-bucket.md | **Invalid default bucket.** Documents and runtime use `zeroshot_learning_output`, contradicting the constitution’s `zeroshot-learning-output`. Strict validation rejects the runtime default; the error recommends that same invalid value. Align documents, configuration, examples, and tests through T032/T010. |
| C2 | **CRITICAL** | spec.md, tasks.md, constitution.md | **CI enforcement is underspecified and absent.** T018 covers offline tests and build exclusions, but not the full required lint, hygiene, live-MinIO, and merge-protection gates. Expand explicit task coverage. Remote branch protection was not inspected. |
| C3 | **CRITICAL** | spec.md, requirements.txt, Dockerfile | **Reproducibility requirements are weaker than the constitution.** “Pin/document” does not require immutable image digests. Dependencies have lower bounds, no lock exists, and images are mutable. Expand T030 to cover locked local/CI/container installation and digest pinning. |
| C4 | **CRITICAL** | docker-compose.yml, Dockerfile | **Unsafe deployment/build defaults.** Compose embeds usable development credentials and publishes MinIO on all host interfaces. No Docker build exclusions protect `COPY . .`. Extend T018/T033 to cover environment-injected server credentials, loopback publishing, and build-context checks. |
| C5 | **CRITICAL** | classifier.py | **Inference bypasses managed local artifacts.** Repository IDs are passed directly to Transformers without explicit PT/local-only loading. Additionally, `model_id` changes before loading succeeds: a failed switch from A to B can cause a subsequent B request to reuse A’s pipeline. Add a failing regression test and fix under T009/T031. |
| C6 | **CRITICAL** | model_manager.py, 2_Classify_Text.py | **Model provenance is not implemented.** Downloads do not resolve/pass immutable revisions; manifests omit provenance; the UI reports `"main"` as the actual revision. Complete T031 and verify selector/SHA propagation into stored predictions. |
| C7 | **CRITICAL** | 1_Admin.py, 2_Classify_Text.py | **Configuration-driven labels and gating are incomplete.** “Save labels” reports success without saving. Both pages hardcode labels; classification remains enabled without a ready model or valid labels. Complete T027/T014/T034. |
| C8 | **CRITICAL** | minio_storage.py, classifier.py | **Persistence and prediction contracts are unenforced.** Upload passes bytes instead of a readable stream, mutates the payload, and serializes twice. Predictions are not fully validated or sorted; the shared validator is unused. Complete T009–T011 with strict contract tests. |
| C9 | **CRITICAL** | 2_Classify_Text.py, model_manager.py, logging_config.py | **Safe errors and operation-wide logging are missing.** Raw external exceptions reach users; storage failures are labeled classification failures rather than explicitly “not saved.” Only label helpers call the structured logger. Complete T029/T033 and redaction tests. |
| C10 | **CRITICAL** | model_manager.py | **Failed publication can destroy existing artifacts.** The previous incomplete directory is deleted before staging is renamed. A rename failure loses both copies, contrary to preservation requirements. Extend T024’s regression coverage and define rollback behavior. |
| I1 | **HIGH** | data-model.md, data-model.md | **Data-model examples contradict the contracts.** The registry key is corrupted and one task value is a bucket name. The prediction has two candidates but only one ranked result. Correct examples and validate them against the intended schemas. |
| A1 | **MEDIUM** | constitution.md | **Ratification remains ambiguous.** The document says the original date is unverified but supplies a date followed by “confirm original adoption date.” Resolve through an explicit governance review, not by inferring history. |
| D1 | **LOW** | spec.md, spec.md | **Overlapping requirements lack an explicit precedence rule.** Original bullets, broad acceptance criteria, and FR contracts repeat behavior with different precision. Consolidate or cross-reference them while preserving historical review notes. |

### Coverage summary

“Has task” means work is associated with a requirement—not that implementation or tests are complete.

| Requirement key | Has task? | Task IDs | Evidence/status |
|---|---|---|---|
| FR-001: local inference | Yes | T009, T031 | Local-only loading and cache correctness incomplete |
| FR-002: revisions | Yes | T031 | SHA resolution and provenance incomplete |
| FR-003: labels | Yes | T027, T034 | Helpers exist; UI persistence missing |
| FR-004: prediction | Yes | T009, T013, T034 | Contract helper not integrated |
| FR-005: storage | Yes | T010, T011, T033 | Invalid default and upload defect |
| FR-006: failure semantics | Yes | T013, T014, T033, T034 | Gating and sanitized errors incomplete |
| FR-007: observability | Yes | T029 | Service-wide events/redaction tests missing |
| FR-008: verification | Partial | T015, T016, T018, T020, T034 | New constitutional gates need explicit scope |
| FR-009: reproducibility | Partial | T030, T031 | Lock, digest requirements, and evidence incomplete |
| At least two models | Yes | T002 | Registry contains both models |
| Model availability/local-path display | Yes | T012, T013 | Availability exists; complete UI acceptance unverified |
| Safe staged lifecycle/readiness | Yes | T005, T006, T021–T025 | Substantial structural tests; publication gap remains |
| Selected-model deletion | Yes | T007, T021, T025 | Implementation and test definitions exist |
| Cache cleanup | Yes | T008 | Missing-cache test exists; destructive-path safeguards need coverage |
| Documented startup | Yes | T017, T019, T020 | Documentation exists; live startup not verified here |

**Unmapped tasks:** None identified at feature/workflow level. However, required-status enforcement and automated hygiene checks lack explicit task ownership.

### Missing or outdated tests

Static inventory: **34 test functions**—30 model-manager, three classifier, one storage. This is not a passing-test count.

Priority additions:

- **Inference:** successful mocked classification, local-only PT flags, failed-model-switch recovery, sorting, malformed results, and finite scores.
- **Lifecycle:** immutable revisions, selector changes, publication rollback, and rejecting dangerous cache-directory configurations.
- **Storage:** readable stream, Unicode byte length, payload immutability, timestamp-derived keys, bucket races, sanitized failures, and live round trips.
- **Configuration/UI/logging:** atomic label persistence, invalid settings, submit gating, explicit unsaved status, structured events, and redaction.

Two existing tests also need revision:

- test_model_manager.py requires raw exception text, contradicting safe-error requirements.
- test_minio_storage.py depends on real configuration and checks only an object-path shape—not upload behavior.

### Incomplete acceptance criteria

The spec.md are **not established by this review**:

- Startup and real model download/delete require fresh execution evidence.
- Default bucket creation is blocked by invalid configuration.
- Classification bypasses required local-loading and provenance contracts.
- Persistence has a confirmed upload-interface defect.
- Current unit-suite, live integration, and real-model results remain unverified.

The existing validation.md correctly identifies outstanding evidence. Historical “64 passed” results must remain historical.

### Metrics

- **Normalized requirement groups:** 15, including nine numbered FR groups.
- **Tasks:** 34 — 19 checked, 15 pending.
- **Coarse task association:** 15/15; **not** full subrequirement or constitutional coverage.
- **Findings:** 13 — 10 critical, one high, one medium, one low.
- **Ambiguity findings:** 1.
- **Duplication findings:** 1.

### Next actions

1. Resolve C1–C4 in the specification, plan, and task scopes before further application implementation.
2. Update planning with `/speckit-plan`, explicitly preserving existing artifacts and addressing these findings.
3. Revise task coverage with `/speckit-tasks`, preserving completed work and historical evidence.
4. Rerun `/speckit-analyze`, then use scoped `/speckit-implement` requests.
5. Run offline, live-MinIO, and real-model checks separately and record actual outcomes.

Would you like concrete remediation edits proposed for the top five findings, **without applying them yet**?