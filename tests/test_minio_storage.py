from app.services.minio_storage import MinIOStorage


def test_object_path_follows_expected_structure(monkeypatch):
    # Synthetic settings only: never depend on a developer's .env or real server.
    for key, value in {
        "MINIO_ENDPOINT": "localhost:9000",
        "MINIO_ACCESS_KEY": "unit-test-access",
        "MINIO_SECRET_KEY": "unit-test-secret-not-a-real-credential",
        "MINIO_BUCKET": "unit-test-predictions",
        "MINIO_SECURE": "false",
    }.items():
        monkeypatch.setenv(key, value)
    storage = MinIOStorage()
    path = storage.build_object_path("abc123")
    assert path.startswith("predictions/")
    assert path.endswith("/abc123.json")
