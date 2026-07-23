import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_companies,
    get_company_dashboard,
    get_financial_ratios,
    get_profit_loss,
    get_cash_flow,
)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Company Profile",
    page_icon="🏢",
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

# ---------------------------------------------------
# HERO
# ---------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🏢 Company Profile</h1>
        <p>
        Search any Nifty100 company and explore its financial
        performance, ratios and business profile.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------
# LOAD COMPANIES
# ---------------------------------------------------

companies = get_companies()

if companies.empty:
    st.error("Company master data not found.")
    st.stop()

company_name = st.selectbox(
    "🔍 Select Company",
    companies["company_name"].tolist(),
)

company_id = companies.loc[
    companies["company_name"] == company_name,
    "id",
].iloc[0]

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

profile_df = get_company_dashboard(company_id)
ratios = get_financial_ratios(company_id)
pl = get_profit_loss(company_id)
cf = get_cash_flow(company_id)

if profile_df.empty:
    st.error("Company profile not available.")
    st.stop()

profile = profile_df.iloc[0]

# ---------------------------------------------------
# COMPANY CARD
# ---------------------------------------------------

st.markdown("<br>", unsafe_allow_html=True)

left, right = st.columns([1.5, 1])

with left:
    st.markdown(
        f"""
        <div class="card">
            <h2>🏢 {profile['company_name']}</h2>
            <p>{profile['about_company']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:

    st.markdown(
        f"""
        <div class="card">

        <h4>Sector</h4>
        <p>{profile['broad_sector']}</p>

        <hr>

        <h4>Sub Sector</h4>
        <p>{profile['sub_sector']}</p>

        <hr>

        <h4>Market Cap Category</h4>
        <p>{profile['market_cap_category']}</p>

        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

st.markdown("---")
st.subheader("📊 Financial Highlights")

if ratios.empty:
    st.warning("Financial ratios not available.")
    st.stop()

latest = ratios.iloc[-1]

latest_cf = cf.iloc[-1] if not cf.empty else None

roe = latest.get("return_on_equity_pct", None)
roce = profile.get("roce_percentage", None)
npm = latest.get("net_profit_margin_pct", None)
de = latest.get("debt_to_equity", None)
rev_cagr = latest.get("revenue_cagr_5yr", None)

fcf = None
if latest_cf is not None and "free_cash_flow_cr" in latest_cf.index:
    fcf = latest_cf["free_cash_flow_cr"]

c1, c2, c3, c4, c5, c6 = st.columns(6)

def fmt(value, suffix=""):
    if isinstance(value, (int, float)):
        return f"{value:.2f}{suffix}"
    return "N/A"

with c1:
    st.metric("📈 ROE", fmt(roe, "%"))

with c2:
    st.metric("🏦 ROCE", fmt(roce, "%"))

with c3:
    st.metric("💰 Net Profit Margin", fmt(npm, "%"))

with c4:
    st.metric("⚖ Debt / Equity", fmt(de))

with c5:
    st.metric("📊 Revenue CAGR", fmt(rev_cagr, "%"))

with c6:
    if isinstance(fcf, (int, float)):
        st.metric("💵 Free Cash Flow", f"{fcf:.2f} Cr")
    else:
        st.metric("💵 Free Cash Flow", "N/A")


# ---------------------------------------------------
# REVENUE & NET PROFIT CHARTS
# ---------------------------------------------------

st.markdown("---")
st.subheader("📈 Revenue & Net Profit (10-Year Trend)")

if not pl.empty:

    chart_df = pl.copy()
    chart_df["year"] = chart_df["year"].astype(str)

    left_chart, right_chart = st.columns(2)

    # ---------------- Revenue Chart ----------------

    with left_chart:

        revenue_fig = go.Figure()

        revenue_fig.add_trace(
            go.Bar(
                x=chart_df["year"],
                y=chart_df["sales"],
                marker_color="#3B82F6",
                name="Revenue",
            )
        )

        revenue_fig.update_layout(
            template="plotly_dark",
            title="Revenue",
            height=420,
            margin=dict(l=20, r=20, t=50, b=20),
            hovermode="x unified",
        )

        st.plotly_chart(
            revenue_fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "responsive": True,
            },
        )

    # ---------------- Net Profit Chart ----------------

    with right_chart:

        profit_fig = go.Figure()

        profit_fig.add_trace(
            go.Bar(
                x=chart_df["year"],
                y=chart_df["net_profit"],
                marker_color="#10B981",
                name="Net Profit",
            )
        )

        profit_fig.update_layout(
            template="plotly_dark",
            title="Net Profit",
            height=420,
            margin=dict(l=20, r=20, t=50, b=20),
            hovermode="x unified",
        )

        st.plotly_chart(
            profit_fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "responsive": True,
            },
        )

else:
    st.info("Profit & Loss data not available.")

# ---------------------------------------------------
# ROE TREND
# ---------------------------------------------------

st.markdown("---")
st.subheader("📉 ROE Trend")

if not ratios.empty:

    roe_fig = go.Figure()

    roe_fig.add_trace(
        go.Scatter(
            x=ratios["year"].astype(str),
            y=ratios["return_on_equity_pct"],
            mode="lines+markers",
            line=dict(color="#3B82F6", width=3),
            marker=dict(size=8),
            name="ROE",
        )
    )

    roe_fig.update_layout(
        template="plotly_dark",
        height=420,
        xaxis_title="Year",
        yaxis_title="ROE (%)",
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified",
    )

    st.plotly_chart(
        roe_fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
        },
    )
# ---------------------------------------------------
# OPERATING PROFIT MARGIN TREND
# ---------------------------------------------------

st.markdown("---")
st.subheader("📊 Operating Profit Margin Trend")

if not ratios.empty:

    opm_fig = go.Figure()

    opm_fig.add_trace(
        go.Scatter(
            x=ratios["year"].astype(str),
            y=ratios["operating_profit_margin_pct"],
            mode="lines+markers",
            line=dict(color="#F59E0B", width=3),
            marker=dict(size=8),
            name="OPM",
        )
    )

    opm_fig.update_layout(
        template="plotly_dark",
        height=420,
        xaxis_title="Year",
        yaxis_title="OPM (%)",
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified",
    )

    st.plotly_chart(
        opm_fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
        },
    )

# ---------------------------------------------------
# FINANCIAL SUMMARY
# ---------------------------------------------------

st.markdown("---")
st.subheader("📋 Financial Summary")

col1, col2, col3, col4 = st.columns(4)

face_value = profile.get("face_value")
book_value = profile.get("book_value")
eps = latest.get("earnings_per_share")
dividend = latest.get("dividend_payout_ratio_pct")

def metric_value(value, suffix=""):
    if isinstance(value, (int, float)):
        return f"{value:.2f}{suffix}"
    return "N/A"

with col1:
    st.metric("💵 Face Value", metric_value(face_value))

with col2:
    st.metric("📚 Book Value", metric_value(book_value))

with col3:
    st.metric("📈 EPS", metric_value(eps))

with col4:
    st.metric("🎯 Dividend Payout", metric_value(dividend, "%"))

# ---------------------------------------------------
# COMPANY LINKS
# ---------------------------------------------------

st.markdown("---")
st.subheader("🌐 Company Links")

c1, c2, c3 = st.columns(3)

website = profile.get("website")
nse = profile.get("nse_profile")
bse = profile.get("bse_profile")

with c1:
    if pd.notna(website) and str(website).strip():
        st.link_button(
    "🌍 Official Website",
    website,
    use_container_width=True,
)
    else:
        st.info("Website unavailable")

with c2:
    if pd.notna(nse) and str(nse).strip():
        st.link_button(
    "📈 NSE Profile", nse,
    use_container_width=True,
)
    else:
        st.info("NSE Profile unavailable")

with c3:
    if pd.notna(bse) and str(bse).strip():
       st.link_button(
    "🏦 BSE Profile", bse,
    use_container_width=True,
)
    else:
        st.info("BSE Profile unavailable")


