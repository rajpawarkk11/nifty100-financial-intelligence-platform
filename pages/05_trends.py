import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_companies,
    get_financial_ratios,
    get_profit_loss,
    get_cash_flow,
)

st.set_page_config(
    page_title="Trend Analysis",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>

.block-container{
    padding-top:1.2rem;
}

.metric-card{
    background:white;
    border-radius:14px;
    padding:18px;
    box-shadow:0 3px 10px rgba(0,0,0,.08);
    text-align:center;
}

.metric-title{
    color:#6b7280;
    font-size:14px;
}

.metric-value{
    font-size:28px;
    font-weight:700;
    color:#0f172a;
}

.hero{
    background:linear-gradient(135deg,#2563eb,#4f46e5);
    padding:28px;
    border-radius:18px;
    color:white;
    margin-bottom:20px;
}

div[data-testid="stMetric"]{
    background:#1f2937;
    border:1px solid #374151;
    border-radius:14px;
    padding:16px;
    box-shadow:0 4px 12px rgba(0,0,0,0.35);
}

div[data-testid="stMetricLabel"]{
    color:#9CA3AF !important;
    font-weight:600;
}

div[data-testid="stMetricValue"]{
    color:#FFFFFF !important;
    font-size:32px !important;
    font-weight:700;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>📈 Trend Analysis Dashboard</h1>
<p>
Analyze long-term financial trends, compare multiple business metrics,
evaluate YoY growth, and download historical data.
</p>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# Load Companies
# -----------------------------

companies = get_companies()

if companies.empty:
    st.error("No companies found.")
    st.stop()

company_name = st.selectbox(
    "🔍 Select Company",
    companies["company_name"].tolist()
)

company_id = companies.loc[
    companies["company_name"] == company_name,
    "id"
].iloc[0]


# -----------------------------
# Load Tables
# -----------------------------

ratios = get_financial_ratios(company_id)
pl = get_profit_loss(company_id)
cf = get_cash_flow(company_id)

if pl.empty:
    st.warning("No historical data available.")
    st.stop()


# -----------------------------
# Keep Required Columns
# -----------------------------

pl = pl[
    [
        "year",
        "sales",
        "operating_profit",
        "net_profit",
        "eps",
        "opm_percentage",
    ]
].copy()

ratios = ratios[
    [
        "year",
        "return_on_equity_pct",
        "net_profit_margin_pct",
        "debt_to_equity",
        "interest_coverage",
        "cash_from_operations_cr",
        "free_cash_flow_cr",
        "revenue_cagr_3yr",
        "revenue_cagr_5yr",
        "pat_cagr_3yr",
        "pat_cagr_5yr",
    ]
].copy()

cf = cf[
    [
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity",
        "net_cash_flow",
    ]
].copy()


# -----------------------------
# Remove Duplicate Years
# -----------------------------

pl = (
    pl.sort_values("year")
      .drop_duplicates(subset="year", keep="last")
)

ratios = (
    ratios.sort_values("year")
          .drop_duplicates(subset="year", keep="last")
)

cf = (
    cf.sort_values("year")
      .drop_duplicates(subset="year", keep="last")
)


# -----------------------------
# Merge Tables
# -----------------------------

trend_df = (
    pl.merge(
        ratios,
        on="year",
        how="outer"
    )
    .merge(
        cf,
        on="year",
        how="outer"
    )
)

trend_df = trend_df[
    trend_df["year"] != "TTM"
].copy()

trend_df = trend_df.sort_values("year")

trend_df.reset_index(
    drop=True,
    inplace=True,
)


# -----------------------------
# Numeric Conversion
# -----------------------------

for col in trend_df.columns:

    if col != "year":

        trend_df[col] = pd.to_numeric(
            trend_df[col],
            errors="coerce"
        )


trend_df = trend_df.fillna(0)


# -----------------------------
# Available Metrics
# -----------------------------

metric_map = {
    "Revenue":"sales",
    "Operating Profit":"operating_profit",
    "Net Profit":"net_profit",
    "EPS":"eps",
    "Operating Margin %":"opm_percentage",
    "Net Profit Margin %":"net_profit_margin_pct",
    "ROE %":"return_on_equity_pct",
    "Debt To Equity":"debt_to_equity",
    "Interest Coverage":"interest_coverage",
    "Cash From Operations":"cash_from_operations_cr",
    "Free Cash Flow":"free_cash_flow_cr",
    "Revenue CAGR 3Y":"revenue_cagr_3yr",
    "Revenue CAGR 5Y":"revenue_cagr_5yr",
    "PAT CAGR 3Y":"pat_cagr_3yr",
    "PAT CAGR 5Y":"pat_cagr_5yr",
    "Operating Cash Flow":"operating_activity",
    "Investing Cash Flow":"investing_activity",
    "Financing Cash Flow":"financing_activity",
    "Net Cash Flow":"net_cash_flow",
}

selected_metrics = st.multiselect(
    "📊 Select up to 3 Metrics",
    list(metric_map.keys()),
    default=[
        "Revenue",
        "Net Profit",
    ],
    max_selections=3,
)

# ============================================================
# Trend Chart
# ============================================================

st.divider()

st.subheader("📈 Financial Trend Analysis")

if len(selected_metrics) == 0:
    st.info("Please select at least one metric.")
    st.stop()

fig = go.Figure()

for metric in selected_metrics:

    column = metric_map[metric]

    fig.add_trace(
        go.Scatter(
            x=trend_df["year"],
            y=trend_df[column],
            mode="lines+markers",
            name=metric,
            line=dict(width=3),
            marker=dict(size=8),
            hovertemplate=
                "<b>%{x}</b><br>"
                + metric
                + ": %{y:,.2f}<extra></extra>",
        )
    )

fig.update_layout(
    height=600,
    template="plotly_white",
    hovermode="closest",
    legend=dict(
        orientation="h",
        y=1.08,
        x=0,
    ),
    margin=dict(
        l=20,
        r=20,
        t=40,
        b=20,
    ),
    xaxis_title="Financial Year",
    yaxis_title="Value",
)
fig.update_xaxes(
    showgrid=False
)

fig.update_yaxes(
    gridcolor="rgba(180,180,180,0.15)"
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# ============================================================
# YoY Growth
# ============================================================

st.divider()

st.subheader("📊 Year-on-Year Growth")

growth_metric = st.selectbox(
    "Metric",
    list(metric_map.keys()),
    index=0,
)

growth_column = metric_map[growth_metric]

growth_df = trend_df[
    ["year", growth_column]
].copy()

growth_df.rename(
    columns={
        growth_column: "Value"
    },
    inplace=True,
)

growth_df["Previous"] = growth_df["Value"].shift(1)

growth_df["YoY Growth %"] = (
    (
        growth_df["Value"] -
        growth_df["Previous"]
    )
    /
    growth_df["Previous"].replace(0, pd.NA)
) * 100

growth_df["YoY Growth %"] = (
    growth_df["YoY Growth %"]
    .replace([float("inf"), float("-inf")], pd.NA)
)

growth_df["YoY Growth %"] = pd.to_numeric(
    growth_df["YoY Growth %"],
    errors="coerce"
)

growth_df["YoY Growth %"] = growth_df["YoY Growth %"].round(2)

growth_df = growth_df.dropna(
    subset=["YoY Growth %"]
)


fig_growth = px.bar(
    growth_df,
    x="year",
    y="YoY Growth %",
    text="YoY Growth %",
)

fig_growth.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
)

fig_growth.update_layout(
    template="plotly_white",
    height=500,
    xaxis_title="Year",
    yaxis_title="Growth %",
)

st.plotly_chart(
    fig_growth,
    use_container_width=True,
)


# ============================================================
# Helper: Latest Valid Value
# ============================================================

def latest_valid(column_name):

    data = trend_df.copy()

    data = data[data[column_name].notna()]
    data = data[data[column_name] != 0]

    if data.empty:
        return 0

    return data.iloc[-1][column_name]


# ============================================================
# Latest Performance Cards
# ============================================================

st.divider()

st.subheader("📌 Latest Performance")

latest = trend_df.sort_values("year").iloc[-1]

latest_revenue = latest_valid("sales")
latest_profit = latest_valid("net_profit")
latest_roe = latest_valid("return_on_equity_pct")
latest_margin = latest_valid("net_profit_margin_pct")
latest_de = latest_valid("debt_to_equity")
latest_ic = latest_valid("interest_coverage")
# --------------------------------------------------
# Helper: Latest Valid Value
# --------------------------------------------------

def latest_valid(column_name):

    data = trend_df.copy()

    data = data[
        data[column_name].notna()
    ]

    data = data[
        data[column_name] != 0
    ]

    if data.empty:
        return 0

    return data.iloc[-1][column_name]

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
    "Revenue",
    f"{latest_revenue:,.2f}"
)

with col2:

   st.metric(
    "Net Profit",
    f"{latest_profit:,.2f}"
)

with col3:

   st.metric(
    "Net Margin %",
    f"{latest_margin:.2f}%"
)

# ============================================================
# Trend Summary
# ============================================================

st.divider()

st.subheader("📋 Trend Summary")

summary = pd.DataFrame({
    "Metric": selected_metrics,
    "Latest Value": [
        latest[metric_map[m]]
        for m in selected_metrics
    ],
})

summary["Latest Value"] = (
    summary["Latest Value"]
    .round(2)
)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True,
)

# ============================================================
# Detailed Statistics
# ============================================================

st.divider()

st.subheader("📊 Metric Statistics")

stats_rows = []

for metric in selected_metrics:

    column = metric_map[metric]

    series = trend_df[column].dropna()

    if series.empty:
        continue

    max_idx = series.idxmax()
    min_idx = series.idxmin()

    stats_rows.append({
        "Metric": metric,
        "Average": round(series.mean(), 2),
        "Maximum": round(series.max(), 2),
        "Max Year": trend_df.loc[max_idx, "year"],
        "Minimum": round(series.min(), 2),
        "Min Year": trend_df.loc[min_idx, "year"],
        "Latest": round(series.iloc[-1], 2),
    })

stats_df = pd.DataFrame(stats_rows)

st.dataframe(
    stats_df,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# Historical Financial Data
# ============================================================

st.divider()

st.subheader("📄 Historical Financial Data")

display_df = trend_df.copy()

display_df = display_df.rename(
    columns={
        "year": "Year",
        "sales": "Revenue",
        "operating_profit": "Operating Profit",
        "net_profit": "Net Profit",
        "eps": "EPS",
        "opm_percentage": "OPM %",
        "net_profit_margin_pct": "Net Margin %",
        "return_on_equity_pct": "ROE %",
        "debt_to_equity": "Debt / Equity",
        "interest_coverage": "Interest Coverage",
        "cash_from_operations_cr": "Cash From Operations",
        "free_cash_flow_cr": "Free Cash Flow",
        "operating_activity": "Operating Cash Flow",
        "investing_activity": "Investing Cash Flow",
        "financing_activity": "Financing Cash Flow",
        "net_cash_flow": "Net Cash Flow",
        "revenue_cagr_3yr": "Revenue CAGR 3Y",
        "revenue_cagr_5yr": "Revenue CAGR 5Y",
        "pat_cagr_3yr": "PAT CAGR 3Y",
        "pat_cagr_5yr": "PAT CAGR 5Y",
    }
)

numeric_cols = display_df.select_dtypes(include="number").columns

display_df[numeric_cols] = (
    display_df[numeric_cols]
    .round(2)
)

st.dataframe(
    display_df,
    use_container_width=True,
    height=450,
)


# ============================================================
# Download CSV
# ============================================================

csv = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Trend Data (CSV)",
    data=csv,
    file_name=f"{company_name}_trend_analysis.csv",
    mime="text/csv",
)


# ============================================================
# Key Insights
# ============================================================

st.divider()

st.subheader("💡 Quick Insights")

latest = trend_df.iloc[-1]
previous = trend_df.iloc[-2] if len(trend_df) > 1 else latest

insights = []

if latest["sales"] > previous["sales"]:
    insights.append("✅ Revenue increased compared to the previous year.")
else:
    insights.append("⚠ Revenue decreased compared to the previous year.")

if latest["net_profit"] > previous["net_profit"]:
    insights.append("✅ Net Profit improved over the previous year.")
else:
    insights.append("⚠ Net Profit declined over the previous year.")

if latest["return_on_equity_pct"] >= 15:
    insights.append("✅ Strong Return on Equity indicates efficient capital utilization.")
else:
    insights.append("⚠ ROE is below 15%, indicating room for improvement.")

if latest["debt_to_equity"] <= 1:
    insights.append("✅ Debt level appears healthy.")
else:
    insights.append("⚠ Company is relatively highly leveraged.")

if latest["interest_coverage"] >= 3:
    insights.append("✅ Interest coverage is comfortable.")
else:
    insights.append("⚠ Interest coverage is relatively weak.")

for item in insights:
    st.write(item)


# ============================================================
# Footer
# ============================================================

st.divider()

st.caption(
    "📈 Trend Analysis Dashboard | "
    "NIFTY 100 Financial Intelligence Platform | "
)