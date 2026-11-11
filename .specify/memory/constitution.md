<!--
Sync Impact Report — temporary review material; remove before committing.
Version change: 1.1.0 → 1.2.0 (MINOR: materially expanded enforceable guidance).
Modified principles (prior numbered sections consolidated without removing commitments):
- Reproducibility → I. Reproducible Environments and Model Provenance
- Technology Consistency; Separation of Concerns → II. Required Stack and Service Boundaries
- Model Lifecycle Management → III. Configuration-Driven Model Lifecycle
- Configuration and Secrets; Security and Privacy → IV. Secrets and Artifact Hygiene
- Data Persistence → V. MinIO Persistence and Honest Success Semantics
- Observability; Error Handling → VI. Structured Logging and Safe Failures
- Testing Standards; Quality Gates → VII. Enforced Automated Testing
- Documentation → VIII. Reproduction Documentation and Evidence
Added sections: explicit Governance amendment/version policy and required CI/merge gates.
Purpose/Scope, Decision Record Process, and Compliance Check are retained under
Scope and Operating Constraints, Development Workflow and Quality Gates, and Governance.
Removed sections: none substantively; headings reorganized to the resolved scaffold.
Correction: default bucket is zeroshot-learning-output, not the invalid underscore spelling.
Follow-up: TODO(RATIFICATION_DATE) requires historical confirmation; first Git appearance
on 2026-11-10 is not proof of original ratification.
Follow-up: ADR-001, spec.md, and the README bucket paragraph retain contradictory spellings;
align through the subsequent specification/planning workflow (T032), not this command.
Implementation gaps remain tracked in T009–T014, T016, T018, T020, and T027–T034;
this review does not certify implementation compliance or passing tests.
Templates and commands remain unchanged: the constitution workflow reads them at runtime.
-->

# Zero-Shot Text Classification Platform Constitution

## Core Principles

### I. Reproducible Environments and Model Provenance

- The project MUST document its supported Python runtime and maintain a repeatable dependency
  lock with exact resolved versions. Local setup, CI, and container builds MUST use that lock;
  reproducible releases MUST pin container images to immutable digests.
- Model identifiers and revision selectors MUST be declared in version-controlled configuration.
  Downloads MUST resolve selectors to immutable Hugging Face commits and download those commits.
  The selector and resolved commit MUST be recorded in the local manifest and prediction record.
- Legacy artifacts with unverified provenance MUST report an unknown revision, never fabricate
  `main` or a commit. They MUST NOT count as reproducible release evidence.
- Environment-specific paths, endpoints, buckets, and cache locations MUST be configurable without
  source edits. Reproduction evidence MUST identify application version, runtime, dependency lock,
  model revision, and relevant execution settings; cross-device bitwise equality is not promised.

Rationale: reproduction requires recoverable software and artifact identities, not mutable defaults.

### II. Required Stack and Service Boundaries

- Application logic MUST use Python, PyTorch, Hugging Face Transformers, Streamlit, and MinIO.
  Shell, YAML, and JSON MAY support tooling, configuration, and deployment.
- Inference MUST explicitly select the PyTorch backend and load validated local model/tokenizer
  artifacts with local-only loading and remote code disabled. Classification MUST NOT silently
  download models, switch frameworks, or substitute a different configured model.
- Streamlit MUST remain a presentation/orchestration layer. Model lifecycle, classification,
  prediction validation, and MinIO persistence MUST reside in independently testable services;
  shared configuration MUST be loaded through utilities rather than duplicated in pages.

Rationale: fixed technology contracts and isolated services enable offline testing and predictable use.

### III. Configuration-Driven Model Lifecycle

- A declarative model registry MUST drive available model choices and their revisions. Candidate
  labels MUST come from a shared persisted configuration, not separate hardcoded UI lists.
  Configuration MUST be validated; label saves MUST be atomic and visible to both pages.
- Downloads MUST be explicit administrative operations into a controlled `MODEL_DIR`. Safe model
  identifiers, collision-free paths, and containment checks MUST prevent traversal and symlink
  escapes during download and deletion.
- Downloads MUST be staged and published only after validating configuration, tokenizer artifacts,
  complete nonempty PyTorch weights (including indexed shards), and a completion manifest.
  Directory existence or a partial download MUST NOT imply readiness.
- Valid existing artifacts matching the requested configuration MUST be reused. Failed downloads
  MUST clean up only their own staging data and preserve pre-existing artifacts.
- Model deletion and Hugging Face cache cleanup MUST be explicit administrator actions, scoped
  to configured managed locations. Lifecycle changes MUST invalidate affected inference caches.

Rationale: configuration is the source of truth; readiness and cleanup must be safe and observable.

### IV. Secrets and Artifact Hygiene

- Credentials and tokens MUST be injected through environment variables or an untracked local
  `.env`; required secrets MUST fail validation when absent. Source code and deployment files
  MUST NOT supply embedded credentials or usable fallback secrets.
- Credentials, tokens, local secret files, downloaded model/tokenizer artifacts, model caches,
  and persisted user prediction data MUST NOT be committed to Git or included in image build
  contexts. Example environment files MUST contain placeholders only.
- Ignore rules and automated repository/build-context checks MUST enforce these exclusions.
  A tracked-file review MUST supplement ignore rules, which do not protect already tracked files.
- Secrets and raw input MUST NOT appear in logs or user-facing errors. Prediction JSON intentionally
  contains input text; access to that bucket MUST be restricted and its privacy implications documented.
- Without authentication, the UI and storage endpoints MUST be limited to local/trusted use and
  bind to loopback by default. Untrusted exposure requires authentication, authorization, and TLS.

Rationale: reproducibility never requires distributing secrets, large runtime artifacts, or user data.

### V. MinIO Persistence and Honest Success Semantics

- MinIO MUST be the prediction system of record. A classification request MUST NOT be reported as
  successfully saved until its validated JSON record has been written to MinIO.
- `MINIO_BUCKET` MUST remain configurable, defaulting to `zeroshot-learning-output`. Invalid S3
  bucket names MUST be rejected, not silently rewritten. This corrects the underscore spelling
  in the previous constitution; no existing bucket or data is automatically renamed or migrated.
- Prediction records MUST preserve request ID, UTC timestamp, input, candidate labels, ranked
  results, predicted class, confidence, model identity/provenance, and application version.
  Numeric scores MUST be finite, and object keys MUST support request correlation.
- Storage failure MAY leave an inference result visible, but the UI MUST explicitly state that
  it was not saved. Local files MUST NOT become a fallback prediction store; temporary processing
  files and model caches are permitted.

Rationale: an inference result and a durable prediction are different outcomes.

### VI. Structured Logging and Safe Failures

- Model download/reuse/deletion, cache cleanup, label saves, inference, and MinIO writes MUST emit
  parseable structured JSON events covering success and failure.
- Event metadata MUST be allowlisted and include operation, outcome, timestamp, and, when relevant,
  request ID, model ID/revision, duration, and a sanitized error category.
- Logs MUST NOT contain raw input, credentials, tokens, arbitrary payload dictionaries, or raw
  external exception messages. Tests MUST verify both valid event structure and redaction.
- Invalid configuration/input, unavailable models, failed downloads, and storage failures MUST
  produce actionable sanitized errors without a false success indication. Input MUST be sanitized
  and validated before inference; prediction records MUST be validated before persistence.
  Errors MUST NOT expose credentials or trigger unsafe fallback behavior.

Rationale: operators need correlated evidence without leaking sensitive data through diagnostics.

### VII. Enforced Automated Testing

- Each behavior change MUST include automated tests; regressions MUST first have a failing test
  that reproduces the defect. Service dependencies MUST support deterministic mocks or fixtures.
- The default offline suite MUST require neither model downloads nor a live MinIO instance.
  It MUST cover configuration/labels, lifecycle safety/readiness/provenance, explicit local PyTorch
  loading, cache reuse/invalidation, prediction validation, storage contracts/failures, logging
  privacy, and Streamlit input gating and persistence-status behavior.
- CI MUST run lint, offline tests, and secret/artifact hygiene checks on every pull request and
  protected-branch update. Required checks MUST block merging on failure or missing execution;
  local test success alone MUST NOT replace enforced CI checks.
- A separate CI job MUST verify real MinIO write/read behavior using synthetic data and a unique
  test-owned bucket. Integration cleanup MUST NOT affect shared or production data. Local live
  integration tests MUST be explicitly enabled; missing infrastructure is blocked/skipped, not passed.
- Release acceptance MUST include passing required CI checks, live MinIO tests, and a separately
  recorded real-model download → local PyTorch inference → MinIO persistence smoke check.
  Offline mocks MUST NOT be presented as evidence of live integration or real-model correctness.

Rationale: mandatory, visible gates prevent completion claims based on incomplete or mocked evidence.

### VIII. Reproduction Documentation and Evidence

- The README MUST document setup, locked installation, configuration/secrets, architecture, model
  download/reuse/deletion, labels, MinIO usage, test modes, quick start, and troubleshooting.
- Documentation MUST distinguish implemented behavior from planned work and identify validation
  commands, environment, outcomes, and blockers. Historical passes MUST NOT certify later changes.
- Specifications, plans, tasks, and decision records MUST remain traceable to these principles.
  Spec-first remediation MUST be described honestly, without inventing the original creation order.

Rationale: a new developer must be able to reproduce both behavior and the evidence supporting it.

## Scope and Operating Constraints

The platform supports learning and demonstrating reproducible MLOps: a local configuration-driven
model registry, Streamlit administration and classification, candidate labels, model lifecycle
management, JSON prediction persistence in MinIO, automated tests, and documentation.

User authentication, multi-user administration, large-scale production orchestration, and non-MinIO
storage backends are outside v1 scope. Their absence does not permit unsafe public exposure.
Real model downloads, destructive cache operations, and live storage cleanup require explicit intent;
routine tests MUST use mocks, temporary directories, synthetic data, and test-owned resources.

## Development Workflow and Quality Gates

1. Review the constitution before changing the specification, then update the plan and tasks before
   application changes. Record deliberate exceptions through the governance process.
2. Every plan and pull request MUST map applicable principles to implementation and test evidence.
   Verify environment/config-driven behavior, no committed secrets/artifacts, local-only PyTorch
   inference, revision provenance, persisted labels, safe errors, and structured logging.
3. Required CI lint, offline tests, hygiene checks, and the separate MinIO job MUST pass before
   merge. Repository maintainers MUST configure required status checks; absent CI or branch
   enforcement is an open compliance gap, not an implicit waiver.
4. Final submissions/releases MUST satisfy acceptance criteria and document the live-model smoke
   check separately. Failed, skipped, blocked, and unexecuted checks MUST remain visible.

This constitution confirms governing requirements, not implementation readiness. Existing R1 gaps
remain in the [task backlog](../../specs/001-zero-shot-platform/tasks.md), with actual verification in
[validation evidence](../../specs/001-zero-shot-platform/validation.md). This amendment does not run
tests, install CI, change application behavior, or certify those gaps as resolved.

## Governance

- This constitution governs specifications, plans, implementation, and reviews. Conflicting lower-level
  documents MUST be aligned before affected implementation proceeds; historical evidence MUST remain
  labeled with its original scope rather than retroactively rewritten as a new pass.
- Amendments MUST record the reason, affected principles, compatibility impact, migration actions,
  and required evidence. The project maintainer MUST approve the amendment in review before merge.
- Constitution versions MUST follow semantic versioning: MAJOR for incompatible principle removal
  or redefinition, MINOR for new principles or materially expanded guidance, PATCH for wording-only
  clarifications. Preserve the original ratification date and update the amendment date on changes.
- Exceptions MUST have a written decision record stating scope, rationale, risk, mitigation, owner,
  and expiry/review condition, with maintainer approval. Exceptions MUST NOT be implicit or used to
  misrepresent failing checks as passes. A conflict with a non-negotiable principle requires an
  explicit constitution amendment, not merely a lower-level decision record.
- All pull requests and final submissions MUST include a compliance review. Deferred implementation
  work MUST remain tracked and MUST NOT be represented as compliant until the required evidence exists.

The original adoption date is unverified. The constitution first appears in available Git history
on 2026-11-10, which does not establish its ratification date or the original implementation sequence.

**Version**: 1.2.0 | **Ratified**:2026-11-11: confirm original adoption date | **Last Amended**: 2026-11-11
