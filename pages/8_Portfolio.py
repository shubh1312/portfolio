import streamlit as st
from components.sidebar import sidebar
from components.dashboard import dashboard
from utils.theme import apply_custom_styles
from utils.db import init_db

apply_custom_styles()
init_db()

active_ids = sidebar()
st.title("Portfolio")
dashboard(active_ids, is_global=True)
