import streamlit as st


def top_companies_table(df):

    table = df.copy()

    table.columns = [
        "Company",
        "Sector",
        "Quality Score"
    ]

    table.insert(
        0,
        "Rank",
        range(1, len(table) + 1)
    )

    table["Quality Score"] = table["Quality Score"].round(2)

    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        height=420
    )