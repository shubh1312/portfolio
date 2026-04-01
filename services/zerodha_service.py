import os
import json
import pandas as pd
import streamlit as st
from kiteconnect import KiteConnect
from services.portfolio_service import get_or_create_account, save_holdings

TOKEN_FILE = "data/zerodha_tokens.json"

def get_kite_instance(account_id):
    """Get KiteConnect instance with stored access token if available."""
    api_key = st.secrets.get(f"ZERODHA_{account_id}_API_KEY", "")
    if not api_key or "your_api_key" in api_key:
        return None
        
    kite = KiteConnect(api_key=api_key)
    
    # Try to load token from file
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            tokens = json.load(f)
            if str(account_id) in tokens:
                 kite.set_access_token(tokens[str(account_id)])
    
    return kite

def save_access_token(account_id, access_token):
    """Store access token in a persistent file."""
    os.makedirs("data", exist_ok=True)
    tokens = {}
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            tokens = json.load(f)
    
    tokens[str(account_id)] = access_token
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f)

def sync_from_kite_api(api_key, api_secret, access_token, account_name, account_id):
    """Sync Equity holdings from Kite."""
    display_name = st.secrets.get(f"ZERODHA_{account_id}_DISPLAY_NAME", account_name)
    user_id = st.secrets.get(f"ZERODHA_{account_id}_USER_ID", str(account_id))
    full_name = f"{display_name} ({user_id})" if display_name != account_name else display_name
    
    try:
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        holdings = kite.holdings()
        if not holdings: return False

        df = pd.DataFrame(holdings)
        df_mapped = pd.DataFrame({
            'ticker': df['tradingsymbol'],
            'quantity': df['quantity'],
            'avg_price': df['average_price'],
            'current_price': df['last_price'],
            'total_invested': df['quantity'] * df['average_price']
        })
        
        acc_id = get_or_create_account("Zerodha", full_name, user_id, asset_category="Indian Stock Market")
        save_holdings(df_mapped, acc_id, currency="INR")
        return True
    except Exception as e:
        st.error(f"Kite API Error ({full_name}): {e}")
        return False

def sync_mf_from_kite_api(api_key, api_secret, access_token, account_name, account_id):
    """Sync Mutual Fund holdings from Zerodha (Coin)."""
    display_name = st.secrets.get(f"ZERODHA_{account_id}_DISPLAY_NAME", account_name)
    user_id = st.secrets.get(f"ZERODHA_{account_id}_USER_ID", str(account_id))
    full_name = f"{display_name} Coin ({user_id})"
    
    try:
        kite = KiteConnect(api_key=api_key)
        kite.set_access_token(access_token)
        holdings = kite.mf_holdings() # GET /portfolio/mf/holdings
        
        if not holdings:
            st.warning(f"No Mutual Fund holdings found for {full_name}.")
            return False

        df = pd.DataFrame(holdings)
        # MF fields: tradingsymbol, fund (name), quantity, average_price, last_price (NAV)
        df_mapped = pd.DataFrame({
            'ticker': df['fund'], # Use fund name as ticker for MF
            'quantity': df['quantity'],
            'avg_price': df['average_price'],
            'current_price': df['last_price'],
            'total_invested': df['quantity'] * df['average_price']
        })
        
        acc_id = get_or_create_account("Zerodha Coin", full_name, f"{user_id}_MF", asset_category="Indian Mutual Funds")
        save_holdings(df_mapped, acc_id, currency="INR")
        return True
    except Exception as e:
        st.error(f"Kite MF API Error ({full_name}): {e}")
        return False

def generate_kite_session(account_id, request_token):
    """Exchange request_token for access_token and persist it."""
    api_key = st.secrets.get(f"ZERODHA_{account_id}_API_KEY", "")
    api_secret = st.secrets.get(f"ZERODHA_{account_id}_API_SECRET", "")
    
    try:
        kite = KiteConnect(api_key=api_key)
        data = kite.generate_session(request_token, api_secret=api_secret)
        save_access_token(account_id, data["access_token"])
        return data["access_token"]
    except Exception as e:
        display_name = st.secrets.get(f"ZERODHA_{account_id}_DISPLAY_NAME", f"Account {account_id}")
        st.error(f"Failed to generate session for {display_name}: {e}")
        return None
