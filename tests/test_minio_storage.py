from app.services.minio_storage import MinIOStorage


def test_object_path_follows_expected_structure():
    storage = MinIOStorage()
    path = storage.build_object_path("abc123")
    assert path.startswith("predictions/")
    assert path.endswith("/abc123.json")
