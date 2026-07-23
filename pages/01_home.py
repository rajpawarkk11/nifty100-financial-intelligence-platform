import streamlit as st
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder

from src.dashboard.utils.db import (
    get_home_summary,
    get_available_years,
    get_sector_breakdown,
    get_top_quality_companies,
)

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------

years = (
    get_available_years()["year"]
    .astype(int)
    .sort_values()
    .tolist()
)

# Show only 2019–2024
years = [year for year in years if 2019 <= year <= 2024]

selected_year = st.sidebar.selectbox(
    "📅 Financial Year",
    years,
    index=len(years) - 1,   # Default = 2024
    key="home_year_select"
)

summary = get_home_summary(str(selected_year))

sector_df = get_sector_breakdown()

top5 = get_top_quality_companies(str(selected_year))

# ----------------------------------------------------
# CSS
# ----------------------------------------------------

st.markdown("""
<style>

/* --------------------------
Main Layout
---------------------------*/

.block-container{
    max-width:1750px;
    padding-top:1rem;
    padding-left:2.2rem;
    padding-right:2.2rem;
    padding-bottom:2rem;
}

/* --------------------------
Sidebar
---------------------------*/

section[data-testid="stSidebar"]{
    background:#161B26;
    border-right:1px solid #2D3748;
}

section[data-testid="stSidebar"] *{
    color:white;
}

/* --------------------------
Hero Card
---------------------------*/

.hero-card{

background:linear-gradient(
135deg,
#172554,
#1E3A8A,
#1E293B
);

border-radius:28px;

padding:35px;

border:1px solid rgba(255,255,255,.08);

box-shadow:
0 12px 30px rgba(0,0,0,.35);

}

/* --------------------------
Right Stat Cards
---------------------------*/

.stat-card{

background:linear-gradient(
135deg,
#24324A,
#1E293B
);

border-radius:20px;

padding:22px;

text-align:center;

border:1px solid #334155;

transition:.30s;

}

.stat-card:hover{

transform:translateY(-6px);

border-color:#3B82F6;

}

/* --------------------------
KPI Cards
---------------------------*/

.metric-box{

background:linear-gradient(
135deg,
#1E293B,
#263548
);

border-left:6px solid #3B82F6;

border-radius:18px;

padding:24px;

transition:.30s;

box-shadow:
0 8px 25px rgba(0,0,0,.25);

}

.metric-box:hover{

transform:translateY(-6px);

border-left:6px solid #10B981;

}

/* --------------------------
Chart Cards
---------------------------*/

[data-testid="stVerticalBlockBorderWrapper"]{

background:#161B26;

border-radius:20px;

border:1px solid #334155;

padding:12px;

}

/* --------------------------
Titles
---------------------------*/

.metric-title{

font-size:13px;

color:#CBD5E1;

margin-top:8px;

}

.metric-value{

font-size:34px;

font-weight:700;

color:white;

margin-top:10px;

}

.section-title{

font-size:30px;

font-weight:700;

color:white;

margin-bottom:14px;

}

.stApp{

background:

linear-gradient(
180deg,
#0F172A 0%,
#111827 45%,
#172033 100%
);

}

.metric-box,
.stat-card{

transition:
all .35s ease;

}

.metric-box:hover,
.stat-card:hover{

transform:
translateY(-8px);

box-shadow:
0 18px 35px rgba(59,130,246,.25);

}

::-webkit-scrollbar{

width:10px;

}

::-webkit-scrollbar-thumb{

background:#3B82F6;

border-radius:50px;

}

::-webkit-scrollbar-track{

background:#111827;

}.stButton>button{

background:#2563EB;

color:white;

border-radius:12px;

padding:.5rem 1rem;

border:none;

font-weight:600;

transition:.3s;

}

.stButton>button:hover{

background:#1D4ED8;

transform:translateY(-2px);

}

.stSelectbox{

margin-bottom:15px;

}

</style>
""", unsafe_allow_html=True)




# ----------------------------------------------------
# PREMIUM HERO
# ----------------------------------------------------

left, right = st.columns([7,3], gap="large")

with left:

    st.markdown(f"""
<div class="hero-card">

<div style="display:flex;align-items:center;gap:18px;">

<div style="
font-size:62px;
">
📊
</div>

<div>

<div style="
font-size:52px;
font-weight:800;
line-height:58px;
color:white;
">
Nifty100 Financial Intelligence Platform
</div>

<div style="
margin-top:16px;
font-size:19px;
color:#CBD5E1;
">
Industry-grade dashboard for analysing India's largest listed companies with interactive analytics and financial insights.
</div>

<div style="
margin-top:22px;
display:flex;
gap:12px;
">

<span style="
background:#2563EB;
padding:8px 18px;
border-radius:999px;
font-size:14px;
font-weight:600;
color:white;
">
📊 Analytics
</span>

<span style="
background:#059669;
padding:8px 18px;
border-radius:999px;
font-size:14px;
font-weight:600;
color:white;
">
📈 Live Dashboard
</span>

<span style="
background:#7C3AED;
padding:8px 18px;
border-radius:999px;
font-size:14px;
font-weight:600;
color:white;
">
🏆 Nifty100
</span>

</div>

</div>

</div>

</div>
""", unsafe_allow_html=True)

with right:

    x, y, z = st.columns(3)

    cards = [
        ("📅", "Updated", "Jul 2026"),
        ("🏢", "Companies", summary["total_companies"]),
        ("📆", "Years", len(years)),
    ]

    for col, (icon, title, value) in zip([x, y, z], cards):

        with col:

            st.markdown(f"""
<div class="stat-card">

<div style="
font-size:24px;
">
{icon}
</div>

<div style="
font-size:13px;
color:#CBD5E1;
margin-top:10px;
">
{title}
</div>

<div style="
font-size:34px;
font-weight:700;
color:white;
margin-top:12px;
">
{value}
</div>

</div>
""", unsafe_allow_html=True)

st.markdown("")


# ----------------------------------------------------
# PREMIUM KPI CARDS
# ----------------------------------------------------

st.markdown(
    '<div class="section-title">📊 Financial Highlights</div>',
    unsafe_allow_html=True,
)

cards = [
    ("📈", "Average ROE", f'{summary["avg_roe"]:.2f}%', "#10B981"),
    ("💰", "Median PE", f'{summary["median_pe"]:.2f}', "#F59E0B"),
    ("🏦", "Median Debt", f'{summary["median_de"]:.2f}', "#3B82F6"),
    ("🏢", "Companies", f'{summary["total_companies"]}', "#8B5CF6"),
    ("📊", "Revenue CAGR", f'{summary["median_revenue_cagr"]:.2f}%', "#06B6D4"),
    ("✅", "Debt Free", f'{summary["debt_free_companies"]}', "#22C55E"),
]

cols = st.columns(6, gap="medium")

for col, (icon, title, value, color) in zip(cols, cards):

    with col:

        st.markdown(
            f"""
<div style="
background:linear-gradient(135deg,#1E293B,#263548);
border-left:6px solid {color};
border-radius:18px;
padding:24px;
height:185px;
box-shadow:0 10px 25px rgba(0,0,0,.25);
transition:.3s;
">

<div style="
font-size:34px;
">
{icon}
</div>

<div style="
margin-top:18px;
font-size:14px;
color:#CBD5E1;
">
{title}
</div>

<div style="
margin-top:18px;
font-size:38px;
font-weight:800;
color:white;
">
{value}
</div>

<div style="
margin-top:12px;
height:4px;
background:{color};
border-radius:999px;
">
</div>

</div>
""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)



# ----------------------------------------------------
# PREMIUM ANALYTICS
# ----------------------------------------------------

left_chart, right_table = st.columns([1.55, 1], gap="large")

# ====================================================
# SECTOR DISTRIBUTION
# ====================================================

with left_chart:

    with st.container(border=True):

        st.markdown(
            "### 🏭 Sector Distribution"
        )

        fig = px.pie(
            sector_df,
            names="broad_sector",
            values="company_count",
            hole=0.76,
            color_discrete_sequence=px.colors.qualitative.Bold,
        )

        fig.update_traces(

            textinfo="percent",

            textfont_size=14,

            marker=dict(
                line=dict(
                    color="#111827",
                    width=2
                )
            ),

            pull=[0.02]*len(sector_df),
        )

        fig.update_layout(

            template="plotly_dark",

            paper_bgcolor="#161B26",

            plot_bgcolor="#161B26",

            font_color="white",

            height=600,

            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10,
            ),

            legend=dict(

                orientation="v",

                y=0.50,

                x=1.03,

                bgcolor="rgba(0,0,0,0)",
            ),

        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo":False
            },
        )

# ====================================================
# TOP 5 QUALITY
# ====================================================

with right_table:

    with st.container(border=True):

        st.markdown(
            "### 🏆 Top 5 Quality Companies"
        )

        table = top5.copy()

        table.columns = [

            "Company",

            "Sector",

            "Quality Score"

        ]

        table.insert(

            0,

            "Rank",

            range(
                1,
                len(table)+1
            )

        )

        table["Quality Score"] = (
            table["Quality Score"].round(2)
        )

        gb = GridOptionsBuilder.from_dataframe(table)

        gb.configure_default_column(

            sortable=True,

            filter=True,

            resizable=True,

        )

        gb.configure_grid_options(

            rowHeight=42,

            headerHeight=45,

            animateRows=True,

        )

        gb.configure_pagination(

            paginationAutoPageSize=True,

        )

        AgGrid(
            table,
            gridOptions=gb.build(),
            theme="streamlit",
            height=600,
            fit_columns_on_grid_load=True,
            key="quality_grid",
       )

st.markdown("")



st.markdown("---")

st.markdown("""
<div style="text-align:center;padding:18px;color:#94A3B8;font-size:15px;">

<b>Nifty100 Financial Intelligence Platform</b><br>

Built with ❤️ using
<b>Streamlit</b>,
<b>Plotly</b>,
<b>SQLite</b>,
<b>Pandas</b>,
<b>AG Grid</b>

</div>
""", unsafe_allow_html=True)