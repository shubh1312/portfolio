import streamlit as st
from components.sidebar import sidebar
from components.dashboard import dashboard
from utils.theme import apply_custom_styles

apply_custom_styles()

active_ids = sidebar(category="Crypto")
st.title("Crypto")
st.caption("Holdings synced from Google Sheet · prices from CoinGecko")

if not active_ids:
    st.info("Sync your holdings from the sidebar and enable at least one account.")
else:
    dashboard(active_ids)
