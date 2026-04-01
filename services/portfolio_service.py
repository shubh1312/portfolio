import sqlite3
import pandas as pd
from datetime import datetime
from utils.db import execute_query, DB_NAME

def get_or_create_account(platform, broker_id, default_name, asset_category='US Market'):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Check by broker_id and platform
    c.execute('SELECT id, name FROM accounts WHERE platform = ? AND broker_id = ?', (platform, broker_id))
    row = c.fetchone()
    if row:
        acc_id = row[0]
        # Optionally update category
        c.execute('UPDATE accounts SET asset_category = ? WHERE id = ?', (asset_category, acc_id))
    else:
        # Create new
        c.execute('INSERT INTO accounts (platform, name, broker_id, asset_category) VALUES (?, ?, ?, ?)', (platform, default_name, broker_id, asset_category))
        acc_id = c.lastrowid
    conn.commit()
    conn.close()
    return acc_id

def update_account_name(acc_id, new_name):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('UPDATE accounts SET name = ? WHERE id = ?', (new_name, acc_id))
    conn.commit()
    conn.close()

def delete_account(acc_id):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('DELETE FROM holdings WHERE account_id = ?', (acc_id,))
    conn.execute('DELETE FROM accounts WHERE id = ?', (acc_id,))
    conn.commit()
    conn.close()

def save_holdings(df, account_id, currency='USD'):
    conn = sqlite3.connect(DB_NAME)
    # Clear old holdings for this account to avoid ghost entries
    conn.execute('DELETE FROM holdings WHERE account_id = ?', (account_id,))
    for _, row in df.iterrows():
        conn.execute('''
            INSERT INTO holdings (account_id, ticker, quantity, avg_price, current_price, total_invested, currency, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (account_id, row['ticker'], row['quantity'], row['avg_price'], row['current_price'], row['total_invested'], currency, datetime.now()))
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

def get_all_accounts(category=None):
    conn = sqlite3.connect(DB_NAME)
    if category:
        df = pd.read_sql_query("SELECT * FROM accounts WHERE asset_category = ?", conn, params=(category,))
    else:
        df = pd.read_sql_query("SELECT * FROM accounts", conn)
    conn.close()
    return df

def update_account_status(acc_id, is_active):
    conn = sqlite3.connect(DB_NAME)
    conn.execute('UPDATE accounts SET is_active = ? WHERE id = ?', (int(is_active), acc_id))
    conn.commit()
    conn.close()
