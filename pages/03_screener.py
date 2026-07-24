import streamlit as st
import pandas as pd

from src.dashboard.utils.db import get_screener_data

st.set_page_config(
    page_title="Stock Screener",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Nifty 100 Stock Screener")
st.caption("Filter companies using financial ratios and quality metrics.")

# -----------------------------------------------------
# Load Data
# -----------------------------------------------------

df = get_screener_data().copy()

st.dataframe(
    df.sort_values(
        "return_on_equity_pct",
        ascending=False
    ).head(10)
)
st.subheader("Highest Quality Score")

st.dataframe(
    df.sort_values(
        "composite_quality_score",
        ascending=False
    ).head(10)
)

if df.empty:
    st.warning("No screener data available.")
    st.stop()

# -----------------------------------------------------
# Clean Data
# -----------------------------------------------------

numeric_columns = [
    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "free_cash_flow_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "composite_quality_score",
    "market_cap_crore",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# -----------------------------------------------------
# Sidebar Filters
# -----------------------------------------------------

st.sidebar.header("Filters")

# Sector
sector_options = sorted(df["broad_sector"].dropna().unique())

selected_sector = st.sidebar.multiselect(
    "Sector",
    sector_options,
    default=sector_options
)

# Market Cap Category
cap_options = sorted(df["market_cap_category"].dropna().unique())

selected_cap = st.sidebar.multiselect(
    "Market Cap Category",
        cap_options,
        default=cap_options
    )
company_options = sorted(
    df["company_name"].dropna().unique()
)

selected_company = st.sidebar.multiselect(
    "Company",
    company_options
)

# ROE
min_roe = st.sidebar.slider(
    "Minimum ROE (%)",
    0,
    50,
    0
)

# Debt
max_debt = st.sidebar.slider(
    "Maximum Debt / Equity",
    0.0,
    10.0,
    10.0,
    0.1
)

# PE
max_pe = st.sidebar.slider(
    "Maximum PE",
    0,
    150,
    150
)

# PB
max_pb = st.sidebar.slider(
    "Maximum PB",
    0,
    30,
    30
)

# Dividend Yield
min_dividend = st.sidebar.slider(
    "Minimum Dividend Yield (%)",
    0.0,
    10.0,
    0.0,
    0.1
)

# Interest Coverage
min_interest = st.sidebar.slider(
    "Minimum Interest Coverage",
    0,
    100,
    0
)

# Free Cash Flow
min_fcf = st.sidebar.number_input(
    "Minimum Free Cash Flow (Cr)",
    value=0.0,
    step=100.0
)

# Revenue CAGR
min_rev = st.sidebar.slider(
    "Minimum Revenue CAGR 5Y",
    -20,
    50,
    -20
)

# PAT CAGR
min_pat = st.sidebar.slider(
    "Minimum PAT CAGR 5Y",
    -20,
    50,
    -20
)

# Quality
min_quality = st.sidebar.slider(
    "Minimum Quality Score",
    0,
    100,
    0
)

# -----------------------------------------------------
# Presets
# -----------------------------------------------------

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Screens")
st.sidebar.markdown("---")

top_n = st.sidebar.selectbox(
    "Show Top",
    [25, 50, 75, 100],
    index=3
)

preset = st.sidebar.selectbox(
    "Choose Preset",
    [
        "Custom",
        "High Quality",
        "Growth",
        "Value",
        "Dividend",
        "Low Debt",
        "High ROE",
    ]
)

filtered = df.copy()

#if selected_company:

 #   filtered = filtered[
  #      filtered["company_name"].isin(selected_company)
   # ]

# -----------------------------------------------------
# Base Filters
# -----------------------------------------------------

filtered = filtered[
    filtered["broad_sector"].isin(selected_sector)
]

filtered = filtered[
    filtered["market_cap_category"].isin(selected_cap)
]

filtered = filtered[
    filtered["return_on_equity_pct"].fillna(0) >= min_roe
]

filtered = filtered[
    filtered["debt_to_equity"].fillna(999) <= max_debt
]

filtered = filtered[
    filtered["revenue_cagr_5yr"].fillna(-999) >= min_rev
]

filtered = filtered[
    filtered["pat_cagr_5yr"].fillna(-999) >= min_pat
]

filtered = filtered[
    filtered["composite_quality_score"].fillna(0) >= min_quality
]

filtered = filtered[
    filtered["pe_ratio"].fillna(9999) <= max_pe
]

filtered = filtered[
    filtered["pb_ratio"].fillna(9999) <= max_pb
]

filtered = filtered[
    filtered["dividend_yield_pct"].fillna(0) >= min_dividend
]

filtered = filtered[
    filtered["interest_coverage"].fillna(0) >= min_interest
]

filtered = filtered[
    filtered["free_cash_flow_cr"].fillna(-999999) >= min_fcf
]
# -----------------------------------------------------
# Preset Logic
# -----------------------------------------------------

if preset == "High Quality":

    filtered = filtered[
        filtered["composite_quality_score"].fillna(0) >= 80
    ]

    filtered = filtered[
        filtered["return_on_equity_pct"].fillna(0) >= 15
    ]

    filtered = filtered[
        filtered["debt_to_equity"].fillna(999) <= 1
    ]

elif preset == "Growth":

    filtered = filtered[
        filtered["revenue_cagr_5yr"].fillna(-999) >= 15
    ]

    filtered = filtered[
        filtered["pat_cagr_5yr"].fillna(-999) >= 15
    ]

elif preset == "Value":

    filtered = filtered[
        filtered["pe_ratio"].fillna(9999) <= 20
    ]

    filtered = filtered[
        filtered["pb_ratio"].fillna(9999) <= 3
    ]

elif preset == "Dividend":

    filtered = filtered[
        filtered["dividend_yield_pct"].fillna(0) >= 2
    ]

elif preset == "Low Debt":

    filtered = filtered[
        filtered["debt_to_equity"].fillna(999) <= 0.5
    ]

elif preset == "High ROE":

    filtered = filtered[
        filtered["return_on_equity_pct"].fillna(0) >= 20
    ]

filtered = filtered.sort_values(
    by=[
        "composite_quality_score",
        "return_on_equity_pct",
        "revenue_cagr_5yr"
    ],
    ascending=False,
    na_position="last"
)

filtered = filtered[
    (filtered["return_on_equity_pct"] <= 100)
    | (filtered["return_on_equity_pct"].isna())
]

filtered = filtered[
    (filtered["composite_quality_score"] <= 100)
    | (filtered["composite_quality_score"].isna())
]

filtered = filtered.head(top_n)

# -----------------------------------------------------
# KPI Cards
# -----------------------------------------------------

st.markdown("---")

if filtered.empty:
    st.warning("No companies match the selected filters.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Companies", len(filtered))

with col2:
    if filtered.empty:
        st.metric("Average ROE", "N/A")
    else:
        st.metric(
            "Average ROE",
            f"{filtered['return_on_equity_pct'].dropna().mean():.2f}%"
        )

with col3:
    avg_pe = (
    filtered["pe_ratio"]
    .replace(0, pd.NA)
    .dropna()
    .mean()
)
    if pd.isna(avg_pe):
        st.metric("Average PE", "N/A")
    else:
        st.metric("Average PE", f"{avg_pe:.2f}")

with col4:
    if filtered.empty:
        st.metric("Quality Score", "N/A")
    else:
        st.metric(
            "Quality Score",
           f"{filtered['composite_quality_score'].dropna().mean():.1f}"
        )

st.markdown("---")

st.markdown("### Screener Summary")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Highest ROE",
        f"{filtered['return_on_equity_pct'].max():.2f}%"
    )

with c2:
    st.metric(
        "Highest Quality Score",
        f"{filtered['composite_quality_score'].max():.1f}"
    )

with c3:
    st.metric(
        "Average Dividend Yield",
        f"{filtered['dividend_yield_pct'].fillna(0).mean():.2f}%"
    )

# -----------------------------------------------------
# Display Table
# -----------------------------------------------------

display_columns = [
    "id",
    "company_name",
    "broad_sector",
    "market_cap_category",
    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "interest_coverage",
    "free_cash_flow_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "composite_quality_score",
    "market_cap_crore",
    "pe_ratio",
    "pb_ratio",
    "dividend_yield_pct",
]

display_df = filtered[display_columns].copy()

display_df = display_df.round(
    {
        "return_on_equity_pct": 2,
        "operating_profit_margin_pct": 2,
        "debt_to_equity": 2,
        "interest_coverage": 2,
        "free_cash_flow_cr": 2,
        "revenue_cagr_5yr": 2,
        "pat_cagr_5yr": 2,
        "composite_quality_score": 1,
        "market_cap_crore": 2,
        "pe_ratio": 2,
        "pb_ratio": 2,
        "dividend_yield_pct": 2,
    }
)

display_df = display_df.rename(
    columns={
        "id": "Ticker",
        "company_name": "Company",
        "broad_sector": "Sector",
        "market_cap_category": "Market Cap",
        "return_on_equity_pct": "ROE %",
        "operating_profit_margin_pct": "OPM %",
        "debt_to_equity": "Debt/Equity",
        "interest_coverage": "Interest Coverage",
        "free_cash_flow_cr": "Free Cash Flow",
        "revenue_cagr_5yr": "Revenue CAGR 5Y",
        "pat_cagr_5yr": "PAT CAGR 5Y",
        "composite_quality_score": "Quality Score",
        "market_cap_crore": "Market Cap (Cr)",
        "pe_ratio": "PE",
        "pb_ratio": "PB",
        "dividend_yield_pct": "Dividend Yield %",
    }
)

st.subheader(f"Results ({len(display_df)})")

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=650
)

# -----------------------------------------------------
# Download CSV
# -----------------------------------------------------

csv = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Results as CSV",
    data=csv,
   file_name="nifty100_stock_screener.csv",
    mime="text/csv",
)

# -----------------------------------------------------
# Footer
# -----------------------------------------------------

st.markdown("---")
st.caption(
    "Financial Intelligence Platform • Nifty 100 Screener • "
    "Filter by Quality, Growth, Value, Dividend and Financial Ratios"
)