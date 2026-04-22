import streamlit as st
from components.sidebar import sidebar
from components.dashboard import dashboard
from utils.theme import apply_custom_styles, THEME
from services.zerodha_service import generate_kite_session

apply_custom_styles()

# ── Zerodha OAuth redirect handler ───────────────────────────────────────────
# Set Kite Connect redirect URL to: http://localhost:8501/indian-stocks?acc=1
if "request_token" in st.query_params:
    _req_token  = st.query_params.get("request_token", "")
    _target_acc = st.query_params.get("acc")
    if _target_acc and _req_token:
        with st.status(f"Authenticating Zerodha account {_target_acc}…", expanded=True) as _s:
            _token = generate_kite_session(_target_acc, _req_token)
            if _token:
                _s.update(label=f"✅ Account {_target_acc} connected — sync from the sidebar.", state="complete", expanded=False)
            else:
                _s.update(label="❌ Authentication failed. Try logging in again.", state="error")
    else:
        st.warning("⚠️ Ensure your Kite redirect URL ends with `?acc=1` (or `?acc=2`, `?acc=3`).")
    st.query_params.clear()

active_ids = sidebar(category="Indian Stock Market")
st.title("Indian Stocks")
dashboard(active_ids)
