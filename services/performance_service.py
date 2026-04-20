import pandas as pd
import numpy as np
import streamlit as st
from datetime import date, datetime
from typing import Optional, Dict, List, Tuple
from utils.db import fetch_data
from scipy.optimize import newton
import warnings

warnings.filterwarnings("ignore")

# ── Google Sheet config ────────────────────────────────────────────────────────
SHEET_ID = "1z_22sy-HriW9LvBQLQ7TEsdhASHV_f0AdwbawXfC5l0"
CASH_GID = "1981161998"
CASH_GSHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
    f"/export?format=csv&gid={CASH_GID}"
)

# Canonical asset class names (must match accounts.asset_category in DB)
ASSET_CLASSES = [
    "US Market",
    "Indian Stock Market",
    "Indian Mutual Funds",
    "Crypto",
    "Lending",
]

ASSET_ICONS = {
    "US Market": "🇺🇸",
    "Indian Stock Market": "📈",
    "Indian Mutual Funds": "🏦",
    "Crypto": "₿",
    "Lending": "🤝",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean_number(val) -> float:
    if isinstance(val, str):
        val = val.replace("₹", "").replace(",", "").replace(" ", "").strip()
        try:
            return float(val)
        except ValueError:
            return 0.0
    return float(val) if pd.notnull(val) else 0.0


def _parse_date(val) -> Optional[date]:
    if pd.isnull(val) or str(val).strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(val).strip(), fmt).date()
        except ValueError:
            continue
    return None


def _years_since(d: date) -> float:
    return (date.today() - d).days / 365.25


def _days_since(d: date) -> float:
    return (date.today() - d).days


def _cagr(current: float, invested: float, years: float) -> Optional[float]:
    """Returns CAGR as a decimal (0.12 = 12%). Returns None if data is invalid."""
    if years <= 0 or invested <= 0 or current <= 0:
        return None
    return (current / invested) ** (1 / years) - 1


def _abs_return(current: float, invested: float) -> Optional[float]:
    if invested <= 0:
        return None
    return (current - invested) / invested * 100


def _convert_currency(amount: float, from_currency: str, to_currency: str, fx_rate: float = 83.0) -> float:
    """
    Convert amount from one currency to another.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency (USD, INR, EUR, etc)
        to_currency: Target currency (USD, INR, EUR, etc)
        fx_rate: Exchange rate (USD to INR, default 83.0)
    
    Returns:
        Converted amount
    """
    # Normalize currency codes
    from_curr = str(from_currency).strip().upper() if from_currency else "INR"
    to_curr = str(to_currency).strip().upper() if to_currency else "INR"
    
    if from_curr == to_curr:
        return amount
    
    # Only support USD-INR conversion for now
    if from_curr == "USD" and to_curr == "INR":
        return amount * fx_rate
    elif from_curr == "INR" and to_curr == "USD":
        return amount / fx_rate
    else:
        # Unsupported currency pair, return as-is
        return amount


def _calculate_irr(cash_flows: List[Tuple[date, float]], current_value: float) -> Optional[float]:
    """
    Calculates Money-Weighted Return (Internal Rate of Return / IRR).
    
    Args:
        cash_flows: List of (date, amount) tuples. Positive = investment, Negative = withdrawal
        current_value: Final portfolio value in INR (today)
    
    Returns:
        IRR as decimal (0.12 = 12%), or None if calculation fails
        
    Example:
        cash_flows = [
            (date(2021, 3, 15), 300000),   # Initial investment
            (date(2024, 1, 15), 50000),    # Additional investment
            (date(2025, 6, 20), -20000),   # Withdrawal
        ]
        irr = _calculate_irr(cash_flows, 550000)  # Current portfolio value
    """
    if not cash_flows or current_value <= 0:
        return None
    
    # Sort by date
    cash_flows = sorted(cash_flows, key=lambda x: x[0])
    
    # Build NPV function: compound all cash flows forward to today at rate r
    def npv(rate):
        pv = 0
        for flow_date, amount in cash_flows:
            days = _days_since(flow_date)
            years = days / 365.25
            # Compound past investments forward at rate r
            # Past outflows (investments) compound to today
            pv += amount * ((1 + rate) ** years)
        
        # Subtract current value (what we have today)
        pv -= current_value
        return pv
    
    try:
        # Use Newton-Raphson to find IRR (rate where NPV = 0)
        # Start with initial guess of 0.1 (10%)
        irr = newton(npv, 0.1, maxiter=100)
        
        # Sanity check: IRR should be reasonable
        if -1 < irr < 10:  # Between -100% and 1000%
            return irr
        return None
    except:
        # Newton-Raphson failed
        return None


def _calculate_segmented_cagr(cash_flows: List[Tuple[date, float]], current_value: float) -> Optional[float]:
    """
    Returns simple CAGR from oldest investment to today.
    Allocates current value proportionally to each cash flow for blended return.
    """
    if not cash_flows or current_value <= 0:
        return None
    
    total_invested = sum(cf[1] for cf in cash_flows if cf[1] > 0)
    if total_invested <= 0:
        return None
    
    # Find earliest date
    earliest_date = min(cf[0] for cf in cash_flows)
    years = _years_since(earliest_date)
    
    if years <= 0:
        return None
    
    return _cagr(current_value, total_invested, years)


# ── Transaction-based helpers ──────────────────────────────────────────────────

def fetch_transaction_data() -> pd.DataFrame:
    """
    Fetches transaction data from Google Sheet (Transactions tab).
    Uses gsheet_service if available, falls back to CSV export.
    
    Returns DataFrame with columns:
    - asset_class
    - amount (positive = investment, negative = withdrawal)
    - investment_date
    - currency (USD, INR, etc - defaults to INR)
    - notes
    """
    try:
        from services.gsheet_service import fetch_transactions_sheet_data
        return fetch_transactions_sheet_data()
    except Exception as e:
        st.warning(f"Could not load from gsheet service: {e}. Ensure 'Transactions' sheet exists.")
        return pd.DataFrame()


def fetch_cash_data() -> Dict[str, Tuple[float, str]]:
    """
    Fetches cash reserves from Cash sheet (gid=1981161998).
    
    Returns Dict: { asset_class: (cash_amount, currency) }
    Expected columns: asset_class, amount (or cash), currency
    Currency defaults to INR if not specified
    """
    try:
        df = pd.read_csv(CASH_GSHEET_URL)
        if df.empty:
            return {}
        
        # Normalize column names
        df.columns = [c.strip().lower() for c in df.columns]
        
        # Handle both "cash" and "amount" columns
        cash_col = None
        for col in df.columns:
            if "cash" in col or "amount" in col:
                cash_col = col
                break
        
        if cash_col is None:
            st.warning("Cash sheet: Could not find 'cash' or 'amount' column")
            return {}
        
        # Clean and build dictionary
        result = {}
        for _, row in df.iterrows():
            asset = str(row.get("asset_class", "")).strip()
            cash = _clean_number(row.get(cash_col, 0))
            currency = str(row.get("currency", "INR")).strip().upper()
            
            if asset and cash > 0:
                result[asset] = (cash, currency)
        
        return result
    
    except Exception as e:
        st.warning(f"Could not load Cash sheet: {e}")
        return {}


def _parse_transactions_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans transaction DataFrame.
    Defaults currency to INR if not provided.
    """
    if df.empty:
        return df
    
    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    required = {"asset_class", "amount", "investment_date"}
    missing = required - set(df.columns)
    if missing:
        st.error(f"Transactions sheet missing columns: {missing}")
        return pd.DataFrame()
    
    # Clean data
    df["amount"] = df["amount"].apply(_clean_number)
    df["investment_date"] = df["investment_date"].apply(_parse_date)
    df["notes"] = df.get("notes", "").fillna("")
    df["asset_class"] = df["asset_class"].str.strip()
    
    # Handle currency column (default to INR if missing)
    if "currency" not in df.columns:
        df["currency"] = "INR"
    else:
        df["currency"] = df["currency"].fillna("INR").str.upper()
    
    # Remove rows with invalid data
    df = df.dropna(subset=["asset_class", "amount", "investment_date"])
    
    return df.reset_index(drop=True)


def get_asset_class_transactions(asset_class: str, transactions_df: pd.DataFrame, target_currency: str = "INR", fx_rate: float = 83.0) -> List[Tuple[date, float]]:
    """
    Returns list of (date, amount) tuples for a specific asset class.
    Converts all amounts to target_currency.
    Filtered and sorted by date.
    
    Args:
        asset_class: Asset class to filter by
        transactions_df: Transaction DataFrame
        target_currency: Target currency for conversion (INR, USD, etc)
        fx_rate: Exchange rate for USD-INR conversion
    """
    filtered = transactions_df[transactions_df["asset_class"] == asset_class].copy()
    if filtered.empty:
        return []
    
    filtered = filtered.sort_values("investment_date")
    
    # Convert amounts to target currency
    result = []
    for _, row in filtered.iterrows():
        amount = row["amount"]
        currency = row.get("currency", "INR")
        converted = _convert_currency(amount, currency, target_currency, fx_rate)
        result.append((row["investment_date"], converted))
    
    return result


# ── DB helpers ────────────────────────────────────────────────────────────────

def _get_current_values_from_db(fx_rate: float = 83.0) -> Dict[str, float]:
    """
    Returns a dict { asset_class: current_value_in_INR }.
    US Market holdings are converted using fx_rate (USD → INR).
    """
    query = """
        SELECT
            a.asset_category,
            h.quantity,
            h.current_price,
            h.currency
        FROM holdings h
        JOIN accounts a ON h.account_id = a.id
        WHERE a.is_active = 1
          AND h.quantity > 0
          AND h.current_price > 0
    """
    df = fetch_data(query)
    if df.empty:
        return {}

    df["value"] = df["quantity"] * df["current_price"]
    # Convert USD → INR
    df["value_inr"] = df.apply(
        lambda r: r["value"] * fx_rate if r["currency"] == "USD" else r["value"],
        axis=1,
    )

    result = (
        df.groupby("asset_category")["value_inr"]
        .sum()
        .to_dict()
    )
    return result


# ── Transaction-based Performance (Money-Weighted Return) ─────────────────────

def build_performance_data_from_transactions(fx_rate: float = 83.0, target_currency: str = "INR") -> pd.DataFrame:
    """
    NEW: Builds performance data from transaction-level records.
    Uses Money-Weighted Return (IRR) for accuracy.
    
    Fetches cash from separate Cash sheet and adds to current_value.
    Converts all amounts to target_currency.
    
    Args:
        fx_rate: Exchange rate for USD-INR conversion
        target_currency: Target currency for all calculations (INR, USD, etc)
    
    Returns DataFrame with one row per asset class:
    - asset_class
    - transactions (list of tuples, converted to target_currency)
    - total_invested (sum of positive amounts, converted to target_currency)
    - net_movements (includes withdrawals)
    - earliest_date
    - transaction_count
    - cash_reserves (converted to target_currency)
    - current_value (live_data + cash_reserves, in target_currency)
    - gain (current_value - total_invested)
    - abs_return_pct
    - irr_pct (Money-Weighted Return)
    - segmented_cagr_pct
    - has_live_data
    - has_cash (cash_reserves > 0)
    - icon
    """
    transactions_df = fetch_transaction_data()
    if transactions_df.empty:
        return pd.DataFrame()
    
    transactions_df = _parse_transactions_dataframe(transactions_df)
    if transactions_df.empty:
        return pd.DataFrame()
    
    # Fetch cash reserves from separate Cash sheet
    cash_by_asset = fetch_cash_data()
    
    live_values = _get_current_values_from_db(fx_rate)
    
    rows = []
    for asset_class in transactions_df["asset_class"].unique():
        # Get transactions converted to target currency
        txns = get_asset_class_transactions(asset_class, transactions_df, target_currency, fx_rate)
        if not txns:
            continue
        
        # Calculate metrics from transactions only
        total_invested = sum(amt for _, amt in txns if amt > 0)
        net_movements = sum(amt for _, amt in txns)
        earliest_date = min(d for d, _ in txns)
        txn_count = len(txns)
        
        # Get live data and cash reserves (with currency conversion)
        current_value = live_values.get(asset_class, None)
        cash_amount, cash_currency = cash_by_asset.get(asset_class, (0, "INR"))
        cash_reserves = _convert_currency(cash_amount, cash_currency, target_currency, fx_rate)
        
        has_live_data = current_value is not None
        display_value = current_value if has_live_data else net_movements
        
        # Convert display_value to target currency if needed (it's from DB in INR)
        if target_currency != "INR" and display_value > 0:
            display_value = _convert_currency(display_value, "INR", target_currency, fx_rate)
        
        # Add cash reserves to current value (but NOT to total_invested)
        total_with_cash = display_value + cash_reserves
        
        # Calculate returns from total (invested + current returns + cash)
        gain = (total_with_cash - total_invested) if total_invested > 0 else cash_reserves
        abs_ret = _abs_return(total_with_cash, total_invested) if total_invested > 0 else None
        
        years = _years_since(earliest_date)
        
        # Calculate IRR (Money-Weighted Return) using total_with_cash
        irr = None
        if total_invested > 0:
            irr = _calculate_irr(txns, total_with_cash)
        
        # Calculate segmented CAGR (simple CAGR from earliest to today)
        seg_cagr = None
        if total_invested > 0:
            seg_cagr = _calculate_segmented_cagr(txns, total_with_cash)
        
        rows.append({
            "asset_class": asset_class,
            "transactions": txns,
            "total_invested": total_invested,
            "net_movements": net_movements,
            "earliest_date": earliest_date,
            "transaction_count": txn_count,
            "cash_reserves": cash_reserves,
            "current_value": total_with_cash,  # Includes cash
            "gain": gain,
            "abs_return_pct": abs_ret,
            "years": years,
            "irr_pct": (irr * 100) if irr is not None else None,
            "segmented_cagr_pct": (seg_cagr * 100) if seg_cagr is not None else None,
            "has_live_data": has_live_data,
            "has_cash": cash_reserves > 0,
            "icon": ASSET_ICONS.get(asset_class, "📦"),
        })
    
    if not rows:
        return pd.DataFrame()
    
    return pd.DataFrame(rows)


def compute_portfolio_totals_from_transactions(df: pd.DataFrame) -> dict:
    """
    Computes portfolio-level metrics using transaction-based data.
    """
    total_capital = df["total_invested"].sum()
    total_value = df["current_value"].sum()
    total_gain = total_value - total_capital
    total_abs_ret = _abs_return(total_value, total_capital)
    
    # Portfolio IRR (Money-Weighted)
    all_transactions = []
    for _, row in df.iterrows():
        all_transactions.extend(row["transactions"])
    
    portfolio_irr = None
    portfolio_cagr = None
    portfolio_years = None
    
    if all_transactions:
        earliest = min(d for d, _ in all_transactions)
        portfolio_years = _years_since(earliest)
        
        if total_value > 0:
            portfolio_irr = _calculate_irr(all_transactions, total_value)
            portfolio_cagr = _calculate_segmented_cagr(all_transactions, total_value)
    
    return {
        "total_capital": total_capital,
        "total_value": total_value,
        "total_gain": total_gain,
        "abs_return_pct": total_abs_ret,
        "portfolio_irr_pct": (portfolio_irr * 100) if portfolio_irr is not None else None,
        "portfolio_cagr_pct": (portfolio_cagr * 100) if portfolio_cagr is not None else None,
        "portfolio_years": portfolio_years,
    }
