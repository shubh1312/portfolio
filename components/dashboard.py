import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils.theme import THEME, CHART_COLORS, RING_COLORS, BAR_VALUE, BAR_COST, BAR_V_EDGE, BAR_C_EDGE, _plotly_layout
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

        n = len(labels)
        ring_colors = (RING_COLORS * (n // len(RING_COLORS) + 1))[:n]
        total_val = sum(values)

        fig_pie = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.86,
            marker=dict(
                colors=ring_colors,
                line=dict(color="#0d1117", width=2),
            ),
            textfont=dict(size=10, color="#c9d1d9", family="Inter, sans-serif"),
            textposition="outside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{percent}<br>" + sym + "%{value:,.0f}<extra></extra>",
        ))
        fig_pie.update_layout(
            **_plotly_layout(
                showlegend=False,
                margin=dict(t=38, b=40, l=40, r=40),
                title=dict(text=title, font=dict(color="#8b949e", size=12), x=0),
                annotations=[dict(
                    text=f"<b>{sym}{total_val:,.0f}</b>",
                    x=0.5, y=0.5, showarrow=False, align="center",
                    font=dict(size=13, color="#e6edf3", family="JetBrains Mono, monospace"),
                )],
            )
        )
        col_ctx.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # ── Aggregate per ticker (shared by block view + table) ───────────────────
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
    agg_df["weighted_avg_price_disp"] = agg_df["total_cost_disp"]  / agg_df["quantity"]
    agg_df["current_price_disp"]      = agg_df["total_value_disp"] / agg_df["quantity"]
    agg_df["net_gain_disp"]           = agg_df["total_value_disp"] - agg_df["total_cost_disp"]
    agg_df["net_gain_pct"]            = agg_df["net_gain_disp"]    / agg_df["total_cost_disp"] * 100
    agg_df["portfolio_weight_pct"]    = agg_df["total_value_disp"] / total_value * 100 if total_value > 0 else 0

    # ── Block / Heatmap view ──────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Block view</div>", unsafe_allow_html=True)

    is_light = st.session_state.get("app_theme", "dark") == "light"
    sep_color = "#eef1f7" if is_light else "#0d1117"
    txt_color = "#ffffff"

    tree_labels   = agg_df["ticker"].tolist()
    tree_values   = agg_df["total_value_disp"].tolist()
    tree_gains    = agg_df["net_gain_pct"].tolist()
    tree_weights  = agg_df["portfolio_weight_pct"].tolist()
    tree_text     = [f"{g:+.2f}%" for g in tree_gains]

    fig_tree = go.Figure(go.Treemap(
        labels=tree_labels,
        values=tree_values,
        parents=[""] * len(tree_labels),
        text=tree_text,
        customdata=tree_weights,
        texttemplate="<b>%{label}</b><br>%{text}",
        textfont=dict(family="JetBrains Mono, monospace", size=13, color=txt_color),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Value: " + sym + "%{value:,.0f}<br>"
            "Weight: %{customdata:.1f}%<br>"
            "Gain: %{text}<extra></extra>"
        ),
        marker=dict(
            colors=tree_gains,
            colorscale=[
                [0.00, "#7f1d1d"],   # heavy loss — deep crimson
                [0.30, "#dc2626"],   # loss       — vivid red
                [0.46, "#b91c1c"],   # small loss — dark red
                [0.50, "#27272a"],   # breakeven  — dark zinc
                [0.54, "#15803d"],   # small gain — dark green
                [0.70, "#16a34a"],   # gain       — vivid green
                [1.00, "#14532d"],   # heavy gain — deep green
            ],
            cmid=0,
            cmin=-8,
            cmax=8,
            showscale=False,
            line=dict(width=2, color=sep_color),
        ),
        tiling=dict(pad=2),
    ))
    fig_tree.update_layout(
        **_plotly_layout(
            margin=dict(t=4, b=4, l=4, r=4),
            height=440,
        )
    )
    st.plotly_chart(fig_tree, use_container_width=True)

    st.divider()

    # ── Holdings table ────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Holdings breakdown</div>", unsafe_allow_html=True)

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

    # Avatar color palette (bg, fg) pairs
    _AV = [
        ("rgba(88,166,255,0.18)",  "#58a6ff"),
        ("rgba(129,140,248,0.18)", "#818cf8"),
        ("rgba(188,140,255,0.18)", "#bc8cff"),
        ("rgba(247,120,186,0.18)", "#f778ba"),
        ("rgba(248,81,73,0.18)",   "#f85149"),
        ("rgba(255,153,102,0.18)", "#ff9966"),
        ("rgba(227,179,65,0.18)",  "#e3b341"),
        ("rgba(63,185,80,0.18)",   "#3fb950"),
        ("rgba(45,212,191,0.18)",  "#2dd4bf"),
        ("rgba(121,192,255,0.18)", "#79c0ff"),
    ]

    def _av(ticker):
        return _AV[sum(ord(c) for c in ticker) % len(_AV)]

    COLS = [0.35, 1.7, 0.65, 1.05, 1.05, 1.3, 0.9, 0.9, 1.35]
    HEADERS = [
        ("",            None),
        ("Ticker",      "ticker"),
        ("Qty",         "quantity"),
        ("Invested",    "total_cost_disp"),
        ("Value",       "total_value_disp"),
        ("Weight",      "portfolio_weight_pct"),
        ("Avg Buy",     "weighted_avg_price_disp"),
        ("CMP",         "current_price_disp"),
        ("Gain / Loss", "net_gain_disp"),
    ]

    h_cols = st.columns(COLS)
    for i, (label, key) in enumerate(HEADERS):
        if not label:
            continue
        icon = (" ↑" if st.session_state.agg_sort_dir == "asc" else " ↓") \
               if st.session_state.agg_sort_col == key else ""
        if h_cols[i].button(f"{label}{icon}", key=f"h_{key}"):
            toggle_sort(key)
            st.rerun()

    st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

    for _, stock in agg_df.iterrows():
        ticker   = stock["ticker"]
        qty      = stock["quantity"]
        inv      = stock["total_cost_disp"]
        val      = stock["total_value_disp"]
        wpct     = stock["portfolio_weight_pct"]
        avg_b    = stock["weighted_avg_price_disp"]
        curr_p   = stock["current_price_disp"]
        gain_a   = stock["net_gain_disp"]
        gain_p   = stock["net_gain_pct"]
        platform = stock.get("platform", "")

        is_gain  = gain_p >= 0
        gc       = "#3fb950" if is_gain else "#f85149"
        g_bg     = "rgba(63,185,80,0.10)"  if is_gain else "rgba(248,81,73,0.10)"
        g_border = "rgba(63,185,80,0.22)"  if is_gain else "rgba(248,81,73,0.22)"
        g_sign   = "+" if gain_a >= 0 else ""

        av_bg, av_fg = _av(ticker)
        initials = ticker[:3].upper()

        is_exp = ticker in st.session_state.expanded_tickers

        with st.container(border=True):
            r = st.columns(COLS)

            if r[0].button("▼" if is_exp else "▶", key=f"btn_{ticker}"):
                if is_exp:
                    st.session_state.expanded_tickers.remove(ticker)
                else:
                    st.session_state.expanded_tickers.add(ticker)
                st.rerun()

            r[1].markdown(f"""
<div class='ticker-cell'>
  <div class='t-avatar' style='background:{av_bg};color:{av_fg};'>{initials}</div>
  <div>
    <div class='t-name'>{ticker}</div>
    <div class='t-sub'>{platform}</div>
  </div>
</div>""", unsafe_allow_html=True)

            r[2].markdown(f"""
<div class='h-col'>
  <div class='h-lbl'>QTY</div>
  <div class='h-val'>{qty:,.2f}</div>
</div>""", unsafe_allow_html=True)

            r[3].markdown(f"""
<div class='h-col'>
  <div class='h-lbl'>INVESTED</div>
  <div class='h-val'>{sym}{inv:,.0f}</div>
</div>""", unsafe_allow_html=True)

            r[4].markdown(f"""
<div class='h-col'>
  <div class='h-lbl'>VALUE</div>
  <div class='h-val'>{sym}{val:,.0f}</div>
</div>""", unsafe_allow_html=True)

            r[5].markdown(f"""
<div class='h-col'>
  <div class='h-lbl'>WEIGHT</div>
  <div class='wbar-track'><div class='wbar-fill' style='width:{min(wpct, 100):.1f}%;'></div></div>
  <div class='h-val' style='font-size:11px;color:#58a6ff;margin-top:1px;'>{wpct:.1f}%</div>
</div>""", unsafe_allow_html=True)

            r[6].markdown(f"""
<div class='h-col'>
  <div class='h-lbl'>AVG BUY</div>
  <div class='h-val'>{sym}{avg_b:,.2f}</div>
</div>""", unsafe_allow_html=True)

            r[7].markdown(f"""
<div class='h-col'>
  <div class='h-lbl'>CMP</div>
  <div class='h-val'>{sym}{curr_p:,.2f}</div>
</div>""", unsafe_allow_html=True)

            r[8].markdown(f"""
<div class='h-col'>
  <div class='h-lbl'>GAIN / LOSS</div>
  <div class='g-badge' style='background:{g_bg};color:{gc};border:1px solid {g_border};'>{g_sign}{sym}{gain_a:,.0f}</div>
  <div class='g-pct' style='color:{gc};'>{gain_p:+.2f}%</div>
</div>""", unsafe_allow_html=True)

        if is_exp:
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

    st.divider()
