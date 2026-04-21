import streamlit as st
import pandas as pd

from services.market_data import fetch_usd_inr_rate, update_prices_in_db
from services.email_sync import sync_latest_reports_from_email
from services.portfolio_service import (
    get_all_accounts, delete_account, update_account_name,
    update_account_status, get_or_create_account, save_holdings,
)
from services.parsers import parse_vested, parse_indmoney, parse_zerodha
from services.zerodha_service import sync_from_kite_api, sync_mf_from_kite_api, get_token_info


def sidebar(category=None):
    FINNHUB_KEY = st.secrets.get("FINNHUB_API_KEY", "")
    AV_KEY      = st.secrets.get("ALPHAVANTAGE_API_KEY", "")

    # ── Zerodha OAuth redirect handler ────────────────────────────────────────
    if "request_token" in st.query_params:
        request_token = st.query_params["request_token"]
        st.sidebar.markdown("""
        <div style="background:rgba(199,246,81,.08);padding:12px 14px;
             border-radius:8px;border:1px solid rgba(199,246,81,.2);margin-bottom:12px;
             font-size:12px;color:#EDE6D6;">
            <strong>Zerodha login detected</strong><br>
            Select the account to link this session to:
        </div>
        """, unsafe_allow_html=True)
        cols = st.sidebar.columns(3)
        for i in range(1, 4):
            display_name = st.secrets.get(f"ZERODHA_{i}_DISPLAY_NAME", f"Acc {i}")
            if cols[i - 1].button(display_name, key=f"oauth_acc_{i}"):
                from services.zerodha_service import generate_kite_session
                if generate_kite_session(i, request_token):
                    st.toast(f"{display_name} authenticated", icon="✓")
                    st.query_params.clear()
                    st.rerun()

    with st.sidebar:
        # ── Currency toggle ────────────────────────────────────────────────────
        use_inr = st.toggle("Show in INR (₹)", value=(category != "US Market"))
        st.session_state.use_inr = use_inr
        if use_inr:
            rate = fetch_usd_inr_rate()
            if rate:
                st.caption(f"$1 = ₹{rate:,.2f}")

        # ── Sync actions (contextual per page) ────────────────────────────────
        has_sync = category in ("US Market", "Crypto", "Indian Mutual Funds",
                                "Indian Stock Market", "Lending")
        if has_sync:
            st.markdown("<div class='sidebar-header'>Sync</div>", unsafe_allow_html=True)

        if category in ("US Market", "Crypto", "Indian Mutual Funds"):
            label_map = {
                "US Market":           "Refresh US prices",
                "Crypto":              "Refresh crypto prices",
                "Indian Mutual Funds": "Refresh MF prices",
            }
            if st.button(label_map[category], key="refresh_prices"):
                if category == "US Market" and not FINNHUB_KEY and not AV_KEY:
                    st.sidebar.error("API keys missing in secrets.toml.")
                else:
                    with st.spinner("Updating prices…"):
                        update_prices_in_db(FINNHUB_KEY, AV_KEY, category=category)
                        st.rerun()

        if category == "US Market":
            if st.button("Sync reports from email", key="sync_email"):
                with st.spinner("Syncing…"):
                    sync_latest_reports_from_email()
                    st.rerun()

        if category == "Indian Stock Market":
            _zerodha_sync_ui(mode="stocks")

        if category == "Indian Mutual Funds":
            _zerodha_sync_ui(mode="mf")
            if st.button("Sync Paytm MFs from Google Sheet", key="sync_paytm_mf"):
                from services.mf_service import sync_mf_from_gsheet
                with st.spinner("Fetching…"):
                    if sync_mf_from_gsheet():
                        st.rerun()

        if category == "Crypto":
            if st.button("Sync crypto from Google Sheet", key="sync_crypto"):
                from services.crypto_service import sync_crypto_from_gsheet
                with st.spinner("Fetching…"):
                    if sync_crypto_from_gsheet():
                        st.rerun()

        if category == "Lending":
            if st.button("Sync lending from Google Sheet", key="sync_lending"):
                from services.lending_service import sync_lending_from_gsheet
                with st.spinner("Fetching…"):
                    if sync_lending_from_gsheet():
                        st.rerun()

        # ── Accounts ──────────────────────────────────────────────────────────
        st.markdown("<div class='sidebar-header'>Accounts</div>", unsafe_allow_html=True)

        accounts_df = get_all_accounts(category)
        active_ids  = []
        if not accounts_df.empty:
            for _, acc in accounts_df.iterrows():
                col_check, col_name, col_del = st.columns([0.15, 0.7, 0.15])
                is_checked = col_check.checkbox(
                    "", value=bool(acc["is_active"]),
                    key=f"acc_chk_{acc['id']}", label_visibility="collapsed",
                )
                new_name = col_name.text_input(
                    "", value=acc["name"],
                    key=f"acc_name_{acc['id']}", label_visibility="collapsed",
                )
                if col_del.button("✕", key=f"del_{acc['id']}"):
                    delete_account(acc["id"])
                    st.rerun()
                if new_name != acc["name"]:
                    update_account_name(acc["id"], new_name)
                    st.rerun()
                if is_checked:
                    active_ids.append(acc["id"])
                if is_checked != bool(acc["is_active"]):
                    update_account_status(acc["id"], is_checked)
                    st.rerun()
        else:
            st.caption(f"No {'  ' + category if category else ''} accounts yet.")

        # ── Import ─────────────────────────────────────────────────────────────
        if category in ("US Market", "Indian Stock Market", "Indian Mutual Funds"):
            st.markdown("<div class='sidebar-header'>Import</div>", unsafe_allow_html=True)

            label_map = {
                "US Market":           ("INDmoney / Vested CSV or XLSX", ["csv", "xlsx", "xls"]),
                "Indian Stock Market": ("Zerodha Console XLSX / CSV",    ["csv", "xlsx"]),
                "Indian Mutual Funds": ("Coin / Paytm Money files",      ["csv", "xlsx"]),
            }
            lbl, exts = label_map[category]
            uploaded = st.file_uploader(lbl, type=exts, accept_multiple_files=True,
                                        label_visibility="collapsed")
            if uploaded and st.button("Process files", key="process_files"):
                _process_files(uploaded, category)

        # ── Fetch summary (collapsed) ──────────────────────────────────────────
        if "latest_fetch_results" in st.session_state:
            with st.expander("Last fetch summary"):
                st.dataframe(
                    pd.DataFrame(st.session_state.latest_fetch_results),
                    use_container_width=True, hide_index=True,
                )

        return active_ids


def _zerodha_sync_ui(mode: str):
    """Render per-account Zerodha auth status, login link, and sync button."""
    from datetime import datetime, date

    any_configured = False
    for i in range(1, 4):
        api_key = st.secrets.get(f"ZERODHA_{i}_API_KEY", "")
        if not api_key or "your_api_key" in api_key:
            continue
        any_configured = True

        display_name = st.secrets.get(f"ZERODHA_{i}_DISPLAY_NAME", f"Acc {i}")
        user_id      = st.secrets.get(f"ZERODHA_{i}_USER_ID", "")
        label        = f"{display_name} ({user_id})" if user_id else display_name

        token_info = get_token_info(i)
        is_today   = False
        if token_info and token_info.get("timestamp"):
            ts = datetime.fromisoformat(token_info["timestamp"])
            is_today = ts.date() == date.today()

        is_valid = token_info and token_info.get("access_token") and is_today

        if is_valid:
            if st.button(
                f"Sync {label}" if mode == "stocks" else f"Sync Coin {label}",
                key=f"sync_{mode}_{i}",
            ):
                api_secret = st.secrets.get(f"ZERODHA_{i}_API_SECRET", "")
                with st.spinner("Syncing…"):
                    if mode == "stocks":
                        ok = sync_from_kite_api(api_key, api_secret,
                                                token_info["access_token"], display_name, i)
                    else:
                        ok = sync_mf_from_kite_api(api_key, api_secret,
                                                   token_info["access_token"], display_name, i)
                    if ok:
                        st.toast(f"{display_name} synced")
                        st.rerun()
        else:
            status = "token expired" if (token_info and token_info.get("access_token")) else "not logged in"
            st.caption(f"{label}: {status}")
            login_url = f"https://kite.zerodha.com/connect/login?v=3&api_key={api_key}"
            st.link_button(f"Login — {display_name}", login_url, use_container_width=True)

    if not any_configured:
        st.caption("No Zerodha accounts configured in secrets.toml.")


def _process_files(uploaded_files, category):
    from services.portfolio_service import get_or_create_account, save_holdings

    processed = 0
    for f in uploaded_files:
        try:
            is_vested = False
            if f.name.endswith(".xlsx"):
                try:
                    xls_test = pd.ExcelFile(f)
                    if {"Holdings", "User Details"} <= set(xls_test.sheet_names):
                        is_vested = True
                    f.seek(0)
                except Exception:
                    pass

            if category == "US Market":
                if is_vested:
                    df, b_id = parse_vested(f, f.name)
                    acc_id = get_or_create_account("Vested", b_id, b_id, asset_category="US Market")
                else:
                    df, b_id = parse_indmoney(f, f.name)
                    acc_id = get_or_create_account("INDmoney", b_id, b_id, asset_category="US Market")
                currency = "USD"
            elif category == "Indian Stock Market":
                df, b_id = parse_zerodha(f, f.name)
                acc_id = get_or_create_account("Zerodha", b_id, b_id, asset_category="Indian Stock Market")
                currency = "INR"
            elif category == "Indian Mutual Funds":
                st.warning("Mutual Fund file parser not yet implemented.")
                continue

            if not df.empty:
                save_holdings(df, acc_id, currency=currency)
                processed += 1
        except Exception as e:
            st.error(f"Error processing {f.name}: {e}")

    if processed > 0:
        st.success(f"Processed {processed} file(s).")
        st.rerun()
