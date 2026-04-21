import streamlit as st
from components.sidebar import sidebar
from components.dashboard import dashboard
from utils.theme import apply_custom_styles
from services.zerodha_service import generate_kite_session

apply_custom_styles()

# ── Zerodha OAuth redirect handler ───────────────────────────────────────────
if "request_token" in st.query_params:
    request_token = st.query_params["request_token"]
    target_acc    = st.query_params.get("acc")
    if target_acc:
        with st.status(f"Authenticating Zerodha account {target_acc}…", expanded=True) as s:
            token = generate_kite_session(target_acc, request_token)
            if token:
                s.update(label="Authenticated — you can now sync Coin holdings.", state="complete", expanded=False)
                st.query_params.clear()
            else:
                s.update(label="Authentication failed.", state="error")

active_ids = sidebar(category="Indian Mutual Funds")
st.title("Mutual Funds")
dashboard(active_ids)
