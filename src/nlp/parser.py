import os
import re
import logging
import pandas as pd

# -----------------------------
# Configuration
# -----------------------------

INPUT_FILE = "data/raw/analysis.xlsx"
CAGR_FILE = "output/cagr_review.csv"

OUTPUT_PARSED = "output/analysis_parsed.csv"
OUTPUT_FAILURES = "output/parse_failures.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s : %(message)s"
)

# -----------------------------
# Regex Patterns
# -----------------------------

PATTERNS = [
    r"(\d+)\s*Years?\s*:?\s*(-?[\d.]+)%",
    r"(\d+)\s*Years?\s*(-?[\d.]+)%",
    r"Last\s*Year\s*:?\s*(-?[\d.]+)%",
    r"1\s*Year\s*:?\s*(-?[\d.]+)%",
    r"TTM\s*:?\s*(-?[\d.]+)%"
]

TARGET_COLUMNS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe"
]

def parse_text(metric_name, text):

    if pd.isna(text):
        return None

    text = str(text).strip()

    for pattern in PATTERNS:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            if "TTM" in pattern:

             return {
        "metric_type": metric_name,
        "period_years": 0,
        "value_pct": float(match.group(1))
    }

            if "Last" in pattern:

                return {
                    "metric_type": metric_name,
                    "period_years": 1,
                    "value_pct": float(match.group(1))
                }

            elif "1\\s*Year" in pattern:

                return {
                    "metric_type": metric_name,
                    "period_years": 1,
                    "value_pct": float(match.group(1))
                }

            else:

                return {
                    "metric_type": metric_name,
                    "period_years": int(match.group(1)),
                    "value_pct": float(match.group(2))
                }

    return None

def load_analysis():

    logging.info("Loading analysis.xlsx...")

    df = pd.read_excel(INPUT_FILE, header=1)

    return df


def parse_analysis(df):

    parsed_rows = []
    failures = []

    for _, row in df.iterrows():

        company = row["company_id"]

        for metric in TARGET_COLUMNS:

            parsed = parse_text(metric, row[metric])

            if parsed:

                parsed_rows.append({
                    "company_id": company,
                    **parsed
                })

            else:

                failures.append({
                    "company_id": company,
                    "metric_type": metric,
                    "original_text": row[metric]
                })

    parsed_df = pd.DataFrame(parsed_rows)
    failures_df = pd.DataFrame(failures)

    return parsed_df, failures_df

def cross_validate(parsed_df):

    logging.info("Cross validating against Ratio Engine...")

    if not os.path.exists(CAGR_FILE):

        logging.warning("cagr_review.csv not found. Skipping validation.")

        return parsed_df

    ratio_df = pd.read_csv(CAGR_FILE)

    validation = []

    for _, row in parsed_df.iterrows():

        company = row["company_id"]
        period = row["period_years"]
        value = row["value_pct"]

        if row["metric_type"] == "compounded_sales_growth":

         col = f"revenue_cagr_{period}yr"

        elif row["metric_type"] == "compounded_profit_growth":

         col = f"pat_cagr_{period}yr"

        else:

            continue

        if col not in ratio_df.columns:
            continue

        company_rows = ratio_df[ratio_df["company_id"] == company]

        if company_rows.empty:
            continue

        computed = company_rows.iloc[-1][col]

        if pd.isna(computed):
            continue

        diff = abs(float(computed) - float(value))

        validation.append({
            "company_id": company,
            "metric_type": row["metric_type"],
            "period_years": period,
            "parsed_value": value,
            "computed_value": computed,
            "difference_pct": round(diff, 2),
            "review_required": diff > 5
        })

    if validation:

        validation_df = pd.DataFrame(validation)

        validation_df.to_csv(
            "output/cagr_cross_validation.csv",
            index=False
        )

    return parsed_df

def main():

    df = load_analysis()

    parsed_df, failures_df = parse_analysis(df)

    parsed_df = cross_validate(parsed_df)

    parsed_df.to_csv(
        OUTPUT_PARSED,
        index=False
    )

    failures_df.to_csv(
        OUTPUT_FAILURES,
        index=False
    )

    logging.info("Done.")
    logging.info(f"Parsed rows : {len(parsed_df)}")
    logging.info(f"Failures    : {len(failures_df)}")


if __name__ == "__main__":
    main()