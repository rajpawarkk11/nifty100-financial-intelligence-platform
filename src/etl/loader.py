"""
Excel Loader + SQLite Connection
for N100 Financial Intelligence Platform
"""

from pathlib import Path
import sqlite3
import pandas as pd

DB_FILE = Path("db/nifty100.db")

SPECIAL_FILES = [
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx"
]


def get_connection():
    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


def load_excel(file_path):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"{file_path} not found"
        )

    if file_path.name in SPECIAL_FILES:

        df = pd.read_excel(
            file_path,
            header=1
        )

    else:

        df = pd.read_excel(
            file_path
        )

    return df


if __name__ == "__main__":

    conn = get_connection()

    print("Database Connected")

    conn.close()

    print("Connection Closed")