import pandas as pd
import streamlit as st
from services.portfolio_service import get_or_create_account, save_holdings

LENDING_SHEET_ID = "1z_22sy-HriW9LvBQLQ7TEsdhASHV_f0AdwbawXfC5l0"
LENDING_GID = "1312242874"
LENDING_GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{LENDING_SHEET_ID}/export?format=csv&gid={LENDING_GID}"

def clean_amount(val):
    if isinstance(val, str):
        val = val.replace('₹', '').replace(',', '').strip()
        try:
            return float(val)
        except ValueError:
            return 0.0
    return float(val) if pd.notnull(val) else 0.0

def sync_lending_from_gsheet():
    """Fetch lending money from Google Sheet and save to database."""
    try:
        df = pd.read_csv(LENDING_GSHEET_URL)
        if df.empty:
            st.error("Google Sheet is empty.")
            return False

        # Ensure valid rows
        df = df.dropna(subset=['name', 'amount'])
        
        # Clean currency columns
        df['amount_clean'] = df['amount'].apply(clean_amount)
        
        acc_name = "Lending"

        # Map to our schema
        mapped_df = pd.DataFrame({
            'ticker': df['name'],           # Use borrower name as ticker
            'name': df['name'],             
            'quantity': 1,                  # Quantity is 1
            'avg_price': df['amount_clean'],
            'current_price': df['amount_clean'], # Current value = invested value
            'total_invested': df['amount_clean']
        })
        
        acc_id = get_or_create_account("Google Sheets", acc_name, "GS_Lending", asset_category="Lending")
        save_holdings(mapped_df, acc_id, currency="INR")
            
        return True
    except Exception as e:
        st.error(f"Failed to sync Lending Sheet: {e}")
        return False
