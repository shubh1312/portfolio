import streamlit as st
from components.sidebar import sidebar
from components.dashboard import dashboard
from utils.theme import apply_custom_styles

st.set_page_config(page_title="Lending", page_icon="🤝", layout="wide")
apply_custom_styles()

active_ids = sidebar(category="Lending")

st.markdown("### 🤝 Lending Tracker")
st.markdown("""
Your lending details are synced directly from your **Google Sheet**. 
The current value is listed identically to the invested amount.
""")

if not active_ids:
    st.info("Sync your lending from the sidebar (Google Sheet).")
else:
    dashboard(active_ids)
