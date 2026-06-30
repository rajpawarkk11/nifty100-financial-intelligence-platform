import sqlite3
import pandas as pd

from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_label,
    capex_intensity,
    capex_label,
    fcf_conversion_rate,
    capital_allocation_pattern,
)

conn = sqlite3.connect("db/nifty100.db")

query = """
SELECT
cf.company_id,
cf.year,
cf.operating_activity,
cf.investing_activity,
cf.financing_activity,
pl.net_profit,
pl.sales,
pl.operating_profit
FROM cashflow cf
JOIN profitandloss pl
ON cf.company_id = pl.company_id
AND cf.year = pl.year
ORDER BY cf.company_id, cf.year
"""

df = pd.read_sql(query, conn)

# -----------------------------
# CFO/PAT Ratio
# -----------------------------

df["cfo_pat_ratio"] = (
    df["operating_activity"] /
    df["net_profit"]
)

df.loc[
    df["net_profit"] == 0,
    "cfo_pat_ratio"
] = None

# -----------------------------
# 5-Year Rolling Average
# -----------------------------

df["cfo_quality_score"] = (
    df.groupby("company_id")["cfo_pat_ratio"]
      .transform(
          lambda x: x.rolling(
              window=5,
              min_periods=1
          ).mean()
      )
)

records = []

for _, row in df.iterrows():

    fcf = free_cash_flow(
        row["operating_activity"],
        row["investing_activity"],
    )

    quality_score = (
        None
        if pd.isna(row["cfo_quality_score"])
        else round(
            row["cfo_quality_score"],
            2
        )
    )

    quality_label = cfo_quality_label(
        quality_score,
    )

    capex = capex_intensity(
        row["investing_activity"],
        row["sales"],
    )

    capex_type = capex_label(
        capex,
    )

    conversion = fcf_conversion_rate(
        fcf,
        row["operating_profit"],
    )

    pattern = capital_allocation_pattern(
        row["operating_activity"],
        row["investing_activity"],
        row["financing_activity"],
        quality_score,
    )

    records.append({
    "company_id": row["company_id"],
    "year": row["year"],

    # Required by Sprint PDF
    "cfo_sign": "+" if row["operating_activity"] >= 0 else "-",
    "cfi_sign": "+" if row["investing_activity"] >= 0 else "-",
    "cff_sign": "+" if row["financing_activity"] >= 0 else "-",

    # KPI Values
    "free_cash_flow": fcf,
    "cfo_quality_score": quality_score,
    "cfo_quality_label": quality_label,
    "capex_intensity": capex,
    "capex_label": capex_type,
    "fcf_conversion_rate": conversion,

    # Pattern
    "pattern_label": pattern,
})

result = pd.DataFrame(records)

result.to_csv(
    "output/capital_allocation.csv",
    index=False,
)

print("=" * 50)
print("Rows Processed :", len(result))
print("Saved -> output/capital_allocation.csv")
print("=" * 50)

conn.close()