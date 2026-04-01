import pandas as pd
import streamlit as st

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
    if 'ticker' in mapped_df.columns:
        # Stop processing rows if "disclaimer" is found in the ticker column
        disclaimer_mask = mapped_df['ticker'].astype(str).str.contains('disclaimer', case=False, na=False)
        if disclaimer_mask.any():
            stop_idx = mapped_df[disclaimer_mask].index[0]
            mapped_df = mapped_df.iloc[:stop_idx]
            
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
    # Vested XLSX with multiple sheets: ['User Details', 'Holdings']
    broker_id = filename if filename else file.name
    try:
        xls = pd.read_excel(file, sheet_name=None)
    except Exception as e:
        st.error(f"Vested Excel parsing failed: {e}")
        return pd.DataFrame(), broker_id

    # 1. Precise Extraction of Broker ID (Govt Id/PAN) from "User Details"
    if 'User Details' in xls:
        user_df = xls['User Details']
        if 'Govt Id' in user_df.columns and not user_df.empty:
            broker_id = str(user_df.iloc[0]['Govt Id'])
        elif 'User' in user_df.columns and not user_df.empty:
            # Fallback to User name if Govt Id missing
            broker_id = str(user_df.iloc[0]['User'])

    # 2. Extract Holdings
    if 'Holdings' in xls:
        df = xls['Holdings']
    else:
        # Fallback to the first non-user-details sheet found
        df = pd.DataFrame()
        for name, sheet in xls.items():
            if name != 'User Details':
                df = sheet
                break

    if df.empty:
        return pd.DataFrame(), broker_id

    # Precise Vested Column Mapping
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
        # Stop processing rows if "disclaimer" is found (mirroring INDmoney logic)
        disclaimer_mask = mapped_df['ticker'].astype(str).str.contains('disclaimer', case=False, na=False)
        if disclaimer_mask.any():
            stop_idx = mapped_df[disclaimer_mask].index[0]
            mapped_df = mapped_df.iloc[:stop_idx]

        # Calculate total_invested if missing
        if 'total_invested' not in mapped_df.columns and 'quantity' in mapped_df.columns and 'avg_price' in mapped_df.columns:
             mapped_df['total_invested'] = mapped_df['quantity'] * mapped_df['avg_price']
        
        final_df = mapped_df[['ticker', 'quantity', 'avg_price', 'current_price', 'total_invested']].copy()
        return final_df.dropna(subset=['ticker']), broker_id

    return pd.DataFrame(), broker_id
