import requests
import streamlit as st
import time
from datetime import datetime
import pandas as pd
from utils.db import execute_query, fetch_data

@st.cache_data(ttl=3600) # Cache exchange rate for 1 hour
def fetch_usd_inr_rate():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        response.raise_for_status()
        data = response.json()
        return data.get("rates", {}).get("INR", 83.0) # Fallback to 83.0 if not found
    except Exception as e:
        st.warning("Could not fetch live USD/INR rate. Using fallback 83.0.")
        return 83.0

def fetch_live_price(ticker, finnhub_key, av_key):
    # Skip cash or unsupported tickers
    if ticker.upper() in ['USD', 'INR', 'CASH']:
        return None

    # Clean ticker (e.g., remove suffixes if needed, though most US stocks are just the symbol)
    clean_ticker = ticker.strip().upper()
    
    # 1. Try Finnhub
    if finnhub_key:
        try:
            url = f"https://finnhub.io/api/v1/quote?symbol={clean_ticker}&token={finnhub_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'c' in data and data['c'] > 0:
                    return data['c']
            elif response.status_code == 429: # Rate limit
                print(f"Finnhub rate limit hit for {clean_ticker}")
            else:
                print(f"Finnhub error {response.status_code} for {clean_ticker}")
        except Exception as e:
            print(f"Finnhub fetch error for {clean_ticker}: {e}")

    # 2. Fallback to Alpha Vantage
    if av_key:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={clean_ticker}&apikey={av_key}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'Global Quote' in data and '05. price' in data['Global Quote']:
                    price_str = data['Global Quote']['05. price']
                    if price_str:
                        return float(price_str)
            elif response.status_code == 429:
                print(f"Alpha Vantage rate limit hit for {clean_ticker}")
            else:
                print(f"Alpha Vantage empty/error for {clean_ticker}: {data}")
        except Exception as e:
            print(f"Alpha Vantage fetch error for {clean_ticker}: {e}")

    return None

def update_prices_in_db(finnhub_key, av_key):
    if not finnhub_key and not av_key:
        st.sidebar.warning("API Keys missing. Cannot fetch live prices.")
        return

    # Get all unique tickers from DB
    unique_tickers_df = fetch_data("SELECT DISTINCT ticker FROM holdings")
    if unique_tickers_df.empty:
        return

    progress_text = "Fetching live prices. Please wait..."
    my_bar = st.progress(0, text=progress_text)
    total_tickers = len(unique_tickers_df)
    
    updated_count = 0
    fetch_results = []
    
    for i, row in unique_tickers_df.iterrows():
        ticker = row['ticker']
        live_price = fetch_live_price(ticker, finnhub_key, av_key)
        
        status = "Success" if live_price is not None else "Failed"
        if live_price is not None:
            # Update current_price in holdings table
            update_query = """
            UPDATE holdings 
            SET current_price = ?,
                last_updated = ?
            WHERE ticker = ?
            """
            execute_query(update_query, (live_price, datetime.now(), ticker))
            updated_count += 1
        
        fetch_results.append({
            "Ticker": ticker,
            "Price": f"${live_price:.2f}" if live_price else "N/A",
            "Status": status
        })
            
        # Respect rate limits
        time.sleep(0.5) 
        my_bar.progress((i + 1) / total_tickers, text=f"Fetched {ticker} ({i+1}/{total_tickers})")
    
    st.session_state.latest_fetch_results = fetch_results
    my_bar.empty()
    st.sidebar.success(f"Updated {updated_count} holding(s).")
