import json
import logging
from datetime import datetime, timezone


ALLOWED_FIELDS = {"model_id", "revision", "request_id", "label_count", "latency_ms", "error_type", "object_path"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
            **getattr(record, "event_fields", {}),
        }, ensure_ascii=False, allow_nan=False)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("zeroshot_app")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return logger


def log_event(event: str, **metadata) -> None:
    """Call with fixed event names and reviewed metadata, never raw exception text."""
    fields = {key: value for key, value in metadata.items() if key in ALLOWED_FIELDS}
    configure_logging().info(event, extra={"event_fields": fields})
