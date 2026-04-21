"""
FastAPI Backend for Orbit Portfolio
Provides REST API endpoints for the React frontend
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, date
from typing import List, Dict, Optional
import sys
import os

# Add parent directory to path to import existing services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.portfolio_service import (
    get_all_accounts, load_filtered_holdings, get_or_create_account, 
    save_holdings, delete_account, update_account_name, update_account_status
)
from services.performance_service import (
    build_performance_data_from_transactions, 
    compute_portfolio_totals_from_transactions,
    fetch_transaction_data, fetch_cash_data
)
from services.market_data import (
    fetch_usd_inr_rate, update_prices_in_db, fetch_live_price
)
from services.crypto_service import update_crypto_live_prices
from services.mf_service import update_mf_live_prices
from utils.db import fetch_data, execute_query

# Initialize FastAPI app
app = FastAPI(
    title="Orbit Portfolio API",
    description="REST API for Orbit Portfolio Manager",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────
# PORTFOLIO ENDPOINTS
# ──────────────────────────────────────────────────────────────

@app.get("/api/portfolio/summary")
async def get_portfolio_summary(currency: str = Query("INR", regex="^(INR|USD)$")):
    """Get portfolio summary: total value, invested, gain, etc."""
    try:
        fx_rate = fetch_usd_inr_rate() or 83.0
        perf_df = build_performance_data_from_transactions(fx_rate=fx_rate, target_currency=currency)
        totals = compute_portfolio_totals_from_transactions(perf_df)
        
        return {
            "status": "success",
            "data": {
                "total_invested": totals.get("total_capital", totals.get("total_invested", 0)),
                "total_value": totals.get("total_value", 0),
                "total_gain": totals.get("total_gain", 0),
                "abs_return_pct": totals.get("abs_return_pct", totals.get("total_return_pct", 0)),
                "irr_pct": totals.get("portfolio_irr_pct", totals.get("irr_pct", None)),
                "cagr_pct": totals.get("portfolio_cagr_pct", totals.get("cagr_pct", None)),
                "portfolio_years": totals.get("portfolio_years", None),
                "last_updated": datetime.now().isoformat(),
                "currency": currency,
                "fx_rate": fx_rate
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/portfolio/assets")
async def get_asset_classes(currency: str = Query("INR", regex="^(INR|USD)$")):
    """Get breakdown by asset class"""
    try:
        fx_rate = fetch_usd_inr_rate() or 83.0
        perf_df = build_performance_data_from_transactions(fx_rate=fx_rate, target_currency=currency)
        
        assets = []
        for _, row in perf_df.iterrows():
            assets.append({
                "asset_class": row["asset_class"],
                "total_value": row["current_value"],
                "total_invested": row["total_invested"],
                "gain": row["gain"],
                "gain_pct": row["abs_return_pct"],
                "irr_pct": row["irr_pct"],
                "cagr_pct": row["segmented_cagr_pct"],
                "cash_reserves": row["cash_reserves"],
                "transaction_count": row["transaction_count"],
                "earliest_date": row["earliest_date"].isoformat() if row["earliest_date"] else None,
                "icon": row["icon"]
            })
        
        return {
            "status": "success",
            "data": assets,
            "currency": currency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────
# HOLDINGS ENDPOINTS
# ──────────────────────────────────────────────────────────────

@app.get("/api/holdings")
async def get_holdings(
    asset_class: Optional[str] = None,
    currency: str = Query("INR", regex="^(INR|USD)$")
):
    """Get all holdings, optionally filtered by asset class"""
    try:
        # Get all active accounts
        accounts = get_all_accounts()
        if accounts.empty:
            return {"status": "success", "data": [], "currency": currency}
        
        account_ids = accounts[accounts["is_active"] == 1]["id"].tolist()
        holdings = load_filtered_holdings(account_ids)

        cat_map = accounts.set_index("id")["asset_category"].to_dict()
        holdings["asset_category"] = holdings["account_id"].map(cat_map)

        if asset_class:
            holdings = holdings[holdings["asset_category"] == asset_class]
        
        fx_rate = fetch_usd_inr_rate() or 83.0
        
        # Convert to JSON-serializable format
        holdings_list = []
        for _, h in holdings.iterrows():
            # Currency conversion
            if currency == "INR" and h["currency"] == "USD":
                multiplier = fx_rate
            elif currency == "USD" and h["currency"] == "INR":
                multiplier = 1 / fx_rate
            else:
                multiplier = 1
            
            holdings_list.append({
                "id": h["id"],
                "ticker": h["ticker"],
                "asset_category": h["asset_category"],
                "quantity": h["quantity"],
                "avg_price": h["avg_price"] * multiplier,
                "current_price": h["current_price"] * multiplier,
                "currency": h["currency"],
                "total_invested": h["quantity"] * h["avg_price"] * multiplier,
                "current_value": h["quantity"] * h["current_price"] * multiplier,
                "gain": (h["current_price"] - h["avg_price"]) * h["quantity"] * multiplier,
                "gain_pct": ((h["current_price"] - h["avg_price"]) / h["avg_price"] * 100) if h["avg_price"] > 0 else 0,
                "last_updated": h["last_updated"].isoformat() if hasattr(h["last_updated"], "isoformat") else str(h["last_updated"]) if h["last_updated"] else None,
            })
        
        return {
            "status": "success",
            "data": holdings_list,
            "count": len(holdings_list),
            "currency": currency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────
# TRANSACTIONS ENDPOINTS
# ──────────────────────────────────────────────────────────────

@app.get("/api/transactions")
async def get_transactions(
    asset_class: Optional[str] = None,
    currency: str = Query("INR", regex="^(INR|USD)$")
):
    """Get transaction history"""
    try:
        txn_df = fetch_transaction_data()
        
        if asset_class:
            txn_df = txn_df[txn_df["asset_class"] == asset_class]
        
        fx_rate = fetch_usd_inr_rate() or 83.0
        
        transactions = []
        for _, row in txn_df.iterrows():
            # Currency conversion
            if currency == "INR" and row.get("currency", "INR") == "USD":
                multiplier = fx_rate
            elif currency == "USD" and row.get("currency", "INR") == "INR":
                multiplier = 1 / fx_rate
            else:
                multiplier = 1
            
            transactions.append({
                "id": row.get("id", None),
                "asset_class": row["asset_class"],
                "amount": row["amount"] * multiplier,
                "currency": row.get("currency", "INR"),
                "investment_date": row["investment_date"].isoformat() if hasattr(row["investment_date"], "isoformat") else str(row["investment_date"]),
                "notes": row.get("notes", ""),
                "type": "Withdrawal" if row["amount"] < 0 else "Investment"
            })
        
        return {
            "status": "success",
            "data": sorted(transactions, key=lambda x: x["investment_date"], reverse=True),
            "count": len(transactions),
            "currency": currency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────
# CASH RESERVES ENDPOINTS
# ──────────────────────────────────────────────────────────────

@app.get("/api/cash")
async def get_cash_reserves(currency: str = Query("INR", regex="^(INR|USD)$")):
    """Get cash reserves by asset class"""
    try:
        cash_data = fetch_cash_data()
        fx_rate = fetch_usd_inr_rate() or 83.0
        
        reserves = []
        for asset_class, (amount, cash_currency) in cash_data.items():
            # Convert currency if needed
            if currency == "INR" and cash_currency == "USD":
                converted = amount * fx_rate
            elif currency == "USD" and cash_currency == "INR":
                converted = amount / fx_rate
            else:
                converted = amount
            
            reserves.append({
                "asset_class": asset_class,
                "amount": converted,
                "native_amount": amount,
                "native_currency": cash_currency,
                "currency": currency
            })
        
        return {
            "status": "success",
            "data": reserves,
            "total": sum(r["amount"] for r in reserves),
            "currency": currency
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────
# PRICE UPDATE ENDPOINTS
# ──────────────────────────────────────────────────────────────

@app.post("/api/prices/refresh")
async def refresh_prices(
    category: str = Query("US Market", regex="^(US Market|Indian Stock Market|Mutual Funds|Crypto)$"),
    finnhub_key: Optional[str] = None,
    av_key: Optional[str] = None
):
    """Trigger price update for given category"""
    try:
        # Get keys from environment if not provided
        if not finnhub_key:
            finnhub_key = os.getenv("FINNHUB_API_KEY", "")
        if not av_key:
            av_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
        
        update_prices_in_db(finnhub_key, av_key, category=category)
        
        return {
            "status": "success",
            "message": f"Updated prices for {category}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────
# ACCOUNTS ENDPOINTS
# ──────────────────────────────────────────────────────────────

@app.get("/api/accounts")
async def get_accounts():
    """Get all accounts"""
    try:
        accounts = get_all_accounts()
        accounts_list = accounts[accounts["is_active"] == 1].to_dict("records")
        
        return {
            "status": "success",
            "data": accounts_list,
            "count": len(accounts_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────
# HEALTH CHECK
# ──────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
