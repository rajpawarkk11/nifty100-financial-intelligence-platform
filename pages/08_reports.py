import streamlit as st
import requests

from src.dashboard.utils.db import (
    get_companies,
)

st.set_page_config(
    page_title="Annual Reports",
    page_icon="📄",
    layout="wide",
)

st.markdown("""
<style>

.block-container{
    max-width:1700px;
    padding-top:1rem;
}

.hero{
background:linear-gradient(135deg,#172554,#1E3A8A,#1E293B);
padding:25px;
border-radius:20px;
color:white;
margin-bottom:25px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">

<h1>📄 Annual Reports Dashboard</h1>

<p>
Explore annual financial performance,
key metrics and downloadable company reports.
</p>

</div>
""", unsafe_allow_html=True)

companies = get_companies()

company_name = st.selectbox(
    "Select Company",
    companies["company_name"]
)

company_id = companies.loc[
    companies["company_name"] == company_name,
    "id"
].iloc[0]


import plotly.express as px

from src.dashboard.utils.db import (
    get_profit_loss,
    get_financial_ratios,
    get_annual_reports,
)

# -----------------------------------
# Load Data
# -----------------------------------

pl_df = get_profit_loss(company_id)
ratio_df = get_financial_ratios(company_id)

reports_df = get_annual_reports(company_id)


if pl_df.empty or ratio_df.empty:
    st.warning("No report data available.")
    st.stop()

pl_df = pl_df.sort_values("year")
pl_df = (
    pl_df
    .drop_duplicates(subset=["year"], keep="last")
    .reset_index(drop=True)
)
ratio_df = ratio_df.sort_values("year")

latest_pl = pl_df.iloc[-1]
latest_ratio = ratio_df.iloc[-1]

# -----------------------------------
# KPI Cards
# -----------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Revenue",
        f"₹ {latest_pl['sales']:,.2f} Cr"
    )

with col2:
    st.metric(
        "Net Profit",
        f"₹ {latest_pl['net_profit']:,.2f} Cr"
    )

with col3:
    st.metric(
        "EPS",
        f"{latest_ratio['earnings_per_share']:.2f}"
    )

with col4:
    st.metric(
        "ROE",
        f"{latest_ratio['return_on_equity_pct']:.2f}%"
    )

st.divider()

# -----------------------------------
# Financial Summary
# -----------------------------------

st.subheader("📊 Financial Summary")

summary = pl_df[
    [
        "year",
        "sales",
        "operating_profit",
        "net_profit",
    ]
]

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True,
)

# -----------------------------------
# Revenue Trend
# -----------------------------------

st.subheader("📈 Revenue Trend")

fig = px.line(
    pl_df,
    x="year",
    y="sales",
    markers=True,
)

fig.update_layout(height=450)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# -----------------------------------
# Net Profit Trend
# -----------------------------------

st.subheader("💰 Net Profit Trend")

fig = px.bar(
    pl_df,
    x="year",
    y="net_profit",
)

fig.update_layout(height=450)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# -----------------------------------
# Annual Reports
# -----------------------------------

st.divider()

st.subheader("📄 Annual Reports")

if reports_df.empty:

    st.warning("No annual reports available.")

else:

    reports_df = reports_df.sort_values(
        "year",
        ascending=False,
    )

    for _, row in reports_df.iterrows():

        year = row["year"]
        url = row["annual_report"]

        col1, col2 = st.columns([1, 4])

        with col1:

            st.write(f"**{year}**")

        with col2:

            if (
                url is None
                or str(url).strip() == ""
                or str(url).lower() == "null"
            ):

                st.error("🔴 Report Unavailable")

            else:

                try:

                    response = requests.head(
                        url,
                        allow_redirects=True,
                        timeout=5,
                    )

                    if response.status_code == 404:

                        st.error("🔴 Report Unavailable")

                    else:

                        st.markdown(
                            f"[📥 Open Annual Report]({url})"
                        )

                except Exception:

                    st.error("🔴 Report Unavailable")


# -----------------------------------
# CSV Download
# -----------------------------------

st.download_button(
    "📥 Download Financial Summary",
    summary.to_csv(index=False).encode("utf-8"),
    "financial_summary.csv",
    "text/csv",
)