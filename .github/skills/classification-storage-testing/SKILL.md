---
name: classification-storage-testing
description: 'Implement, debug, or test zero-shot inference and MinIO prediction persistence. Use for candidate-label validation, classifier pipeline behavior, prediction JSON contracts, storage failures, or end-to-end classification verification.'
---

# Classification and storage testing

## Read first

Paths are relative to the repository root:
- `app/services/classifier.py`
- `app/services/minio_storage.py`
- `app/pages/2_Classify_Text.py`
- `app/utils/config.py` and `configs/labels.yaml`
- `specs/001-zero-shot-platform/data-model.md`
- `tests/test_classifier.py` and `tests/test_minio_storage.py`

## Inference workflow

1. Trace input text, selected model, and candidate labels from the page to `ZeroShotClassifier.classify`.
2. Preserve blank-input rejection and the requirement for at least two unique, nonempty labels. The current label validation strips whitespace, preserves order, and deduplicates case-sensitively; do not silently change those semantics.
3. Mock `_get_pipeline` for result-shaping tests so they require neither Transformers initialization nor model downloads. Return deterministic `labels` and `scores` from the fake callable.
4. Assert predicted class, confidence, normalized candidate labels, ranked predictions, and model identifier. When changing pipeline caching, separately test reuse and model switching with a mocked pipeline factory.
5. Verify the selected local model path and configured labels actually reach inference; do not assume the UI already enforces the intended configuration contract.

## Persistence workflow

1. Check the prediction payload against the data model. The page currently assembles `request_id`, `timestamp`, `input_text`, `predicted_class`, `confidence`, `candidate_labels`, `ranked_predictions`, `model`, `model_revision`, and `application_version`.
2. Preserve the object-key convention `predictions/YYYY/MM/DD/{request_id}.json` and the environment-configured bucket.
3. Patch `app.services.minio_storage.Minio` before constructing `MinIOStorage`. Test both existing and missing buckets without connecting to a server.
4. Capture `put_object` arguments and verify JSON round-tripping, Unicode handling, content type, and encoded byte length.
5. Make the fake client honor the real SDK contract: MinIO `put_object` expects a readable binary stream, not raw bytes. A permissive mock that accepts anything is not sufficient evidence that uploads work.
6. Cover supplied and generated request IDs, bucket failures, and upload failures. Treat a classification as successfully persisted only after the write succeeds; never add a silent local fallback.
7. Do not log credentials or full private input text. Use synthetic text in fixtures and integration checks.

## Validation

From the repository root, using the selected Python environment:

```sh
python -m pytest -q tests/test_classifier.py tests/test_minio_storage.py
python -m pytest -q
```

The existing MinIO test checks object-path formatting only; it does not verify an upload. Add coverage for the behavior changed rather than describing the current suite as an integration suite.

For an explicitly requested live integration check:
- Confirm a reachable development MinIO endpoint and test credentials without printing secrets. The Compose hostname `minio` is for the container network; host-run clients generally use `localhost:9000` with the current port mapping.
- Use a dedicated test bucket and unique object prefix, and fetch uploaded JSON to verify its contents.
- Keep integration tests opt-in and separate from offline unit tests.
- Delete only test-owned objects if cleanup is authorized; never clear a shared bucket.
- Report separately which mocked tests and which live checks ran. Do not download a model just to test storage.