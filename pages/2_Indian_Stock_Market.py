import streamlit as st
from components.sidebar import sidebar
from components.dashboard import dashboard
from utils.theme import apply_custom_styles

st.set_page_config(page_title="Indian Stock Market", page_icon="🇮🇳", layout="wide")
apply_custom_styles()

active_ids = sidebar(category="Indian Stock Market")
dashboard(active_ids)
