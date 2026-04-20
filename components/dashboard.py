import streamlit as st
import pandas as pd
import plotly.express as px

from utils.theme import THEME
from services.market_data import fetch_usd_inr_rate
from services.portfolio_service import load_filtered_holdings

def dashboard(active_ids, is_global=False):
    plotly_template = "plotly_white"
    chart_bars = ['#ffd166', '#06d6a0'] 

    if not active_ids:
        st.info("Please select at least one active account in the sidebar.")
        return

    # --- LOAD & PREPROCESS ---
    df = load_filtered_holdings(active_ids)
    if df.empty:
        st.info("No holdings found for the selected accounts.")
        return

    if is_global and 'asset_category' not in df.columns:
        from services.portfolio_service import get_all_accounts
        accs = get_all_accounts()
        if not accs.empty and 'id' in accs.columns and 'asset_category' in accs.columns:
            df = df.merge(accs[['id', 'asset_category']], left_on='account_id', right_on='id', how='left')
        else:
            df['asset_category'] = 'Unknown'

    df['total_value'] = df['quantity'] * df['current_price']
    df['total_cost'] = df.get('total_invested', df['quantity'] * df['avg_price'])
    
    # Filter out 0 invested value
    df = df[df['total_cost'] > 0].copy()
    
    if df.empty:
        st.info("No active holdings (invested > 0) found for the selected accounts.")
        return

    df['gain_loss'] = df['total_value'] - df['total_cost']
    
    # --- CURRENCY HANDLING ---
    use_inr = st.session_state.get('use_inr', False)
    fx_rate = fetch_usd_inr_rate()
    if not fx_rate: fx_rate = 83.0 # Fallback
    
    sym = "₹" if use_inr else "$"
    plotly_sym = "₹%{text:,.0f}" if use_inr else "$%{text:,.0f}"

    def to_display_currency(val, native_currency):
        if use_inr: # Showing in INR
            return val * fx_rate if native_currency == 'USD' else val
        else: # Showing in USD
            return val / fx_rate if native_currency == 'INR' else val

    # Add display versions of currency columns
    df['total_value_disp'] = df.apply(lambda r: to_display_currency(r['total_value'], r['currency']), axis=1)
    df['total_cost_disp'] = df.apply(lambda r: to_display_currency(r['total_cost'], r['currency']), axis=1)
    df['gain_loss_disp'] = df.apply(lambda r: to_display_currency(r['gain_loss'], r['currency']), axis=1)
    df['avg_price_disp'] = df.apply(lambda r: to_display_currency(r['avg_price'], r['currency']), axis=1)
    df['current_price_disp'] = df.apply(lambda r: to_display_currency(r['current_price'], r['currency']), axis=1)

    # --- PORTFOLIO METRICS ---
    total_portfolio_value = df['total_value_disp'].sum()
    total_cost = df['total_cost_disp'].sum()
    total_gain = total_portfolio_value - total_cost
    total_gain_pct = (total_gain / total_cost) * 100 if total_cost > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Total Invested", f"{sym}{total_cost:,.2f}")
    col2.metric("Total Value", f"{sym}{total_portfolio_value:,.2f}")
    col3.metric("Total Gain/Loss", f"{sym}{total_gain:,.2f}", f"{total_gain_pct:.2f}%")
    col4.metric("Tickers", f"{len(df['ticker'].unique())}")
    col5.metric("Active Accounts", f"{len(df['account_id'].unique())}")

    st.divider()

    # --- CHARTS (TOP) ---
    st.header("📊 Portfolio Visualization")
    df['labeled_account'] = df['platform'] + " (" + df['account_name'] + ")"
    
    bar_group_col = 'asset_category' if is_global else 'labeled_account'
    bar_label = 'Asset Category' if is_global else 'Account'
    
    # Calculate account-level sums for bar charts
    account_sums = df.groupby([bar_group_col]).agg({
        'total_cost_disp': 'sum',
        'total_value_disp': 'sum'
    }).reset_index()
    account_sums = account_sums.sort_values(by='total_value_disp', ascending=False)
    
    # Melt for grouped bar chart
    account_melted = account_sums.melt(id_vars=[bar_group_col], value_vars=['total_cost_disp', 'total_value_disp'], 
                                       var_name='Type', value_name='Amount')
    account_melted['Type'] = account_melted['Type'].replace({'total_cost_disp': 'Invested', 'total_value_disp': 'Current Value'})

    # 1. Invested vs Current Value by Account (Grouped Bar)
    fig_acc = px.bar(
        account_melted, x=bar_group_col, y='Amount', color='Type', barmode='group',
        text='Amount',
        title=f'Invested vs Current Value by {bar_label}',
        labels={bar_group_col: bar_label, 'Amount': f'Amount ({sym})'},
        color_discrete_map={'Invested': chart_bars[0], 'Current Value': chart_bars[1]} 
    )
    fig_acc.update_traces(texttemplate=plotly_sym, textposition='outside')
    
    # Calculate a nice max Y range to prevent text clipping
    max_val = account_melted['Amount'].max()
    y_max = max_val * 1.15 if max_val > 0 else 1 
    
    fig_acc.update_layout(
        template=plotly_template, 
        uniformtext_minsize=8, 
        uniformtext_mode='hide', 
        font=dict(color=THEME['text']),
        title=dict(font=dict(color=THEME['primary'])),
        legend=dict(
            title='', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color=THEME['text'])
        ),
        xaxis=dict(gridcolor=THEME['border'], zerolinecolor=THEME['border'], tickfont=dict(color=THEME['text'])),
        yaxis=dict(title=f'Amount ({sym})', range=[0, y_max], gridcolor=THEME['border'], zerolinecolor=THEME['border'], tickfont=dict(color=THEME['text'])),
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_acc, use_container_width=True)

    pie_group_col = 'asset_category' if is_global else 'ticker'
    pie_label = 'Asset Category' if is_global else 'Holdings'

    # Calculate ticker-level sums for pie charts
    ticker_sums = df.groupby(pie_group_col).agg({
        'total_cost_disp': 'sum',
        'total_value_disp': 'sum'
    }).reset_index()

    c1, c2 = st.columns(2)
    
    # 2. All Holdings by Invested Amount (Pie)
    fig_all_inv = px.pie(
        ticker_sums, values='total_cost_disp', names=pie_group_col, 
        title=f'All {pie_label} (Invested)', hole=0.4
    )
    fig_all_inv.update_traces(textposition='inside', textinfo='percent+label', insidetextorientation='horizontal')
    fig_all_inv.update_layout(
        template=plotly_template, font=dict(color=THEME['text']), title=dict(font=dict(color=THEME['primary'])),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=0, l=10, r=10), showlegend=False
    )
    c1.plotly_chart(fig_all_inv, use_container_width=True)

    # 3. All Holdings by Current Value (Pie)
    fig_all_val = px.pie(
        ticker_sums, values='total_value_disp', names=pie_group_col, 
        title=f'All {pie_label} (Current Value)', hole=0.4
    )
    fig_all_val.update_traces(textposition='inside', textinfo='percent+label', insidetextorientation='horizontal')
    fig_all_val.update_layout(
        template=plotly_template, font=dict(color=THEME['text']), title=dict(font=dict(color=THEME['primary'])),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=0, l=10, r=10), showlegend=False
    )
    c2.plotly_chart(fig_all_val, use_container_width=True)

    st.divider()

    # --- AGGREGATION FOR UNIFIED TABLE ---
    agg_df = df.groupby('ticker').agg({
        'quantity': 'sum',
        'total_cost_disp': 'sum',
        'total_value_disp': 'sum',
        'platform': lambda x: ", ".join(sorted(set(x))),
        'account_name': 'count'
    }).reset_index()
    
    agg_df['weighted_avg_price_disp'] = agg_df['total_cost_disp'] / agg_df['quantity']
    agg_df['current_price_disp'] = agg_df['total_value_disp'] / agg_df['quantity']
    agg_df['net_gain_disp'] = agg_df['total_value_disp'] - agg_df['total_cost_disp']
    agg_df['net_gain_pct'] = (agg_df['net_gain_disp'] / agg_df['total_cost_disp']) * 100
    agg_df['portfolio_cost_pct'] = (agg_df['total_cost_disp'] / total_cost) * 100 if total_cost > 0 else 0
    agg_df['portfolio_weight_pct'] = (agg_df['total_value_disp'] / total_portfolio_value) * 100 if total_portfolio_value > 0 else 0
    agg_df.rename(columns={'account_name': 'accounts_count'}, inplace=True)

    # --- SORTING & EXPANSION STATE ---
    if 'agg_sort_col' not in st.session_state:
        st.session_state.agg_sort_col = 'total_value_disp'
    if 'agg_sort_dir' not in st.session_state:
        st.session_state.agg_sort_dir = 'desc'
    if 'expanded_tickers' not in st.session_state:
        st.session_state.expanded_tickers = set()

    def toggle_sort(col):
        if st.session_state.agg_sort_col == col:
            st.session_state.agg_sort_dir = 'asc' if st.session_state.agg_sort_dir == 'desc' else 'desc'
        else:
            st.session_state.agg_sort_col = col
            st.session_state.agg_sort_dir = 'desc'

    # Apply sorting
    agg_df = agg_df.sort_values(st.session_state.agg_sort_col, ascending=(st.session_state.agg_sort_dir == 'asc'))

    # --- UNIFIED HOLDINGS TABLE ---
    st.header("📇 Unified Holdings Breakdown")
    
    h_cols = st.columns([1.2, 0.8, 1, 0.7, 1, 0.7, 1, 1, 1, 1, 0.6])
    headers = [
        ("Ticker", "ticker"), ("Qty", "quantity"), ("Invested", "total_cost_disp"), 
        ("% Cost", "portfolio_cost_pct"), ("Value", "total_value_disp"), ("% Weight", "portfolio_weight_pct"),
        ("Avg Buy", "weighted_avg_price_disp"), ("Curr Price", "current_price_disp"), 
        ("Gain Amt", "net_gain_disp"), ("Gain %", "net_gain_pct"),
        ("Acc", "accounts_count")
    ]
    
    for i, (label, key) in enumerate(headers):
        sort_icon = ""
        if st.session_state.agg_sort_col == key:
            sort_icon = " ↑" if st.session_state.agg_sort_dir == 'asc' else " ↓"
        if h_cols[i].button(f"{label}{sort_icon}", key=f"h_{key}"):
            toggle_sort(key)
            st.rerun()

    st.markdown("<hr style='margin: 0px; border-top: 1px solid #1E293B;'>", unsafe_allow_html=True)

    # Data Rows
    for _, stock in agg_df.iterrows():
        ticker = stock['ticker']
        qty = stock['quantity']
        inv_disp = stock['total_cost_disp']
        cost_pct = stock['portfolio_cost_pct']
        val_disp = stock['total_value_disp']
        weight_pct = stock['portfolio_weight_pct']
        avg_buy_disp = stock['weighted_avg_price_disp']
        curr_price_disp = stock['current_price_disp']
        gain_amt_disp = stock['net_gain_disp']
        gain_p = stock['net_gain_pct']
        acc_count = stock['accounts_count']
        
        color = "#02b84b" if gain_p >= 0 else "#d93025"
        gain_str = f"{gain_p:+.2f}%"

        r_cols = st.columns([1.2, 0.8, 1, 0.7, 1, 0.7, 1, 1, 1, 1, 0.6])
        
        is_expanded = ticker in st.session_state.expanded_tickers
        arrow = "▼" if is_expanded else "▶"
        
        if r_cols[0].button(f"{arrow} {ticker}", key=f"btn_{ticker}"):
            if is_expanded:
                st.session_state.expanded_tickers.remove(ticker)
            else:
                st.session_state.expanded_tickers.add(ticker)
            st.rerun()
            
        r_cols[1].markdown(f"<p class='row-text'>{qty:,.2f}</p>", unsafe_allow_html=True)
        r_cols[2].markdown(f"<p class='row-text'>{sym}{inv_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[3].markdown(f"<p class='row-text' style='color:#a855f7;'>{cost_pct:.1f}%</p>", unsafe_allow_html=True)
        r_cols[4].markdown(f"<p class='row-text'>{sym}{val_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[5].markdown(f"<p class='row-text' style='color:#6366f1; font-weight:bold;'>{weight_pct:.1f}%</p>", unsafe_allow_html=True)
        r_cols[6].markdown(f"<p class='row-text'>{sym}{avg_buy_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[7].markdown(f"<p class='row-text'>{sym}{curr_price_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[8].markdown(f"<p class='row-text' style='color:{color};'>{sym}{gain_amt_disp:,.2f}</p>", unsafe_allow_html=True)
        r_cols[9].markdown(f"<p class='row-text' style='color:{color}; font-weight:bold;'>{gain_str}</p>", unsafe_allow_html=True)
        r_cols[10].markdown(f"<p class='row-text' style='text-align: center;'>{acc_count}</p>", unsafe_allow_html=True)
        
        if is_expanded:
            with st.container():
                st.markdown(f"<div style='padding-left: 20px; font-size: 0.8rem;'>**Detailed breakdown for {ticker}**</div>", unsafe_allow_html=True)
                ticker_df = df[df['ticker'] == ticker][['account_name', 'platform', 'quantity', 'avg_price_disp', 'current_price_disp', 'total_cost_disp', 'total_value_disp', 'gain_loss_disp']].copy()
                ticker_df['gain_loss_pct'] = (ticker_df['gain_loss_disp'] / ticker_df['total_cost_disp']) * 100
                ticker_df['% Portfolio'] = (ticker_df['total_value_disp'] / total_portfolio_value) * 100
                st.dataframe(
                    ticker_df.style.format({
                        'avg_price_disp': sym + '{:,.2f}',
                        'current_price_disp': sym + '{:,.2f}',
                        'total_cost_disp': sym + '{:,.2f}',
                        'total_value_disp': sym + '{:,.2f}',
                        'gain_loss_disp': sym + '{:,.2f}',
                        'gain_loss_pct': '{:.2f}%',
                        '% Portfolio': '{:.2f}%'
                    }).applymap(lambda x: 'color: #02b84b' if isinstance(x, (int, float)) and x > 0 else ('color: #d93025' if isinstance(x, (int, float)) and x < 0 else ''), subset=['gain_loss_disp', 'gain_loss_pct']),
                    use_container_width=True
                )
        
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

    st.divider()
