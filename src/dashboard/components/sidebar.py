from streamlit_option_menu import option_menu
import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div style="padding:20px 10px 10px 10px;">
                <h2 style="color:white;margin-bottom:0;">
                    📊 Nifty100
                </h2>

                <p style="color:#94A3B8;">
                    Financial Intelligence
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        page = option_menu(
            menu_title=None,
            options=[
                "Home",
                "Company Profile",
                "Stock Screener",
                "Peer Comparison",
                "Trend Analysis",
                "Sector Analysis",
                "Capital Allocation",
                "Annual Reports",
            ],
            icons=[
                "house-fill",
                "building",
                "search",
                "people-fill",
                "graph-up-arrow",
                "pie-chart-fill",
                "cash-stack",
                "file-earmark-text",
            ],
            default_index=0,
            styles={
                "container": {
                    "background-color": "#08111F",
                    "padding": "0px",
                },
                "icon": {
                    "color": "#A855F7",
                    "font-size": "18px",
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "5px",
                    "padding": "12px",
                    "border-radius": "14px",
                    "color": "white",
                },
                "nav-link-selected": {
                    "background": "linear-gradient(90deg,#7C3AED,#9333EA)",
                    "color": "white",
                },
            },
        )

        st.markdown("---")

        st.info("📅 FY 2024")

        st.markdown(
            """
            <div style="
            background:#111827;
            padding:16px;
            border-radius:16px;
            border:1px solid #30363d;
            color:white;
            margin-top:20px;
            ">
            <b>Raj Pawar</b><br>
            Dashboard Administrator
            </div>
            """,
            unsafe_allow_html=True,
        )

    return page