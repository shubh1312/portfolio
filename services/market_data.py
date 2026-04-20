import requests
import streamlit as st
import time
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from utils.db import execute_query, fetch_data

# Thread-safe lock and session for connection pooling
_progress_lock = Lock()
_session = requests.Session()  # Reuse connections for faster requests

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
            response = _session.get(url, timeout=3)  # Reduced from 5 to 3 seconds
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
            response = _session.get(url, timeout=3)  # Reduced from 5 to 3 seconds
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

def update_prices_in_db(finnhub_key, av_key, category=None):
    if category == "US Market":
        if not finnhub_key and not av_key:
            st.sidebar.warning("US Market API Keys missing. Cannot fetch live prices.")
            return

        # Get all unique tickers from DB for this category
        query = """
        SELECT DISTINCT h.ticker 
        FROM holdings h
        JOIN accounts a ON h.account_id = a.id
        WHERE a.asset_category = 'US Market'
        """
        unique_tickers_df = fetch_data(query)
    elif category == "Crypto":
        from services.crypto_service import update_crypto_live_prices
        with st.spinner("Updating Crypto prices from Binance..."):
            updated_count = update_crypto_live_prices()
            if updated_count:
                st.sidebar.success(f"Updated {updated_count} Crypto coin(s).")
            else:
                st.sidebar.warning("No Crypto prices updated.")
        return
    elif category == "Indian Mutual Funds":
        from services.mf_service import update_mf_live_prices
        with st.spinner("Updating MF prices from mfapi.in..."):
            updated_count = update_mf_live_prices()
            if updated_count:
                st.sidebar.success(f"Updated {updated_count} MF(s).")
            else:
                st.sidebar.warning("No MF prices updated.")
        return
    else:
        # Fallback to all if no category (or ignore based on user request)
        return

    if unique_tickers_df.empty:
        st.sidebar.info("No holdings found to update.")
        return

    progress_text = f"Fetching {category} prices (⚡ turbo mode). Please wait..."
    my_bar = st.progress(0, text=progress_text)
    total_tickers = len(unique_tickers_df)
    
    updated_count = 0
    fetch_results = []
    completed_count = 0
    batch_updates = []  # Batch database updates
    
    # Worker function for thread pool
    def fetch_ticker_price(row):
        """Fetch price for a single ticker"""
        ticker = row['ticker']
        live_price = fetch_live_price(ticker, finnhub_key, av_key)
        return {
            'ticker': ticker,
            'price': live_price,
        }
    
    # Use ThreadPoolExecutor with aggressive parallelization
    # max_workers=20 = fetch 20 prices simultaneously (faster with modern APIs)
    with ThreadPoolExecutor(max_workers=20) as executor:
        # Submit all tasks
        futures = {
            executor.submit(fetch_ticker_price, row): row 
            for _, row in unique_tickers_df.iterrows()
        }
        
        # Process completed tasks as they finish
        for future in as_completed(futures):
            try:
                result = future.result()
                ticker = result['ticker']
                live_price = result['price']
                
                if live_price is not None:
                    # Batch updates instead of individual updates (much faster)
                    batch_updates.append((live_price, datetime.now(), ticker))
                    updated_count += 1
                
                # Display correctly based on category in summary
                price_display = f"${live_price:,.2f}" if live_price else "N/A"
                status = "✓" if live_price is not None else "✗"
                
                fetch_results.append({
                    "Ticker": ticker,
                    "Price": price_display,
                    "Status": status
                })
                
                # Update progress less frequently to avoid slowdown
                completed_count += 1
                if completed_count % 5 == 0 or completed_count == total_tickers:
                    with _progress_lock:
                        my_bar.progress(
                            completed_count / total_tickers, 
                            text=f"Fetched {completed_count}/{total_tickers}"
                        )
                    
            except Exception as e:
                print(f"Error in thread: {e}")
                completed_count += 1
    
    # Batch update database (much faster than individual updates)
    if batch_updates:
        try:
            update_query = """
            UPDATE holdings 
            SET current_price = ?,
                last_updated = ?
            WHERE ticker = ?
            """
            for price, timestamp, ticker in batch_updates:
                execute_query(update_query, (price, timestamp, ticker))
        except Exception as e:
            print(f"Batch update error: {e}")
    
    st.session_state.latest_fetch_results = fetch_results
    my_bar.empty()
    st.sidebar.success(f"✓ Updated {updated_count} {category} holding(s).")
