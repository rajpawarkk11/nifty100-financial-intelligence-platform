import streamlit as st


def kpi_card(title, value, icon, color="#7C3AED"):

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-top">

                <div>

                    <div class="metric-title">
                        {title}
                    </div>

                    <div class="metric-value">
                        {value}
                    </div>

                </div>

                <div class="metric-icon"
                     style="background:{color};">

                    {icon}

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )