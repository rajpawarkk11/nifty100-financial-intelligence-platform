import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("output")

validation_results = []


def add_failure(rule, severity, table_name, message):
    validation_results.append({
        "rule": rule,
        "severity": severity,
        "table": table_name,
        "message": message
    })


# ==========================
# DQ-01
# Company PK uniqueness
# ==========================

companies = pd.read_excel(
    RAW_DIR / "companies.xlsx",
    header=1
)

if companies["id"].duplicated().any():

    add_failure(
        "DQ-01",
        "CRITICAL",
        "companies.xlsx",
        "Duplicate company ID found"
    )


# ==========================
# DQ-02
# (company_id, year) uniqueness
# ==========================

for file_name in [
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx"
]:

    df = pd.read_excel(
        RAW_DIR / file_name,
        header=1
    )

    if df[
        ["company_id", "year"]
    ].duplicated().any():

        add_failure(
            "DQ-02",
            "CRITICAL",
            file_name,
            "Duplicate (company_id, year)"
        )


# ==========================
# DQ-03
# FK Integrity
# ==========================

valid_ids = set(
    companies["id"]
)

for file_name in [
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "financial_ratios.xlsx",
    "market_cap.xlsx",
    "sectors.xlsx",
    "stock_prices.xlsx"
]:

    if file_name in [
        "financial_ratios.xlsx",
        "market_cap.xlsx",
        "sectors.xlsx",
        "stock_prices.xlsx"
    ]:

        df = pd.read_excel(
            RAW_DIR / file_name
        )

    else:

        df = pd.read_excel(
            RAW_DIR / file_name,
            header=1
        )

    invalid = ~df["company_id"].isin(valid_ids)

    if invalid.any():

        add_failure(
            "DQ-03",
            "CRITICAL",
            file_name,
            f"{invalid.sum()} invalid company IDs"
        )


# ==========================
# DQ-04
# Balance Sheet Check
# ==========================

bs = pd.read_excel(
    RAW_DIR / "balancesheet.xlsx",
    header=1
)

bs["difference_pct"] = (
    abs(
        bs["total_assets"]
        - bs["total_liabilities"]
    )
    /
    bs["total_assets"]
) * 100

if (bs["difference_pct"] > 1).any():

    add_failure(
        "DQ-04",
        "WARNING",
        "balancesheet.xlsx",
        f"{(bs['difference_pct'] > 1).sum()} rows failed balance sheet check"
    )


# ==========================
# DQ-05
# OPM Cross Check
# ==========================

pl = pd.read_excel(
    RAW_DIR / "profitandloss.xlsx",
    header=1
)

pl = pl[
    pl["sales"] > 0
]

pl["calc_opm"] = (
    pl["operating_profit"]
    /
    pl["sales"]
) * 100

pl["opm_diff"] = abs(
    pl["calc_opm"]
    -
    pl["opm_percentage"]
)

if (pl["opm_diff"] > 1).any():

    add_failure(
        "DQ-05",
        "WARNING",
        "profitandloss.xlsx",
        f"{(pl['opm_diff'] > 1).sum()} rows failed OPM validation"
    )


# ==========================
# DQ-06
# Positive Sales
# ==========================

negative_sales = pl[
    pl["sales"] <= 0
]

if len(negative_sales) > 0:

    add_failure(
        "DQ-06",
        "WARNING",
        "profitandloss.xlsx",
        f"{len(negative_sales)} rows have non-positive sales"
    )


# ==========================
# Export Results
# ==========================

OUTPUT_DIR.mkdir(
    exist_ok=True
)

result_df = pd.DataFrame(
    validation_results
)

if result_df.empty:

    result_df = pd.DataFrame([
        {
            "rule": "NONE",
            "severity": "INFO",
            "table": "ALL",
            "message": "No validation failures"
        }
    ])

result_df.to_csv(
    OUTPUT_DIR /
    "validation_failures.csv",
    index=False
)

print(result_df)
print("\nValidation Complete")