import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.logo("https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png")

st.title("📊 Nifty 100 Financial Intelligence Platform")

st.markdown("""
Welcome to the **Nifty 100 Financial Intelligence Dashboard**.

### Available Dashboard Modules

- 🏠 Home
- 🏢 Company Profile
- 🔍 Screener
- 🤝 Peer Comparison
- 📈 Trend Analysis
- 🏭 Sector Analysis
- 💰 Capital Allocation
- 📄 Annual Reports

Select a page from the left sidebar.
""")

st.info("Sprint 4 • Dashboard Scaffold Initialized Successfully")