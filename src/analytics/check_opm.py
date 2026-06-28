import sqlite3
import pandas as pd
import os

from src.analytics.ratios import operating_profit_margin

os.makedirs("output", exist_ok=True)

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql("""
SELECT
company_id,
year,
sales,
operating_profit,
opm_percentage
FROM profitandloss
""", conn)

results = []

for _, row in df.iterrows():

    calc = operating_profit_margin(
        row["operating_profit"],
        row["sales"]
    )

    source = row["opm_percentage"]

    if calc is None:
        continue

    diff = abs(calc - source)

    if diff > 1:

        results.append({
            "company_id": row["company_id"],
            "year": row["year"],
            "calculated_opm": round(calc, 2),
            "source_opm": source,
            "difference": round(diff, 2)
        })

result_df = pd.DataFrame(results)

result_df.to_csv(
    "output/opm_mismatches.csv",
    index=False
)

print("=" * 50)
print("Total OPM mismatches:", len(result_df))
print("Saved -> output/opm_mismatches.csv")
print("=" * 50)

conn.close()