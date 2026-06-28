import sqlite3
import pandas as pd
import os

from src.analytics.ratios import (
    debt_to_equity,
    interest_coverage_ratio,
    net_debt,
    asset_turnover
)

os.makedirs("output", exist_ok=True)

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT
p.company_id,
p.year,
p.sales,
p.operating_profit,
p.other_income,
p.interest,
b.equity_capital,
b.reserves,
b.borrowings,
b.investments,
b.total_assets
FROM profitandloss p
JOIN balancesheet b
ON p.company_id=b.company_id
AND p.year=b.year
"""

df = pd.read_sql(query, conn)

results = []

for _, row in df.iterrows():

    de = debt_to_equity(
        row["borrowings"],
        row["equity_capital"],
        row["reserves"]
    )

    icr = interest_coverage_ratio(
        row["operating_profit"],
        row["other_income"],
        row["interest"]
    )

    nd = net_debt(
        row["borrowings"],
        row["investments"]
    )

    at = asset_turnover(
        row["sales"],
        row["total_assets"]
    )

    results.append({
        "company_id": row["company_id"],
        "year": row["year"],
        "debt_to_equity": de,
        "interest_coverage": icr,
        "net_debt": nd,
        "asset_turnover": at
    })

result_df = pd.DataFrame(results)

result_df.to_csv(
    "output/leverage_review.csv",
    index=False
)

print("=" * 50)
print("Rows Processed :", len(result_df))
print("Saved -> output/leverage_review.csv")
print("=" * 50)

conn.close()