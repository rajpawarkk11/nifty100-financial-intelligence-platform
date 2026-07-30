"""
Sprint 5 – Day 31
Cash Flow Intelligence Module
Specification Compliant
"""

from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd

# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"

CAPITAL_FILE = PROJECT_ROOT / "output" / "capital_allocation.csv"

OUTPUT_FILE = PROJECT_ROOT / "output" / "cashflow_intelligence.xlsx"

DISTRESS_FILE = PROJECT_ROOT / "output" / "distress_alerts.csv"


# ============================================================
# LABELS
# ============================================================

def cfo_quality_label(score):

    if pd.isna(score):
        return "N/A"

    if score > 1:
        return "High Quality"

    if score >= 0.5:
        return "Moderate"

    return "Accrual Risk"


def capex_label(value):

    if pd.isna(value):
        return "N/A"

    if value < 3:
        return "Asset Light"

    if value <= 8:
        return "Moderate"

    return "Capital Intensive"


# ============================================================
# DATABASE
# ============================================================

def load_database():

    con = sqlite3.connect(DB_PATH)

    companies = pd.read_sql(
        """
        SELECT
            id AS company_id,
            company_name
        FROM companies
        """,
        con,
    )

    sectors = pd.read_sql(
        """
        SELECT
            company_id,
            broad_sector
        FROM sectors
        """,
        con,
    )

    pnl = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            sales,
            operating_profit,
            net_profit
        FROM profitandloss
        ORDER BY company_id, year
        """,
        con,
    )

    cashflow = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            investing_activity,
            financing_activity,
            net_cash_flow
        FROM cashflow
        ORDER BY company_id, year
        """,
        con,
    )

    balance = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            borrowings
        FROM balancesheet
        ORDER BY company_id, year
        """,
        con,
    )

    ratios = pd.read_sql(
        """
        SELECT
            company_id,
            year,
            debt_to_equity,
            interest_coverage,
            free_cash_flow_cr,
            cash_from_operations_cr
        FROM financial_ratios
        ORDER BY company_id, year
        """,
        con,
    )

    con.close()

    return (
        companies,
        sectors,
        pnl,
        cashflow,
        balance,
        ratios,
    )


# ============================================================
# HELPERS
# ============================================================

def latest(df):

    return (
        df
        .sort_values("year")
        .groupby("company_id", as_index=False)
        .tail(1)
        .copy()
    )


def last5(df):

    return (
        df
        .sort_values("year")
        .groupby("company_id")
        .tail(5)
        .copy()
    )


def safe_divide(a, b):

    if pd.isna(a) or pd.isna(b):
        return np.nan

    if b == 0:
        return np.nan

    return a / b

# ============================================================
# KPI CALCULATIONS
# ============================================================

def build_dataset():

    companies, sectors, pnl, cashflow, balance, ratios = load_database()

    # ---------- Last 5 Years ----------
    cf5 = last5(cashflow)
    pnl5 = last5(pnl)
    bal5 = last5(balance)

    history = (
        cf5.merge(
            pnl5,
            on=["company_id", "year"],
            how="left",
        )
        .merge(
            bal5,
            on=["company_id", "year"],
            how="left",
        )
    )

    # ---------- CFO/PAT Ratio ----------
    history["cfo_pat_ratio"] = history.apply(
        lambda r: safe_divide(
            r["operating_activity"],
            r["net_profit"],
        ),
        axis=1,
    )

    # ---------- 5-Year Average ----------
    quality = (
        history.groupby("company_id")["cfo_pat_ratio"]
        .mean()
        .round(2)
        .reset_index(name="cfo_quality_score")
    )

    quality["cfo_quality_label"] = quality[
        "cfo_quality_score"
    ].apply(cfo_quality_label)

    # ---------- Latest Year ----------
    latest_cf = latest(cashflow)
    latest_pnl = latest(pnl)
    latest_bal = latest(balance)
    latest_ratios = latest(ratios)

    df = (
        companies
        .merge(sectors, on="company_id", how="left")
        .merge(latest_cf, on="company_id", how="left")
        .merge(latest_pnl, on=["company_id", "year"], how="left")
        .merge(latest_bal, on=["company_id", "year"], how="left")
        .merge(latest_ratios, on=["company_id", "year"], how="left")
        .merge(quality, on="company_id", how="left")
    )

    return df, history


# ============================================================
# KPI ENGINE
# ============================================================

def calculate_kpis(df, history):

    # -------------------------------
    # Free Cash Flow
    # -------------------------------

    df["free_cash_flow"] = (
        df["operating_activity"] +
        df["investing_activity"]
    )

    # -------------------------------
    # CapEx Intensity
    # -------------------------------

    df["capex_intensity_pct"] = (
        abs(df["investing_activity"])
        /
        df["sales"].replace(0, np.nan)
        *
        100
    ).round(2)

    df["capex_label"] = df[
        "capex_intensity_pct"
    ].apply(capex_label)

    # -------------------------------
    # FCF Conversion
    # -------------------------------

    df["fcf_conversion_pct"] = (
        df["free_cash_flow"]
        /
        df["operating_profit"].replace(0, np.nan)
        *
        100
    ).round(2)

    # -------------------------------
    # FCF CAGR (5Y)
    # -------------------------------

    fcf = history.copy()

    fcf["fcf"] = (
        fcf["operating_activity"] +
        fcf["investing_activity"]
    )

    rows = []

    for cid, grp in fcf.groupby("company_id"):

        grp = grp.sort_values("year")

        if len(grp) < 5:

            rows.append(
                {
                    "company_id": cid,
                    "fcf_cagr_5yr": np.nan,
                }
            )

            continue

        start = grp.iloc[0]["fcf"]
        end = grp.iloc[-1]["fcf"]

        if pd.isna(start) or pd.isna(end):
            cagr = np.nan

        elif start <= 0 or end <= 0:
            cagr = np.nan

        else:

            cagr = (
                (
                    end
                    /
                    start
                ) ** (1 / 4)
                - 1
            ) * 100

        rows.append(
            {
                "company_id": cid,
                "fcf_cagr_5yr": round(cagr, 2)
                if pd.notna(cagr)
                else np.nan,
            }
        )

    fcf_df = pd.DataFrame(rows)

    df = df.merge(
        fcf_df,
        on="company_id",
        how="left",
    )

    return df, history

# ============================================================
# DISTRESS + DELEVERAGING
# ============================================================

def apply_flags(df, history):

    # -------------------------------
    # Distress Signal
    # CFO < 0 AND CFF > 0
    # -------------------------------

    df["distress_flag"] = (
        (df["operating_activity"] < 0)
        &
        (df["financing_activity"] > 0)
    )

    # -------------------------------
    # Deleveraging
    # CFF < 0 AND Borrowings declining YoY
    # -------------------------------

    borrowing = (
        history.sort_values(["company_id", "year"])
        .groupby("company_id")
        .tail(2)
    )

    deleveraging = {}

    for cid, grp in borrowing.groupby("company_id"):

        if len(grp) < 2:
            deleveraging[cid] = False
            continue

        grp = grp.sort_values("year")

        prev_borrow = grp.iloc[0]["borrowings"]
        curr_borrow = grp.iloc[1]["borrowings"]

        curr_cff = grp.iloc[1]["financing_activity"]

        deleveraging[cid] = (
            (curr_cff < 0)
            and
            (curr_borrow < prev_borrow)
        )

    df["deleveraging_flag"] = df["company_id"].map(
        deleveraging
    ).fillna(False)

    return df


# ============================================================
# CAPITAL ALLOCATION
# ============================================================

def merge_capital_allocation(df):

    capital = pd.read_csv(CAPITAL_FILE)

    capital = (
        capital
        .sort_values("year")
        .groupby("company_id", as_index=False)
        .tail(1)
    )

    capital = capital.rename(
        columns={
            "pattern_label": "capital_allocation_label"
        }
    )

    df = df.merge(
        capital[
            [
                "company_id",
                "capital_allocation_label",
            ]
        ],
        on="company_id",
        how="left",
    )

    return df


# ============================================================
# EXPORT
# ============================================================

def export_reports(df):

    df = df.rename(
    columns={
        "broad_sector": "sector"
    }
)

    final = df[
        [
            "company_id",
            "company_name",
            "sector",
            "cfo_quality_score",
            "cfo_quality_label",
            "capex_intensity_pct",
            "capex_label",
            "fcf_cagr_5yr",
            "fcf_conversion_pct",
            "distress_flag",
            "deleveraging_flag",
            "capital_allocation_label",
        ]
    ].copy()

    final.to_excel(
        OUTPUT_FILE,
        index=False,
    )

    distress = df[
        df["distress_flag"]
    ][
        [
            "company_id",
            "company_name",
            "operating_activity",
            "financing_activity",
            "net_profit",
        ]
    ].copy()

    distress.columns = [
        "company_id",
        "company_name",
        "cfo_value",
        "cff_value",
        "latest_net_profit",
    ]

    distress.to_csv(
        DISTRESS_FILE,
        index=False,
    )

    print("=" * 60)
    print("Cash Flow Intelligence Complete")
    print("=" * 60)
    print("Companies :", len(final))
    print("Distress  :", len(distress))
    print("Excel     :", OUTPUT_FILE)
    print("CSV       :", DISTRESS_FILE)


# ============================================================
# MAIN
# ============================================================

def main():

    print("Loading database...")

    df, history = build_dataset()

    print("Calculating KPIs...")

    df, history = calculate_kpis(df, history)

    print("Applying flags...")

    df = apply_flags(df, history)

    print("Capital allocation...")

    df = merge_capital_allocation(df)

    print("Exporting reports...")

    export_reports(df)

    print("Done.")


if __name__ == "__main__":
    main()

