"""
Sprint 2 - Day 12
Populate financial_ratios Table
"""

import sqlite3
import pandas as pd

from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    roe,
    debt_to_equity,
    interest_coverage_ratio,
    asset_turnover,
)

from src.analytics.cashflow_kpis import (
    free_cash_flow,
)

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr,
)

conn = sqlite3.connect("db/nifty100.db")

profit = pd.read_sql("SELECT * FROM profitandloss", conn)
balance = pd.read_sql("SELECT * FROM balancesheet", conn)
cash = pd.read_sql("SELECT * FROM cashflow", conn)

profit = profit.drop_duplicates()
balance = balance.drop_duplicates()

cash = cash[
    ~(
        (cash["operating_activity"] == 0)
        & (cash["investing_activity"] == 0)
        & (cash["financing_activity"] == 0)
    )
]

cash = (
    cash.sort_values("id")
    .drop_duplicates(
        subset=["company_id", "year"],
        keep="first",
    )
)

df = (
    profit.merge(
        balance,
        on=["company_id", "year"],
        how="inner",
    )
    .merge(
        cash,
        on=["company_id", "year"],
        how="left",
    )
)

df["year_num"] = (
    df["year"]
    .astype(str)
    .str.extract(r"(\d{4})")[0]
)

df["year_num"] = pd.to_numeric(
    df["year_num"],
    errors="coerce",
)

print("Rows:", len(df))

# =====================================================
# KPI CALCULATIONS
# =====================================================

df["net_profit_margin_pct"] = df.apply(
    lambda r: net_profit_margin(r["net_profit"], r["sales"]), axis=1
)

df["operating_profit_margin_pct"] = df.apply(
    lambda r: operating_profit_margin(r["operating_profit"], r["sales"]), axis=1
)

df["return_on_equity_pct"] = df.apply(
    lambda r: roe(
        r["net_profit"],
        r["equity_capital"],
        r["reserves"],
    ),
    axis=1,
)

df["debt_to_equity"] = df.apply(
    lambda r: debt_to_equity(
        r["borrowings"],
        r["equity_capital"],
        r["reserves"],
    ),
    axis=1,
)

df["interest_coverage"] = df.apply(
    lambda r: interest_coverage_ratio(
        r["operating_profit"],
        r["other_income"],
        r["interest"],
    ),
    axis=1,
)

df["asset_turnover"] = df.apply(
    lambda r: asset_turnover(
        r["sales"],
        r["total_assets"],
    ),
    axis=1,
)

df["free_cash_flow_cr"] = df.apply(
    lambda r: free_cash_flow(
        r["operating_activity"],
        r["investing_activity"],
    ),
    axis=1,
)

df["capex_cr"] = df["investing_activity"].abs()

df["earnings_per_share"] = df["eps"]

df["book_value_per_share"] = (
    (df["equity_capital"] + df["reserves"])
    / df["equity_capital"]
)

df.loc[
    df["equity_capital"] == 0,
    "book_value_per_share"
] = pd.NA

df["dividend_payout_ratio_pct"] = df["dividend_payout"]

df["total_debt_cr"] = df["borrowings"]

df["cash_from_operations_cr"] = df["operating_activity"]

print("KPI calculations completed.")

# =====================================================
# CAGR CALCULATIONS
# =====================================================

df["revenue_cagr_5yr"] = pd.NA
df["pat_cagr_5yr"] = pd.NA
df["eps_cagr_5yr"] = pd.NA

annual = (
    df[df["year_num"].notna()]
    .sort_values(["company_id", "year_num"])
    .copy()
)

for company, grp in annual.groupby("company_id"):

    grp = grp.reset_index()

    if len(grp) < 6:
        continue

    for i in range(5, len(grp)):

        idx = grp.loc[i, "index"]

        rev, _ = revenue_cagr(
            grp.loc[i - 5, "sales"],
            grp.loc[i, "sales"],
            5,
        )

        pat, _ = pat_cagr(
            grp.loc[i - 5, "net_profit"],
            grp.loc[i, "net_profit"],
            5,
        )

        eps_val, _ = eps_cagr(
            grp.loc[i - 5, "eps"],
            grp.loc[i, "eps"],
            5,
        )

        df.at[idx, "revenue_cagr_5yr"] = rev
        df.at[idx, "pat_cagr_5yr"] = pat
        df.at[idx, "eps_cagr_5yr"] = eps_val

# =====================================================
# COMPOSITE SCORE
# =====================================================

df["composite_quality_score"] = (
    df["return_on_equity_pct"].fillna(0)
    + df["net_profit_margin_pct"].fillna(0)
    + (df["asset_turnover"].fillna(0) * 10)
) / 3

# =====================================================
# SAVE TO SQLITE
# =====================================================

cursor = conn.cursor()

cursor.execute("DELETE FROM financial_ratios")

cols = [
    "company_id",
    "year",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "return_on_equity_pct",
    "debt_to_equity",
    "interest_coverage",
    "asset_turnover",
    "free_cash_flow_cr",
    "capex_cr",
    "earnings_per_share",
    "book_value_per_share",
    "dividend_payout_ratio_pct",
    "total_debt_cr",
    "cash_from_operations_cr",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "eps_cagr_5yr",
    "composite_quality_score",
]

df[cols].to_sql(
    "financial_ratios",
    conn,
    if_exists="append",
    index=False,
)

count = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM financial_ratios",
    conn,
)

print("=" * 60)
print("financial_ratios populated successfully")
print(count)
print("=" * 60)

conn.close()