from __future__ import annotations

import streamlit as st

from app.services.model_manager import ModelManager
from app.utils.config import get_app_version

st.set_page_config(page_title="Admin", page_icon="⚙️")

st.title("Model and Label Administration")

model_manager = ModelManager()

st.subheader("Configured models")
models = model_manager.refresh_local_models()
for model in models:
    with st.container():
        st.write(f"- {model['name']} ({model['id']}) | status: {model['status']}")
        if st.button(f"Download {model['name']}", key=f"download_{model['id']}"):
            success, message, _ = model_manager.download_model(model['id'])
            st.success(message) if success else st.error(message)

        if st.button(f"Delete {model['name']}", key=f"delete_{model['id']}"):
            success, message = model_manager.delete_model(model['id'])
            st.success(message) if success else st.error(message)

st.subheader("Local model directory")
st.write(str(model_manager.model_dir))
st.write(f"HF cache: {model_manager.hf_home}")

if st.button("Clear Hugging Face cache"):
    ok, msg = model_manager.clear_hf_cache()
    st.success(msg) if ok else st.error(msg)

st.subheader("Candidate labels")
existing = ["sports", "politics", "technology", "finance", "health", "education"]
selected = st.multiselect("Labels", existing, default=existing)
if st.button("Save labels"):
    st.success(f"Saved {len(selected)} labels.")

st.caption(f"Application version: {get_app_version()}")
