import streamlit as st

# ── Dark palette (GitHub-inspired) ───────────────────────────────────────────
THEME = {
    "bg": "#0d1117", "bg_1": "#161b22", "bg_2": "#21262d", "bg_3": "#30363d",
    "line": "#21262d", "line_2": "#30363d",
    "fg": "#e6edf3", "fg_dim": "#c9d1d9", "fg_mute": "#8b949e", "fg_faint": "#484f58",
    "accent": "#58a6ff", "accent_2": "#388bfd",
    "gain": "#3fb950", "loss": "#f85149", "neutral": "#e3b341", "info": "#58a6ff",
    "text": "#e6edf3", "mut": "#8b949e", "border": "#21262d",
    "primary": "#e6edf3", "sec_bg": "#161b22",
    "lime": "#58a6ff", "lime_dim": "#388bfd", "lime_ink": "#0d1117",
}

# ── Light palette (glass / FlowMail-inspired) ─────────────────────────────────
LIGHT_THEME = {
    "bg": "#eef1f7", "bg_1": "#ffffff", "bg_2": "#f8fafc", "bg_3": "#f1f5f9",
    "line": "#e2e8f0", "line_2": "#cbd5e1",
    "fg": "#0f172a", "fg_dim": "#1e293b", "fg_mute": "#64748b", "fg_faint": "#94a3b8",
    "accent": "#6366f1", "accent_2": "#4f46e5",
    "gain": "#16a34a", "loss": "#dc2626", "neutral": "#d97706", "info": "#6366f1",
    "text": "#0f172a", "mut": "#64748b", "border": "#e2e8f0",
    "primary": "#0f172a", "sec_bg": "#f8fafc",
}

# Pie / multi-series colours (work on both themes)
CHART_COLORS = ["#58a6ff", "#3fb950", "#e3b341", "#f85149", "#bc8cff", "#79c0ff"]

# Thin-ring donut spectral palette
RING_COLORS = [
    "#58a6ff", "#818cf8", "#bc8cff", "#f778ba",
    "#f85149", "#ff9966", "#e3b341", "#3fb950",
    "#2dd4bf", "#79c0ff",
]

# Bar chart colours
BAR_VALUE  = "rgba(56,139,253,0.80)"
BAR_COST   = "rgba(56,139,253,0.15)"
BAR_V_EDGE = "rgba(56,139,253,0.00)"
BAR_C_EDGE = "rgba(56,139,253,0.30)"


def _plotly_layout(**overrides):
    """Theme-aware Plotly layout base."""
    is_light = st.session_state.get("app_theme", "dark") == "light"
    if is_light:
        font_color  = "#64748b"
        grid_color  = "rgba(203,213,225,0.6)"
        tick_color  = "#94a3b8"
        hover_bg    = "#ffffff"
        hover_bdr   = "#e2e8f0"
        hover_font  = "#0f172a"
    else:
        font_color  = "#8b949e"
        grid_color  = "rgba(48,54,61,0.7)"
        tick_color  = "#6e7681"
        hover_bg    = "#161b22"
        hover_bdr   = "#30363d"
        hover_font  = "#e6edf3"

    base = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", color=font_color, size=12),
        xaxis=dict(
            gridcolor=grid_color, zerolinecolor=grid_color,
            tickfont=dict(color=tick_color, size=11), showline=False,
        ),
        yaxis=dict(
            gridcolor=grid_color, zerolinecolor=grid_color,
            tickfont=dict(color=tick_color, size=11), showline=False,
        ),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=font_color, size=11)),
        hoverlabel=dict(
            bgcolor=hover_bg, bordercolor=hover_bdr,
            font=dict(color=hover_font, size=12),
        ),
        margin=dict(t=46, b=20, l=10, r=10),
    )
    base.update(overrides)
    return base


# ── CSS generators ────────────────────────────────────────────────────────────

def _base_css() -> str:
    """Structural CSS shared by both themes — fonts, layout, shapes."""
    return """
    @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    html { scroll-behavior: smooth !important; }
    * { -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; box-sizing: border-box; }
    .main, [data-testid="stAppViewContainer"] > section { transform: translateZ(0); will-change: scroll-position; }

    /* Metric cards — shape */
    [data-testid="stMetric"] {
        border-radius: 12px !important; padding: 16px 20px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stMetricLabel"] p {
        font-size: 10px !important; text-transform: uppercase !important;
        letter-spacing: 0.12em !important; font-weight: 600 !important; margin: 0 !important;
    }
    [data-testid="stMetricValue"] > div {
        font-family: 'JetBrains Mono', ui-monospace, monospace !important;
        font-size: 1.15rem !important; font-weight: 500 !important; letter-spacing: -0.02em !important;
    }
    [data-testid="stMetricDelta"] svg { display: none !important; }
    [data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', ui-monospace, monospace !important; font-size: 0.7rem !important; }

    /* Headings — shape */
    h1 { font-family: 'Instrument Serif', Georgia, serif !important; font-size: 1.65rem !important; font-weight: 400 !important; letter-spacing: -0.02em !important; margin: 0 !important; }
    h2 { font-size: 0.95rem !important; font-weight: 600 !important; letter-spacing: -0.01em !important; margin-top: 0.75rem !important; margin-bottom: 0.2rem !important; }
    h3 { font-size: 0.85rem !important; font-weight: 600 !important; }

    /* Buttons — shape */
    .stButton > button {
        border-radius: 8px !important; font-size: 12px !important; font-weight: 500 !important;
        padding: 6px 14px !important;
        transition: background 0.15s ease, border-color 0.15s ease, transform 0.1s ease !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }
    .stLinkButton a {
        border-radius: 8px !important; font-weight: 600 !important; font-size: 12px !important;
        backdrop-filter: blur(8px) !important; -webkit-backdrop-filter: blur(8px) !important;
        transition: background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    [data-testid="column"] button { background: transparent !important; border: none !important; box-shadow: none !important; padding: 2px 4px !important; font-size: 11px !important; }
    [data-testid="column"] button:hover { background: transparent !important; border: none !important; transform: none !important; }

    /* Inputs — shape */
    input, select, textarea { border-radius: 8px !important; }

    /* Sidebar nav — shape */
    [data-testid="stSidebarNav"] a { border-radius: 6px !important; padding: 8px 10px !important; font-size: 13px !important; transition: background 0.15s ease, color 0.15s ease; }
    .sidebar-header { font-size: 10px !important; text-transform: uppercase !important; letter-spacing: 0.16em !important; padding: 14px 0 4px !important; margin: 0 !important; font-weight: 600 !important; }

    /* Structural */
    hr { border: none !important; margin: 0.5rem 0 !important; }
    .stCaption p, [data-testid="stCaptionContainer"] p { font-size: 0.72rem !important; }
    [data-testid="stWidgetLabel"] p { font-size: 0.75rem !important; font-weight: 500 !important; }
    [data-testid="stAlert"] { border-radius: 10px !important; }
    [data-testid="stExpander"] { border-radius: 10px !important; transition: border-color 0.15s ease; }
    [data-testid="stExpander"] summary { font-size: 12px !important; }
    [data-testid="stFileUploader"], [data-testid="stFileUploaderDropzone"] { border-radius: 10px !important; }
    [data-testid="column"] { padding: 0 4px !important; }
    [data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; }
    [data-testid="stToast"] { border-radius: 10px !important; }
    [data-testid="stSidebar"] > div { padding-top: 1.4rem !important; }
    [data-testid="stToggle"] p { font-size: 0.8rem !important; }

    /* Holding row cards — shape */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
        margin-bottom: 4px !important;
    }

    /* Holdings table custom classes — layout only */
    .row-text { font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 0.72rem; margin: 0 !important; padding: 3px 0 !important; line-height: 1.4 !important; }
    .row-divider { height: 1px; margin: 0; }
    .ticker-cell { display: flex; align-items: center; gap: 10px; padding: 4px 0; }
    .t-avatar { width: 36px; height: 36px; border-radius: 9px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 800; letter-spacing: 0.02em; }
    .h-col { display: flex; flex-direction: column; justify-content: center; padding: 4px 0; }
    .h-lbl { font-size: 9px; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; margin-bottom: 3px; }
    .h-val { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 500; }
    .wbar-track { height: 4px; border-radius: 4px; overflow: hidden; margin: 5px 0 3px; width: 50%; }
    .wbar-fill { height: 100%; border-radius: 4px; }
    .g-badge { display: inline-block; padding: 3px 9px; border-radius: 6px; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; white-space: nowrap; margin-bottom: 4px; }
    .g-pct { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; }
    .section-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.18em; padding-bottom: 10px; margin-bottom: 16px; font-weight: 700; }

    /* Performance & auth cards — shape */
    .perf-metric-card { border-radius: 12px; padding: 18px 20px; margin-bottom: 10px; transition: border-color 0.2s ease; }
    .metric-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 6px; }
    .metric-value { font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 1.3rem; font-weight: 500; letter-spacing: -0.02em; }
    .metric-sub { font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: 0.7rem; margin-top: 4px; }
    .auth-card { border-radius: 12px; padding: 1.4rem; margin-bottom: 0.75rem; transition: border-color 0.2s ease; }
    .status-badge { padding: 2px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; font-family: 'JetBrains Mono', ui-monospace, monospace; letter-spacing: 0.04em; }
    .asset-card { border-radius: 10px; padding: 16px; margin-bottom: 12px; transition: border-color 0.2s ease; }
    .success-badge { display:inline-block; background:rgba(63,185,80,.12); color:#3fb950; border:1px solid rgba(63,185,80,.25); padding:2px 8px; border-radius:6px; font-size:.7rem; font-weight:700; font-family:'JetBrains Mono',monospace; }
    .danger-badge  { display:inline-block; background:rgba(248,81,73,.12);  color:#f85149; border:1px solid rgba(248,81,73,.25);  padding:2px 8px; border-radius:6px; font-size:.7rem; font-weight:700; font-family:'JetBrains Mono',monospace; }
    .warning-badge { display:inline-block; background:rgba(227,179,65,.12); color:#e3b341; border:1px solid rgba(227,179,65,.25); padding:2px 8px; border-radius:6px; font-size:.7rem; font-weight:700; font-family:'JetBrains Mono',monospace; }
    .status-active  { background:rgba(63,185,80,.12);  color:#3fb950; border:1px solid rgba(63,185,80,.25); }
    .status-expired { background:rgba(248,81,73,.12);  color:#f85149; border:1px solid rgba(248,81,73,.25); }
    .status-warning { background:rgba(227,179,65,.12); color:#e3b341; border:1px solid rgba(227,179,65,.25); }

    /* Plotly */
    .js-plotly-plot .plotly .main-svg { background: transparent !important; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-thumb { border-radius: 4px; transition: background 0.2s ease; }
    """


def _dark_css() -> str:
    return """
    /* ── DARK THEME COLORS ────────────────────────────────────────────── */
    .stApp, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse 90% 45% at 50% -10%, rgba(33,60,120,0.22) 0%, transparent 60%),
            radial-gradient(ellipse 55% 40% at 88% 108%, rgba(80,54,150,0.13) 0%, transparent 55%),
            #0d1117 !important;
        min-height: 100vh;
    }
    [data-testid="stHeader"] { background: rgba(13,17,23,0.88) !important; }

    [data-testid="stSidebar"] { background: #0d1117 !important; border-right: 1px solid #21262d !important; }
    [data-testid="stSidebarNav"] a { color: #8b949e !important; }
    [data-testid="stSidebarNav"] a:hover { background: rgba(177,186,196,0.08) !important; color: #e6edf3 !important; }
    [data-testid="stSidebarNav"] a[aria-selected="true"], [data-testid="stSidebarNav"] a[aria-current="page"] { background: rgba(56,139,253,0.1) !important; border: 1px solid rgba(56,139,253,0.2) !important; color: #e6edf3 !important; font-weight: 600 !important; }
    .sidebar-header { color: #484f58 !important; }

    [data-testid="stMetric"] { background: #161b22 !important; border: 1px solid #21262d !important; }
    [data-testid="stMetric"]:hover { border-color: #30363d !important; box-shadow: 0 0 0 1px rgba(56,139,253,0.1) !important; }
    [data-testid="stMetricLabel"] p { color: #8b949e !important; }
    [data-testid="stMetricValue"] > div { color: #e6edf3 !important; }

    h1 { color: #e6edf3 !important; }
    h2 { color: #e6edf3 !important; }
    h3 { color: #8b949e !important; }
    p, li { color: #8b949e !important; }

    .stButton > button { background: #21262d !important; color: #c9d1d9 !important; border: 1px solid #30363d !important; box-shadow: 0 0 transparent !important; }
    .stButton > button:hover { background: #30363d !important; border-color: #8b949e !important; color: #e6edf3 !important; transform: translateY(-1px) !important; box-shadow: 0 3px 12px rgba(0,0,0,0.3) !important; }
    .stLinkButton a { background: rgba(188,140,255,0.10) !important; border: 1px solid rgba(188,140,255,0.28) !important; color: #bc8cff !important; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06) !important; }
    .stLinkButton a:hover { background: rgba(188,140,255,0.18) !important; border-color: rgba(188,140,255,0.45) !important; box-shadow: 0 0 12px rgba(188,140,255,0.2), inset 0 1px 0 rgba(255,255,255,0.08) !important; transform: translateY(-1px) !important; }
    [data-testid="column"] button { color: #484f58 !important; }
    [data-testid="column"] button:hover { color: #8b949e !important; }

    input, select, textarea { background: #0d1117 !important; color: #c9d1d9 !important; border: 1px solid #30363d !important; }
    input:focus, select:focus, textarea:focus { border-color: #388bfd !important; outline: none !important; box-shadow: 0 0 0 3px rgba(56,139,253,0.15) !important; }
    [data-baseweb="input"] { background: #0d1117 !important; }
    [data-testid="stToggle"] p { color: #8b949e !important; }

    hr { border-top: 1px solid #21262d !important; }
    .stCaption p, [data-testid="stCaptionContainer"] p { color: #6e7681 !important; }
    [data-testid="stWidgetLabel"] p { color: #8b949e !important; }
    [data-testid="stAlert"] { background: #161b22 !important; border: 1px solid #21262d !important; }
    [data-testid="stAlert"] p { color: #8b949e !important; }
    [data-testid="stExpander"] { background: #161b22 !important; border: 1px solid #21262d !important; }
    [data-testid="stExpander"]:hover { border-color: #30363d !important; }
    [data-testid="stExpander"] summary { color: #8b949e !important; }
    [data-testid="stFileUploader"], [data-testid="stFileUploaderDropzone"] { background: #161b22 !important; border: 1px dashed #30363d !important; }
    [data-testid="stDataFrame"] { border: 1px solid #21262d !important; }
    [data-testid="stToast"] { background: #161b22 !important; border: 1px solid #30363d !important; color: #e6edf3 !important; }
    .stSpinner > div > div { border-top-color: #58a6ff !important; }
    .js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text, .js-plotly-plot .plotly .gtitle, .js-plotly-plot .plotly .legendtext { fill: #8b949e !important; }

    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #21262d; }
    ::-webkit-scrollbar-thumb:hover { background: #30363d; }

    [data-testid="stVerticalBlockBorderWrapper"] { background: #161b22 !important; border: 1px solid #21262d !important; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: #30363d !important; box-shadow: 0 2px 12px rgba(0,0,0,0.25) !important; }

    .row-text { color: #c9d1d9; }
    .row-divider { background: #21262d; }
    .t-name { color: #e6edf3; }
    .t-sub  { color: #6e7681; }
    .h-lbl  { color: #484f58; }
    .h-val  { color: #c9d1d9; }
    .wbar-track { background: rgba(56,139,253,0.10); }
    .wbar-fill  { background: linear-gradient(90deg, #388bfd 0%, #58a6ff 100%); }
    .section-label { color: #484f58; border-bottom: 1px solid #21262d; }

    .perf-metric-card { background: #161b22; border: 1px solid #21262d; }
    .perf-metric-card:hover { border-color: #30363d; }
    .metric-label { color: #6e7681; }
    .metric-value { color: #e6edf3; }
    .metric-sub   { color: #6e7681; }
    .auth-card { background: #161b22; border: 1px solid #21262d; }
    .auth-card:hover { border-color: #30363d; }
    .auth-card h4 { color: #e6edf3 !important; margin-bottom: 4px; }
    .asset-card { background: #161b22; border: 1px solid #21262d; }
    .asset-card:hover { border-color: #30363d; }
    .irr-label { display:inline-block; background:rgba(88,166,255,.12); color:#58a6ff; border:1px solid rgba(88,166,255,.25); padding:4px 8px; border-radius:6px; font-size:.7rem; font-weight:700; font-family:'JetBrains Mono',monospace; }
    """


def _light_css() -> str:
    return """
    /* ── LIGHT THEME COLORS (glass / FlowMail-inspired) ──────────────── */
    .stApp, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse 80% 50% at 20% -15%, rgba(99,102,241,0.10) 0%, transparent 55%),
            radial-gradient(ellipse 60% 45% at 85% 105%, rgba(6,182,212,0.07) 0%, transparent 55%),
            radial-gradient(ellipse 50% 40% at 60% 50%,  rgba(248,250,252,0.5) 0%, transparent 70%),
            #eef1f7 !important;
        min-height: 100vh;
    }
    [data-testid="stHeader"] { background: rgba(238,241,247,0.88) !important; backdrop-filter: blur(12px) !important; }

    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.82) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(203,213,225,0.6) !important;
        box-shadow: 4px 0 24px rgba(0,0,0,0.04) !important;
    }
    [data-testid="stSidebarNav"] a { color: #1e293b !important; }
    [data-testid="stSidebarNav"] a:hover { background: rgba(99,102,241,0.08) !important; color: #0f172a !important; }
    [data-testid="stSidebarNav"] a[aria-selected="true"], [data-testid="stSidebarNav"] a[aria-current="page"] { background: rgba(99,102,241,0.12) !important; border: 1px solid rgba(99,102,241,0.28) !important; color: #3730a3 !important; font-weight: 600 !important; }
    .sidebar-header { color: #475569 !important; }

    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.68) !important;
        border: 1px solid rgba(203,213,225,0.7) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stMetric"]:hover { border-color: rgba(148,163,184,0.7) !important; box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important; }
    [data-testid="stMetricLabel"] p { color: #374151 !important; }
    [data-testid="stMetricValue"] > div { color: #0f172a !important; }

    h1 { color: #0f172a !important; }
    h2 { color: #111827 !important; }
    h3 { color: #1f2937 !important; }
    p, li { color: #1f2937 !important; }

    .stButton > button { background: rgba(255,255,255,0.75) !important; color: #111827 !important; border: 1px solid rgba(148,163,184,0.6) !important; box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important; }
    .stButton > button:hover { background: rgba(255,255,255,0.95) !important; border-color: #94a3b8 !important; color: #0f172a !important; transform: translateY(-1px) !important; box-shadow: 0 4px 14px rgba(0,0,0,0.1) !important; }
    .stLinkButton a { background: rgba(99,102,241,0.08) !important; border: 1px solid rgba(99,102,241,0.30) !important; color: #3730a3 !important; box-shadow: inset 0 1px 0 rgba(255,255,255,0.5) !important; }
    .stLinkButton a:hover { background: rgba(99,102,241,0.14) !important; border-color: rgba(99,102,241,0.45) !important; box-shadow: 0 0 12px rgba(99,102,241,0.15) !important; transform: translateY(-1px) !important; }
    [data-testid="column"] button { color: #374151 !important; }
    [data-testid="column"] button:hover { color: #111827 !important; }

    input, select, textarea { background: rgba(255,255,255,0.90) !important; color: #0f172a !important; border: 1px solid rgba(148,163,184,0.7) !important; }
    input:focus, select:focus, textarea:focus { border-color: #6366f1 !important; outline: none !important; box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important; }
    [data-baseweb="input"] { background: rgba(255,255,255,0.90) !important; }
    [data-testid="stToggle"] p { color: #111827 !important; }

    hr { border-top: 1px solid rgba(148,163,184,0.4) !important; }
    .stCaption p, [data-testid="stCaptionContainer"] p { color: #374151 !important; }
    [data-testid="stWidgetLabel"] p { color: #111827 !important; }
    [data-testid="stAlert"] { background: rgba(255,255,255,0.65) !important; border: 1px solid rgba(203,213,225,0.7) !important; }
    [data-testid="stAlert"] p { color: #1e293b !important; }
    [data-testid="stExpander"] { background: rgba(255,255,255,0.6) !important; border: 1px solid rgba(203,213,225,0.7) !important; backdrop-filter: blur(8px) !important; }
    [data-testid="stExpander"]:hover { border-color: rgba(148,163,184,0.6) !important; }
    [data-testid="stExpander"] summary { color: #111827 !important; }
    [data-testid="stFileUploader"], [data-testid="stFileUploaderDropzone"] { background: rgba(255,255,255,0.5) !important; border: 1px dashed rgba(148,163,184,0.7) !important; }
    [data-testid="stDataFrame"] { border: 1px solid rgba(203,213,225,0.7) !important; }
    [data-testid="stToast"] { background: rgba(255,255,255,0.88) !important; border: 1px solid rgba(203,213,225,0.7) !important; color: #0f172a !important; }
    .stSpinner > div > div { border-top-color: #6366f1 !important; }
    .js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text, .js-plotly-plot .plotly .gtitle, .js-plotly-plot .plotly .legendtext { fill: #374151 !important; }

    ::-webkit-scrollbar-track { background: #eef1f7; }
    ::-webkit-scrollbar-thumb { background: #94a3b8; }
    ::-webkit-scrollbar-thumb:hover { background: #64748b; }

    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255,255,255,0.65) !important;
        border: 1px solid rgba(203,213,225,0.7) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: rgba(100,116,139,0.5) !important; box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important; }

    .row-text { color: #0f172a; }
    .row-divider { background: #94a3b8; }
    .t-name { color: #0f172a; }
    .t-sub  { color: #374151; }
    .h-lbl  { color: #374151; }
    .h-val  { color: #0f172a; }
    .wbar-track { background: rgba(99,102,241,0.12); }
    .wbar-fill  { background: linear-gradient(90deg, #6366f1 0%, #818cf8 100%); }
    .section-label { color: #1e293b; border-bottom: 1px solid rgba(148,163,184,0.4); }

    .perf-metric-card { background: rgba(255,255,255,0.65); border: 1px solid rgba(203,213,225,0.7); backdrop-filter: blur(10px); box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .perf-metric-card:hover { border-color: rgba(100,116,139,0.4); }
    .metric-label { color: #374151; }
    .metric-value { color: #0f172a; }
    .metric-sub   { color: #374151; }
    .auth-card { background: rgba(255,255,255,0.65); border: 1px solid rgba(203,213,225,0.7); backdrop-filter: blur(10px); }
    .auth-card:hover { border-color: rgba(100,116,139,0.4); }
    .auth-card h4 { color: #0f172a !important; margin-bottom: 4px; }
    .asset-card { background: rgba(255,255,255,0.6); border: 1px solid rgba(203,213,225,0.7); }
    .asset-card:hover { border-color: rgba(100,116,139,0.4); }
    .irr-label { display:inline-block; background:rgba(99,102,241,.12); color:#3730a3; border:1px solid rgba(99,102,241,.28); padding:4px 8px; border-radius:6px; font-size:.7rem; font-weight:700; font-family:'JetBrains Mono',monospace; }
    """


def apply_custom_styles():
    # ── Theme state ───────────────────────────────────────────────────────────
    if "app_theme" not in st.session_state:
        st.session_state.app_theme = "dark"

    # ── Toggle in sidebar (renders at top of every page's sidebar) ────────────
    with st.sidebar:
        is_light = st.toggle(
            "☀️  Light mode",
            value=(st.session_state.app_theme == "light"),
            key="_theme_toggle",
        )
        st.session_state.app_theme = "light" if is_light else "dark"

    # ── Inject CSS ────────────────────────────────────────────────────────────
    theme_css = _light_css() if st.session_state.app_theme == "light" else _dark_css()
    st.markdown(f"<style>{_base_css()}{theme_css}</style>", unsafe_allow_html=True)
