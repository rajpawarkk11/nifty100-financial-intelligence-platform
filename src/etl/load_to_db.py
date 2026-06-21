from pathlib import Path
import sqlite3
import pandas as pd

DB_FILE = Path("db/nifty100.db")
RAW_DIR = Path("data/raw")

FILE_CONFIG = {
    "companies": ("companies.xlsx", 1),
    "profitandloss": ("profitandloss.xlsx", 1),
    "balancesheet": ("balancesheet.xlsx", 1),
    "cashflow": ("cashflow.xlsx", 1),
    "documents": ("documents.xlsx", 1),
    "financial_ratios": ("financial_ratios.xlsx", 0),
    "market_cap": ("market_cap.xlsx", 0),
    "peer_groups": ("peer_groups.xlsx", 0),
    "sectors": ("sectors.xlsx", 0),
    "stock_prices": ("stock_prices.xlsx", 0)
}

conn = sqlite3.connect(DB_FILE)
conn.execute("PRAGMA foreign_keys = OFF")

audit_rows = []

LOAD_ORDER = [
    "companies",
    "profitandloss",
    "balancesheet",
    "cashflow",
    "documents",
    "financial_ratios",
    "market_cap",
    "peer_groups",
    "sectors",
    "stock_prices"
]

for table in LOAD_ORDER:

    file_name, header_row = FILE_CONFIG[table]

    print(f"Loading {table}...")

    df = pd.read_excel(
        RAW_DIR / file_name,
        header=header_row
    )

    df.to_sql(
        table,
        conn,
        if_exists="append",
        index=False
    )

    audit_rows.append({
        "table_name": table,
        "rows_loaded": len(df)
    })

audit_df = pd.DataFrame(audit_rows)

Path("output").mkdir(exist_ok=True)

audit_df.to_csv(
    "output/load_audit.csv",
    index=False
)

print("\nLoad Complete")
print(audit_df)

conn.commit()
conn.close()