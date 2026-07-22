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

header_left, header_right = st.columns([1, 4])

with header_left:
    if company["company_logo"]:
        st.image(company["company_logo"], width=120)

with header_right:
    st.title(company["company_name"])

    st.caption(
        f"{company['broad_sector']} • {company['market_cap_category']}"
    )

    button_col1, button_col2, button_col3 = st.columns(3)

with button_col1:
        if company["website"]:
            st.link_button("🌐 Website", company["website"])

with button_col2:
        if company["nse_profile"]:
            st.link_button("📈 NSE Profile", company["nse_profile"])

with button_col3:
        if company["bse_profile"]:
            st.link_button("📊 BSE Profile", company["bse_profile"])

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