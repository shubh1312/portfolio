import pandas as pd
import sys

file_path = "/Users/shubham/projects/portfolio/files/Vested_Holdings.xlsx"

try:
    # Vested files can have headers at the top or sub-headings
    df = pd.read_excel(file_path)
    print("\n--- Columns Found ---")
    print(df.columns.tolist())
    print("\n--- First 5 Rows ---")
    print(df.head())
    
    # Check if there's any hidden metadata
    full_df = pd.read_excel(file_path, header=None)
    print("\n--- Raw First 10 Rows ---")
    for i, row in full_df.head(10).iterrows():
        print(f"Row {i}: {' '.join(map(str, row.values))}")

except Exception as e:
    print(f"Error: {e}")
