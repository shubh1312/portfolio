import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.theme import THEME, CHART_COLORS, BAR_VALUE, BAR_COST, BAR_V_EDGE, BAR_C_EDGE, _plotly_layout
from services.market_data import fetch_usd_inr_rate
from services.portfolio_service import load_filtered_holdings


def dashboard(active_ids, is_global=False):
    if not active_ids:
        st.info("Select at least one active account from the sidebar.")
        return

    # ── Load & preprocess ─────────────────────────────────────────────────────
    df = load_filtered_holdings(active_ids)
    if df.empty:
        st.info("No holdings found for the selected accounts.")
        return

    if is_global and "asset_category" not in df.columns:
        from services.portfolio_service import get_all_accounts
        accs = get_all_accounts()
        if not accs.empty and "id" in accs.columns and "asset_category" in accs.columns:
            df = df.merge(accs[["id", "asset_category"]], left_on="account_id", right_on="id", how="left")
        else:
            df["asset_category"] = "Unknown"

    df["total_value"] = df["quantity"] * df["current_price"]
    df["total_cost"]  = df.get("total_invested", df["quantity"] * df["avg_price"])
    df = df[df["total_cost"] > 0].copy()

    if df.empty:
        st.info("No active holdings (invested > 0) found.")
        return

    df["gain_loss"] = df["total_value"] - df["total_cost"]

    # ── Currency ──────────────────────────────────────────────────────────────
    use_inr  = st.session_state.get("use_inr", False)
    fx_rate  = fetch_usd_inr_rate() or 83.0
    sym      = "₹" if use_inr else "$"

    def to_disp(val, native):
        if use_inr:
            return val * fx_rate if native == "USD" else val
        return val / fx_rate if native == "INR" else val

    df["total_value_disp"]   = df.apply(lambda r: to_disp(r["total_value"],   r["currency"]), axis=1)
    df["total_cost_disp"]    = df.apply(lambda r: to_disp(r["total_cost"],    r["currency"]), axis=1)
    df["gain_loss_disp"]     = df.apply(lambda r: to_disp(r["gain_loss"],     r["currency"]), axis=1)
    df["avg_price_disp"]     = df.apply(lambda r: to_disp(r["avg_price"],     r["currency"]), axis=1)
    df["current_price_disp"] = df.apply(lambda r: to_disp(r["current_price"], r["currency"]), axis=1)

    # ── Portfolio totals ──────────────────────────────────────────────────────
    total_value    = df["total_value_disp"].sum()
    total_cost     = df["total_cost_disp"].sum()
    total_gain     = total_value - total_cost
    total_gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0

    # ── Metric cards (glass) ──────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Invested",      f"{sym}{total_cost:,.0f}")
    c2.metric("Current Value", f"{sym}{total_value:,.0f}")
    c3.metric("Gain / Loss",   f"{sym}{total_gain:,.0f}", f"{total_gain_pct:+.2f}%")
    c4.metric("Tickers",       str(df["ticker"].nunique()))
    c5.metric("Accounts",      str(df["account_id"].nunique()))

    st.divider()

    # ── Chart prep ────────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Portfolio breakdown</div>", unsafe_allow_html=True)

    df["labeled_account"] = df["platform"] + " (" + df["account_name"] + ")"
    bar_col   = "asset_category" if is_global else "labeled_account"
    bar_label = "Asset Class"    if is_global else "Account"
    pie_col   = "asset_category" if is_global else "ticker"
    pie_label = "Asset Class"    if is_global else "Holdings"

    acct_sums = (
        df.groupby(bar_col)
        .agg(
            total_cost_disp =("total_cost_disp",  "sum"),
            total_value_disp=("total_value_disp", "sum"),
        )
        .reset_index()
        .sort_values("total_value_disp", ascending=False)
    )

    # ── Grouped bar chart — glass bars ────────────────────────────────────────
    categories = acct_sums[bar_col].tolist()
    inv_vals   = acct_sums["total_cost_disp"].tolist()
    val_vals   = acct_sums["total_value_disp"].tolist()

    fig_bar = go.Figure()

    # Ghost bars — Invested
    fig_bar.add_trace(go.Bar(
        name="Invested",
        x=categories,
        y=inv_vals,
        text=inv_vals,
        marker=dict(
            color=BAR_COST,
            line=dict(color=BAR_C_EDGE, width=1),
            cornerradius=8,
        ),
        texttemplate=sym + "%{text:,.0f}",
        textposition="outside",
        textfont=dict(color="rgba(241,241,243,0.38)", size=10),
        hovertemplate="<b>%{x}</b><br>Invested: " + sym + "%{y:,.0f}<extra></extra>",
        width=0.35,
    ))

    # Solid bars — Current Value
    fig_bar.add_trace(go.Bar(
        name="Current Value",
        x=categories,
        y=val_vals,
        text=val_vals,
        marker=dict(
            color=BAR_VALUE,
            line=dict(color=BAR_V_EDGE, width=0),
            cornerradius=8,
        ),
        texttemplate=sym + "%{text:,.0f}",
        textposition="outside",
        textfont=dict(color="rgba(241,241,243,0.62)", size=10),
        hovertemplate="<b>%{x}</b><br>Value: " + sym + "%{y:,.0f}<extra></extra>",
        width=0.35,
    ))

    max_v = max(val_vals or [1]) * 1.22
    fig_bar.update_layout(
        **_plotly_layout(
            barmode="group",
            bargap=0.3,
            bargroupgap=0.08,
            yaxis=dict(
                range=[0, max_v],
                gridcolor="rgba(255,255,255,0.04)",
                zerolinecolor="rgba(255,255,255,0.04)",
                tickfont=dict(color="rgba(241,241,243,0.4)", size=11),
                showline=False,
            ),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="right", x=1,
                bgcolor="rgba(0,0,0,0)",
                font=dict(color="rgba(241,241,243,0.55)", size=11),
            ),
            title=dict(
                text=f"Invested vs Current Value — by {bar_label}",
                font=dict(color="rgba(241,241,243,0.45)", size=12),
                x=0,
            ),
        )
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Donut charts ──────────────────────────────────────────────────────────
    ticker_sums = (
        df.groupby(pie_col)
        .agg(
            total_cost_disp =("total_cost_disp",  "sum"),
            total_value_disp=("total_value_disp", "sum"),
        )
        .reset_index()
    )

    cl, cr = st.columns(2)
    for col_ctx, val_col, title in [
        (cl, "total_cost_disp",  f"By {pie_label} — Invested"),
        (cr, "total_value_disp", f"By {pie_label} — Current Value"),
    ]:
        labels = ticker_sums[pie_col].tolist()
        values = ticker_sums[val_col].tolist()

        fig_pie = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.52,
            marker=dict(
                colors=CHART_COLORS[:len(labels)] if len(labels) <= len(CHART_COLORS)
                       else (CHART_COLORS * (len(labels) // len(CHART_COLORS) + 1))[:len(labels)],
                line=dict(color="#08090E", width=2),
            ),
            textfont=dict(size=11, color="rgba(241,241,243,0.82)"),
            textposition="inside",
            textinfo="percent+label",
            pull=[0.025] * len(labels),
            insidetextorientation="horizontal",
            hovertemplate="<b>%{label}</b><br>%{percent}<br>" + sym + "%{value:,.0f}<extra></extra>",
        ))
        fig_pie.update_layout(
            **_plotly_layout(
                showlegend=False,
                margin=dict(t=38, b=8, l=10, r=10),
                title=dict(text=title, font=dict(color="rgba(241,241,243,0.45)", size=12), x=0),
            )
        )
        col_ctx.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # ── Holdings table ────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Holdings breakdown</div>", unsafe_allow_html=True)

    agg_df = (
        df.groupby("ticker")
        .agg(
            quantity        =("quantity",       "sum"),
            total_cost_disp =("total_cost_disp", "sum"),
            total_value_disp=("total_value_disp","sum"),
            platform        =("platform",        lambda x: ", ".join(sorted(set(x)))),
            accounts_count  =("account_name",    "count"),
        )
        .reset_index()
    )
    agg_df["weighted_avg_price_disp"] = agg_df["total_cost_disp"]   / agg_df["quantity"]
    agg_df["current_price_disp"]      = agg_df["total_value_disp"]  / agg_df["quantity"]
    agg_df["net_gain_disp"]           = agg_df["total_value_disp"]  - agg_df["total_cost_disp"]
    agg_df["net_gain_pct"]            = agg_df["net_gain_disp"]     / agg_df["total_cost_disp"] * 100
    agg_df["portfolio_cost_pct"]      = agg_df["total_cost_disp"]   / total_cost   * 100 if total_cost   > 0 else 0
    agg_df["portfolio_weight_pct"]    = agg_df["total_value_disp"]  / total_value  * 100 if total_value  > 0 else 0

    # Sort state
    if "agg_sort_col" not in st.session_state:
        st.session_state.agg_sort_col = "total_value_disp"
    if "agg_sort_dir" not in st.session_state:
        st.session_state.agg_sort_dir = "desc"
    if "expanded_tickers" not in st.session_state:
        st.session_state.expanded_tickers = set()

    def toggle_sort(col):
        if st.session_state.agg_sort_col == col:
            st.session_state.agg_sort_dir = "asc" if st.session_state.agg_sort_dir == "desc" else "desc"
        else:
            st.session_state.agg_sort_col = col
            st.session_state.agg_sort_dir = "desc"

    agg_df = agg_df.sort_values(
        st.session_state.agg_sort_col,
        ascending=(st.session_state.agg_sort_dir == "asc"),
    )

    COLS = [1.2, 0.8, 1, 0.7, 1, 0.7, 1, 1, 1, 1, 0.6]
    HEADERS = [
        ("Ticker",      "ticker"),
        ("Qty",         "quantity"),
        ("Invested",    "total_cost_disp"),
        ("% Cost",      "portfolio_cost_pct"),
        ("Value",       "total_value_disp"),
        ("% Weight",    "portfolio_weight_pct"),
        ("Avg Buy",     "weighted_avg_price_disp"),
        ("Curr Price",  "current_price_disp"),
        ("Gain Amt",    "net_gain_disp"),
        ("Gain %",      "net_gain_pct"),
        ("Acc",         "accounts_count"),
    ]

    h_cols = st.columns(COLS)
    for i, (label, key) in enumerate(HEADERS):
        icon = (" ↑" if st.session_state.agg_sort_dir == "asc" else " ↓") \
               if st.session_state.agg_sort_col == key else ""
        if h_cols[i].button(f"{label}{icon}", key=f"h_{key}"):
            toggle_sort(key)
            st.rerun()

    st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

    for _, stock in agg_df.iterrows():
        ticker    = stock["ticker"]
        qty       = stock["quantity"]
        inv       = stock["total_cost_disp"]
        cpct      = stock["portfolio_cost_pct"]
        val       = stock["total_value_disp"]
        wpct      = stock["portfolio_weight_pct"]
        avg_b     = stock["weighted_avg_price_disp"]
        curr_p    = stock["current_price_disp"]
        gain_a    = stock["net_gain_disp"]
        gain_p    = stock["net_gain_pct"]
        acc_n     = stock["accounts_count"]

        gc = THEME["gain"] if gain_p >= 0 else THEME["loss"]

        r = st.columns(COLS)
        is_exp = ticker in st.session_state.expanded_tickers
        if r[0].button(f"{'▼' if is_exp else '▶'} {ticker}", key=f"btn_{ticker}"):
            if is_exp:
                st.session_state.expanded_tickers.remove(ticker)
            else:
                st.session_state.expanded_tickers.add(ticker)
            st.rerun()

        r[1].markdown(f"<p class='row-text'>{qty:,.2f}</p>",                                                         unsafe_allow_html=True)
        r[2].markdown(f"<p class='row-text'>{sym}{inv:,.0f}</p>",                                                    unsafe_allow_html=True)
        r[3].markdown(f"<p class='row-text' style='color:#58a6ff;'>{cpct:.1f}%</p>",                                 unsafe_allow_html=True)
        r[4].markdown(f"<p class='row-text'>{sym}{val:,.0f}</p>",                                                    unsafe_allow_html=True)
        r[5].markdown(f"<p class='row-text' style='color:#3fb950;font-weight:600;'>{wpct:.1f}%</p>",                 unsafe_allow_html=True)
        r[6].markdown(f"<p class='row-text'>{sym}{avg_b:,.2f}</p>",                                                  unsafe_allow_html=True)
        r[7].markdown(f"<p class='row-text'>{sym}{curr_p:,.2f}</p>",                                                 unsafe_allow_html=True)
        r[8].markdown(f"<p class='row-text' style='color:{gc};'>{sym}{gain_a:,.0f}</p>",                             unsafe_allow_html=True)
        r[9].markdown(f"<p class='row-text' style='color:{gc};font-weight:600;'>{gain_p:+.2f}%</p>",                 unsafe_allow_html=True)
        r[10].markdown(f"<p class='row-text' style='text-align:center;'>{acc_n}</p>",                                unsafe_allow_html=True)

        if is_exp:
            with st.container():
                sub = df[df["ticker"] == ticker][[
                    "account_name", "platform", "quantity",
                    "avg_price_disp", "current_price_disp",
                    "total_cost_disp", "total_value_disp", "gain_loss_disp",
                ]].copy()
                sub["gain_pct"]    = sub["gain_loss_disp"] / sub["total_cost_disp"] * 100
                sub["% Portfolio"] = sub["total_value_disp"] / total_value * 100
                st.dataframe(
                    sub.style
                    .format({
                        "avg_price_disp":     sym + "{:,.2f}",
                        "current_price_disp": sym + "{:,.2f}",
                        "total_cost_disp":    sym + "{:,.0f}",
                        "total_value_disp":   sym + "{:,.0f}",
                        "gain_loss_disp":     sym + "{:,.0f}",
                        "gain_pct":           "{:.2f}%",
                        "% Portfolio":        "{:.2f}%",
                    })
                    .applymap(
                        lambda x: f"color:{THEME['gain']}" if isinstance(x, (int, float)) and x > 0
                                  else (f"color:{THEME['loss']}" if isinstance(x, (int, float)) and x < 0 else ""),
                        subset=["gain_loss_disp", "gain_pct"],
                    ),
                    use_container_width=True,
                )

        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

    st.divider()
