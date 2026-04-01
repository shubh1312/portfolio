import streamlit as st
import pandas as pd
import os

from services.market_data import fetch_usd_inr_rate, update_prices_in_db
from services.email_sync import sync_latest_reports_from_email
from services.portfolio_service import (
    get_all_accounts, delete_account, update_account_name, 
    update_account_status, get_or_create_account, save_holdings
)
from services.parsers import parse_vested, parse_indmoney, parse_zerodha
from services.zerodha_service import sync_from_kite_api, get_kite_instance

def sidebar(category=None):
    FINNHUB_KEY = st.secrets.get("FINNHUB_API_KEY", "")
    AV_KEY = st.secrets.get("ALPHAVANTAGE_API_KEY", "")

    # Global: Catch-all for Kite Redirect
    query_params = st.query_params
    if "request_token" in query_params:
        request_token = query_params["request_token"]
        st.sidebar.markdown("""
        <div style="background-color:#fff3cd; padding:15px; border-radius:10px; border:1px solid #ffeeba; margin-bottom:15px;">
            <strong>Incoming Zerodha Login</strong><br>
            Request token detected. Which account should we save this for?
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.sidebar.columns(3)
        for i in range(1, 4):
            display_name = st.secrets.get(f"ZERODHA_{i}_DISPLAY_NAME", f"Acc {i}")
            if cols[i-1].button(display_name):
                from services.zerodha_service import generate_kite_session
                if generate_kite_session(i, request_token):
                    st.toast(f"✅ {display_name} Authenticated!", icon="🚀")
                    st.query_params.clear()
                    st.rerun()

    with st.sidebar:
        st.markdown(f"<div class='sidebar-header'>{category if category else 'Global'} Settings</div>", unsafe_allow_html=True)
        
        # Currency Toggle
        use_inr = st.toggle("Show all in INR (₹)", value=(category != "US Market"))
        st.session_state.use_inr = use_inr
        
        if use_inr:
            rate = fetch_usd_inr_rate()
            if rate:
                st.caption(f"Conversion Rate: $1 = ₹{rate:,.2f}")
            
        st.markdown("<div class='sidebar-header'>Maintenance</div>", unsafe_allow_html=True)
        if category in ["US Market", "Crypto", "Indian Mutual Funds"]:
            if st.button(f"🔄 Refresh {category} Prices"):
                if category == "US Market" and not FINNHUB_KEY and not AV_KEY:
                    st.sidebar.error("API Keys missing in secrets.toml.")
                else:
                    with st.spinner("Updating prices..."):
                        update_prices_in_db(FINNHUB_KEY, AV_KEY, category=category)
                        st.rerun()
        else:
            st.info(f"Price sync not needed for {category if category else 'Global'}.")

        if category == "US Market":
            if st.button("📧 Sync US Reports from Email"):
                with st.spinner("Syncing..."):
                    sync_latest_reports_from_email()
                    st.rerun()
        
        if category == "Indian Stock Market":
            # API Sync Option for Zerodha
            st.markdown("---")
            st.caption("⚡ Automated Zerodha Sync")
            auth_needed = False
            for i in range(1, 4):
                api_key = st.secrets.get(f"ZERODHA_{i}_API_KEY", "")
                if api_key and "your_api_key" not in api_key:
                    display_name = st.secrets.get(f"ZERODHA_{i}_DISPLAY_NAME", f"Acc {i}")
                    user_id = st.secrets.get(f"ZERODHA_{i}_USER_ID", "")
                    label = f"{display_name} ({user_id})" if user_id else display_name
                    
                    kite = get_kite_instance(i)
                    if kite and kite.access_token:
                        if st.button(f"Sync Stocks {label}", key=f"sync_btn_{i}"):
                            api_secret = st.secrets.get(f"ZERODHA_{i}_API_SECRET", "")
                            with st.spinner(f"Syncing..."):
                                if sync_from_kite_api(api_key, api_secret, kite.access_token, display_name, i):
                                    st.toast(f"✅ {display_name} Stocks synced!")
                                    st.rerun()
                    else:
                        st.caption(f"⚠️ {label}: Login required")
                        auth_needed = True
            
            if auth_needed:
                if st.button("🔗 Go to Zerodha Connect", key="go_auth_stocks"):
                    st.switch_page("pages/5_Zerodha_Connect.py")
        
        if category == "Indian Mutual Funds":
            # API Sync Option for Zerodha Coin
            st.markdown("---")
            st.caption("⚡ Automated Zerodha Coin Sync")
            auth_needed = False
            for i in range(1, 4):
                api_key = st.secrets.get(f"ZERODHA_{i}_API_KEY", "")
                if api_key and "your_api_key" not in api_key:
                    display_name = st.secrets.get(f"ZERODHA_{i}_DISPLAY_NAME", f"Acc {i}")
                    user_id = st.secrets.get(f"ZERODHA_{i}_USER_ID", "")
                    label = f"{display_name} ({user_id})" if user_id else display_name
                    
                    kite = get_kite_instance(i)
                    if kite and kite.access_token:
                        if st.button(f"Sync Coin {label}", key=f"sync_mf_btn_{i}"):
                            api_secret = st.secrets.get(f"ZERODHA_{i}_API_SECRET", "")
                            from services.zerodha_service import sync_mf_from_kite_api
                            with st.spinner(f"Syncing Coin..."):
                                if sync_mf_from_kite_api(api_key, api_secret, kite.access_token, display_name, i):
                                    st.toast(f"✅ {display_name} Coin synced!")
                                    st.rerun()
                    else:
                        st.caption(f"⚠️ {label}: Login required")
                        auth_needed = True
            
            if auth_needed:
                if st.button("🔗 Go to Zerodha Connect", key="go_auth_mf"):
                    st.switch_page("pages/5_Zerodha_Connect.py")
            
            st.markdown("---")
            st.caption("⚡ Paytm Money (Google Sheet) Sync")
            if st.button("🔄 Sync Paytm MFs from Google Sheet"):
                from services.mf_service import sync_mf_from_gsheet
                with st.spinner("Fetching Google Sheet..."):
                    if sync_mf_from_gsheet():
                        st.success("Paytm MF holdings synced!")
                        st.rerun()

        if category == "Crypto":
            st.markdown("---")
            st.caption("⚡ Google Sheet Core Sync")
            if st.button("🔄 Sync Crypto from Google Sheet"):
                from services.crypto_service import sync_crypto_from_gsheet
                with st.spinner("Fetching Google Sheet..."):
                    if sync_crypto_from_gsheet():
                        st.success("Crypto holdings synced!")
                        st.rerun()

        if category == "Lending":
            st.markdown("---")
            st.caption("⚡ Google Sheet Core Sync")
            if st.button("🔄 Sync Lending from Google Sheet"):
                from services.lending_service import sync_lending_from_gsheet
                with st.spinner("Fetching Google Sheet..."):
                    if sync_lending_from_gsheet():
                        st.success("Lending data synced!")
                        st.rerun()

        if "latest_fetch_results" in st.session_state:
            with st.expander("📊 Latest Fetch Summary"):
                results_df = pd.DataFrame(st.session_state.latest_fetch_results)
                st.dataframe(results_df, use_container_width=True, hide_index=True)

        # Account Management
        header = f"{category} Accounts" if category else "All Accounts"
        st.markdown(f"<div class='sidebar-header'>{header}</div>", unsafe_allow_html=True)
        
        accounts_df = get_all_accounts(category)
        active_ids = []
        if not accounts_df.empty:
            for _, acc in accounts_df.iterrows():
                col_check, col_name, col_del = st.columns([0.15, 0.7, 0.15])
                is_checked = col_check.checkbox("", value=bool(acc['is_active']), key=f"acc_chk_{acc['id']}", label_visibility="collapsed")
                new_name = col_name.text_input("", value=acc['name'], key=f"acc_name_{acc['id']}", label_visibility="collapsed")
                
                if col_del.button("🗑️", key=f"del_{acc['id']}"):
                    delete_account(acc['id'])
                    st.rerun()

                if new_name != acc['name']:
                    update_account_name(acc['id'], new_name)
                    st.rerun()
                
                if is_checked:
                    active_ids.append(acc['id'])
                if is_checked != bool(acc['is_active']):
                    update_account_status(acc['id'], is_checked)
                    st.rerun()
        else:
            st.info(f"No {category if category else ''} accounts found.")

        # Import Logic based on category
        st.markdown("<div class='sidebar-header'>Import Data</div>", unsafe_allow_html=True)
        
        if category == "US Market":
            uploaded_files = st.file_uploader("Upload INDmoney/Vested files (US)", type=['csv', 'xlsx', 'xls'], accept_multiple_files=True)
            if uploaded_files and st.button("Process US Files"):
                process_files(uploaded_files, "US Market")
        
        elif category == "Indian Stock Market":
            uploaded_files = st.file_uploader("Upload Zerodha Console XLSX/CSV", type=['csv', 'xlsx'], accept_multiple_files=True)
            if uploaded_files and st.button("Process Zerodha Files"):
                process_files(uploaded_files, "Indian Stock Market")
                
        elif category == "Indian Mutual Funds":
            uploaded_files = st.file_uploader("Upload Coin/Paytm Money files", type=['csv', 'xlsx'], accept_multiple_files=True)
            if uploaded_files and st.button("Process Mutual Fund Files"):
                process_files(uploaded_files, "Indian Mutual Funds")

        elif not category:
            st.caption("Go to specific pages to import data.")

        return active_ids

def process_files(uploaded_files, category):
    processed_count = 0
    for uploaded_file in uploaded_files:
        try:
            # Heuristic for detection
            is_vested = False
            if uploaded_file.name.endswith('.xlsx'):
                try:
                    xls_test = pd.ExcelFile(uploaded_file)
                    if 'Holdings' in xls_test.sheet_names and 'User Details' in xls_test.sheet_names:
                        is_vested = True
                    uploaded_file.seek(0)
                except:
                    pass

            if category == "US Market":
                if is_vested:
                    df, b_id = parse_vested(uploaded_file, uploaded_file.name)
                    acc_id = get_or_create_account("Vested", b_id, b_id, asset_category="US Market")
                else:
                    df, b_id = parse_indmoney(uploaded_file, uploaded_file.name)
                    acc_id = get_or_create_account("INDmoney", b_id, b_id, asset_category="US Market")
                currency = 'USD'
            elif category == "Indian Stock Market":
                df, b_id = parse_zerodha(uploaded_file, uploaded_file.name)
                acc_id = get_or_create_account("Zerodha", b_id, b_id, asset_category="Indian Stock Market")
                currency = 'INR'
            elif category == "Indian Mutual Funds":
                # Placeholder for Mutual Fund parser
                st.warning("Mutual Fund parser not implemented yet.")
                continue
            
            if not df.empty:
                save_holdings(df, acc_id, currency=currency)
                processed_count += 1
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")
    
    if processed_count > 0:
        st.success(f"Successfully processed {processed_count} file(s)!")
        st.rerun()
