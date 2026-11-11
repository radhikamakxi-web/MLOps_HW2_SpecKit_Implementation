from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

import streamlit as st

from app.services.classifier import ZeroShotClassifier
from app.services.minio_storage import MinIOStorage
from app.services.model_manager import ModelManager
from app.utils.config import get_app_version

st.set_page_config(page_title="Text Classification", page_icon="📝")

st.title("Zero-Shot Classification")

model_manager = ModelManager()
classifier = ZeroShotClassifier()

available_models = [model["id"] for model in model_manager.refresh_local_models() if model["status"] == "available"]
label_options = ["sports", "politics", "technology", "finance", "health", "education"]

if not available_models:
    st.warning("No local models are available. Download one from the admin page first.")

selected_model = st.selectbox("Select model", available_models or ["No model available"])
selected_labels = st.multiselect("Candidate labels", label_options, default=["sports", "politics", "technology", "finance"])
text = st.text_area("Input text", value="The team won the championship after a very close game.")

if st.button("Classify"):
    try:
        result = classifier.classify(text, selected_labels, selected_model)
        st.write("### Predicted class")
        st.write(result["predicted_class"])
        st.write("### Confidence")
        st.write(result["confidence"])
        st.write("### Ranked predictions")
        for idx, item in enumerate(result["ranked_predictions"], start=1):
            st.write(f"{idx}. {item['label']} — {item['score']:.4f}")

        payload = {
            "request_id": str(uuid4()),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "input_text": text,
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "candidate_labels": result["candidate_labels"],
            "ranked_predictions": result["ranked_predictions"],
            "model": result["model"],
            "model_revision": "main",
            "application_version": get_app_version(),
        }
        storage = MinIOStorage()
        object_path = storage.save_prediction(payload)
        st.success(f"Prediction saved to MinIO at {object_path}")
    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Classification failed: {exc}")
