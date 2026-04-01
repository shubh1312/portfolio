import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Unified Portfolio Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme import apply_custom_styles
from utils.db import init_db
from components.sidebar import sidebar
from components.dashboard import dashboard

# Apply styles and initialize database
apply_custom_styles()
init_db()

if __name__ == "__main__":
    active_ids = sidebar()
    dashboard(active_ids)
