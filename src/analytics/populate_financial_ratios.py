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

print("=" * 70)
print("TOP ROE DEBUG")
print("=" * 70)

debug = df[
    [
        "company_id",
        "year",
        "net_profit",
        "equity_capital",
        "reserves",
        "return_on_equity_pct",
    ]
].sort_values(
    "return_on_equity_pct",
    ascending=False
)

print(debug.head(20))

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

for col in [
    "revenue_cagr_3yr",
    "revenue_cagr_5yr",
    "revenue_cagr_10yr",
    "pat_cagr_3yr",
    "pat_cagr_5yr",
    "pat_cagr_10yr",
    "eps_cagr_3yr",
    "eps_cagr_5yr",
    "eps_cagr_10yr",
    "revenue_cagr_3yr_flag",
    "revenue_cagr_5yr_flag",
    "revenue_cagr_10yr_flag",
    "pat_cagr_3yr_flag",
    "pat_cagr_5yr_flag",
    "pat_cagr_10yr_flag",
    "eps_cagr_3yr_flag",
    "eps_cagr_5yr_flag",
    "eps_cagr_10yr_flag",
]:
    df[col] = pd.NA

annual = (
    df[df["year_num"].notna()]
    .sort_values(["company_id", "year_num"])
    .copy()
)

periods = [3, 5, 10]

for company, grp in annual.groupby("company_id"):

    grp = grp.reset_index()

    for years in periods:

        if len(grp) < years + 1:
            continue

        for i in range(years, len(grp)):

            idx = grp.loc[i, "index"]

            rev, rev_flag = revenue_cagr(
                grp.loc[i-years, "sales"],
                grp.loc[i, "sales"],
                years,
            )

            pat, pat_flag = pat_cagr(
                grp.loc[i-years, "net_profit"],
                grp.loc[i, "net_profit"],
                years,
            )

            eps, eps_flag = eps_cagr(
                grp.loc[i-years, "eps"],
                grp.loc[i, "eps"],
                years,
            )

            df.at[idx, f"revenue_cagr_{years}yr"] = rev
            df.at[idx, f"pat_cagr_{years}yr"] = pat
            df.at[idx, f"eps_cagr_{years}yr"] = eps

            df.at[idx, f"revenue_cagr_{years}yr_flag"] = rev_flag
            df.at[idx, f"pat_cagr_{years}yr_flag"] = pat_flag
            df.at[idx, f"eps_cagr_{years}yr_flag"] = eps_flag

print("=" * 60)
print("3Y / 5Y / 10Y CAGR Completed")
print("=" * 60)

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

    "revenue_cagr_3yr",
    "revenue_cagr_5yr",
    "revenue_cagr_10yr",

    "pat_cagr_3yr",
    "pat_cagr_5yr",
    "pat_cagr_10yr",

    "eps_cagr_3yr",
    "eps_cagr_5yr",
    "eps_cagr_10yr",

    "revenue_cagr_3yr_flag",
    "revenue_cagr_5yr_flag",
    "revenue_cagr_10yr_flag",

    "pat_cagr_3yr_flag",
    "pat_cagr_5yr_flag",
    "pat_cagr_10yr_flag",

    "eps_cagr_3yr_flag",
    "eps_cagr_5yr_flag",
    "eps_cagr_10yr_flag",

    "composite_quality_score",
]
df[cols].to_sql(
    "financial_ratios",
    conn,
    if_exists="append",
    index=False,
)
print("=" * 60)
print("CAGR Verification")
print("=" * 60)

verify = pd.read_sql("""
SELECT
COUNT(*) AS rows,
COUNT(revenue_cagr_3yr) AS rev3,
COUNT(revenue_cagr_5yr) AS rev5,
COUNT(revenue_cagr_10yr) AS rev10,
COUNT(pat_cagr_3yr) AS pat3,
COUNT(pat_cagr_5yr) AS pat5,
COUNT(pat_cagr_10yr) AS pat10,
COUNT(eps_cagr_3yr) AS eps3,
COUNT(eps_cagr_5yr) AS eps5,
COUNT(eps_cagr_10yr) AS eps10
FROM financial_ratios
""", conn)

print(verify)
count = pd.read_sql(
    "SELECT COUNT(*) AS cnt FROM financial_ratios",
    conn,
)

print("=" * 60)
print("financial_ratios populated successfully")
print(count)
print("=" * 60)

conn.close()