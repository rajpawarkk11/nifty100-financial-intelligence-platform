"""
Sprint 3 - Day 15
Financial Screener Engine
"""

import sqlite3
import yaml
import pandas as pd


CONFIG_PATH = "config/screener_config.yaml"


def load_config():

    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def load_financial_data():

    conn = sqlite3.connect("db/nifty100.db")

    df = pd.read_sql(
        """
        SELECT
            fr.*,
            s.broad_sector
        FROM financial_ratios fr
        LEFT JOIN sectors s
        ON fr.company_id = s.company_id
        """,
        conn,
    )

    conn.close()

    return df


def apply_filters(
    df,
    filters
):

    result = df.copy()

    for key, value in filters.items():

        column = value["column"]
        operator = value["operator"]
        threshold = value.get("value")

        if threshold is None:
            continue

        if column not in result.columns:
            continue


        # Financial companies skip D/E filter
        if column == "debt_to_equity":

            mask = (
                result["broad_sector"]
                .astype(str)
                .str.lower()
                == "financials"
            )

            non_financial = result[~mask]

            if operator == "<=":
                non_financial = (
                    non_financial[
                        non_financial[column]
                        <= threshold
                    ]
                )

            result = pd.concat(
                [
                    result[mask],
                    non_financial
                ]
            )

            continue


        # Debt free ICR handling
        if column == "interest_coverage":

            result[column] = (
                result[column]
                .fillna(float("inf"))
            )


        if operator == ">=":

            result = result[
                result[column] >= threshold
            ]


        elif operator == "<=":

            result = result[
                result[column] <= threshold
            ]


    if "composite_quality_score" in result.columns:

        result = result.sort_values(
            "composite_quality_score",
            ascending=False,
        )


    return result


def run_screener(
    custom_filters
):

    df = load_financial_data()

    return apply_filters(
        df,
        custom_filters,
    )


if __name__ == "__main__":

    config = load_config()

    df = load_financial_data()

    print("=" * 50)
    print("Companies Loaded:", df["company_id"].nunique())
    print("Rows Loaded:", len(df))
    print("Available Filters:",
          len(config["filters"]))
    print("=" * 50)