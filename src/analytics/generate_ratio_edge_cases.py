import sqlite3
import pandas as pd
from pathlib import Path

conn = sqlite3.connect("db/nifty100.db")

df = pd.read_sql("""
SELECT
    fr.company_id,
    fr.year,
    fr.return_on_equity_pct,
    c.roe_percentage,
    c.roce_percentage,
    s.broad_sector
FROM financial_ratios fr
LEFT JOIN companies c
ON fr.company_id = c.id
LEFT JOIN sectors s
ON fr.company_id = s.company_id
ORDER BY fr.company_id, fr.year
""", conn)

conn.close()

Path("output").mkdir(exist_ok=True)

count = 0

with open(
    "output/ratio_edge_cases.log",
    "w",
    encoding="utf-8"
) as log_file:

    for _, row in df.iterrows():

        is_financial = (
            str(row["broad_sector"]).strip().lower()
            == "financials"
        )

        # -----------------------
        # ROE Cross Check
        # -----------------------
        if (
            pd.notna(row["roe_percentage"])
            and
            pd.notna(row["return_on_equity_pct"])
        ):

            diff = abs(
                row["roe_percentage"]
                - row["return_on_equity_pct"]
            )

            if diff > 5:

                if row["roe_percentage"] < 1:
                    category = "Data Source Issue"
                elif diff > 20:
                    category = "Formula Discrepancy"
                else:
                    category = "Version Difference"

                log_file.write(
                    f"[ROE] "
                    f"{row['company_id']} "
                    f"{row['year']} "
                    f"Source={row['roe_percentage']:.2f} "
                    f"Calculated={row['return_on_equity_pct']:.2f} "
                    f"Difference={diff:.2f} "
                    f"Category={category}\n"
                )

                count += 1

        # -----------------------
        # ROCE Cross Check
        # -----------------------
        if pd.notna(row["roce_percentage"]):

            if is_financial:

                log_file.write(
                    f"[INFO] "
                    f"{row['company_id']} "
                    f"{row['year']} "
                    f"Financial sector carve-out applied\n"
                )

                continue

            if pd.notna(row["return_on_equity_pct"]):

                diff = abs(
                    row["roce_percentage"]
                    - row["return_on_equity_pct"]
                )

                if diff > 5:

                    log_file.write(
                        f"[ROCE] "
                        f"{row['company_id']} "
                        f"{row['year']} "
                        f"Source={row['roce_percentage']:.2f} "
                        f"Calculated={row['return_on_equity_pct']:.2f} "
                        f"Difference={diff:.2f} "
                        f"Category=Formula Discrepancy\n"
                    )

                    count += 1

print("=" * 50)
print("Edge Cases Logged :", count)
print("Saved -> output/ratio_edge_cases.log")
print("=" * 50)