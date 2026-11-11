"""Shared prediction contract: independent of Streamlit and the storage SDK."""
import math
import re
from datetime import datetime, timezone
from uuid import UUID

from app.utils.config import validate_labels


def utc_timestamp(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if timestamp.tzinfo is None or timestamp.utcoffset().total_seconds() != 0:
            raise ValueError
        return timestamp.astimezone(timezone.utc)
    except (ValueError, AttributeError, TypeError):
        raise ValueError("Prediction timestamp must be timezone-aware UTC ISO 8601.") from None


def valid_score(value) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and 0 <= value <= 1


def validate_prediction(payload: dict) -> None:
    if not isinstance(payload, dict):
        raise ValueError("Prediction must be a JSON object.")
    required = {"request_id", "timestamp", "input_text", "predicted_class", "confidence",
                "candidate_labels", "ranked_predictions", "model", "model_name", "model_revision",
                "application_version", "inference_latency_ms"}
    if not required.issubset(payload):
        raise ValueError("Prediction is missing required metadata.")
    try:
        UUID(payload["request_id"])
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Prediction request_id must be a UUID.") from None
    utc_timestamp(payload["timestamp"])
    for key in ("input_text", "model", "model_name", "application_version"):
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise ValueError("Prediction text and model/application metadata must be nonempty strings.")
    labels = validate_labels(payload["candidate_labels"])
    if labels != payload["candidate_labels"]:
        raise ValueError("Prediction candidate labels must already be normalized.")
    ranked = payload["ranked_predictions"]
    if not isinstance(ranked, list) or len(ranked) != len(labels):
        raise ValueError("Prediction ranking must cover each candidate label.")
    if any(not isinstance(item, dict) or not isinstance(item.get("label"), str)
           or not valid_score(item.get("score")) for item in ranked):
        raise ValueError("Prediction ranking contains invalid labels or scores.")
    scores = [item["score"] for item in ranked]
    if set(item["label"] for item in ranked) != set(labels) or scores != sorted(scores, reverse=True):
        raise ValueError("Prediction ranking must contain each candidate once, in descending score order.")
    if (not valid_score(payload["confidence"]) or payload["predicted_class"] != ranked[0]["label"]
            or payload["confidence"] != scores[0]):
        raise ValueError("Prediction class/confidence must match the highest-ranked result.")
    revision = payload["model_revision"]
    if revision is not None and (not isinstance(revision, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", revision)):
        raise ValueError("Prediction revision must be an immutable commit or null when unknown.")
    latency = payload["inference_latency_ms"]
    if isinstance(latency, bool) or not isinstance(latency, (int, float)) or not math.isfinite(latency) or latency < 0:
        raise ValueError("Prediction latency must be finite and nonnegative.")