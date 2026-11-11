# Data Model

**R1 review:** Updated after constitution, specification, and plan; before tasks/code.

## 1. Model Configuration

```yaml
zeroshot_learning_outputmodels:
  - id: MoritzLaurer/deberta-v3-base-zeroshot-v2.0
    name: DeBERTa Zero-Shot v2
    task: zeroshot_learning_output
    revision: main
  - id: facebook/bart-large-mnli
    name: BART MNLI
    task: zero-shot-classification
    revision: main
```

### Local completion manifest

Local model directories also contain an application-owned `.model-complete.json`
written only after download completion and structural validation:

```json
{
  "version": 1,
  "model_id": "facebook/bart-large-mnli",
  "requested_revision": "main",
  "resolved_revision": "0123456789abcdef0123456789abcdef01234567",
  "files": {
    "config.json": 123,
    "tokenizer_config.json": 456,
    "tokenizer.json": 789,
    "model.safetensors": 1000
  }
}
```

Sizes above are illustrative byte counts. `files` records the required artifacts
selected by validation, including a weight index and all its shards when present.
Readiness requires matching model ID, manifest version, and current artifact sizes.
This metadata is local runtime state, not a committed model configuration or a
cryptographic proof that the weights can be loaded.

## 2. Label Configuration

```yaml
labels:
  - sports
  - politics
  - technology
```

## 3. Prediction Record

```json
{
  "request_id": "uuid",
  "timestamp": "ISO-8601",
  "input_text": "text",
  "predicted_class": "sports",
  "confidence": 0.96,
  "candidate_labels": ["sports", "politics"],
  "ranked_predictions": [{"label": "sports", "score": 0.96}],
  "model": "MoritzLaurer/deberta-v3-base-zeroshot-v2.0",
  "model_name": "DeBERTa Zero-Shot v2",
  "model_revision": "0123456789abcdef0123456789abcdef01234567",
  "model_requested_revision": "main",
  "application_version": "0.1.0",
  "inference_latency_ms": 12.3
}
```

## 4. R1 validation and state rules

- Label YAML has one `labels` list of strings. Normalize by trimming, dropping
  empty entries/exact duplicates, preserving order, and requiring at least two.
  Save through a same-directory temporary file and atomic replace. Invalid input
  must not overwrite the last valid configuration.
- Model `revision` is a selector, not necessarily a commit. Resolve it to a
  40-character hexadecimal SHA before downloading; persist both. The example SHA
  above is illustrative, not a real model version. Legacy manifests without
  provenance expose `model_revision: null`; never pretend `main` is an exact SHA.
- Cache identity includes local path and completion-manifest identity, so a
  newly downloaded artifact is not served by the old pipeline.
- Prediction `request_id` is a UUID; `timestamp` is timezone-aware UTC ISO 8601.
  `input_text`, model ID/name, and app version are nonempty strings. Scores must be
  finite numbers in [0,1]; ranking covers each candidate once in descending order;
  the first label/score must match `predicted_class` and `confidence`.
- `model_revision` is a resolved SHA or null. Latency is finite, nonnegative
  milliseconds. The storage service validates the record and must not mutate it.
- Object path: `predictions/YYYY/MM/DD/{request_id}.json`, using the record's UTC
  timestamp. Default bucket: `zeroshot_learning_output`; no name normalization.
- Request states: validated → inferred → persisted. Only persisted is overall
  success. Inference/storage failures are separate; an inferred result with failed
  storage is NOT saved and cannot be treated as a complete successful request.
