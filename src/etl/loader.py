"""
Excel Loader for N100 Project.
"""

from pathlib import Path
import pandas as pd


SPECIAL_FILES = [
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx"
]


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