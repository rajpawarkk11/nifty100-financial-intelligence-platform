"""
Sprint 3 Day 16
Preset Financial Screeners
"""

from src.screener.engine import run_screener


PRESETS = {

    "Quality Compounder": {

        "roe_min": {
            "column": "return_on_equity_pct",
            "operator": ">=",
            "value": 15,
        },

        "debt_to_equity_max": {
            "column": "debt_to_equity",
            "operator": "<=",
            "value": 1,
        },

        "fcf_min": {
            "column": "free_cash_flow_cr",
            "operator": ">=",
            "value": 0,
        },

        "revenue_cagr_5yr_min": {
            "column": "revenue_cagr_5yr",
            "operator": ">=",
            "value": 10,
        },
    },


    "Value Pick": {

        "pe_max": {
            "column": "pe_ratio",
            "operator": "<=",
            "value": 40,
        },

        "pb_max": {
            "column": "pb_ratio",
            "operator": "<=",
            "value": 3,
        },

        "debt_to_equity_max": {
            "column": "debt_to_equity",
            "operator": "<=",
            "value": 2,
        },

        "dividend_yield_min": {
            "column": "dividend_yield_pct",
            "operator": ">=",
            "value": 1,
        },
    },


    "Growth Accelerator": {

        "pat_cagr_5yr_min": {
            "column": "pat_cagr_5yr",
            "operator": ">=",
            "value": 20,
        },

        "revenue_cagr_5yr_min": {
            "column": "revenue_cagr_5yr",
            "operator": ">=",
            "value": 15,
        },

        "debt_to_equity_max": {
            "column": "debt_to_equity",
            "operator": "<=",
            "value": 2,
        },
    },


    "Dividend Champion": {

        "dividend_yield_min": {
            "column": "dividend_yield_pct",
            "operator": ">=",
            "value": 2,
        },

        "dividend_payout": {
            "column": "dividend_payout_ratio_pct",
            "operator": "<=",
            "value": 80,
        },

        "fcf_min": {
            "column": "free_cash_flow_cr",
            "operator": ">=",
            "value": 0,
        },
    },


    "Debt Free Blue Chip": {

        "debt": {
            "column": "debt_to_equity",
            "operator": "<=",
            "value": 0,
        },

        "roe": {
            "column": "return_on_equity_pct",
            "operator": ">=",
            "value": 12,
        },

        "sales": {
            "column": "sales",
            "operator": ">=",
            "value": 5000,
        },
    },


    "Turnaround Watch": {

        "revenue_cagr_3yr": {
            "column": "revenue_cagr_3yr",
            "operator": ">=",
            "value": 20,
        },

        "fcf": {
            "column": "free_cash_flow_cr",
            "operator": ">=",
            "value": 0,
        },
    },

}


if __name__ == "__main__":

    for name, filters in PRESETS.items():

        df = run_screener(filters)

        print(
            name,
            "=>",
            df["company_id"].nunique(),
            "companies"
        )