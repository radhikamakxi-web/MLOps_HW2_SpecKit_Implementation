# ADR-001: Honest Spec Kit adoption and a valid MinIO bucket

**Status:** Accepted for remediation R1, under the user's request to fix the audited gaps and recommendations.

## Context and historical limitation

Application code existed before the official Specify CLI/workflows were installed.
The original artifact creation order and prior constitution review cannot be proven
from this workspace, which has no Git metadata. Do not backdate artifacts or claim
that installation retroactively satisfies the homework's spec-first requirement.

## Decision: forward sequence

For R1, review and update the constitution first, then specification, plan, data
model, and tasks, before application changes. Use the installed official templates,
skills, and prerequisite checks to support this sequence. Record actual validation
results and unexecuted checks in `validation.md`. Future Git history/agent transcripts
may provide additional evidence, but none will be invented for the original work.

## Decision: bucket compatibility

Use `zeroshot_learning_output` as the default bucket. Standard S3/MinIO bucket
names do not allow underscores, so `zeroshot_learning_output` cannot be relied on
for a working deployment. Keep `MINIO_BUCKET` configurable and validate it with
the MinIO SDK's strict naming rules. Do not silently normalize a user-supplied name.

This is an explicit exception to the literal homework example, not to its core
requirement: MinIO remains the only prediction system of record. Update the
constitution, specification, configuration, tests, and README consistently. The
original homework document remains unchanged. Explain the exception at submission;
this record is not evidence of instructor approval.

## Impact, risks, and mitigation

- Existing environments must set a valid bucket name; no bucket/data is renamed,
  migrated, deleted, or copied automatically.
- Tests use unique test-owned buckets; production/shared buckets are never cleared.
- External downloads and services can fail. Failed inference/storage must not be
  reported as a successful saved prediction; local files are not a fallback store.
- Offline tests establish mocked contracts only. Real MinIO and real model loading
  require separate evidence. Docker is currently installed but the daemon was not
  reachable at the start of R1; this is a validation blocker, not a passing test.
