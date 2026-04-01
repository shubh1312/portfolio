import streamlit as st

THEME = {
    "bg": "#F8FAFC",
    "sec_bg": "#FFFFFF",
    "text": "#1E293B",
    "mut": "#64748B",
    "border": "#E2E8F0",
    "primary": "#0F172A",
    "accent": "#6366F1",
    "accent_light": "#EEF2FF"
}

def apply_custom_styles():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Force Light Mode variables even if System is Dark */
    :root {{
        --primary-color: {THEME['accent']};
        --background-color: {THEME['bg']};
        --secondary-background-color: {THEME['sec_bg']};
        --text-color: {THEME['text']};
        --font: 'Inter', sans-serif;
    }}

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif !important;
        color: {THEME['text']} !important;
    }}

    /* Global Backgrounds - Persistent */
    .stApp {{
        background-color: {THEME['bg']} !important;
    }}
    
    [data-testid="stAppViewContainer"] {{ 
        background-color: {THEME['bg']} !important; 
    }}
    
    [data-testid="stSidebar"] {{ 
        background-color: {THEME['sec_bg']} !important; 
        border-right: 1px solid {THEME['border']} !important; 
    }}
    
    [data-testid="stHeader"] {{ 
        background-color: {THEME['bg']} !important; 
        background: transparent !important;
    }}
    
    /* Metrics as Compact Boxes */
    [data-testid="stMetric"] {{
        background-color: {THEME['sec_bg']} !important;
        padding: 10px !important;
        border-radius: 8px !important;
        border: 1px solid {THEME['border']} !important;
    }}
    [data-testid="stMetricLabel"] p {{ color: {THEME['mut']} !important; font-size: 0.75rem !important; }}
    [data-testid="stMetricValue"] > div {{ 
        color: {THEME['primary']} !important; 
        font-weight: 700 !important; 
        font-size: 1.1rem !important;
    }}
    
    /* Ensure inputs don't turn dark */
    input, select, textarea, [data-baseweb="select"] {{
        background-color: {THEME['sec_bg']} !important;
        color: {THEME['text']} !important;
        border-color: {THEME['border']} !important;
    }}
    
    /* ... existing styles ... */
    h1 {{ 
        color: {THEME['primary']} !important; 
        font-size: 1.2rem !important; 
        font-weight: 700 !important; 
        letter-spacing: -0.025em !important;
        margin-bottom: 0.1rem !important;
        margin-top: 0px !important;
    }}
    h2 {{ 
        color: {THEME['primary']} !important; 
        font-size: 1rem !important; 
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
        margin-bottom: 0.25rem !important;
    }}
    
    [data-testid="column"] {{
        padding: 0px 4px !important;
    }}
    
    .row-text {{
        font-size: 0.7rem;
        margin: 0px !important;
        padding: 0px !important;
        line-height: 1.2 !important;
        color: {THEME['text']};
    }}

    .account-count {{
        font-size: 0.6rem;
        color: {THEME['mut']};
        vertical-align: super;
        margin-left: 2px;
    }}
    
    /* Better Button Aesthetics - Light Indigo */
    .stButton>button {{
        border: 1px solid {THEME['border']} !important;
        background-color: {THEME['accent_light']} !important;
        color: {THEME['primary']} !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        padding: 4px 12px !important;
        border-radius: 6px !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }}
    .stButton>button:hover {{
        background-color: #E0E7FF !important;
        border-color: {THEME['accent']} !important;
        box-shadow: 0 1px 3px rgba(99,102,241,0.15) !important;
        transform: translateY(-1px);
    }}

    /* Table Expansion Buttons - Keep Subtle */
    [data-testid="column"] button {{
        background-color: transparent !important;
        color: {THEME['accent']} !important;
        box-shadow: none !important;
        padding: 0px !important;
    }}
    [data-testid="column"] button:hover {{
        background-color: transparent !important;
        transform: none !important;
        box-shadow: none !important;
        color: {THEME['primary']} !important;
    }}

    /* Sidebar Toggle Visibility */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{
        color: {THEME['text']} !important;
        font-weight: 500;
        font-size: 0.8rem;
    }}
    
    /* Center the Delete Button Icon */
    [data-testid="column"]:last-child button {{
        margin-top: 4px !important;
        font-size: 0.9rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }}

    hr {{ 
        border-top: 1px solid {THEME['border']} !important; 
        margin: 0.25rem 0 !important;
    }}
    
    .stDivider {{
         margin-top: 0.5rem !important;
         margin-bottom: 0.5rem !important;
    }}
    
    /* Sidebar Account Row Alignment */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {{
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    /* Ensure the trash button doesn't have extra padding and is centered */
    [data-testid="stSidebar"] .stButton button {{
        margin: 0 auto !important;
        display: block !important;
    }}

    /* Global Toggle Styling */
    .st-emotion-cache-170v3ix {{
        color: {THEME['text']} !important;
    }}

    /* Fix Plotly text visibility globally */
    .js-plotly-plot .plotly .main-svg {{
        background: transparent !important;
    }}
    .js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text, .js-plotly-plot .plotly .gtitle {{
        fill: {THEME['text']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)
