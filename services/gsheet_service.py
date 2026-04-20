"""
Google Sheets API service for reading and writing performance transaction data.
Supports both gspread (OAuth) and CSV export methods.
"""
import pandas as pd
import gspread
import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
import json
import os

# ── Sheet Configuration ───────────────────────────────────────────────────────
SHEET_ID = "1z_22sy-HriW9LvBQLQ7TEsdhASHV_f0AdwbawXfC5l0"
TRANSACTIONS_SHEET_NAME = "Transactions"
SUMMARY_SHEET_NAME = "Summary"

# CSV export method (fallback, read-only)
# Note: gid=2098678572 is the Transactions sheet ID
TRANSACTIONS_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/export?format=csv&gid=2098678572"
)


# ── Initialization & Authentication ────────────────────────────────────────────

@st.cache_resource
def get_gsheet_client():
    """
    Returns authenticated gspread client.
    Requires service account JSON or Streamlit secrets configured.
    """
    try:
        # Method 1: Try Streamlit secrets (recommended)
        if "google_service_account" in st.secrets:
            creds_dict = st.secrets["google_service_account"]
            gc = gspread.service_account_from_dict(creds_dict)
            return gc
    except Exception as e:
        st.warning(f"Google Sheets API not configured: {e}")
        return None

    return None


@st.cache_data(ttl=300)
def fetch_transactions_sheet_data() -> pd.DataFrame:
    """
    Fetches transaction data from Google Sheet.
    Falls back to CSV if gspread unavailable.
    
    Returns DataFrame with columns:
    - asset_class
    - amount (can be negative for withdrawals)
    - investment_date
    - notes
    """
    # Try gspread first (live data)
    gc = get_gsheet_client()
    if gc:
        try:
            sheet = gc.open_by_key(SHEET_ID)
            # Try to get "Transactions" worksheet
            try:
                ws = sheet.worksheet(TRANSACTIONS_SHEET_NAME)
            except gspread.exceptions.WorksheetNotFound:
                # Fallback to first sheet
                ws = sheet.sheet1
            
            data = ws.get_all_records()
            if data:
                df = pd.DataFrame(data)
                df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
                return df
        except Exception as e:
            st.warning(f"Gspread read failed: {e}. Using CSV fallback.")

    # Fallback: Read CSV export
    try:
        df = pd.read_csv(TRANSACTIONS_CSV_URL)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Failed to fetch transactions: {e}")
        return pd.DataFrame()


def add_transaction(
    asset_class: str,
    amount: float,
    investment_date: str,
    notes: str = ""
) -> bool:
    """
    Adds a new transaction to Google Sheet.
    
    Args:
        asset_class: e.g., "Crypto", "US Market"
        amount: Positive for investment, negative for withdrawal
        investment_date: Format YYYY-MM-DD
        notes: Optional description
    
    Returns:
        True if successful, False otherwise
    """
    gc = get_gsheet_client()
    if not gc:
        st.error("""
        🔴 Google Sheets API not configured.
        
        To enable transaction updates, set up Streamlit secrets:
        
        1. Create `.streamlit/secrets.toml`:
        ```toml
        [google_service_account]
        type = "service_account"
        project_id = "your-project-id"
        private_key_id = "..."
        private_key = "..."
        client_email = "..."
        client_id = "..."
        auth_uri = "https://accounts.google.com/o/oauth2/auth"
        token_uri = "https://oauth2.googleapis.com/token"
        auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
        client_x509_cert_url = "..."
        ```
        
        See: https://console.cloud.google.com/
        """)
        return False

    try:
        sheet = gc.open_by_key(SHEET_ID)
        
        # Create or get Transactions worksheet
        try:
            ws = sheet.worksheet(TRANSACTIONS_SHEET_NAME)
        except gspread.exceptions.WorksheetNotFound:
            # Create if doesn't exist
            ws = sheet.add_worksheet(title=TRANSACTIONS_SHEET_NAME, rows=100, cols=4)
            # Add headers
            ws.append_row(["asset_class", "amount", "investment_date", "notes"])
        
        # Append new row
        ws.append_row([asset_class, amount, investment_date, notes])
        
        st.success(f"✅ Transaction added: {asset_class} {amount:+,.0f} on {investment_date}")
        # Clear cache to refresh data
        st.cache_data.clear()
        return True
        
    except Exception as e:
        st.error(f"Failed to add transaction: {e}")
        return False


def update_transaction(
    row_index: int,
    asset_class: str,
    amount: float,
    investment_date: str,
    notes: str = ""
) -> bool:
    """
    Updates an existing transaction.
    row_index is 1-based (0 is header)
    """
    gc = get_gsheet_client()
    if not gc:
        st.error("Google Sheets API not configured.")
        return False

    try:
        sheet = gc.open_by_key(SHEET_ID)
        ws = sheet.worksheet(TRANSACTIONS_SHEET_NAME)
        
        # Update row (row_index is 1-based)
        ws.update_values(
            [["asset_class", "amount", "investment_date", "notes"]],
            {
                "range": f"A{row_index}:D{row_index}",
                "values": [[asset_class, amount, investment_date, notes]]
            }
        )
        st.success(f"✅ Transaction updated")
        st.cache_data.clear()
        return True
        
    except Exception as e:
        st.error(f"Failed to update transaction: {e}")
        return False


def delete_transaction(row_index: int) -> bool:
    """
    Deletes a transaction row.
    """
    gc = get_gsheet_client()
    if not gc:
        st.error("Google Sheets API not configured.")
        return False

    try:
        sheet = gc.open_by_key(SHEET_ID)
        ws = sheet.worksheet(TRANSACTIONS_SHEET_NAME)
        ws.delete_rows(row_index)
        st.success(f"✅ Transaction deleted")
        st.cache_data.clear()
        return True
        
    except Exception as e:
        st.error(f"Failed to delete transaction: {e}")
        return False
