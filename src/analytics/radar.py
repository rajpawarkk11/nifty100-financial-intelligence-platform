"""
Sprint 3 Day 19
Radar Chart Generator
"""

import os
import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = "db/nifty100.db"
OUTPUT_DIR = "reports/radar_charts"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True,
)

METRICS = [

    "return_on_equity_pct",
    "operating_profit_margin_pct",
    "net_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "composite_quality_score",

]


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

    return df
def plot_radar(company_row, peer_average, peer_name):

    labels = [
        "ROE",
        "OPM",
        "NPM",
        "D/E",
        "FCF",
        "PAT CAGR",
        "Revenue CAGR",
        "Composite",
    ]

    company = (
        company_row[METRICS]
        .fillna(0)
        .astype(float)
        .values
    )

    peer = (
        peer_average[METRICS]
        .fillna(0)
        .astype(float)
        .values
    )

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False,
    )

    company = np.concatenate(
        [company, [company[0]]]
    )

    peer = np.concatenate(
        [peer, [peer[0]]]
    )

    angles = np.concatenate(
        [angles, [angles[0]]]
    )

    fig = plt.figure(figsize=(8, 8))

    ax = plt.subplot(
        111,
        polar=True,
    )

    ax.plot(
        angles,
        company,
        linewidth=2,
        label=company_row["company_id"],
    )

    ax.fill(
        angles,
        company,
        alpha=0.25,
    )

    ax.plot(
        angles,
        peer,
        linestyle="--",
        linewidth=2,
        label=f"{peer_name} Average",
    )

    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels,
        fontsize=10,
    )

    plt.title(
        f"{company_row['company_id']} - {peer_name}",
        fontsize=12,
    )

    plt.legend(
        loc="upper right"
    )

    filename = os.path.join(

        OUTPUT_DIR,

        f"{company_row['company_id']}_radar.png",

    )

    plt.savefig(
        filename,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()
def generate_all_charts():

    df = load_data()

    # Nifty100 average (used for standalone charts)
    nifty_average = (
        df[METRICS]
        .fillna(0)
        .mean()
    )

    generated = 0

    for _, company in df.iterrows():

        peer_name = company["peer_group_name"]

        # Company has no peer group
        if pd.isna(peer_name):

            plot_radar(
                company,
                nifty_average,
                "Nifty100 Average",
            )

            generated += 1
            continue

        peer_df = df[
            df["peer_group_name"] == peer_name
        ]

        peer_average = (
            peer_df[METRICS]
            .fillna(0)
            .mean()
        )

        plot_radar(
            company,
            peer_average,
            peer_name,
        )

        generated += 1

    print("=" * 60)
    print("Radar Charts Generated :", generated)
    print("Output Folder :", OUTPUT_DIR)
    print("=" * 60)


if __name__ == "__main__":

    generate_all_charts()