import streamlit as st

pg = st.navigation([
    st.Page("pages/7_Performance.py",         title="Performance",    default=True),
    st.Page("pages/1_US_Market.py",           title="US Market"),
    st.Page("pages/2_Indian_Stock_Market.py", title="Indian Stocks"),
    st.Page("pages/3_Indian_Mutual_Funds.py", title="Mutual Funds"),
    st.Page("pages/4_Crypto.py",              title="Crypto"),
    st.Page("pages/6_Lending.py",             title="Lending"),
    st.Page("Net_Worth.py",                   title="Portfolio"),
])

pg.run()
