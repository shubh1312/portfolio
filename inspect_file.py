import pandas as pd
import sys

file_path = "/Users/shubham/projects/portfolio/files/IND-HOLDINGS_REPORTXX221052937-2026-03-11-V04.xls"

try:
    # 1. Check if we can find the header row
    full_df = pd.read_excel(file_path, header=None)
    header_row_idx = 0
    for i, row in full_df.iterrows():
        row_str = " ".join(map(str, row.values))
        print(f"Row {i}: {row_str}")
        if any(keyword in row_str for keyword in ['Instrument Name', 'Symbol', 'Ticker']):
            header_row_idx = i
            print(f"Found header at row {i}")
            break
    
    # 2. Read with detected header
    df = pd.read_excel(file_path, header=header_row_idx)
    print("\n--- Columns Found ---")
    print(df.columns.tolist())
    print("\n--- First 5 Rows ---")
    print(df.head())

except Exception as e:
    print(f"Error: {e}")
