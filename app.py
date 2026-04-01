import streamlit as st

# Using st.navigation to give 'app.py' a proper label in the sidebar
pg = st.navigation([
    st.Page("Net_Worth.py", title="Net Worth", icon="💰", default=True),
    st.Page("pages/1_US_Market.py", title="US Market"),
    st.Page("pages/2_Indian_Stock_Market.py", title="Indian Stock Market"),
    st.Page("pages/3_Indian_Mutual_Funds.py", title="Indian Mutual Funds"),
    st.Page("pages/4_Crypto.py", title="Crypto"),
    st.Page("pages/6_Lending.py", title="Lending"),
    st.Page("pages/5_Zerodha_Connect.py", title="Zerodha Connect"),
])

pg.run()
