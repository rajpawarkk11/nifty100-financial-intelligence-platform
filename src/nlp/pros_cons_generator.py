import os
import pandas as pd

OUTPUT_DIR = "output"
RAW_DIR = "data/raw"

CAGR_FILE = os.path.join(OUTPUT_DIR, "cagr_review.csv")
LEVERAGE_FILE = os.path.join(OUTPUT_DIR, "leverage_review.csv")
CAPITAL_FILE = os.path.join(OUTPUT_DIR, "capital_allocation.csv")
VALUATION_FILE = os.path.join(OUTPUT_DIR, "valuation_flags.csv")

RATIOS_FILE = os.path.join(RAW_DIR, "financial_ratios.xlsx")
MARKET_FILE = os.path.join(RAW_DIR, "market_cap.xlsx")
BALANCE_FILE = os.path.join(RAW_DIR, "balancesheet.xlsx")
PL_FILE = os.path.join(RAW_DIR, "profitandloss.xlsx")

OUTPUT_FILE = os.path.join(OUTPUT_DIR, "pros_cons_generated.csv")

def load_csv(path):
    return pd.read_csv(path)


def load_excel(path, **kwargs):
    return pd.read_excel(path, **kwargs)


def add_rule(records, company_id, rule_type, rule_id, text, confidence):

    print(company_id, rule_type, rule_id)

    if confidence > 60:
        records.append(
            {
                "company_id": company_id,
                "type": rule_type,
                "rule_id": rule_id,
                "text": text,
                "confidence_pct": confidence,
            }
        )


def load_data():

    data = {}

    data["cagr"] = load_csv(CAGR_FILE)
    data["leverage"] = load_csv(LEVERAGE_FILE)
    data["capital"] = load_csv(CAPITAL_FILE)
    data["valuation"] = load_csv(VALUATION_FILE)

    data["ratios"] = load_excel(RATIOS_FILE)
    data["market"] = load_excel(MARKET_FILE)

    data["balance"] = load_excel(BALANCE_FILE, header=1)
    data["profit"] = load_excel(PL_FILE, header=1)

    return data

def latest(df):

    return (
        df.sort_values("year")
        .groupby("company_id")
        .tail(1)
        .reset_index(drop=True)
    )

def latest(df):

    return (
        df.sort_values("year")
        .groupby("company_id")
        .tail(1)
        .reset_index(drop=True)
    )

def latest_by_company(df):
    return (
        df.sort_values("year")
        .groupby("company_id")
        .tail(1)
        .set_index("company_id")
    )


def last_n(df, company_id, n=5):
    return (
        df[df["company_id"] == company_id]
        .sort_values("year")
        .tail(n)
        .reset_index(drop=True)
    )


def increasing(series):
    s = series.dropna().tolist()
    return len(s) >= 3 and all(s[i] > s[i - 1] for i in range(1, len(s)))


def decreasing(series):
    s = series.dropna().tolist()
    return len(s) >= 3 and all(s[i] < s[i - 1] for i in range(1, len(s)))


def consecutive_positive(series, years):
    s = series.tail(years)
    return len(s) == years and (s > 0).all()


def consecutive_negative(series, years):
    s = series.tail(years)
    return len(s) == years and (s < 0).all()



def generate():

    data = load_data()

    records = []

    cagr = data["cagr"]
    leverage = data["leverage"]
    capital = data["capital"]
    valuation = data["valuation"]
    ratios = data["ratios"]
    market = data["market"]

    latest_ratio = latest_by_company(ratios)
    latest_leverage = latest_by_company(leverage)
    latest_capital = latest_by_company(capital)
    latest_market = latest_by_company(market)
    latest_cagr = latest_by_company(cagr)

    companies = sorted(latest_market.index)

    for company in companies:

        print(company)

        m = latest_market.loc[company]

        r = (
            latest_ratio.loc[company]
            if company in latest_ratio.index
            else pd.Series(dtype="object")
        )

        l = (
            latest_leverage.loc[company]
            if company in latest_leverage.index
            else pd.Series(dtype="object")
        )

        c = (
            latest_capital.loc[company]
            if company in latest_capital.index
            else pd.Series(dtype="object")
        )

        g = (
            latest_cagr.loc[company]
            if company in latest_cagr.index
            else pd.Series(dtype="object")
        )

        hist = last_n(ratios, company, 5)

        if hist.empty:
            hist = pd.DataFrame()

        # ---------------- PRO 1 ----------------
        if (
            "return_on_equity_pct" in hist.columns
            and len(hist) >= 3
            and (hist["return_on_equity_pct"].tail(3) > 20).all()
        ):
            add_rule(
                records,
                company,
                "pro",
                "PRO_01",
                "Consistently high return on equity above 20% demonstrates exceptional capital efficiency",
                95,
            )

        # ---------------- PRO 2 ----------------
        if (
            "free_cash_flow_cr" in hist.columns
            and consecutive_positive(hist["free_cash_flow_cr"], 5)
        ):
            add_rule(
                records,
                company,
                "pro",
                "PRO_02",
                "Strong free cash flow generation over 5 years signals healthy business fundamentals",
                90,
            )

        # ---------------- PRO 3 ----------------
        if (
            pd.notna(l.get("debt_to_equity"))
            and l.get("debt_to_equity") == 0
        ):
            add_rule(
                records,
                company,
                "pro",
                "PRO_03",
                "Debt-free balance sheet provides financial flexibility and eliminates interest burden",
                90,
            )

        # ---------------- PRO 4 ----------------
        if (
            pd.notna(g.get("revenue_cagr_5yr"))
            and g.get("revenue_cagr_5yr") > 15
        ):
            add_rule(
                records,
                company,
                "pro",
                "PRO_04",
                "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum",
                85,
            )

                    # ---------------- PRO 5 ----------------
        if (
            pd.notna(r.get("operating_profit_margin_pct"))
            and r.get("operating_profit_margin_pct") > 25
        ):
            add_rule(
                records,
                company,
                "pro",
                "PRO_05",
                "Operating profit margin above 25% indicates strong pricing power and cost discipline",
                88,
            )

        # ---------------- PRO 6 ----------------
        if (
            pd.notna(g.get("pat_cagr_5yr"))
            and g.get("pat_cagr_5yr") > 20
        ):
            add_rule(
                records,
                company,
                "pro",
                "PRO_06",
                "Net profit compounding at above 20% over 5 years creates significant shareholder value",
                90,
            )

        # ---------------- PRO 7 ----------------
        if (
            (pd.notna(l.get("interest_coverage")) and l.get("interest_coverage") > 10)
            or
            (pd.notna(l.get("debt_to_equity")) and l.get("debt_to_equity") == 0)
        ):
            add_rule(
                records,
                company,
                "pro",
                "PRO_07",
                "Very high interest coverage ratio reflects negligible financial stress from debt servicing",
                88,
            )

        # ---------------- PRO 8 ----------------
        if (
            "free_cash_flow" in c.index
            and pd.notna(c.get("free_cash_flow"))
            and pd.notna(m.get("dividend_yield_pct"))
            and m.get("dividend_yield_pct") > 2
            and c.get("free_cash_flow") > 0
        ):
            add_rule(
                records,
                company,
                "pro",
                "PRO_08",
                "Consistent dividend yield above 2% backed by positive free cash flow",
                82,
            )

        # ---------------- PRO 9 ----------------
        if (
            pd.notna(g.get("eps_cagr_5yr"))
            and g.get("eps_cagr_5yr") > 15
        ):
            add_rule(
                records,
                company,
                "pro",
                "PRO_09",
                "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding",
                88,
            )

                    # ---------------- PRO 10 ----------------
        if "return_on_equity_pct" in hist.columns:

            roe_hist = hist["return_on_equity_pct"].dropna().tail(3)

            if len(roe_hist) >= 3 and increasing(roe_hist):

                add_rule(
                    records,
                    company,
                    "pro",
                    "PRO_10",
                    "Return on equity improving for 3 consecutive years shows strengthening business quality",
                    85,
                )

        # ---------------- PRO 11 ----------------
        if (
            pd.notna(g.get("revenue_cagr_5yr"))
            and pd.notna(g.get("pat_cagr_5yr"))
            and g.get("pat_cagr_5yr") > g.get("revenue_cagr_5yr")
        ):

            add_rule(
                records,
                company,
                "pro",
                "PRO_11",
                "Revenue growing slower than profits shows improving operating leverage and scale benefits",
                80,
            )

        # ---------------- PRO 12 ----------------
        if (
            "total_assets" in hist.columns
            and "total_debt_cr" in hist.columns
        ):

            assets = hist["total_assets"].dropna()
            debt = hist["total_debt_cr"].dropna()

            if (
                len(assets) >= 3
                and len(debt) >= 3
                and increasing(assets.tail(3))
                and decreasing(debt.tail(3))
            ):

                add_rule(
                    records,
                    company,
                    "pro",
                    "PRO_12",
                    "Growing asset base funded by internal accruals reflects self-sustaining growth",
                    82,
                )

                        # ---------------- CON 1 ----------------
        if (
            pd.notna(l.get("debt_to_equity"))
            and l.get("debt_to_equity") > 2
        ):
            add_rule(
                records,
                company,
                "con",
                "CON_01",
                f"Debt-to-equity ratio of {l.get('debt_to_equity'):.2f} is elevated for a non-financial company and warrants monitoring",
                90,
            )

        # ---------------- CON 2 ----------------
        if (
            "free_cash_flow_cr" in hist.columns
            and consecutive_negative(hist["free_cash_flow_cr"], 3)
        ):
            add_rule(
                records,
                company,
                "con",
                "CON_02",
                "Free cash flow negative for 3 consecutive years raises concern about cash generation quality",
                90,
            )

        # ---------------- CON 3 ----------------
        if "operating_profit_margin_pct" in hist.columns:

            opm_hist = hist["operating_profit_margin_pct"].dropna().tail(3)

            if len(opm_hist) >= 3 and decreasing(opm_hist):

                add_rule(
                    records,
                    company,
                    "con",
                    "CON_03",
                    "Operating margins declining for 3 consecutive years suggest pricing or cost pressure",
                    85,
                )

        # ---------------- CON 4 ----------------
        if (
            "net_profit" in hist.columns
            and not hist.empty
            and pd.notna(hist.iloc[-1]["net_profit"])
            and hist.iloc[-1]["net_profit"] < 0
        ):
            add_rule(
                records,
                company,
                "con",
                "CON_04",
                "Company reported a net loss in the most recent financial year",
                95,
            )

        # ---------------- CON 5 ----------------
        if "revenue" in hist.columns:

            revenue_hist = hist["revenue"].dropna().tail(2)

            if len(revenue_hist) == 2 and decreasing(revenue_hist):

                add_rule(
                    records,
                    company,
                    "con",
                    "CON_05",
                    "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss",
                    85,
                )

        # ---------------- CON 6 ----------------
        if (
            pd.notna(l.get("interest_coverage"))
            and l.get("interest_coverage") < 1.5
        ):
            add_rule(
                records,
                company,
                "con",
                "CON_06",
                "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations",
                95,
            )

                    # ---------------- CON 7 ----------------
        if (
            pd.notna(r.get("dividend_payout_ratio_pct"))
            and r.get("dividend_payout_ratio_pct") > 100
        ):
            add_rule(
                records,
                company,
                "con",
                "CON_07",
                "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable",
                90,
            )

        # ---------------- CON 8 ----------------
        if "debt_to_equity" in hist.columns:

            debt_hist = hist["debt_to_equity"].dropna().tail(3)

            if len(debt_hist) >= 3 and increasing(debt_hist):

                add_rule(
                    records,
                    company,
                    "con",
                    "CON_08",
                    "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk",
                    82,
                )

        # ---------------- CON 9 ----------------
        if "earnings_per_share" in hist.columns:

            eps_hist = hist["earnings_per_share"].dropna().tail(3)

            if len(eps_hist) >= 3 and decreasing(eps_hist):

                add_rule(
                    records,
                    company,
                    "con",
                    "CON_09",
                    "Earnings per share declining for 3 consecutive years reflects deteriorating profitability",
                    82,
                )

        # ---------------- CON 10 ----------------
        if (
            "return_on_capital_employed_pct" in hist.columns
            and not hist.empty
            and pd.notna(hist.iloc[-1]["return_on_capital_employed_pct"])
            and hist.iloc[-1]["return_on_capital_employed_pct"] < 10
        ):
            add_rule(
                records,
                company,
                "con",
                "CON_10",
                "Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital",
                85,
            )

        # ---------------- CON 11 ----------------
        if (
            "ebitda" in hist.columns
            and not hist.empty
            and pd.notna(l.get("net_debt"))
        ):

            ebitda = hist.iloc[-1]["ebitda"]

            if (
                pd.notna(ebitda)
                and ebitda != 0
                and l.get("net_debt") > (3 * ebitda)
            ):
                add_rule(
                    records,
                    company,
                    "con",
                    "CON_11",
                    "Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility",
                    90,
                )

        # ---------------- CON 12 ----------------
        if (
            pd.notna(g.get("revenue_cagr_5yr"))
            and g.get("revenue_cagr_5yr") < 5
        ):
            add_rule(
                records,
                company,
                "con",
                "CON_12",
                "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum",
                80,
            )

    # ---------------- Ensure every company has at least 1 PRO and 1 CON ----------------

    for company in companies:

        company_records = [x for x in records if x["company_id"] == company]

        has_pro = any(x["type"] == "pro" for x in company_records)
        has_con = any(x["type"] == "con" for x in company_records)

        if not has_pro:
            add_rule(
                records,
                company,
                "pro",
                "PRO_DEFAULT",
                "No major positive financial signal met the high-confidence threshold.",
                61,
            )

        if not has_con:
            add_rule(
                records,
                company,
                "con",
                "CON_DEFAULT",
                "No major financial risk signal met the high-confidence threshold.",
                61,
            )


                # ---------------- Sort & Validate Output ----------------

    df = (
        pd.DataFrame(records)
        .sort_values(
            by=["company_id", "type", "confidence_pct"],
            ascending=[True, True, False],
        )
        .reset_index(drop=True)
    )

    summary = (
        df.groupby(["company_id", "type"])
        .size()
        .unstack(fill_value=0)
    )

    assert (summary["pro"] >= 1).all(), "Some companies are missing PRO rules."
    assert (summary["con"] >= 1).all(), "Some companies are missing CON rules."

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Generated {len(df)} pros/cons")
    print(f"Companies: {df['company_id'].nunique()}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    generate()