import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import os
import requests
import time
import traceback

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Unified Portfolio Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- STYLING ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
        color: #1e2130;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    div[data-testid="stMetricValue"] {
        color: #2b3674;
        font-weight: 700;
        font-size: 1.5rem !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }
    /* Ultra-Compact Table Styling */
    [data-testid="column"] {
        padding: 0px 2px !important;
        margin: 0px !important;
    }
    div.block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1, h2, h3 {
        color: #2b3674;
        margin-bottom: 0.2rem !important;
        margin-top: 0.5rem !important;
        font-size: 1.2rem !important;
    }
    .stDataFrame {
        border: 1px solid #e9ecef;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE SETUP ---
DB_NAME = "portfolio.db"

def execute_query(query, params=()):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        st.error(f"DB Error: {e}")
        return None
    finally:
        if 'conn' in locals() and conn:
            conn.close()

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


def fetch_data(query, params=()):
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"DB Error: {e}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals() and conn:
            conn.close()

def init_db():
    # Accounts table
    execute_query('''
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            name TEXT,
            broker_id TEXT,
            is_active INTEGER DEFAULT 1,
            UNIQUE(platform, broker_id, name)
        )
    ''')
    # Holdings table linked to account
    execute_query('''
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER,
            ticker TEXT,
            quantity REAL,
            avg_price REAL,
            current_price REAL,
            total_invested REAL,
            last_updated DATETIME,
            FOREIGN KEY(account_id) REFERENCES accounts(id),
            UNIQUE(account_id, ticker)
        )
    ''')
    # Settings table for API keys
    execute_query('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

init_db()

# --- SETTINGS HELPERS ---
def get_setting(key, default=""):
    df = fetch_data("SELECT value FROM settings WHERE key = ?", (key,))
    if not df.empty:
        return df.iloc[0]['value']
    return default

def set_setting(key, value):
    execute_query("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))

# --- Live Price API Logic ---
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
    for i, row in unique_tickers_df.iterrows():
        ticker = row['ticker']
        live_price = fetch_live_price(ticker, finnhub_key, av_key)
        
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
            
        # Respect rate limits (Alpha Vantage is 25/day free usually, Finnhub is 60/min)
        # Add a small sleep to avoid getting blocked instantly if using many tickers
        time.sleep(0.5) 
        
        my_bar.progress((i + 1) / total_tickers, text=f"Fetched {ticker} ({i+1}/{total_tickers})")
    
    my_bar.empty()
    st.sidebar.success(f"Updated live prices for {updated_count} holding(s).")
    
# --- End Live Price API Logic ---

# --- HELPERS ---
def get_or_create_account(platform, broker_id, name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT id FROM accounts WHERE platform = ? AND (broker_id = ? OR name = ?)', (platform, broker_id, name))
    row = c.fetchone()
    if row:
        acc_id = row[0]
    else:
        c.execute('INSERT INTO accounts (platform, name, broker_id) VALUES (?, ?, ?)', (platform, name, broker_id))
        acc_id = c.lastrowid
    conn.commit()
    conn.close()
    return acc_id

def save_holdings(df, account_id):
    conn = sqlite3.connect(DB_NAME)
    # Clear old holdings for this account to avoid ghost entries
    conn.execute('DELETE FROM holdings WHERE account_id = ?', (account_id,))
    for _, row in df.iterrows():
        conn.execute('''
            INSERT INTO holdings (account_id, ticker, quantity, avg_price, current_price, total_invested, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (account_id, row['ticker'], row['quantity'], row['avg_price'], row['current_price'], row['total_invested'], datetime.now()))
    conn.commit()
    conn.close()

def load_filtered_holdings(active_account_ids):
    if not active_account_ids:
        return pd.DataFrame()
    conn = sqlite3.connect(DB_NAME)
    ids_str = ','.join(map(str, active_account_ids))
    query = f'''
        SELECT h.*, a.platform, a.name as account_name 
        FROM holdings h 
        JOIN accounts a ON h.account_id = a.id 
        WHERE h.account_id IN ({ids_str})
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_all_accounts():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM accounts", conn)
    conn.close()
    return df

def update_account_status(acc_id, is_active):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('UPDATE accounts SET is_active = ? WHERE id = ?', (int(is_active), acc_id))
    conn.commit()
    conn.close()

# --- PARSERS ---
def parse_indmoney(file, filename=None):
    # INDmoney can be CSV or XLS
    fname = filename if filename else file.name
    if fname.endswith('.csv'):
        df = pd.read_csv(file)
        broker_id = "Unknown_CSV"
    else:
        try:
            full_df = pd.read_excel(file, header=None)
            # Find Broker Account ID in Row 2 (index 2)
            broker_id = str(full_df.iloc[2, 1]) if full_df.shape[0] > 2 else "Unknown"
            
            # Find header row
            header_row_idx = 0
            for i, row in full_df.iterrows():
                row_str = " ".join(map(str, row.values))
                if any(keyword in row_str for keyword in ['Stock Symbol', 'Instrument Name', 'Symbol']):
                    header_row_idx = i
                    break
            
            file.seek(0)
            df = pd.read_excel(file, header=header_row_idx)
        except Exception as e:
            st.error(f"Excel parsing failed: {e}")
            df = pd.read_excel(file)
            broker_id = "Error_Parsing"
    
    col_map = {
        'ticker': ['Stock Symbol', 'Symbol', 'Ticker', 'Instrument Name'],
        'quantity': ['Quantity', 'Qty', 'Units'],
        'avg_price': ['Avg. Price ($)', 'Average Price', 'Avg Price', 'Cost Price'],
        'total_value': ['Total Value ($)', 'Total Value', 'Current Value']
    }
    
    result_cols = {}
    for target, suggestions in col_map.items():
        for suggestion in suggestions:
            match = next((col for col in df.columns if str(col).strip().lower() == suggestion.lower()), None)
            if match:
                result_cols[target] = df[match]
                break
    
    mapped_df = pd.DataFrame(result_cols)
    if 'ticker' in mapped_df.columns and 'quantity' in mapped_df.columns:
        if 'current_price' not in mapped_df.columns and 'total_value' in mapped_df.columns:
            mapped_df['current_price'] = mapped_df['total_value'] / mapped_df['quantity']
        else:
            mapped_df['current_price'] = mapped_df.get('avg_price', 0)
        
        # Calculate Total Invested for INDmoney
        mapped_df['total_invested'] = mapped_df['quantity'] * mapped_df['avg_price']
            
        final_df = mapped_df[['ticker', 'quantity', 'avg_price', 'current_price', 'total_invested']].copy()
        return final_df.dropna(subset=['ticker']), broker_id
    
    return pd.DataFrame(), broker_id

def parse_vested(file, filename=None):
    # Vested XLSX
    df = pd.read_excel(file)
    broker_id = filename if filename else file.name

    col_map = {
        'ticker': ['Ticker', 'Symbol'],
        'quantity': ['Total Shares Held', 'Quantity'],
        'avg_price': ['Average Cost (USD)', 'Avg Cost'],
        'current_price': ['Current Price (USD)', 'CMP'],
        'total_invested': ['Total Amount Invested (USD)', 'Invested Amount']
    }
    
    result_cols = {}
    for target, suggestions in col_map.items():
        for suggestion in suggestions:
            match = next((col for col in df.columns if str(col).strip().lower() == suggestion.lower()), None)
            if match:
                result_cols[target] = df[match]
                break
                
    mapped_df = pd.DataFrame(result_cols)
    if 'ticker' in mapped_df.columns:
        # Fallback for total_invested if column missing
        if 'total_invested' not in mapped_df.columns and 'quantity' in mapped_df.columns and 'avg_price' in mapped_df.columns:
             mapped_df['total_invested'] = mapped_df['quantity'] * mapped_df['avg_price']
             
        final_df = mapped_df[['ticker', 'quantity', 'avg_price', 'current_price', 'total_invested']].copy()
        return final_df.dropna(subset=['ticker']), broker_id
        
    return pd.DataFrame(), broker_id

# --- UI COMPONENTS ---
def sidebar():
    with st.sidebar:
        st.header("Settings")
        theme_mode = st.toggle("🌙 Dark Mode", value=False)
        st.session_state.theme_mode = theme_mode

        use_inr = st.toggle("Show in INR (₹)", value=False)
        st.session_state.use_inr = use_inr
        
        if use_inr:
            rate = fetch_usd_inr_rate()
            st.caption(f"Current Rate: $1 = ₹{rate:,.2f}")
            
        st.divider()

        st.header("API Integration")
        
        finnhub_key = st.text_input("Finnhub API Key", type="password", help="Required for Finnhub live prices.", value=get_setting("FINNHUB_API_KEY"))
        av_key = st.text_input("Alpha Vantage Key", type="password", help="Fallback if Finnhub limit reached.", value=get_setting("ALPHAVANTAGE_API_KEY"))
        
        c1, c2 = st.columns(2)
        if c1.button("💾 Save Keys"):
            set_setting("FINNHUB_API_KEY", finnhub_key)
            set_setting("ALPHAVANTAGE_API_KEY", av_key)
            st.success("Keys saved!")

        if c2.button("🔄 Refresh Live Prices"):
            update_prices_in_db(finnhub_key, av_key)
            st.rerun()

        st.divider()
        st.header("Portfolio Manager")
        
        # 1. Account Toggles
        st.header("Active Accounts")
        accounts_df = get_all_accounts()
        active_ids = []
        if not accounts_df.empty:
            for _, acc in accounts_df.iterrows():
                is_checked = st.checkbox(f"{acc['platform']} - {acc['name']}", value=bool(acc['is_active']), key=f"acc_{acc['id']}")
                if is_checked:
                    active_ids.append(acc['id'])
                if is_checked != bool(acc['is_active']):
                    update_account_status(acc['id'], is_checked)
                    st.rerun()
        else:
            st.info("No accounts imported yet.")

        st.divider()
        st.header("Import Data")
        platform = st.selectbox("Select Platform", ["INDmoney", "Vested"])
        account_name = st.text_input("Friendly Name (optional)", "")
        
        uploaded_file = st.file_uploader(f"Upload {platform} file", type=['csv', 'xlsx', 'xls'])
        
        if uploaded_file and st.button("Manual Process"):
            try:
                if platform == "INDmoney":
                    df, b_id = parse_indmoney(uploaded_file)
                else:
                    df, b_id = parse_vested(uploaded_file)
                
                if not df.empty:
                    name = account_name if account_name else b_id
                    acc_id = get_or_create_account(platform, b_id, name)
                    save_holdings(df, acc_id)
                    st.success(f"Updated {len(df)} holdings!")
                    st.rerun()
            except Exception as e:
                st.exception(e)

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

def dashboard(active_ids):
    # --- THEME INJECTION ---
    dark_mode = st.session_state.get('theme_mode', True)
    if dark_mode:
        bg_col = "#111114"
        sec_bg = "#19191E"
        txt_col = "#FFFFFF"
        txt_mut = "#8B949E"
        border_col = "#2A2A35"
        plotly_template = "plotly_dark"
        chart_bars = ['#F2A900', '#00D1B2'] # Softer but visible yellow and teal for dark mode
    else:
        bg_col = "#F4F6F8"
        sec_bg = "#FFFFFF"
        txt_col = "#1E1E24"
        txt_mut = "#6C757D"
        border_col = "#E5E7EB"
        plotly_template = "plotly_white"
        chart_bars = ['#ffd166', '#06d6a0'] # Original bright colors for light mode

    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background-color: {bg_col} !important; }}
    [data-testid="stSidebar"] {{ background-color: {sec_bg} !important; }}
    [data-testid="stHeader"] {{ background-color: {bg_col} !important; }}
    h1, h2, h3, h4, h5, h6, label {{ color: {txt_col} !important; }}
    p {{ color: {txt_col}; }}
    [data-testid="stMetric"] {{
        background-color: {sec_bg};
        padding: 15px;
        border-radius: 12px;
        border: 1px solid {border_col};
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    [data-testid="stMetricLabel"] p {{ color: {txt_mut} !important; font-weight: 500; font-size: 0.9rem; }}
    [data-testid="stMetricValue"] > div {{ color: {txt_col} !important; }}
    [data-testid="stPlotlyChart"] {{
        background-color: {sec_bg};
        border-radius: 12px;
        padding: 10px;
        border: 1px solid {border_col};
    }}
    hr {{ border-color: {border_col} !important; }}
    .stDataFrame {{ background-color: {sec_bg} !important; }}
    
    /* Fix sidebar white elements in dark mode */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {{ background-color: {sec_bg}; border-color: {border_col}; }}
    [data-testid="stSidebar"] [data-baseweb="select"] * {{ color: {txt_col}; }}
    [data-baseweb="popover"] > div {{ background-color: {sec_bg} !important; border: 1px solid {border_col}; }}
    [data-baseweb="menu"] * {{ color: {txt_col} !important; }}
    [data-baseweb="input"] > div {{ background-color: {sec_bg}; border-color: {border_col}; }}
    [data-baseweb="input"] input {{ color: {txt_col} !important; }}
    [data-testid="stFileUploader"] > section {{ background-color: {sec_bg}; border-color: {border_col}; }}
    
    /* Decrease table row spacing */
    .row-text {{
        font-size: 0.75rem;
        margin: 0px !important;
        padding: 4px 0px !important; /* Reduced padding */
        line-height: 1.1 !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.title("🚀 Unified Portfolio Dashboard")
    
    if not active_ids:
        st.info("Please select at least one active account in the sidebar.")
        return

    # --- LOAD & PREPROCESS ---
    df = load_filtered_holdings(active_ids)
    if df.empty:
        st.info("No holdings found for the selected accounts.")
        return

    df['total_value'] = df['quantity'] * df['current_price']
    df['total_cost'] = df.get('total_invested', df['quantity'] * df['avg_price'])
    
    # Filter out 0 invested value
    df = df[df['total_cost'] > 0].copy()
    
    if df.empty:
        st.info("No active holdings (invested > 0) found for the selected accounts.")
        return

    df['gain_loss'] = df['total_value'] - df['total_cost']
    
    # --- CURRENCY HANDLING ---
    use_inr = st.session_state.get('use_inr', False)
    fx_rate = fetch_usd_inr_rate() if use_inr else 1.0
    sym = "₹" if use_inr else "$"
    
    # Optional: Format strings for plotly
    plotly_sym = "₹%{text:,.0f}" if use_inr else "$%{text:,.0f}"

    # --- PORTFOLIO METRICS ---
    total_portfolio_value = df['total_value'].sum() * fx_rate
    total_cost = df['total_cost'].sum() * fx_rate
    total_gain = total_portfolio_value - total_cost
    total_gain_pct = (total_gain / total_cost) * 100 if total_cost > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Invested", f"{sym}{total_cost:,.2f}")
    col2.metric("Total Value", f"{sym}{total_portfolio_value:,.2f}")
    col3.metric("Total Gain/Loss", f"{sym}{total_gain:,.2f}", f"{total_gain_pct:.2f}%")
    col4.metric("Active Accounts", f"{len(df['account_id'].unique())}")

    st.divider()

    # --- CHARTS (TOP) ---
    st.header("📊 Portfolio Visualization")
    df['labeled_account'] = df['platform'] + " (" + df['account_name'] + ")"
    
    # Calculate account-level sums for bar charts
    account_sums = df.groupby('labeled_account')[['total_cost', 'total_value']].sum().reset_index()
    account_sums['total_cost'] *= fx_rate
    account_sums['total_value'] *= fx_rate
    account_sums = account_sums.sort_values(by='total_value', ascending=False)
    
    # Melt for grouped bar chart
    account_melted = account_sums.melt(id_vars=['labeled_account'], value_vars=['total_cost', 'total_value'], 
                                       var_name='Type', value_name='Amount')
    account_melted['Type'] = account_melted['Type'].replace({'total_cost': 'Invested', 'total_value': 'Current Value'})

    # 1. Invested vs Current Value by Account (Grouped Bar)
    fig_acc = px.bar(
        account_melted, x='labeled_account', y='Amount', color='Type', barmode='group',
        text='Amount',
        title='Invested vs Current Value by Account',
        labels={'labeled_account': 'Account', 'Amount': f'Amount ({sym})'},
        color_discrete_map={'Invested': chart_bars[0], 'Current Value': chart_bars[1]} 
    )
    fig_acc.update_traces(texttemplate=plotly_sym, textposition='outside')
    
    # Calculate a nice max Y range to prevent text clipping
    max_val = account_melted['Amount'].max()
    y_max = max_val * 1.15 if max_val > 0 else 1 # Add 15% headroom
    
    fig_acc.update_layout(
        template=plotly_template, 
        uniformtext_minsize=8, 
        uniformtext_mode='hide', 
        legend=dict(
            title='',
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(title=f'Amount ({sym})', range=[0, y_max]),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_acc, use_container_width=True)

    # Calculate ticker-level sums for pie charts
    ticker_sums = df.groupby('ticker')[['total_cost', 'total_value']].sum().reset_index()
    ticker_sums['total_cost'] *= fx_rate
    ticker_sums['total_value'] *= fx_rate

    c1, c2 = st.columns(2)
    
    # 2. All Holdings by Invested Amount (Pie)
    fig_all_inv = px.pie(
        ticker_sums, values='total_cost', names='ticker', 
        title='All Holdings (Invested)', hole=0.4
    )
    fig_all_inv.update_traces(textposition='inside', textinfo='percent+label')
    fig_all_inv.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    c1.plotly_chart(fig_all_inv, use_container_width=True)

    # 3. All Holdings by Current Value (Pie)
    fig_all_val = px.pie(
        ticker_sums, values='total_value', names='ticker', 
        title='All Holdings (Current Value)', hole=0.4
    )
    fig_all_val.update_traces(textposition='inside', textinfo='percent+label')
    fig_all_val.update_layout(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    c2.plotly_chart(fig_all_val, use_container_width=True)

    st.divider()

    # --- AGGREGATION FOR UNIFIED TABLE ---
    agg_df = df.groupby('ticker').agg({
        'quantity': 'sum',
        'total_cost': 'sum',
        'total_value': 'sum',
        'platform': lambda x: ", ".join(sorted(set(x))),
        'account_name': 'count'
    }).reset_index()
    
    agg_df['weighted_avg_price'] = agg_df['total_cost'] / agg_df['quantity']
    agg_df['current_price'] = agg_df['total_value'] / agg_df['quantity']
    agg_df['net_gain'] = agg_df['total_value'] - agg_df['total_cost']
    agg_df['net_gain_pct'] = (agg_df['net_gain'] / agg_df['total_cost']) * 100
    agg_df.rename(columns={'account_name': 'accounts_count'}, inplace=True)

    # --- SORTING & EXPANSION STATE ---
    if 'agg_sort_col' not in st.session_state:
        st.session_state.agg_sort_col = 'total_value'
    if 'agg_sort_dir' not in st.session_state:
        st.session_state.agg_sort_dir = 'desc'
    if 'expanded_tickers' not in st.session_state:
        st.session_state.expanded_tickers = set()

    def toggle_sort(col):
        if st.session_state.agg_sort_col == col:
            st.session_state.agg_sort_dir = 'asc' if st.session_state.agg_sort_dir == 'desc' else 'desc'
        else:
            st.session_state.agg_sort_col = col
            st.session_state.agg_sort_dir = 'desc'

    # Apply sorting
    agg_df = agg_df.sort_values(
        st.session_state.agg_sort_col, 
        ascending=(st.session_state.agg_sort_dir == 'asc')
    )

    # --- UNIFIED HOLDINGS TABLE ---
    st.header("📇 Unified Holdings Breakdown")
    
    # Header styling
    st.markdown("""
    <style>
        .stButton>button {
            width: 100% !important;
            border: none !important;
            background-color: transparent !important;
            color: #2b3674 !important;
            font-weight: 600 !important;
            text-align: left !important;
            padding: 0px !important;
            min-height: 18px !important;
            line-height: 1.1 !important;
            font-size: 0.75rem !important;
        }
        /* Row text is now globally styled for mode overriding */
        .account-count {
            font-size: 0.65rem;
            color: #6c757d;
            vertical-align: super;
            margin-left: 2px;
        }
        hr {
            margin: 0px !important;
            padding: 0px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Row (9 Columns)
    # Proportions: Ticker:1.2, Qty:0.8, Inv:1, Val:1, Avg:1, Curr:1, GainAmt:1, GainPct:1, Acc:0.6
    h_cols = st.columns([1.2, 0.8, 1, 1, 1, 1, 1, 1, 0.6])
    
    headers = [
        ("Ticker", "ticker"), ("Qty", "quantity"), ("Invested", "total_cost"), 
        ("Value", "total_value"), ("Avg Buy", "weighted_avg_price"), 
        ("Curr Price", "current_price"), ("Gain Amt", "net_gain"), ("Gain %", "net_gain_pct"),
        ("Acc", "accounts_count")
    ]
    
    for i, (label, key) in enumerate(headers):
        sort_icon = ""
        if st.session_state.agg_sort_col == key:
            sort_icon = " ↑" if st.session_state.agg_sort_dir == 'asc' else " ↓"
        if h_cols[i].button(f"{label}{sort_icon}", key=f"h_{key}"):
            toggle_sort(key)
            st.rerun()

    st.markdown("<hr style='margin: 0px; border-top: 2px solid #2b3674;'>", unsafe_allow_html=True)

    # Data Rows
    for _, stock in agg_df.iterrows():
        ticker = stock['ticker']
        qty = stock['quantity']
        inv = stock['total_cost']
        val = stock['total_value']
        avg_buy = stock['weighted_avg_price']
        curr_price = stock['current_price']
        gain_amt = stock['net_gain']
        gain_p = stock['net_gain_pct']
        acc_count = stock['accounts_count']
        
        invested_disp = inv * fx_rate
        val_disp = val * fx_rate
        avg_buy_disp = avg_buy * fx_rate
        curr_price_disp = curr_price * fx_rate
        gain_amt_disp = gain_amt * fx_rate

        # Format metrics
        color = "#02b84b" if gain_p >= 0 else "#d93025"
        gain_str = f"{gain_p:+.2f}%"
        gain_amt_str = f"{sym}{gain_amt_disp:,.2f}"

        # Row Layout (9 Columns)
        r_cols = st.columns([1.2, 0.8, 1, 1, 1, 1, 1, 1, 0.6])
        
        # Clickable Ticker for Expansion
        is_expanded = ticker in st.session_state.expanded_tickers
        arrow = "▼" if is_expanded else "▶"
        
        if r_cols[0].button(f"{arrow} {ticker}", key=f"btn_{ticker}"):
            if is_expanded:
                st.session_state.expanded_tickers.remove(ticker)
            else:
                st.session_state.expanded_tickers.add(ticker)
            st.rerun()
            
        r_cols[1].markdown(f"<p class='row-text'>{qty:,.2f}</p>", unsafe_allow_html=True)
        r_cols[2].markdown(f"<p class='row-text'>{sym}{invested_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[3].markdown(f"<p class='row-text'>{sym}{val_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[4].markdown(f"<p class='row-text'>{sym}{avg_buy_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[5].markdown(f"<p class='row-text'>{sym}{curr_price_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[6].markdown(f"<p class='row-text' style='color:{color};'>{sym}{gain_amt_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[7].markdown(f"<p class='row-text' style='color:{color}; font-weight:bold;'>{gain_str}</p>", unsafe_allow_html=True)
        r_cols[8].markdown(f"<p class='row-text' style='text-align: center;'>{acc_count}</p>", unsafe_allow_html=True)
        
        # Show Expansion
        if is_expanded:
            with st.container():
                st.markdown(f"<div style='padding-left: 20px; font-size: 0.8rem;'>**Detailed breakdown for {ticker}**</div>", unsafe_allow_html=True)
                ticker_df = df[df['ticker'] == ticker][['account_name', 'platform', 'quantity', 'avg_price', 'current_price', 'total_invested', 'total_value', 'gain_loss']].copy()
                
                # Apply fx rate to expansion table
                ticker_df['avg_price'] *= fx_rate
                ticker_df['current_price'] *= fx_rate
                ticker_df['total_invested'] *= fx_rate
                ticker_df['total_value'] *= fx_rate
                ticker_df['gain_loss'] *= fx_rate
                
                # Use account_name and platform for clarity
                ticker_df['gain_loss_pct'] = (ticker_df['gain_loss'] / ticker_df['total_invested']) * 100
                st.dataframe(
                    ticker_df.style.format({
                        'avg_price': sym + '{:,.2f}',
                        'current_price': sym + '{:,.2f}',
                        'total_invested': sym + '{:,.2f}',
                        'total_value': sym + '{:,.2f}',
                        'gain_loss': sym + '{:,.2f}',
                        'gain_loss_pct': '{:.2f}%'
                    }).applymap(lambda x: 'color: #02b84b' if isinstance(x, (int, float)) and x > 0 else ('color: #d93025' if isinstance(x, (int, float)) and x < 0 else ''), subset=['gain_loss', 'gain_loss_pct']),
                    use_container_width=True
                )
        
        st.markdown("<hr style='margin: 0px; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

    st.divider()

# --- MAIN ---
if __name__ == "__main__":
    active_ids = sidebar()
    dashboard(active_ids)
