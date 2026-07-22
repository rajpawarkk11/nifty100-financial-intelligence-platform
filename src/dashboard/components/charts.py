import streamlit as st
import plotly.express as px


def sector_donut_chart(df):

    fig = px.pie(
        df,
        names="broad_sector",
        values="company_count",
        hole=0.62,
    )

    fig.update_traces(
        textinfo="percent",
        hovertemplate="<b>%{label}</b><br>%{value} Companies<extra></extra>"
    )

    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=10, r=10, t=10, b=10),
        legend_title="Sector",
        legend_orientation="v",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )