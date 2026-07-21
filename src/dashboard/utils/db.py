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
        c.about_company,
        c.website,
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