from pathlib import Path
import sqlite3
import pandas as pd


# --------------------------------------------------
# Project Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "db" / "nifty100.db"
MARKET_CAP_FILE = PROJECT_ROOT / "data" / "raw" / "market_cap.xlsx"

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

VALUATION_SUMMARY = OUTPUT_DIR / "valuation_summary.xlsx"
VALUATION_FLAGS = OUTPUT_DIR / "valuation_flags.csv"


# --------------------------------------------------
# Database Connection
# --------------------------------------------------

conn = sqlite3.connect(DATABASE_PATH)


# --------------------------------------------------
# Latest Financial Ratios (2024)
# --------------------------------------------------

financial_query = """
SELECT
    fr.company_id,
    c.company_name,
    s.broad_sector,

    fr.year,

    fr.free_cash_flow_cr,

    mc.pe_ratio,
    mc.pb_ratio,
    mc.ev_ebitda,
    mc.market_cap_crore

FROM financial_ratios fr

JOIN companies c
ON fr.company_id = c.id

LEFT JOIN sectors s
ON fr.company_id = s.company_id

LEFT JOIN market_cap mc
ON fr.company_id = mc.company_id
AND fr.year = mc.year

WHERE fr.year = (
    SELECT MAX(year)
    FROM financial_ratios x
    WHERE x.company_id = fr.company_id
)

ORDER BY c.company_name;
"""


valuation_df = pd.read_sql(financial_query, conn)


# --------------------------------------------------
# Market Cap Excel
# --------------------------------------------------

market_cap_df = pd.read_excel(MARKET_CAP_FILE)


market_cap_df = market_cap_df[
    market_cap_df["year"] == 2024
].copy()


market_cap_df = market_cap_df[
    [
        "company_id",
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
    ]
]


# --------------------------------------------------
# Merge
# --------------------------------------------------

valuation_df = valuation_df.drop(
    columns=[
        "market_cap_crore",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
    ],
    errors="ignore",
)


valuation_df = valuation_df.merge(

    market_cap_df,

    on="company_id",

    how="left"

)


print("Rows :", len(valuation_df))
print(valuation_df.head())

# --------------------------------------------------
# FCF Yield
# --------------------------------------------------

valuation_df["FCF_yield_pct"] = (
    valuation_df["free_cash_flow_cr"]
    / valuation_df["market_cap_crore"]
) * 100


# --------------------------------------------------
# Sector Median PE
# --------------------------------------------------

sector_median = (
    valuation_df.groupby("broad_sector")["pe_ratio"]
    .median()
    .reset_index()
)

sector_median.columns = [
    "broad_sector",
    "sector_median_pe"
]

valuation_df = valuation_df.merge(
    sector_median,
    on="broad_sector",
    how="left"
)


# --------------------------------------------------
# PE vs Sector Median
# --------------------------------------------------

valuation_df["PE_vs_sector_median_pct"] = (
    (
        valuation_df["pe_ratio"]
        - valuation_df["sector_median_pe"]
    )
    /
    valuation_df["sector_median_pe"]
) * 100


# --------------------------------------------------
# Company 5-Year Median PE
# --------------------------------------------------

history = pd.read_sql(
    """
    SELECT
        company_id,
        pe_ratio
    FROM market_cap
    WHERE pe_ratio IS NOT NULL
    """,
    conn
)

median_5yr = (
    history.groupby("company_id")["pe_ratio"]
    .median()
    .reset_index()
)

median_5yr.columns = [
    "company_id",
    "5yr_median_PE"
]

valuation_df = valuation_df.merge(
    median_5yr,
    on="company_id",
    how="left"
)


# --------------------------------------------------
# Valuation Flag
# --------------------------------------------------

def get_flag(row):

    if pd.isna(row["pe_ratio"]) or pd.isna(row["sector_median_pe"]):
        return "Fair"

    if row["pe_ratio"] > row["sector_median_pe"] * 1.5:
        return "Caution"

    if row["pe_ratio"] < row["sector_median_pe"] * 0.7:
        return "Discount"

    return "Fair"


valuation_df["flag"] = valuation_df.apply(
    get_flag,
    axis=1
)


print("\nValuation Preview\n")

print(
    valuation_df[
        [
            "company_name",
            "pe_ratio",
            "sector_median_pe",
            "FCF_yield_pct",
            "5yr_median_PE",
            "PE_vs_sector_median_pct",
            "flag",
        ]
    ].head()
)

# --------------------------------------------------
# Final Output
# --------------------------------------------------

valuation_summary = valuation_df[
    [
        "company_id",
        "company_name",
        "broad_sector",
        "pe_ratio",
        "pb_ratio",
        "ev_ebitda",
        "FCF_yield_pct",
        "5yr_median_PE",
        "PE_vs_sector_median_pct",
        "flag",
    ]
].copy()

valuation_summary.columns = [
    "company_id",
    "company_name",
    "sector",
    "P/E",
    "P/B",
    "EV/EBITDA",
    "FCF_yield_pct",
    "5yr_median_PE",
    "PE_vs_sector_median_pct",
    "flag",
]

valuation_summary = valuation_summary.round(
    {
        "P/E": 2,
        "P/B": 2,
        "EV/EBITDA": 2,
        "FCF_yield_pct": 2,
        "5yr_median_PE": 2,
        "PE_vs_sector_median_pct": 2,
    }
)


# --------------------------------------------------
# Export Excel
# --------------------------------------------------

valuation_summary.to_excel(
    VALUATION_SUMMARY,
    index=False
)


# --------------------------------------------------
# Export Flags CSV
# --------------------------------------------------

valuation_flags = valuation_summary[
    valuation_summary["flag"].isin(
        ["Caution", "Discount"]
    )
]

valuation_flags.to_csv(
    VALUATION_FLAGS,
    index=False
)


# --------------------------------------------------
# Close DB
# --------------------------------------------------

conn.close()


print("\n===================================")
print(" Day 26 Completed Successfully")
print("===================================")

print(f"\nExcel : {VALUATION_SUMMARY}")
print(f"CSV   : {VALUATION_FLAGS}")

print(f"\nTotal Companies : {len(valuation_summary)}")
print(f"Caution         : {(valuation_summary['flag']=='Caution').sum()}")
print(f"Discount        : {(valuation_summary['flag']=='Discount').sum()}")
print(f"Fair            : {(valuation_summary['flag']=='Fair').sum()}")