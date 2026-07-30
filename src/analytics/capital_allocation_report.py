import os
import pandas as pd

OUTPUT_DIR = "output"

CAPITAL_FILE = os.path.join(OUTPUT_DIR, "capital_allocation.csv")
CASHFLOW_FILE = os.path.join(OUTPUT_DIR, "cashflow_intelligence.xlsx")

SUMMARY_FILE = os.path.join(
    OUTPUT_DIR,
    "pattern_distribution_summary.csv"
)

PATTERN_CHANGES_FILE = os.path.join(
    OUTPUT_DIR,
    "pattern_changes.csv"
)


def load_data():
    capital = pd.read_csv(CAPITAL_FILE)
    cashflow = pd.read_excel(CASHFLOW_FILE)
    return capital, cashflow


def verify_dataset(capital, cashflow):
    duplicates = (
        capital
        .groupby(["company_id", "year"])
        .size()
        .reset_index(name="count")
    )

    duplicate_count = len(
        duplicates[duplicates["count"] > 1]
    )

    cashflow_companies = set(cashflow["company_id"])
    capital_companies = set(capital["company_id"])

    missing = sorted(
        cashflow_companies - capital_companies
    )

    return duplicate_count, missing


def latest_pattern_distribution(capital):
    latest = (
        capital
        .sort_values("year")
        .groupby("company_id", as_index=False)
        .tail(1)
    )

    summary = (
        latest["pattern_label"]
        .value_counts()
        .rename_axis("pattern_label")
        .reset_index(name="company_count")
    )

    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    return latest, summary


def build_pattern_changes(capital):
    capital = capital.sort_values(
        ["company_id", "year"]
    )

    rows = []

    for company, grp in capital.groupby("company_id"):

        grp = grp.reset_index(drop=True)

        if len(grp) < 2:
            continue

        previous = grp.iloc[-2]
        latest = grp.iloc[-1]

        if previous["pattern_label"] != latest["pattern_label"]:

            rows.append({
                "company_id": company,
                "previous_year": previous["year"],
                "previous_pattern": previous["pattern_label"],
                "latest_year": latest["year"],
                "latest_pattern": latest["pattern_label"],
                "changed": "Yes"
            })

    changes = pd.DataFrame(rows)

    changes.to_csv(
        PATTERN_CHANGES_FILE,
        index=False
    )

    return changes


def main():

    print("Loading files...")

    capital, cashflow = load_data()

    print("Verifying dataset...")

    duplicate_count, missing = verify_dataset(
        capital,
        cashflow
    )

    print("Generating distribution summary...")

    latest, summary = latest_pattern_distribution(
        capital
    )

    print("Generating pattern changes...")

    changes = build_pattern_changes(
        capital
    )

    print("=" * 60)
    print("Capital Allocation Report Complete")
    print("=" * 60)
    print(f"Companies           : {len(latest)}")
    print(f"Duplicate Records   : {duplicate_count}")
    print(f"Missing Companies   : {len(missing)}")
    print(f"Pattern Changes     : {len(changes)}")
    print(f"Summary CSV         : {SUMMARY_FILE}")
    print(f"Pattern Changes CSV : {PATTERN_CHANGES_FILE}")

    if missing:
        print("\nMissing Company IDs:")
        for company in missing:
            print(f" - {company}")

    print("Done.")


if __name__ == "__main__":
    main()