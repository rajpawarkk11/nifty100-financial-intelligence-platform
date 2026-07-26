import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_companies,
    get_cash_flow,
    get_financial_ratios,
    get_all_financial_ratios,
)

st.set_page_config(
    page_title="Capital Allocation",
    page_icon="💰",
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

<h1>💰 Capital Allocation Dashboard</h1>

<p>
Analyze how companies allocate capital through
CapEx, Free Cash Flow, Debt and Shareholder Returns.
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


# -----------------------------------
# Load Data
# -----------------------------------

cash_df = get_cash_flow(company_id)
ratio_df = get_financial_ratios(company_id)

if cash_df.empty or ratio_df.empty:
    st.warning("No financial data available.")
    st.stop()

# Sort by year
cash_df = cash_df.sort_values("year")
ratio_df = ratio_df.sort_values("year")

latest = ratio_df.iloc[-1]

# -----------------------------------
# KPI Cards
# -----------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Free Cash Flow",
        f"₹ {latest['free_cash_flow_cr']:,.2f} Cr"
    )

with col2:
    st.metric(
        "CapEx",
        f"₹ {latest['capex_cr']:,.2f} Cr"
    )

with col3:
    st.metric(
        "Total Debt",
        f"₹ {latest['total_debt_cr']:,.2f} Cr"
    )

with col4:
    st.metric(
        "Debt / Equity",
        f"{latest['debt_to_equity']:.2f}"
    )

st.divider()

# -----------------------------------
# Cash Flow Activities
# -----------------------------------

st.subheader("💵 Cash Flow Activities")

cash_fig = px.bar(
    cash_df,
    x="year",
    y=[
        "operating_activity",
        "investing_activity",
        "financing_activity",
    ],
    barmode="group",
    title="Operating vs Investing vs Financing Cash Flow",
)

cash_fig.update_layout(height=550)

st.plotly_chart(
    cash_fig,
    use_container_width=True,
)


# -----------------------------------
# Free Cash Flow Trend
# -----------------------------------

st.subheader("📈 Free Cash Flow Trend")

fcf_fig = go.Figure()

fcf_fig.add_trace(
    go.Scatter(
        x=ratio_df["year"],
        y=ratio_df["free_cash_flow_cr"],
        mode="lines+markers",
        name="Free Cash Flow",
    )
)

fcf_fig.update_layout(height=500)

st.plotly_chart(
    fcf_fig,
    use_container_width=True,
)

# ==========================================
# Capital Allocation Pattern Map
# ==========================================

st.divider()
st.subheader("🌳 Capital Allocation Pattern Map")

treemap_df = get_all_financial_ratios().copy()

# Pattern Classification
def classify_pattern(row):

    fcf = row["free_cash_flow_cr"]
    capex = row["capex_cr"]
    debt = row["total_debt_cr"]
    de = row["debt_to_equity"]

    if fcf > 0 and de < 0.5:
        return "Cash Rich"

    elif fcf > capex:
        return "High Free Cash Flow"

    elif capex > fcf and capex > 0:
        return "Growth Investment"

    elif de > 2:
        return "Highly Leveraged"

    elif debt > 10000:
        return "Debt Heavy"

    elif fcf < 0:
        return "Negative Cash Flow"

    elif capex == 0:
        return "Asset Light"

    else:
        return "Balanced"

treemap_df["Pattern"] = treemap_df.apply(
    classify_pattern,
    axis=1
)

treemap_df["TreeSize"] = (
    treemap_df["free_cash_flow_cr"]
    .abs()
    .replace(0, 1)
)

treemap = px.treemap(
    treemap_df,
    path=["Pattern", "company_name"],
    values="TreeSize",
    color="free_cash_flow_cr",
    title="Capital Allocation Patterns",
)
treemap.update_layout(
    height=650,
)

st.plotly_chart(
    treemap,
    use_container_width=True,
)

st.subheader("📋 Companies by Pattern")

selected_pattern = st.selectbox(
    "Choose Pattern",
    sorted(treemap_df["Pattern"].unique())
)

company_table = (
    treemap_df[
        treemap_df["Pattern"] == selected_pattern
    ][[
        "company_name",
        "Pattern",
        "free_cash_flow_cr",
        "capex_cr",
        "total_debt_cr",
        "debt_to_equity",
    ]]
    .drop_duplicates(subset="company_name")
)

st.dataframe(
    company_table,
    use_container_width=True,
    hide_index=True,
)

# -----------------------------------
# Total Debt Trend
# -----------------------------------

st.subheader("🏦 Total Debt Trend")

debt_fig = px.line(
    ratio_df,
    x="year",
    y="total_debt_cr",
    markers=True,
    title="Total Debt Over Time",
)

debt_fig.update_layout(height=450)

st.plotly_chart(
    debt_fig,
    use_container_width=True,
)

# -----------------------------------
# Dividend Payout
# -----------------------------------

st.subheader("💰 Dividend Payout Trend")

dividend_df = ratio_df[
    ratio_df["dividend_payout_ratio_pct"].fillna(0) != 0
]

if dividend_df.empty:
    st.info("Dividend payout data is not available for this company.")
else:

    dividend_fig = px.bar(
        dividend_df,
        x="year",
        y="dividend_payout_ratio_pct",
        title="Dividend Payout Ratio",
    )

    dividend_fig.update_layout(height=450)

    st.plotly_chart(
        dividend_fig,
        use_container_width=True,
    )


