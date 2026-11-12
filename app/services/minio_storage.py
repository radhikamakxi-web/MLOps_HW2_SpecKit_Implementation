from __future__ import annotations

import io
import json
from datetime import datetime, timezone
from uuid import uuid4

from minio import Minio

from app.utils.config import get_minio_settings


class MinIOStorage:
    def __init__(self):
        settings = get_minio_settings()
        self.client = Minio(
            settings["endpoint"],
            access_key=settings["access_key"],
            secret_key=settings["secret_key"],
            secure=settings["secure"],
        )
        self.bucket_name = settings["bucket"]

    def ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def build_object_path(self, request_id: str | None = None) -> str:
        now = datetime.now(timezone.utc)
        request_id = request_id or str(uuid4())
        return f"predictions/{now.year:04d}/{now.month:02d}/{now.day:02d}/{request_id}.json"

    def save_prediction(self, payload: dict) -> str:
        self.ensure_bucket()
        request_id = payload.get("request_id") or str(uuid4())
        payload["request_id"] = request_id
        object_path = self.build_object_path(request_id)
        encoded_data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.client.put_object(
            self.bucket_name,
            object_path,
            data=io.BytesIO(encoded_data),
            length=len(encoded_data),
            content_type="application/json",
        )
        return object_path
