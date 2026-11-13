from __future__ import annotations

from datetime import datetime, timezone
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

DEFAULT_LABELS = ["sports", "politics", "technology", "finance", "health", "education"]
if "label_options" not in st.session_state:
    st.session_state.label_options = DEFAULT_LABELS.copy()
if "selected_labels" not in st.session_state:
    st.session_state.selected_labels = ["sports", "politics", "technology", "finance"]


def add_custom_label() -> None:
    new_label = st.session_state.new_label_input.strip().lower()
    if new_label:
        if new_label not in st.session_state.label_options:
            st.session_state.label_options.append(new_label)
        if new_label not in st.session_state.selected_labels:
            st.session_state.selected_labels.append(new_label)
    st.session_state.new_label_input = ""


if not available_models:
    st.warning("No local models are available. Download one from the admin page first.")

selected_model = st.selectbox("Select model", available_models or ["No model available"])

selected_labels = st.multiselect(
    "Candidate labels",
    options=st.session_state.label_options,
    key="selected_labels",
)

col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
with col1:
    st.text_input(
        "Add a new label",
        key="new_label_input",
        placeholder="Type a new label and press Enter...",
        label_visibility="collapsed",
        on_change=add_custom_label,
    )
with col2:
    st.button("Add", on_click=add_custom_label, use_container_width=True)

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
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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
        try:
            object_path = storage.save_prediction(payload)
            st.success(f"Prediction saved to MinIO at {object_path}")
        except Exception as e:
            st.warning(f"Classification succeeded, but saving the prediction to MinIO failed: {e}")
    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Classification failed: {exc}")
