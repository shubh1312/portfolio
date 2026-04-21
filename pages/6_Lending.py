import streamlit as st
from components.sidebar import sidebar
from components.dashboard import dashboard
from utils.theme import apply_custom_styles

apply_custom_styles()

active_ids = sidebar(category="Lending")
st.title("Lending")
st.caption("Holdings synced from Google Sheet · current value mirrors invested amount")

if not active_ids:
    st.info("Sync your lending data from the sidebar and enable at least one account.")
else:
    dashboard(active_ids)
