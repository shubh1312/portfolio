import streamlit as st
from components.sidebar import sidebar
from components.dashboard import dashboard
from utils.theme import apply_custom_styles

st.set_page_config(page_title="Crypto Market", page_icon="₿", layout="wide")
apply_custom_styles()

active_ids = sidebar(category="Crypto")

st.markdown("### ₿ Crypto Portfolio Tracker")
st.markdown("""
Your crypto holdings are synced directly from your **Google Sheet**. 
Live prices are fetched from **CoinGecko**.
""")

if not active_ids:
    st.info("Sync your holdings from the sidebar (Google Sheet) and select the active accounts below.")
else:
    dashboard(active_ids)
