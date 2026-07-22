import streamlit as st


def dashboard_header(title, subtitle):

    left, right = st.columns([6, 2])

    with left:

        st.markdown(
            f"""
            <div class="header-box">

                <div class="header-title">
                    {title}
                </div>

                <div class="header-subtitle">
                    {subtitle}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:

        st.markdown(
            """
            <div class="header-stat">

                <div class="stat-label">
                    LAST UPDATED
                </div>

                <div class="stat-value">
                    JUL 2026
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )