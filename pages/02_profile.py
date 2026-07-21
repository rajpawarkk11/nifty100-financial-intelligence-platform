import streamlit as st

from src.dashboard.utils.db import (
    get_companies,
    get_company_dashboard
)

st.set_page_config(
    page_title="Company Profile",
    page_icon="🏢",
    layout="wide"
)

st.title("🏢 Company Profile")

companies = get_companies()

selected_company = st.selectbox(
    "Select Company",
    companies["id"],
    format_func=lambda x: companies.loc[
        companies["id"] == x,
        "company_name"
    ].iloc[0]
)

profile = get_company_dashboard(selected_company)

if profile.empty:
    st.error("Company not found.")
    st.stop()

company = profile.iloc[0]

st.header(company["company_name"])

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("ROE", company["roe_percentage"])

with col2:
    st.metric("ROCE", company["roce_percentage"])

with col3:
    st.metric("Book Value", company["book_value"])

st.divider()

left, right = st.columns([2, 1])

with left:
    st.subheader("About Company")
    st.write(company["about_company"])

with right:
    st.subheader("Company Information")

    st.write("**Sector**")
    st.write(company["broad_sector"])

    st.write("**Sub Sector**")
    st.write(company["sub_sector"])

    st.write("**Market Cap**")
    st.write(company["market_cap_category"])

    st.write("**Face Value**")
    st.write(company["face_value"])

    st.write("**Website**")
    st.write(company["website"])