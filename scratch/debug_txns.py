import pandas as pd
import sys

def debug_txns():
    url = "https://docs.google.com/spreadsheets/d/1z_22sy-HriW9LvBQLQ7TEsdhASHV_f0AdwbawXfC5l0/export?format=csv&gid=2098678572"
    df = pd.read_csv(url)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    lending = df[df['asset_class'] == 'Lending']
    pos = lending[lending['amount'] > 0]['amount'].sum()
    neg = lending[lending['amount'] < 0]['amount'].sum()
    
    print(f"Total Positive (Invested): {pos}")
    print(f"Total Negative (Withdrawn): {neg}")
    print(f"Lending Rows:")
    print(lending)

if __name__ == "__main__":
    debug_txns()
