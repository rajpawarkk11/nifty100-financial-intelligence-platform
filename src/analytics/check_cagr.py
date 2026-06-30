import sqlite3
import pandas as pd

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr,
)

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql(
    """
    SELECT
        company_id,
        year,
        sales,
        net_profit,
        eps
    FROM profitandloss
    ORDER BY company_id, year
    """,
    conn,
)

results = []

for company, group in df.groupby("company_id"):

    group = group.reset_index(drop=True)

    for idx in range(len(group)):

        row = group.iloc[idx]

        record = {
            "company_id": row["company_id"],
            "year": row["year"],
        }

        for period in [3, 5, 10]:

            if idx >= period:

                prev = group.iloc[idx - period]

                value, flag = revenue_cagr(
                    prev["sales"],
                    row["sales"],
                    period,
                )
                record[f"revenue_cagr_{period}yr"] = value
                record[f"revenue_flag_{period}yr"] = flag

                value, flag = pat_cagr(
                    prev["net_profit"],
                    row["net_profit"],
                    period,
                )
                record[f"pat_cagr_{period}yr"] = value
                record[f"pat_flag_{period}yr"] = flag

                value, flag = eps_cagr(
                    prev["eps"],
                    row["eps"],
                    period,
                )
                record[f"eps_cagr_{period}yr"] = value
                record[f"eps_flag_{period}yr"] = flag

            else:

                record[f"revenue_cagr_{period}yr"] = None
                record[f"revenue_flag_{period}yr"] = "INSUFFICIENT"

                record[f"pat_cagr_{period}yr"] = None
                record[f"pat_flag_{period}yr"] = "INSUFFICIENT"

                record[f"eps_cagr_{period}yr"] = None
                record[f"eps_flag_{period}yr"] = "INSUFFICIENT"

        results.append(record)

result = pd.DataFrame(results)

result.to_csv(
    "output/cagr_review.csv",
    index=False,
)

print("=" * 50)
print("Rows Processed :", len(result))
print("Saved -> output/cagr_review.csv")
print("=" * 50)

conn.close()