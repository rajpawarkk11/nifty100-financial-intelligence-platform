"""
Sprint 3 Day 18
Peer Percentile Ranking Engine
"""

import sqlite3
import numpy as np
import pandas as pd

DB_PATH = "db/nifty100.db"


METRICS = {

    "return_on_equity_pct": False,

    "operating_profit_margin_pct": False,

    "net_profit_margin_pct": False,

    "debt_to_equity": True,

    "free_cash_flow_cr": False,

    "revenue_cagr_5yr": False,

    "pat_cagr_5yr": False,

    "eps_cagr_5yr": False,

    "interest_coverage": False,

    "asset_turnover": False,

}


def load_data():

    conn = sqlite3.connect(DB_PATH)

    ratios = pd.read_sql(
        """
        SELECT *
        FROM financial_ratios
        """,
        conn,
    )

    peers = pd.read_sql(
        """
        SELECT *
        FROM peer_groups
        """,
        conn,
    )

    conn.close()

    return ratios, peers


def percentile_rank(series, inverse=False):

    s = series.fillna(series.median())

    pct = s.rank(
        pct=True,
        method="average"
    )

    if inverse:

        pct = 1 - pct

    return (pct * 100).round(2)
def compute_peer_percentiles():

    ratios, peers = load_data()

    latest = (

        ratios
        .sort_values("year")
        .groupby("company_id")
        .tail(1)

    )

    df = latest.merge(

        peers,

        on="company_id",

        how="left",

    )

    records = []

    grouped = df.groupby("peer_group_name", dropna=False)

    for peer_name, peer_df in grouped:

        # Companies without peer group

        if pd.isna(peer_name):

            for _, row in peer_df.iterrows():

                records.append({

                    "company_id": row["company_id"],

                    "peer_group_name": "No peer group assigned",

                    "metric": None,

                    "value": None,

                    "percentile_rank": None,

                    "year": row["year"],

                })

            continue

        for metric, inverse in METRICS.items():

            if metric not in peer_df.columns:
                continue

            ranks = percentile_rank(

                peer_df[metric],

                inverse=inverse,

            )

            for idx, (_, row) in enumerate(peer_df.iterrows()):

                records.append({

                    "company_id": row["company_id"],

                    "peer_group_name": peer_name,

                    "metric": metric,

                    "value": row[metric],

                    "percentile_rank": ranks.iloc[idx],

                    "year": row["year"],

                })

    result = pd.DataFrame(records)

    return result
def save_to_sqlite(df):

    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        DROP TABLE IF EXISTS peer_percentiles
        """
    )

    df.to_sql(
        "peer_percentiles",
        conn,
        index=False,
        if_exists="replace",
    )

    conn.commit()

    count = pd.read_sql(
        """
        SELECT COUNT(*) AS total
        FROM peer_percentiles
        """,
        conn,
    )

    print("=" * 60)
    print("Peer Percentiles Generated")
    print(count)
    print("=" * 60)

    conn.close()


if __name__ == "__main__":

    df = compute_peer_percentiles()

    save_to_sqlite(df)

    print(df.head(20))