import streamlit as st
from components.sidebar import sidebar
from components.dashboard import dashboard
from utils.theme import apply_custom_styles
from utils.db import init_db

st.set_page_config(page_title="Net Worth - Unified Portfolio Tracker", page_icon="💰", layout="wide")
apply_custom_styles()
init_db()

# Sidebar with no category means global view
active_ids = sidebar() 
st.header("💰 Net Worth")
dashboard(active_ids, is_global=True)
