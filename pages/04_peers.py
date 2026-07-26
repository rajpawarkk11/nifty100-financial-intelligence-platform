import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_peer_groups,
    get_peer_comparison,
)

st.set_page_config(
    page_title="Peer Comparison",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------

st.markdown(
    """
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

    .card{
        background:#1E293B;
        padding:24px;
        border-radius:18px;
        border:1px solid #334155;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<div class="hero">

<h1>👥 Peer Comparison Dashboard</h1>

<p>
Benchmark Nifty 100 companies against their industry peers using key financial ratios,
        profitability, growth, leverage, cash flow, and overall quality metrics.
</p>

</div>
""", unsafe_allow_html=True)

groups = get_peer_groups()

if groups.empty:
    st.warning("No peer groups available.")
    st.stop()

group = st.selectbox(
    "Select Peer Group",
    groups["peer_group_name"]
)

peer_df = get_peer_comparison(group)

if peer_df.empty:
    st.warning("No companies found.")
    st.stop()

company = st.selectbox(
    "Benchmark Company",
    peer_df["company_name"]
)

metrics = [
    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "free_cash_flow_cr",
    "composite_quality_score",
]

peer_avg = peer_df[metrics].mean(numeric_only=True)

company_row = peer_df[
    peer_df["company_name"] == company
].iloc[0]

# ----------------------------------------
# Normalize metrics to 0–100
# ----------------------------------------

normalized_company = []
normalized_average = []

for metric in metrics:

    max_value = peer_df[metric].max()

    if pd.isna(max_value) or max_value == 0:
        normalized_company.append(0)
        normalized_average.append(0)
        continue

    company_val = company_row[metric]
    avg_val = peer_avg[metric]

    company_val = 0 if pd.isna(company_val) else company_val
    avg_val = 0 if pd.isna(avg_val) else avg_val

    normalized_company.append(
        (company_val / max_value) * 100
    )

    normalized_average.append(
        (avg_val / max_value) * 100
    )

company_values = normalized_company
avg_values = normalized_average

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=company_values,
        theta=[
            "ROE",
            "OPM",
            "Debt",
            "ICR",
            "Revenue CAGR",
            "PAT CAGR",
            "FCF",
            "Quality",
        ],
        fill="toself",
        name=company,
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=avg_values,
        theta=[
            "ROE",
            "OPM",
            "Debt",
            "ICR",
            "Revenue CAGR",
            "PAT CAGR",
            "FCF",
            "Quality",
        ],
        fill="toself",
        name="Peer Average",
    )
)

fig.update_layout(

    title="Company vs Peer Average",

    height=650,

    polar=dict(

        radialaxis=dict(

            visible=True,

            range=[0,100],

            tickfont=dict(size=10)

        )

    ),

    legend=dict(
        orientation="h",
        y=1.1
    )

)

st.plotly_chart(
    fig,
    use_container_width=True,
)

st.markdown("---")

table = peer_df.copy()

table["Benchmark"] = table["company_name"].apply(
    lambda x: "⭐" if x == company else ""
)

table = table[
    [
        "Benchmark",
        "company_name",
        "return_on_equity_pct",
        "operating_profit_margin_pct",
        "debt_to_equity",
        "interest_coverage",
        "revenue_cagr_5yr",
        "pat_cagr_5yr",
        "free_cash_flow_cr",
        "composite_quality_score",
    ]
]

table.columns = [
    "",
    "Company",
    "ROE %",
    "OPM %",
    "Debt / Equity",
    "ICR",
    "Revenue CAGR (5Y)",
    "PAT CAGR (5Y)",
    "Free Cash Flow (Cr)",
    "Quality Score",
]

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True,
)