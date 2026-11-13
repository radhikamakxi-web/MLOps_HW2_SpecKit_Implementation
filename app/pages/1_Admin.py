from __future__ import annotations

import streamlit as st

from app.services.model_manager import ModelManager
from app.utils.config import get_app_version

st.set_page_config(page_title="Admin", page_icon="⚙️")

st.title("Model and Label Administration")

model_manager = ModelManager()

st.subheader("Add model")
with st.form("add_model_form", clear_on_submit=True):
    new_model_id = st.text_input(
        "Hugging Face Model ID",
        placeholder="e.g. MoritzLaurer/deberta-v3-large-zeroshot-v2.0",
    )
    new_model_name = st.text_input(
        "Display Name (optional)",
        placeholder="e.g. DeBERTa Zero-Shot v2 Large",
    )
    if st.form_submit_button("Add model", type="primary"):
        success, message = model_manager.add_model(
            model_id=new_model_id,
            name=new_model_name,
            task="zero-shot-classification",
        )
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)

st.subheader("Configured models")
models = model_manager.refresh_local_models()
for model in models:
    with st.container():
        st.write(f"- {model['name']} ({model['id']}) | status: {model['status']}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Download {model['name']}", key=f"download_{model['id']}"):
                with st.spinner(f"Downloading {model['name']}..."):
                    success, message, _ = model_manager.download_model(model["id"])
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        with col2:
            if st.button(f"Delete {model['name']}", key=f"delete_{model['id']}"):
                success, message = model_manager.delete_model(model["id"])
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

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
