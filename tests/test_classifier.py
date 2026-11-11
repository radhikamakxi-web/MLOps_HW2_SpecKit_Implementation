import pytest

from app.services.classifier import ZeroShotClassifier


def test_validate_labels_rejects_too_few_labels():
    classifier = ZeroShotClassifier()
    with pytest.raises(ValueError):
        classifier.validate_labels(["sports"])


def test_validate_labels_removes_duplicates_and_empty_values():
    classifier = ZeroShotClassifier()
    labels = classifier.validate_labels(["sports", "", "sports", "politics"])
    assert labels == ["sports", "politics"]


def test_classify_rejects_empty_text():
    classifier = ZeroShotClassifier()
    with pytest.raises(ValueError):
        classifier.classify("   ", ["sports", "politics"], "facebook/bart-large-mnli")
