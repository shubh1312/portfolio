import streamlit as st
from services.zerodha_service import generate_kite_session, get_kite_instance, get_token_info
import pandas as pd
from datetime import datetime, date

st.set_page_config(page_title="Zerodha Connect", layout="wide")

# Custom CSS for modern look
st.markdown("""
<style>
    .auth-card {
        padding: 2rem;
        border-radius: 15px;
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-active { background-color: #d4edda; color: #155724; }
    .status-expired { background-color: #f8d7da; color: #721c24; }
    .status-warning { background-color: #fff3cd; color: #856404; }
</style>
""", unsafe_allow_html=True)

st.title("🔗 Zerodha Kite Connectivity")
st.markdown("""
Connect your Zerodha accounts using the official **Kite Connect API**. 
Authentication is required once per day to maintain a valid access token.
""")

# 1. Handle OAuth Redirect
query_params = st.query_params
if "request_token" in query_params:
    request_token = query_params["request_token"]
    # Identify which account this token belongs to.
    # We support an optional 'acc' param in the redirect URL (manual configuration in Kite portal)
    target_acc = query_params.get("acc")
    
    if target_acc:
        with st.status(f"Authenticating Zerodha Account {target_acc}...", expanded=True) as status:
            token = generate_kite_session(target_acc, request_token)
            if token:
                status.update(label="Authentication Successful!", state="complete", expanded=False)
                st.success(f"Account {target_acc} is now connected. You can sync holdings from the sidebar.")
                # Clear URL params
                st.query_params.clear()
            else:
                status.update(label="Authentication Failed", state="error")
    else:
        st.warning("Request token received, but couldn't identify the target account. Please ensure your Redirect URL in Kite Portal includes `?acc=1` (or 2, 3) at the end.")
        if st.button("Manually assign this session to Account..."):
             acc_choice = st.radio("Which account did you just log into?", [1, 2, 3], horizontal=True)
             if st.button("Confirm & Save"):
                 generate_kite_session(acc_choice, request_token)
                 st.query_params.clear()
                 st.rerun()

st.divider()

# 2. Account Status Grid
st.subheader("Configured Accounts")
cols = st.columns(3)

for i in range(1, 4):
    with cols[i-1]:
        api_key = st.secrets.get(f"ZERODHA_{i}_API_KEY", "")
        if not api_key or "your_api_key" in api_key:
            st.info(f"**Account {i}**\n\nNot configured in `secrets.toml`.")
            continue
            
        display_name = st.secrets.get(f"ZERODHA_{i}_DISPLAY_NAME", f"Zerodha {i}")
        user_id = st.secrets.get(f"ZERODHA_{i}_USER_ID", "")
        
        token_info = get_token_info(i)
        is_authenticated = token_info and token_info.get("access_token")
        
        # Calculate status metadata
        ts_text = ""
        status_class = "status-expired"
        status_text = "NOT LOGGED IN"
        
        if is_authenticated:
            if token_info.get("timestamp"):
                ts = datetime.fromisoformat(token_info.get("timestamp"))
                is_today = ts.date() == date.today()
                ts_text = f"<p style='color:gray; font-size:0.8rem; margin-top:-5px;'>Last: {ts.strftime('%d %b, %H:%M')} {'✅' if is_today else '⚠️ (Exp)'}</p>"
                if is_today:
                    status_class = "status-active"
                    status_text = "AUTHENTICATED"
                else:
                    status_class = "status-warning"
                    status_text = "TOKEN EXPIRED"
            else:
                # Token exists but timestamp is unknown (old format)
                ts_text = "<p style='color:orange; font-size:0.8rem; margin-top:-5px;'>⚠️ Login age unknown (Pre-update)</p>"
                status_class = "status-warning"
                status_text = "REFRESH RECOMMENDED"
        
        st.markdown(f"""
        <div class="auth-card">
            <h4>{display_name}</h4>
            <p style='color:gray; font-size:0.9rem;'>{user_id}</p>
            {ts_text}
            <p>API Key: <code>{api_key[:10]}...</code></p>
            <span class="status-badge {status_class}">{status_text}</span>
        </div>
        """, unsafe_allow_html=True)
        
        login_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={api_key}"
        st.link_button(f"Login as {display_name}", login_url, use_container_width=True)
        
        if is_authenticated:
            if st.button(f"Test Sync {display_name}", key=f"test_{i}"):
                from services.zerodha_service import sync_from_kite_api
                api_secret = st.secrets.get(f"ZERODHA_{i}_API_SECRET", "")
                if sync_from_kite_api(api_key, api_secret, token_info['access_token'], display_name, i):
                    st.toast(f"✅ {display_name} holdings synced!")
                else:
                    st.error("Sync failed. If this error persists, try logging in again to refresh the token.")

st.divider()
st.markdown("""
### 💡 Setup Instructions
1. Login to [Kite Connect Developer Portal](https://kite.trade/).
2. For each of your 3 accounts, ensure the **Redirect URL** corresponds to this page.
   - Example for Account 1: `http://localhost:8501/Zerodha_Connect?acc=1`
   - Example for Account 2: `http://localhost:8501/Zerodha_Connect?acc=2`
3. Add your `API_KEY` and `API_SECRET` to `.streamlit/secrets.toml`.
""")
