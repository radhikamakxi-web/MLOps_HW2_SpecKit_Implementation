from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Zero-Shot MLOps", page_icon="🧠", layout="wide")

st.title("Zero-Shot Text Classification Platform")
st.write("Use the pages below to manage models and run inference.")

PAGES = [
    "Admin",
    "Classify Text",
]

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", PAGES)

if selection == "Admin":
    st.switch_page("pages/1_Admin.py")
else:
    st.switch_page("pages/2_Classify_Text.py")
