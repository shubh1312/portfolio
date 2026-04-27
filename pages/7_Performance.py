"""
Enhanced Performance Tracker v2 - Transaction-based with Money-Weighted Returns
Tracks capital invested vs current value with accurate IRR calculations
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, datetime, timedelta

from utils.theme import apply_custom_styles, THEME, RING_COLORS, _plotly_layout
from utils.db import init_db
from services.market_data import fetch_usd_inr_rate
from services.performance_service import (
    build_performance_data_from_transactions,
    compute_portfolio_totals_from_transactions,
    fetch_transaction_data,
    _parse_transactions_dataframe,
    ASSET_CLASSES,
)
from services.gsheet_service import (
    add_transaction,
    fetch_transactions_sheet_data,
)

# ── Page Config ────────────────────────────────────────────────────────────────
apply_custom_styles()
init_db()

# All badge/card styles are provided by apply_custom_styles() in theme.py

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-header'>Display</div>", unsafe_allow_html=True)
    use_inr = st.toggle("Show in INR (₹)", value=True)
    st.session_state.display_currency = "INR" if use_inr else "USD"
    target_currency = "INR" if use_inr else "USD"
    sym = "₹" if use_inr else "$"

    fx_rate = fetch_usd_inr_rate() or 83.0
    st.caption(f"USD/INR: ₹{fx_rate:,.2f}")

    st.markdown("<div class='sidebar-header'>Actions</div>", unsafe_allow_html=True)
    if st.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    with st.expander("Sheet format reference"):
        st.markdown("""
        **Transactions** tab:
        - `asset_class`, `amount` (±), `investment_date`, `currency`, `notes`

        **Cash** tab:
        - `asset_class`, `amount`, `currency`
        """)


# ── Helper Functions ──────────────────────────────────────────────────────────

def format_amount(value: float, sym: str = "₹") -> str:
    """Format currency value"""
    if value is None:
        return "—"
    return f"{sym}{value:,.0f}"


def format_pct(value: float, decimals: int = 2) -> str:
    """Format percentage"""
    if value is None:
        return "—"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def render_asset_card(row, sym: str):
    """Render an asset class card with transactions"""
    asset_class = row["asset_class"]
    icon = row["icon"]
    total_invested = row["total_invested"]
    current_value = row["current_value"]
    cash_reserves = row.get("cash_reserves", 0)
    realised_profit = row.get("realised_profit", 0)
    unrealised_gain = row.get("unrealised_gain", 0)
    gain = row["gain"]
    abs_ret = row["abs_return_pct"]
    irr = row["irr_pct"]
    cagr = row["segmented_cagr_pct"]
    txn_count = row["transaction_count"]
    txns = row["transactions"]
    has_live = row["has_live_data"]
    has_cash = row.get("has_cash", False)
    
    # Calculate effective return %
    irr_pct = irr if irr is not None else cagr
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown(f"""
        <div class='perf-metric-card'>
        <div class='metric-label'>📈 Invested</div>
        <div class='metric-value'>{format_amount(total_invested, sym)}</div>
        <div class='metric-sub'>{txn_count} txns</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='perf-metric-card'>
        <div class='metric-label'>💰 Current</div>
        <div class='metric-value'>{format_amount(current_value, sym)}</div>
        <div class='metric-sub'>{"Live" if has_live else "Manual"}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        rp_color = "#A78BFA" if realised_profit > 0 else "#8b949e"
        st.markdown(f"""
        <div class='perf-metric-card'>
        <div class='metric-label'>🏦 Realised</div>
        <div class='metric-value' style='color:{rp_color};'>{format_amount(realised_profit, sym) if realised_profit != 0 else "—"}</div>
        <div class='metric-sub'>Profit taken</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        up_color = "#16A34A" if unrealised_gain >= 0 else "#DC2626"
        st.markdown(f"""
        <div class='perf-metric-card'>
        <div class='metric-label'>💎 Unrealised</div>
        <div class='metric-value' style='color:{up_color};'>{format_amount(unrealised_gain, sym) if unrealised_gain != 0 else "—"}</div>
        <div class='metric-sub'>Paper gain</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        color = "#16A34A" if gain >= 0 else "#DC2626"
        st.markdown(f"""
        <div class='perf-metric-card'>
        <div class='metric-label'>✨ Total Gain</div>
        <div class='metric-value' style='color:{color};'>{format_amount(gain, sym)}</div>
        <div class='metric-sub'>{format_pct(abs_ret)}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown(f"""
        <div class='perf-metric-card'>
        <div class='metric-label'>🎯 IRR</div>
        <div class='metric-value'>{format_pct(irr_pct) if irr_pct else "—"}</div>
        <div class='metric-sub'><span class='irr-label'>{'MWR' if irr is not None else 'CAGR'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Cash reserves ticker
    if has_cash:
        st.markdown("---")
        st.markdown(f"**💵 Cash Reserves: {format_amount(cash_reserves, sym)}**")
        st.caption("Available for future investment")
    
    # Transaction history
    with st.expander(f"📋 View {txn_count} Transactions", expanded=False):
        st.markdown("**Recent Investments & Withdrawals:**")
        
        for i, (txn_date, amount) in enumerate(sorted(txns, key=lambda x: x[0], reverse=True)):
            sign_str = "+" if amount > 0 else ""
            color_class = "#16A34A" if amount > 0 else "#DC2626"
            
            col_date, col_amt = st.columns([2, 2])
            with col_date:
                st.caption(f"📅 {txn_date.strftime('%d %b %Y')}")
            with col_amt:
                st.markdown(f"<span style='color:{color_class};font-weight:700;'>{sign_str}{format_amount(amount, sym)}</span>", 
                           unsafe_allow_html=True)


# ── Page Header ────────────────────────────────────────────────────────────────
st.markdown("# Performance")
st.markdown("**Track capital invested vs current value with accurate Money-Weighted Returns (IRR)**")
st.divider()

# ── Load Data ──────────────────────────────────────────────────────────────────
with st.spinner("📊 Loading performance data..."):
    perf_df = build_performance_data_from_transactions(fx_rate=fx_rate, target_currency=target_currency)
    if not perf_df.empty:
        totals = compute_portfolio_totals_from_transactions(perf_df)
    else:
        totals = None

if perf_df.empty:
    st.warning("""
    ⚠️ **No transaction data found.**
    
    **Setup Instructions:**
    
    1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1z_22sy-HriW9LvBQLQ7TEsdhASHV_f0AdwbawXfC5l0/
    
    2. Create/verify a **"Transactions"** tab with columns:
    ```
    asset_class    |  amount  |  investment_date  |  notes
    Crypto         |  300000  |  2021-03-15       |  BTC + ETH
    US Market      |  500000  |  2026-04-20       |  New investment
    Indian Stock   |  -10000  |  2026-04-20       |  Profit booking
    ```
    
    3. Click **🔄 Refresh Data** in the sidebar to load.
    
    Or use the **➕ Add Transaction** button below to add data manually.
    """)

else:
    # Display units
    sym = "₹" if use_inr else "$"
    
    def to_display(val: float) -> float:
        # Values are already in target_currency from build_performance_data_from_transactions
        return val
    
    # ── SECTION 1: Portfolio Summary ──────────────────────────────────────────
    st.markdown("### 📊 Portfolio Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    t_cap = to_display(totals["total_capital"])
    t_val = to_display(totals["total_value"])
    t_realised = to_display(totals["total_realised"])
    t_gain = to_display(totals["total_gain"])
    t_ret = totals["abs_return_pct"]
    t_irr = totals["portfolio_irr_pct"]
    t_cagr = totals["portfolio_cagr_pct"]
    t_yrs = totals["portfolio_years"]
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("💰 Total Invested", format_amount(t_cap, sym))
    
    with col2:
        st.metric("📈 Current Value", format_amount(t_val, sym))
    
    with col3:
        rp_label = format_amount(t_realised, sym) if t_realised > 0 else "—"
        st.metric("🏦 Realised Profit", rp_label)
    
    with col4:
        st.metric("✨ Unrealised Gain", format_amount(t_gain, sym), delta=format_pct(t_ret))
    
    with col5:
        st.metric("🎯 Portfolio IRR", format_pct(t_irr) if t_irr else "—")
    
    with col6:
        st.metric("📊 Years Invested", f"{t_yrs:.1f}" if t_yrs else "—")
    
    if t_irr is not None:
        st.info(f"""
        **Portfolio Money-Weighted Return (IRR):** {format_pct(t_irr)}  
        This accounts for the **timing and amount** of each cash flow.
        """)
    
    st.divider()
    
    # ── SECTION 2: Asset Class Breakdown ──────────────────────────────────────
    st.markdown("### 🗂️ Asset Class Performance")
    
    # Sort by invested capital descending
    perf_sorted = perf_df.sort_values("total_invested", ascending=False)
    
    for _, row in perf_sorted.iterrows():
        with st.container(border=True):
            st.markdown(f"#### {row['icon']} {row['asset_class']}")
            render_asset_card(row, sym)
    
    st.divider()
    
    # ── SECTION 3: Charts ─────────────────────────────────────────────────────
    st.markdown("### 📈 Visualizations")
    
    chart_col1, chart_col2 = st.columns(2)
    
    # Chart 1: Allocation by capital — thin ring donut
    with chart_col1:
        labels = perf_df['asset_class'].tolist()
        amounts = perf_df['total_invested'].tolist()
        n = len(labels)
        colors = (RING_COLORS * (n // len(RING_COLORS) + 1))[:n]
        total_inv = sum(amounts)

        fig_alloc = go.Figure(go.Pie(
            labels=labels,
            values=amounts,
            hole=0.86,
            marker=dict(
                colors=colors,
                line=dict(color="#0d1117", width=2),
            ),
            textposition="outside",
            textinfo="percent+label",
            textfont=dict(size=11, color="#c9d1d9", family="Inter, sans-serif"),
            hovertemplate="<b>%{label}</b><br>%{percent}<br>" + sym + "%{value:,.0f}<extra></extra>",
        ))
        fig_alloc.update_layout(
            **_plotly_layout(
                showlegend=False,
                title=dict(text="Capital Allocation", font=dict(color="#8b949e", size=12), x=0),
                margin=dict(t=40, b=70, l=70, r=70),
                annotations=[dict(
                    text=f"<b>{format_amount(total_inv, sym)}</b><br>invested",
                    x=0.5, y=0.5, showarrow=False, align="center",
                    font=dict(size=14, color="#e6edf3", family="JetBrains Mono, monospace"),
                )],
            )
        )
        st.plotly_chart(fig_alloc, use_container_width=True)
    
    # Chart 2: Returns by asset class
    with chart_col2:
        returns_data = perf_df[['asset_class', 'irr_pct']].copy()
        returns_data['irr_pct'] = returns_data['irr_pct'].fillna(0)
        returns_data.columns = ['Asset Class', 'IRR (%)']
        
        fig_ret = px.bar(
            returns_data,
            x='Asset Class',
            y='IRR (%)',
            title='Money-Weighted Returns (IRR) by Asset',
            color=returns_data['IRR (%)'],
            color_continuous_scale=['#DC2626', '#FFFFFF', '#16A34A'],
            labels={'IRR (%)': 'IRR (%)'},
        )
        fig_ret.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_ret, use_container_width=True)
    
    st.divider()

# ── SECTION 4: Add New Transaction ────────────────────────────────────────────
st.markdown("### ➕ Add New Transaction")

with st.form("add_transaction_form"):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        asset = st.selectbox(
            "Asset Class",
            ASSET_CLASSES,
            help="Select the asset class"
        )
    
    with col2:
        amount = st.number_input(
            "Amount (₹)",
            value=0.0,
            step=10000.0,
            help="Positive for investment, Negative for withdrawal"
        )
    
    with col3:
        inv_date = st.date_input(
            "Date",
            value=date.today(),
        )
    
    with col4:
        notes = st.text_input(
            "Notes",
            placeholder="e.g., Additional ETH",
            max_chars=100,
        )
    
    submit = st.form_submit_button("✅ Add Transaction", use_container_width=True)
    
    if submit:
        if amount == 0:
            st.error("❌ Amount cannot be zero")
        else:
            if add_transaction(
                asset_class=asset,
                amount=amount,
                investment_date=inv_date.strftime("%Y-%m-%d"),
                notes=notes,
            ):
                st.success(f"✅ {asset}: {amount:+,.0f} on {inv_date}")
                st.cache_data.clear()
                st.rerun()


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption("""
**📚 Understanding the Metrics:**
- **IRR (Money-Weighted Return):** Accounts for timing & size of every cash flow — the most accurate performance measure
- **Capital Invested:** Total money you put in (gross, never reduced by withdrawals)
- **Realised Profit:** Profits already withdrawn and in your bank — money you've booked
- **Unrealised Gain:** Paper profit still sitting in the portfolio (Current Value − Invested)
- **Current Value:** Live portfolio value from your synced accounts
""")
