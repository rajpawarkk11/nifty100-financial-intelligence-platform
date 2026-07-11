"""
Sprint 3 Day 17
Composite Quality Score Engine
"""

import pandas as pd
import numpy as np


def winsorize_series(series):
    """
    Cap values at 10th and 90th percentile.
    """

    series = series.fillna(series.median())

    lower = series.quantile(0.10)
    upper = series.quantile(0.90)

    return series.clip(lower, upper)


def normalize(series):
    """
    Normalize to 0-100.
    """

    series = winsorize_series(series)

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return pd.Series(
            [50] * len(series),
            index=series.index,
        )

    return (
        (series - minimum)
        / (maximum - minimum)
    ) * 100


def calculate_composite_score(df):

    df = df.copy()

    # ==========================
    # Profitability (35%)
    # ==========================

    profitability = (

        normalize(df["return_on_equity_pct"]) * 0.15

        +

        normalize(df["net_profit_margin_pct"]) * 0.10

        +

        normalize(df["operating_profit_margin_pct"]) * 0.10

    )

    # ==========================
    # Cash Quality (30%)
    # ==========================

    cash_quality = (

        normalize(df["free_cash_flow_cr"]) * 0.15

        +

        normalize(df["cash_from_operations_cr"]) * 0.10

        +

        (
            df["free_cash_flow_cr"]
            .fillna(0)
            .gt(0)
            .astype(int)
            * 100
            * 0.05
        )

    )

    # ==========================
    # Growth (20%)
    # ==========================

    growth = (

        normalize(df["revenue_cagr_5yr"]) * 0.10

        +

        normalize(df["pat_cagr_5yr"]) * 0.10

    )

    # ==========================
    # Leverage (15%)
    # Lower D/E = Better
    # ==========================

    leverage = (

        (100 - normalize(df["debt_to_equity"])) * 0.10

        +

        normalize(
            df["interest_coverage"].fillna(0)
        ) * 0.05

    )

    # ==========================
    # Composite Score
    # ==========================

    df["composite_quality_score"] = (

        profitability
        + cash_quality
        + growth
        + leverage

    ).round(2)

    # ==========================
    # Sector Relative Score
    # ==========================

    if "broad_sector" in df.columns:

        df["sector_relative_score"] = (

            df.groupby("broad_sector")[
                "composite_quality_score"
            ]

            .transform(

                lambda x:

                (
                    (x - x.min())

                    /

                    (

                        x.max() - x.min()

                        if x.max() != x.min()

                        else 1

                    )

                ) * 100

            )

            .round(2)

        )

    else:

        df["sector_relative_score"] = (
            df["composite_quality_score"]
        )

    return df