import streamlit as st

# ── GitHub dark-mode palette ──────────────────────────────────────────────────
# Inspired by github.com's dark theme: navy-black base, blue-tinted surfaces,
# semantic status colours, and a soft indigo/violet hero gradient.
THEME = {
    # Backgrounds (blue-tinted dark, not flat black)
    "bg":        "#0d1117",    # canvas-default
    "bg_1":      "#161b22",    # canvas-overlay / card
    "bg_2":      "#21262d",    # canvas-inset / elevated
    "bg_3":      "#30363d",    # canvas-subtle / active
    # Borders
    "line":      "#21262d",    # border-default (solid)
    "line_2":    "#30363d",    # border-muted
    # Text
    "fg":        "#e6edf3",    # fg-default
    "fg_dim":    "#c9d1d9",    # fg-muted (slightly dimmer)
    "fg_mute":   "#8b949e",    # fg-subtle
    "fg_faint":  "#484f58",    # fg-on-emphasis / disabled
    # Accent — GitHub's interactive blue
    "accent":    "#58a6ff",    # accent-fg
    "accent_2":  "#388bfd",    # accent-emphasis
    # Status colours (GitHub's semantic tokens)
    "gain":      "#3fb950",    # success-fg
    "loss":      "#f85149",    # danger-fg
    "neutral":   "#e3b341",    # attention-fg
    "info":      "#58a6ff",    # accent-fg
    # Compat aliases
    "text":      "#e6edf3",
    "mut":       "#8b949e",
    "border":    "#21262d",
    "primary":   "#e6edf3",
    "sec_bg":    "#161b22",
    "lime":      "#58a6ff",
    "lime_dim":  "#388bfd",
    "lime_ink":  "#0d1117",
}

# Pie / multi-series — GitHub semantic palette on dark
CHART_COLORS = ["#58a6ff", "#3fb950", "#e3b341", "#f85149", "#bc8cff", "#79c0ff"]

# Bar chart colours: GitHub blue accent
BAR_VALUE  = "rgba(56,139,253,0.80)"    # current value — solid blue
BAR_COST   = "rgba(56,139,253,0.15)"    # invested      — ghost blue
BAR_V_EDGE = "rgba(56,139,253,0.00)"
BAR_C_EDGE = "rgba(56,139,253,0.30)"


def _plotly_layout(**overrides):
    """Common GitHub-dark Plotly layout. Merge per-chart overrides on top."""
    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif",
                  color="#8b949e", size=12),
        xaxis=dict(
            gridcolor="rgba(48,54,61,0.7)",
            zerolinecolor="rgba(48,54,61,0.7)",
            tickfont=dict(color="#6e7681", size=11),
            showline=False,
        ),
        yaxis=dict(
            gridcolor="rgba(48,54,61,0.7)",
            zerolinecolor="rgba(48,54,61,0.7)",
            tickfont=dict(color="#6e7681", size=11),
            showline=False,
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8b949e", size=11),
        ),
        hoverlabel=dict(
            bgcolor="#161b22",
            bordercolor="#30363d",
            font=dict(color="#e6edf3", size=12),
        ),
        margin=dict(t=46, b=20, l=10, r=10),
    )
    base.update(overrides)
    return base


def apply_custom_styles():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Smooth scrolling (GitHub-style) ───────────────────────────────── */
    html {{
        scroll-behavior: smooth !important;
    }}
    * {{
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        box-sizing: border-box;
    }}
    /* GPU-accelerated scroll containers */
    .main, [data-testid="stAppViewContainer"] > section {{
        transform: translateZ(0);
        will-change: scroll-position;
    }}

    /* ── App background — GitHub-style dark navy + subtle hero gradient ── */
    .stApp,
    [data-testid="stAppViewContainer"] {{
        background:
            radial-gradient(ellipse 90% 45% at 50% -10%,
                rgba(33,60,120,0.22) 0%, transparent 60%),
            radial-gradient(ellipse 55% 40% at 88% 108%,
                rgba(80,54,150,0.13) 0%, transparent 55%),
            #0d1117 !important;
        min-height: 100vh;
    }}
    [data-testid="stHeader"] {{ background: rgba(13,17,23,0.88) !important; }}

    /* ── Sidebar ────────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {{
        background: #0d1117 !important;
        border-right: 1px solid #21262d !important;
    }}
    [data-testid="stSidebar"] > div {{ padding-top: 1.4rem !important; }}

    /* Nav links */
    [data-testid="stSidebarNav"] a {{
        border-radius: 6px !important;
        padding: 8px 10px !important;
        font-size: 13px !important;
        color: #8b949e !important;
        transition: background 0.15s ease, color 0.15s ease;
    }}
    [data-testid="stSidebarNav"] a:hover {{
        background: rgba(177,186,196,0.08) !important;
        color: #e6edf3 !important;
    }}
    [data-testid="stSidebarNav"] a[aria-selected="true"],
    [data-testid="stSidebarNav"] a[aria-current="page"] {{
        background: rgba(56,139,253,0.1) !important;
        border: 1px solid rgba(56,139,253,0.2) !important;
        color: #e6edf3 !important;
        font-weight: 600 !important;
    }}
    .sidebar-header {{
        font-size: 10px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.16em !important;
        color: #484f58 !important;
        padding: 14px 0 4px !important;
        margin: 0 !important;
        font-weight: 600 !important;
    }}

    /* ── Metric cards ───────────────────────────────────────────────────── */
    [data-testid="stMetric"] {{
        background: #161b22 !important;
        border: 1px solid #21262d !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }}
    [data-testid="stMetric"]:hover {{
        border-color: #30363d !important;
        box-shadow: 0 0 0 1px rgba(56,139,253,0.1) !important;
    }}
    [data-testid="stMetricLabel"] p {{
        color: #8b949e !important;
        font-size: 10px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.12em !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }}
    [data-testid="stMetricValue"] > div {{
        color: #e6edf3 !important;
        font-family: 'JetBrains Mono', ui-monospace, monospace !important;
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        letter-spacing: -0.02em !important;
    }}
    [data-testid="stMetricDelta"] svg {{ display: none !important; }}
    [data-testid="stMetricDelta"] {{
        font-family: 'JetBrains Mono', ui-monospace, monospace !important;
        font-size: 0.7rem !important;
    }}

    /* ── Headings ───────────────────────────────────────────────────────── */
    h1 {{
        color: #e6edf3 !important;
        font-family: 'Instrument Serif', Georgia, serif !important;
        font-size: 1.65rem !important;
        font-weight: 400 !important;
        letter-spacing: -0.02em !important;
        margin: 0 !important;
    }}
    h2 {{
        color: #e6edf3 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.2rem !important;
    }}
    h3 {{ color: #8b949e !important; font-size: 0.85rem !important; font-weight: 600 !important; }}
    p, li {{ color: #8b949e !important; }}

    /* ── Buttons ────────────────────────────────────────────────────────── */
    .stButton > button {{
        background: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        padding: 6px 14px !important;
        transition: background 0.15s ease, border-color 0.15s ease, transform 0.1s ease !important;
        box-shadow: 0 0 transparent !important;
    }}
    .stButton > button:hover {{
        background: #30363d !important;
        border-color: #8b949e !important;
        color: #e6edf3 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.3) !important;
    }}
    .stButton > button:active {{ transform: translateY(0) !important; }}

    /* Link buttons — glass purple */
    .stLinkButton a {{
        background: rgba(188,140,255,0.10) !important;
        border: 1px solid rgba(188,140,255,0.28) !important;
        border-radius: 8px !important;
        color: #bc8cff !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
        transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.06) !important;
    }}
    .stLinkButton a:hover {{
        background: rgba(188,140,255,0.18) !important;
        border-color: rgba(188,140,255,0.45) !important;
        box-shadow: 0 0 12px rgba(188,140,255,0.2), inset 0 1px 0 rgba(255,255,255,0.08) !important;
        transform: translateY(-1px) !important;
    }}

    /* Table row-expand buttons */
    [data-testid="column"] button {{
        background: transparent !important;
        color: #484f58 !important;
        border: none !important;
        box-shadow: none !important;
        padding: 2px 4px !important;
        font-size: 11px !important;
    }}
    [data-testid="column"] button:hover {{
        background: transparent !important;
        color: #8b949e !important;
        border: none !important;
        transform: none !important;
    }}

    /* ── Inputs ─────────────────────────────────────────────────────────── */
    input, select, textarea {{
        background: #0d1117 !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }}
    input:focus, select:focus, textarea:focus {{
        border-color: #388bfd !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(56,139,253,0.15) !important;
    }}
    [data-baseweb="input"] {{ background: #0d1117 !important; }}

    /* ── Toggle ─────────────────────────────────────────────────────────── */
    [data-testid="stToggle"] p {{ color: #8b949e !important; font-size: 0.8rem !important; }}

    /* ── Dividers ───────────────────────────────────────────────────────── */
    hr {{
        border: none !important;
        border-top: 1px solid #21262d !important;
        margin: 0.5rem 0 !important;
    }}

    /* ── Captions ───────────────────────────────────────────────────────── */
    .stCaption p, [data-testid="stCaptionContainer"] p {{
        color: #6e7681 !important;
        font-size: 0.72rem !important;
    }}

    /* ── Widget labels ──────────────────────────────────────────────────── */
    [data-testid="stWidgetLabel"] p {{
        color: #8b949e !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }}

    /* ── Alerts ─────────────────────────────────────────────────────────── */
    [data-testid="stAlert"] {{
        background: #161b22 !important;
        border: 1px solid #21262d !important;
        border-radius: 10px !important;
    }}
    [data-testid="stAlert"] p {{ color: #8b949e !important; }}

    /* ── Expander ───────────────────────────────────────────────────────── */
    [data-testid="stExpander"] {{
        background: #161b22 !important;
        border: 1px solid #21262d !important;
        border-radius: 10px !important;
        transition: border-color 0.15s ease;
    }}
    [data-testid="stExpander"]:hover {{ border-color: #30363d !important; }}
    [data-testid="stExpander"] summary {{ color: #8b949e !important; font-size: 12px !important; }}

    /* ── File uploader ──────────────────────────────────────────────────── */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploaderDropzone"] {{
        background: #161b22 !important;
        border: 1px dashed #30363d !important;
        border-radius: 10px !important;
    }}

    /* ── Column padding ─────────────────────────────────────────────────── */
    [data-testid="column"] {{ padding: 0 4px !important; }}

    /* ── Holdings table rows ────────────────────────────────────────────── */
    .row-text {{
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 0.72rem;
        color: #c9d1d9;
        margin: 0 !important;
        padding: 3px 0 !important;
        line-height: 1.4 !important;
    }}
    .row-divider {{
        height: 1px;
        background: #21262d;
        margin: 0;
    }}

    /* ── Dataframe ──────────────────────────────────────────────────────── */
    [data-testid="stDataFrame"] {{
        border: 1px solid #21262d !important;
        border-radius: 10px !important;
        overflow: hidden;
    }}

    /* ── Toast ──────────────────────────────────────────────────────────── */
    [data-testid="stToast"] {{
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
        color: #e6edf3 !important;
    }}

    /* ── Spinner ────────────────────────────────────────────────────────── */
    .stSpinner > div > div {{ border-top-color: #58a6ff !important; }}

    /* ── Plotly ─────────────────────────────────────────────────────────── */
    .js-plotly-plot .plotly .main-svg {{ background: transparent !important; }}
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text,
    .js-plotly-plot .plotly .gtitle,
    .js-plotly-plot .plotly .legendtext {{ fill: #8b949e !important; }}

    /* ── Scrollbar ──────────────────────────────────────────────────────── */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #0d1117; }}
    ::-webkit-scrollbar-thumb {{
        background: #21262d;
        border-radius: 4px;
        transition: background 0.2s ease;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: #30363d; }}

    /* ── Section label ──────────────────────────────────────────────────── */
    .section-label {{
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #484f58;
        padding-bottom: 10px;
        border-bottom: 1px solid #21262d;
        margin-bottom: 16px;
        font-weight: 700;
    }}

    /* ── Performance cards ──────────────────────────────────────────────── */
    .perf-metric-card {{
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 10px;
        transition: border-color 0.2s ease;
    }}
    .perf-metric-card:hover {{ border-color: #30363d; }}
    .metric-label {{
        font-size: 10px; font-weight: 700;
        color: #6e7681; text-transform: uppercase;
        letter-spacing: 0.12em; margin-bottom: 6px;
    }}
    .metric-value {{
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 1.3rem; color: #e6edf3;
        font-weight: 500; letter-spacing: -0.02em;
    }}
    .metric-sub {{
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 0.7rem; color: #6e7681; margin-top: 4px;
    }}

    /* ── Auth cards (connections page) ─────────────────────────────────── */
    .auth-card {{
        background: #161b22;
        border: 1px solid #21262d;
        border-radius: 12px;
        padding: 1.4rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s ease;
    }}
    .auth-card:hover {{ border-color: #30363d; }}
    .auth-card h4 {{ color: #e6edf3 !important; margin-bottom: 4px; }}
    .status-badge {{
        padding: 2px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 700;
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        letter-spacing: 0.04em;
    }}
    .status-active  {{ background: rgba(63,185,80,.12);  color: #3fb950; border: 1px solid rgba(63,185,80,.25); }}
    .status-expired {{ background: rgba(248,81,73,.12);  color: #f85149; border: 1px solid rgba(248,81,73,.25); }}
    .status-warning {{ background: rgba(227,179,65,.12); color: #e3b341; border: 1px solid rgba(227,179,65,.25); }}

    /* ── Performance badges ─────────────────────────────────────────────── */
    .asset-card {{
        background: #161b22; border: 1px solid #21262d;
        border-radius: 10px; padding: 16px; margin-bottom: 12px;
        transition: border-color 0.2s ease;
    }}
    .asset-card:hover {{ border-color: #30363d; }}
    .success-badge {{
        display:inline-block; background:rgba(63,185,80,.12); color:#3fb950;
        border:1px solid rgba(63,185,80,.25); padding:2px 8px; border-radius:6px;
        font-size:.7rem; font-weight:700; font-family:'JetBrains Mono',monospace;
    }}
    .danger-badge {{
        display:inline-block; background:rgba(248,81,73,.12); color:#f85149;
        border:1px solid rgba(248,81,73,.25); padding:2px 8px; border-radius:6px;
        font-size:.7rem; font-weight:700; font-family:'JetBrains Mono',monospace;
    }}
    .warning-badge {{
        display:inline-block; background:rgba(227,179,65,.12); color:#e3b341;
        border:1px solid rgba(227,179,65,.25); padding:2px 8px; border-radius:6px;
        font-size:.7rem; font-weight:700; font-family:'JetBrains Mono',monospace;
    }}
    .irr-label {{
        display:inline-block; background:rgba(88,166,255,.12); color:#58a6ff;
        border:1px solid rgba(88,166,255,.25); padding:4px 8px; border-radius:6px;
        font-size:.7rem; font-weight:700; font-family:'JetBrains Mono',monospace;
    }}
    </style>
    """, unsafe_allow_html=True)
