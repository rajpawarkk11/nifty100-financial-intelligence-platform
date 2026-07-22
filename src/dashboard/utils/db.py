from pathlib import Path
import sqlite3
import pandas as pd
import streamlit as st

# --------------------------------------------------
# Project Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATABASE_PATH = PROJECT_ROOT / "db" / "nifty100.db"


# --------------------------------------------------
# Database Connection
# --------------------------------------------------

def get_connection():

    return sqlite3.connect(DATABASE_PATH)


# --------------------------------------------------
# Generic SQL Loader
# --------------------------------------------------

@st.cache_data(ttl=600)
def run_query(query, params=None):

    conn = get_connection()

    try:

        if params is None:
            df = pd.read_sql_query(query, conn)

        else:
            df = pd.read_sql_query(
                query,
                conn,
                params=params
            )

    finally:

        conn.close()

    return df
# --------------------------------------------------
# Companies
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_companies():
    query = """
    SELECT
        id,
        company_name
    FROM companies
    ORDER BY company_name;
    """
    return run_query(query)


@st.cache_data(ttl=600)
def get_company_profile(company_id):
    query = """
    SELECT *
    FROM companies
    WHERE id = ?;
    """
    return run_query(query, params=(company_id,))


# --------------------------------------------------
# Financial Ratios
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_financial_ratios(company_id):
    query = """
    SELECT *
    FROM financial_ratios
    WHERE company_id = ?
    ORDER BY year;
    """
    return run_query(query, params=(company_id,))


# --------------------------------------------------
# Profit & Loss
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_profit_loss(company_id):
    query = """
    SELECT *
    FROM profitandloss
    WHERE company_id = ?
    ORDER BY year;
    """
    return run_query(query, params=(company_id,))
# --------------------------------------------------
# Balance Sheet
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_balance_sheet(company_id):
    query = """
    SELECT *
    FROM balancesheet
    WHERE company_id = ?
    ORDER BY year;
    """
    return run_query(query, params=(company_id,))


# --------------------------------------------------
# Cash Flow
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_cash_flow(company_id):
    query = """
    SELECT *
    FROM cashflow
    WHERE company_id = ?
    ORDER BY year;
    """
    return run_query(query, params=(company_id,))


# --------------------------------------------------
# Sector Information
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_sector_data(company_id):
    query = """
    SELECT *
    FROM sectors
    WHERE company_id = ?;
    """
    return run_query(query, params=(company_id,))


# --------------------------------------------------
# Peer Group
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_peer_group(company_id):
    query = """
    SELECT *
    FROM peer_groups
    WHERE company_id = ?;
    """
    return run_query(query, params=(company_id,))


# --------------------------------------------------
# Market Valuation
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_market_cap(company_id):
    query = """
    SELECT *
    FROM market_cap
    WHERE company_id = ?
    ORDER BY year;
    """
    return run_query(query, params=(company_id,))


# --------------------------------------------------
# Annual Reports
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_annual_reports(company_id):
    query = """
    SELECT *
    FROM documents
    WHERE company_id = ?
    ORDER BY year DESC;
    """
    return run_query(query, params=(company_id,))


# --------------------------------------------------
# Company Dashboard Profile
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_company_dashboard(company_id):
    query = """
    SELECT
        c.id,
        c.company_name,
        c.company_logo,
        c.chart_link,
        c.about_company,
        c.website,
        c.nse_profile,
        c.bse_profile,
        c.face_value,
        c.book_value,
        c.roce_percentage,
        c.roe_percentage,
        s.broad_sector,
        s.sub_sector,
        s.market_cap_category
    FROM companies c
    LEFT JOIN sectors s
        ON c.id = s.company_id
    WHERE c.id = ?;
    """
    return run_query(query, params=(company_id,))


# --------------------------------------------------
# Home Dashboard Summary
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_home_summary(year):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        year_pattern = f"%{year}"

        # -------------------------------
        # Average ROE
        # -------------------------------
        cursor.execute("""
            SELECT ROUND(AVG(return_on_equity_pct), 2)
            FROM financial_ratios
            WHERE year LIKE ?;
        """, (year_pattern,))
        avg_roe = cursor.fetchone()[0]

        # -------------------------------
        # Median P/E
        # -------------------------------
        cursor.execute("""
            SELECT pe_ratio
            FROM market_cap
            WHERE year LIKE ?
              AND pe_ratio IS NOT NULL
            ORDER BY pe_ratio;
        """, (year_pattern,))

        values = [row[0] for row in cursor.fetchall()]

        if values:
            n = len(values)
            if n % 2 == 1:
                median_pe = values[n // 2]
            else:
                median_pe = round(
                    (values[n // 2 - 1] + values[n // 2]) / 2,
                    2
                )
        else:
            median_pe = None

        # -------------------------------
        # Median Debt to Equity
        # -------------------------------
        cursor.execute("""
            SELECT debt_to_equity
            FROM financial_ratios
            WHERE year LIKE ?
              AND debt_to_equity IS NOT NULL
            ORDER BY debt_to_equity;
        """, (year_pattern,))

        values = [row[0] for row in cursor.fetchall()]

        if values:
            n = len(values)
            if n % 2 == 1:
                median_de = values[n // 2]
            else:
                median_de = round(
                    (values[n // 2 - 1] + values[n // 2]) / 2,
                    2
                )
        else:
            median_de = None

        # -------------------------------
        # Total Companies
        # -------------------------------
        cursor.execute("""
            SELECT COUNT(DISTINCT company_id)
            FROM financial_ratios
            WHERE year LIKE ?;
        """, (year_pattern,))
        total_companies = cursor.fetchone()[0]

        # -------------------------------
        # Median Revenue CAGR (5 Year)
        # -------------------------------
        cursor.execute("""
            SELECT revenue_cagr_5yr
            FROM financial_ratios
            WHERE year LIKE ?
              AND revenue_cagr_5yr IS NOT NULL
            ORDER BY revenue_cagr_5yr;
        """, (year_pattern,))

        values = [row[0] for row in cursor.fetchall()]

        if values:
            n = len(values)
            if n % 2 == 1:
                median_revenue_cagr = values[n // 2]
            else:
                median_revenue_cagr = round(
                    (values[n // 2 - 1] + values[n // 2]) / 2,
                    2
                )
        else:
            median_revenue_cagr = None

        # -------------------------------
        # Debt Free Companies
        # -------------------------------
        cursor.execute("""
            SELECT COUNT(*)
            FROM financial_ratios
            WHERE year LIKE ?
              AND total_debt_cr = 0;
        """, (year_pattern,))
        debt_free_companies = cursor.fetchone()[0]

        return {
            "avg_roe": avg_roe,
            "median_pe": median_pe,
            "median_de": median_de,
            "total_companies": total_companies,
            "median_revenue_cagr": median_revenue_cagr,
            "debt_free_companies": debt_free_companies,
        }

    finally:
        conn.close()


# --------------------------------------------------
# Available Years
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_available_years():
    query = """
    SELECT DISTINCT
        SUBSTR(year, -4) AS year
    FROM financial_ratios
    ORDER BY year DESC;
    """
    return run_query(query)


# --------------------------------------------------
# Sector Breakdown
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_sector_breakdown():
    query = """
    SELECT
        broad_sector,
        COUNT(*) AS company_count
    FROM sectors
    GROUP BY broad_sector
    ORDER BY company_count DESC;
    """
    return run_query(query)


# --------------------------------------------------
# Top Quality Companies
# --------------------------------------------------

@st.cache_data(ttl=600)
def get_top_quality_companies(year):
    query = """
    SELECT
        c.company_name,
        s.broad_sector,
        f.composite_quality_score
    FROM financial_ratios f
    JOIN companies c
        ON f.company_id = c.id
    LEFT JOIN sectors s
        ON f.company_id = s.company_id
    WHERE f.year LIKE ?
      AND f.composite_quality_score IS NOT NULL
    ORDER BY f.composite_quality_score DESC
    LIMIT 5;
    """

    return run_query(
        query,
        params=(f"%{year}",)
    )