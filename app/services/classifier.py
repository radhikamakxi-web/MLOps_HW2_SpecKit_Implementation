from __future__ import annotations

from typing import Any


class ZeroShotClassifier:
    def __init__(self, model_id: str | None = None):
        self.model_id = model_id
        self._pipeline = None

    def validate_labels(self, candidate_labels: list[str]) -> list[str]:
        if not candidate_labels:
            raise ValueError("At least two candidate labels are required.")
        labels = [str(label).strip() for label in candidate_labels if str(label).strip()]
        unique_labels = []
        seen = set()
        for label in labels:
            if label not in seen:
                unique_labels.append(label)
                seen.add(label)
        if len(unique_labels) < 2:
            raise ValueError("At least two unique candidate labels are required.")
        return unique_labels

    def _get_pipeline(self, model_id: str):
        if self._pipeline is None or self.model_id != model_id:
            try:
                from transformers import pipeline
            except Exception as exc:  # pragma: no cover - environment-dependent
                raise RuntimeError(f"Unable to initialize transformers pipeline: {exc}") from exc
            self.model_id = model_id
            self._pipeline = pipeline(
                task="zero-shot-classification",
                model=model_id,
            )
        return self._pipeline

    def classify(self, text: str, candidate_labels: list[str], model_id: str) -> dict[str, Any]:
        if not text or not str(text).strip():
            raise ValueError("Input text cannot be empty.")

        labels = self.validate_labels(candidate_labels)
        if not model_id:
            raise ValueError("A model must be selected before classification.")

        pipe = self._get_pipeline(model_id)
        result = pipe(text, candidate_labels=labels)
        ranked = [
            {"label": label, "score": float(score)}
            for label, score in zip(result.get("labels", []), result.get("scores", []))
        ]
        predicted = result.get("labels", [])[0] if result.get("labels") else None
        confidence = float(result.get("scores", [0.0])[0]) if result.get("scores") else 0.0
        return {
            "predicted_class": predicted,
            "confidence": confidence,
            "candidate_labels": labels,
            "ranked_predictions": ranked,
            "model": model_id,
        }
