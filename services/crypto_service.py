import pandas as pd
import requests
import streamlit as st
from services.portfolio_service import get_or_create_account, save_holdings
from utils.db import execute_query, fetch_data
from datetime import datetime

# Public Google Sheet CSV Export URL
SHEET_ID = "1z_22sy-HriW9LvBQLQ7TEsdhASHV_f0AdwbawXfC5l0"
GID = "0"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

from services.market_data import fetch_usd_inr_rate

def sync_crypto_from_gsheet():
    """Fetch crypto holdings from Google Sheet and save to database."""
    try:
        df = pd.read_csv(GSHEET_URL)
        if df.empty:
            st.error("Google Sheet is empty.")
            return False

        # Columns: account, symbol, crypto, qty, avg buy price, invested
        # symbol is like BTCUSDT
        
        # Group by account
        accounts = df['account'].unique()
        for acc_name in accounts:
            acc_df = df[df['account'] == acc_name]
            
            # Map to our schema
            mapped_df = pd.DataFrame({
                'ticker': acc_df['symbol'], # Use BTCUSDT as unique ticker
                'name': acc_df['crypto'],   # Optional metadata
                'quantity': acc_df['qty'],
                'avg_price': acc_df['avg buy price'],
                'current_price': acc_df['avg buy price'], # Placeholder
                'total_invested': acc_df['invested']
            })
            
            acc_id = get_or_create_account("Crypto", acc_name, f"GS_{acc_name}", asset_category="Crypto")
            save_holdings(mapped_df, acc_id, currency="INR")
            
        return True
    except Exception as e:
        st.error(f"Failed to sync Crypto Sheet: {e}")
        return False

def update_crypto_live_prices():
    """Fetch live prices from Binance (USD) and convert to INR."""
    # Get all crypto tickers (symbols like BTCUSDT)
    query = """
        SELECT DISTINCT h.ticker 
        FROM holdings h
        JOIN accounts a ON h.account_id = a.id
        WHERE a.asset_category = 'Crypto'
    """
    tickers_df = fetch_data(query)
    if tickers_df.empty:
        return 0
    
    fx_rate = fetch_usd_inr_rate()
    updated_count = 0
    
    for symbol in tickers_df['ticker'].tolist():
        # Using MEXC API instead of Binance to avoid 403 Forbidden geolocation IP errors on Streamlit Cloud
        # MEXC API: GET /api/v3/ticker/price?symbol=BTCUSDT
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                price_usd = float(data['price'])
                price_inr = price_usd * fx_rate
                
                update_query = """
                UPDATE holdings 
                SET current_price = ?,
                    last_updated = ?
                WHERE ticker = ? AND account_id IN (SELECT id FROM accounts WHERE asset_category = 'Crypto')
                """
                execute_query(update_query, (price_inr, datetime.now(), symbol))
                updated_count += 1
            else:
                st.warning(f"Failed to fetch price for {symbol} from MEXC.")
        except Exception as e:
            print(f"MEXC API error for {symbol}: {e}")
            
    return updated_count
