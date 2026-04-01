import streamlit as st
import pandas as pd
import os

from services.market_data import fetch_usd_inr_rate, update_prices_in_db
from services.email_sync import sync_latest_reports_from_email
from services.portfolio_service import (
    get_all_accounts, delete_account, update_account_name, 
    update_account_status, get_or_create_account, save_holdings
)
from services.parsers import parse_vested, parse_indmoney

def sidebar():
    FINNHUB_KEY = st.secrets.get("FINNHUB_API_KEY", "")
    AV_KEY = st.secrets.get("ALPHAVANTAGE_API_KEY", "")

    with st.sidebar:
        st.markdown("<div class='sidebar-header'>Settings</div>", unsafe_allow_html=True)
        use_inr = st.toggle("Show in INR (₹)", value=False)
        st.session_state.use_inr = use_inr
        
        if use_inr:
            rate = fetch_usd_inr_rate()
            st.caption(f"Rate: $1 = ₹{rate:,.2f}")
            
        st.markdown("<div class='sidebar-header'>Maintenance</div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Live Prices"):
            if not FINNHUB_KEY and not AV_KEY:
                st.sidebar.error("API Keys missing in secrets.toml.")
            else:
                update_prices_in_db(FINNHUB_KEY, AV_KEY)
                st.rerun()

        if st.button("📧 Sync from Email"):
            sync_latest_reports_from_email()

        if "latest_fetch_results" in st.session_state:
            with st.expander("📊 Latest Fetch Summary"):
                results_df = pd.DataFrame(st.session_state.latest_fetch_results)
                st.dataframe(results_df, use_container_width=True, hide_index=True)

        st.markdown("<div class='sidebar-header'>Accounts</div>", unsafe_allow_html=True)
        accounts_df = get_all_accounts()
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

        st.markdown("<div class='sidebar-header'>Import</div>", unsafe_allow_html=True)
        uploaded_files = st.file_uploader("Upload INDmoney/Vested files", type=['csv', 'xlsx', 'xls'], accept_multiple_files=True)
        
        if uploaded_files and st.button("Process Files"):
            processed_count = 0
            for uploaded_file in uploaded_files:
                try:
                    # Auto-detect platform
                    content = uploaded_file.getvalue()
                    uploaded_file.seek(0)
                    
                    # Heuristic for detection
                    is_vested = False
                    if uploaded_file.name.endswith('.xlsx'):
                        xls_test = pd.ExcelFile(uploaded_file)
                        if 'Holdings' in xls_test.sheet_names and 'User Details' in xls_test.sheet_names:
                            is_vested = True
                        uploaded_file.seek(0)

                    if is_vested:
                        df, b_id = parse_vested(uploaded_file, uploaded_file.name)
                        acc_id = get_or_create_account("Vested", b_id, b_id)
                    else:
                        # Default to INDmoney or attempt detection
                        df, b_id = parse_indmoney(uploaded_file, uploaded_file.name)
                        acc_id = get_or_create_account("INDmoney", b_id, b_id)
                    
                    if not df.empty:
                        save_holdings(df, acc_id)
                        processed_count += 1
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {e}")
            
            if processed_count > 0:
                st.success(f"Successfully processed {processed_count} file(s)!")
                st.rerun()

        if st.button("🚀 Fast Scan /files"):
            files_dir = "files"
            if os.path.exists(files_dir):
                for f_name in os.listdir(files_dir):
                    f_path = os.path.join(files_dir, f_name)
                    if os.path.isfile(f_path):
                        with open(f_path, 'rb') as f:
                            if 'IND-' in f_name:
                                df, b_id = parse_indmoney(f, f_name)
                                acc_id = get_or_create_account('INDmoney', b_id, b_id)
                            elif 'Vested' in f_name:
                                df, b_id = parse_vested(f, f_name)
                                acc_id = get_or_create_account('Vested', b_id, b_id)
                            else:
                                continue
                            
                            if not df.empty:
                                save_holdings(df, acc_id)
                st.success("Sync complete!")
                st.rerun()

        return active_ids
