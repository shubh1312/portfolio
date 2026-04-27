import sqlite3
import pandas as pd
import sys
import os

# Add project root to path
sys.path.append('/Users/shubham/projects/portfolio')

from services.performance_service import build_performance_data_from_transactions

def check_lending_math():
    try:
        data = build_performance_data_from_transactions()
        lending = data[data['asset_class'] == 'Lending']
        
        if lending.empty:
            print("No Lending data found.")
            return
            
        row = lending.iloc[0]
        print(f"Asset Class: Lending")
        print(f"Invested (Life-time): {row['total_invested']:,.2f}")
        print(f"Current Value (inc. Cash): {row['current_value']:,.2f}")
        print(f"Cash Reserves: {row.get('cash_reserves', 0):,.2f}")
        print(f"Realised Profit: {row['realised_profit']:,.2f}")
        print(f"Unrealised Gain: {row['unrealised_gain']:,.2f}")
        print(f"Total Gain: {row['gain']:,.2f}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_lending_math()
