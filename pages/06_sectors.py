import streamlit as st
import plotly.express as px

from src.dashboard.utils.db import (
    get_sector_analysis_data,
)
st.set_page_config(
    page_title="Sector Analysis",
    page_icon="🏭",
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

<h1>🏭 Sector Analysis Dashboard</h1>

<p>
 Compare companies across sectors using Revenue,
Return on Equity and Market Capitalization.
</p>

</div>
""", unsafe_allow_html=True)

df = get_sector_analysis_data()

if df.empty:
    st.error("No sector data available.")
    st.stop()

st.success(f"{len(df)} companies loaded successfully.")

# -------------------------------
# Sector Filter
# -------------------------------

sector_list = sorted(df["broad_sector"].dropna().unique())

selected_sector = st.selectbox(
    "Select Sector",
    ["All"] + sector_list,
    index=0,
)

if selected_sector != "All":
    chart_df = df[df["broad_sector"] == selected_sector]
else:
    chart_df = df.copy()

# Remove missing values
chart_df = chart_df.dropna(
    subset=[
        "sales",
        "return_on_equity_pct",
        "market_cap_crore",
    ]
)

# -------------------------------
# Bubble Chart
# -------------------------------

chart_df = chart_df[
    chart_df["return_on_equity_pct"].between(-50, 100)
]

fig = px.scatter(
    chart_df,
    x="sales",
    y="return_on_equity_pct",
    size="market_cap_crore",
    color="sub_sector",
    hover_name="company_name",
    size_max=55,
    title="Revenue vs ROE by Sector",
)

fig.update_layout(height=650)

st.plotly_chart(fig, use_container_width=True)


# -----------------------------------
# KPI Cards
# -----------------------------------

kpi_df = chart_df.copy()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Companies",
        len(kpi_df)
    )

with col2:
    st.metric(
        "Avg ROE (%)",
        f"{kpi_df['return_on_equity_pct'].mean():.2f}"
    )

with col3:
    st.metric(
        "Total Revenue",
        f"₹ {kpi_df['sales'].sum():,.0f} Cr"
    )

with col4:
    st.metric(
        "Market Cap",
        f"₹ {kpi_df['market_cap_crore'].sum():,.2f} Cr"
    )

st.divider()

# -----------------------------------
# Sector Median KPI Chart
# -----------------------------------

st.subheader("📈 Sector Median ROE")

median_df = (
    chart_df
    .groupby("broad_sector", as_index=False)
    .agg(
        Median_ROE=("return_on_equity_pct", "median")
    )
)

median_fig = px.bar(
    median_df,
    x="broad_sector",
    y="Median_ROE",
    color="Median_ROE",
    text="Median_ROE",
    title="Median Return on Equity by Sector",
)

median_fig.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside",
)

median_fig.update_layout(
    height=500,
    xaxis_title="Sector",
    yaxis_title="Median ROE (%)",
)

st.plotly_chart(
    median_fig,
    use_container_width=True,
)

st.divider()

# -----------------------------------
# Sector Summary Table
# -----------------------------------

st.subheader("📊 Sector Summary")

summary_df = (
    chart_df
    .groupby("broad_sector", as_index=False)
    .agg(
        Companies=("company_name", "count"),
        Avg_ROE=("return_on_equity_pct", "mean"),
        Total_Revenue=("sales", "sum"),
        Total_Market_Cap=("market_cap_crore", "sum"),
    )
)

summary_df["Avg_ROE"] = summary_df["Avg_ROE"].round(2)

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    label="📥 Download Sector Summary",
    data=summary_df.to_csv(index=False).encode("utf-8"),
    file_name="sector_summary.csv",
    mime="text/csv",
)
