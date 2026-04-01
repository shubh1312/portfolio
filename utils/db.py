import sqlite3
import pandas as pd
import streamlit as st
import os

DB_NAME = os.path.join("data", "portfolio.db")

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
            asset_category TEXT DEFAULT 'US Market',
            is_active INTEGER DEFAULT 1,
            UNIQUE(platform, broker_id, name)
        )
    ''')
    
    # Check if asset_category column exists, if not, add it
    df_acc = fetch_data("PRAGMA table_info(accounts)")
    if 'asset_category' not in df_acc['name'].values:
        execute_query("ALTER TABLE accounts ADD COLUMN asset_category TEXT DEFAULT 'US Market'")

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
            currency TEXT DEFAULT 'USD',
            last_updated DATETIME,
            FOREIGN KEY(account_id) REFERENCES accounts(id),
            UNIQUE(account_id, ticker)
        )
    ''')
    
    # Check if currency column exists, if not, add it
    df_holdings = fetch_data("PRAGMA table_info(holdings)")
    if 'currency' not in df_holdings['name'].values:
        execute_query("ALTER TABLE holdings ADD COLUMN currency TEXT DEFAULT 'USD'")
