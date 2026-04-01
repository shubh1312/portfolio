import pandas as pd
import requests
import streamlit as st
from services.portfolio_service import get_or_create_account, save_holdings
from utils.db import execute_query, fetch_data
from datetime import datetime

PAYTM_SHEET_ID = "1z_22sy-HriW9LvBQLQ7TEsdhASHV_f0AdwbawXfC5l0"
PAYTM_GID = "1686574545"
PAYTM_GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{PAYTM_SHEET_ID}/export?format=csv&gid={PAYTM_GID}"

def clean_currency(val):
    if isinstance(val, str):
        return float(val.replace('₹', '').replace(',', '').strip())
    return float(val)

def sync_mf_from_gsheet():
    """Fetch Paytm Money mutual fund holdings from Google Sheet and save to database."""
    try:
        df = pd.read_csv(PAYTM_GSHEET_URL)
        if df.empty:
            st.error("Google Sheet is empty.")
            return False

        # Columns: symbol, qty, avg buy price, invested, AMFI
        acc_name = "Paytm Money"
        
        # Clean currency columns
        df['avg_price'] = df['avg buy price'].apply(clean_currency)
        df['invested_clean'] = df['invested'].apply(clean_currency)
        
        # Map to our schema
        mapped_df = pd.DataFrame({
            'ticker': df['symbol'], # Use full fund name as ticker
            'name': df['symbol'],
            'quantity': df['qty'],
            'avg_price': df['avg_price'],
            'current_price': df['avg_price'], # Placeholder until live update
            'total_invested': df['invested_clean']
        })
        
        acc_id = get_or_create_account("Paytm Money", acc_name, "GS_Paytm_Money", asset_category="Indian Mutual Funds")
        save_holdings(mapped_df, acc_id, currency="INR")
            
        return True
    except Exception as e:
        st.error(f"Failed to sync Paytm Money Sheet: {e}")
        return False

def update_mf_live_prices():
    """Fetch live NAV for Mutual Funds. For Paytm Money, uses AMFI code from GSheet."""
    
    # 1. Fetch current AMFI mapping from GSheet
    try:
        df = pd.read_csv(PAYTM_GSHEET_URL)
        # Create mapping of symbol -> AMFI
        amfi_mapping = dict(zip(df['symbol'], df['AMFI']))
    except Exception as e:
        print(f"Could not load AMFI mapping from GSheet: {e}")
        amfi_mapping = {}

    # 2. Get all MF tickers from DB
    query = """
        SELECT DISTINCT h.ticker, a.platform 
        FROM holdings h
        JOIN accounts a ON h.account_id = a.id
        WHERE a.asset_category = 'Indian Mutual Funds' AND a.platform = 'Paytm Money'
    """
    tickers_df = fetch_data(query)
    if tickers_df.empty:
        return 0
    
    updated_count = 0
    
    for _, row in tickers_df.iterrows():
        symbol = row['ticker']
        amfi_code = amfi_mapping.get(symbol)
        
        if not amfi_code or pd.isna(amfi_code):
            print(f"Skipping {symbol}, no AMFI code found.")
            continue
            
        # Ensure AMFI is string or int without decimals if it came as float
        try:
            amfi_str = str(int(amfi_code))
        except ValueError:
            amfi_str = str(amfi_code)
            
        url = f"https://api.mfapi.in/mf/{amfi_str}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    latest_nav_str = data['data'][0]['nav']
                    latest_nav = float(latest_nav_str)
                    
                    update_query = """
                    UPDATE holdings 
                    SET current_price = ?,
                        last_updated = ?
                    WHERE ticker = ? AND account_id IN (SELECT id FROM accounts WHERE platform = 'Paytm Money')
                    """
                    execute_query(update_query, (latest_nav, datetime.now(), symbol))
                    updated_count += 1
                else:
                    print(f"No NAV data found for AMFI {amfi_str}")
            else:
                print(f"Failed to fetch NAV for AMFI {amfi_str}.")
        except Exception as e:
            print(f"MF API error for {amfi_str}: {e}")
            
    return updated_count
