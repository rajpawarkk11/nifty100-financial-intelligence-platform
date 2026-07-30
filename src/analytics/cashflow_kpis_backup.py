"""
Sprint 2 – Day 11
Cash Flow KPI Engine
"""

from typing import Optional


def free_cash_flow(
    operating_activity: float,
    investing_activity: float,
) -> float:
    """
    Free Cash Flow = CFO + Investing Activity
    Investing Activity is usually negative.
    """
    return operating_activity + investing_activity


def cfo_quality_score(
    cfo: float,
    pat: float,
) -> Optional[float]:

    if pat == 0:
        return None

    return round(cfo / pat, 2)


def cfo_quality_label(score):

    if score is None:
        return "N/A"

    if score > 1:
        return "High Quality"

    if score >= 0.5:
        return "Moderate"

    return "Accrual Risk"


def capex_intensity(
    investing_activity: float,
    sales: float,
):

    if sales == 0:
        return None

    return round(abs(investing_activity) / sales * 100, 2)


def capex_label(value):

    if value is None:
        return "N/A"

    if value < 3:
        return "Asset Light"

    if value <= 8:
        return "Moderate"

    return "Capital Intensive"


def fcf_conversion_rate(
    free_cash_flow_value: float,
    operating_profit: float,
):

    if operating_profit == 0:
        return None

    return round(
        free_cash_flow_value / operating_profit * 100,
        2,
    )


def capital_allocation_pattern(
    cfo: float,
    cfi: float,
    cff: float,
    cfo_pat_ratio: Optional[float] = None,
):
    """
    8-pattern classifier
    """

    sign = (
        "+" if cfo >= 0 else "-",
        "+" if cfi >= 0 else "-",
        "+" if cff >= 0 else "-",
    )

    if sign == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1:
            return "Shareholder Returns"
        return "Reinvestor"

    if sign == ("+", "+", "-"):
        return "Liquidating Assets"

    if sign == ("-", "+", "+"):
        return "Distress Signal"

    if sign == ("-", "-", "+"):
        return "Growth Funded by Debt"

    if sign == ("+", "+", "+"):
        return "Cash Accumulator"

    if sign == ("-", "-", "-"):
        return "Pre-Revenue"

    if sign == ("+", "-", "+"):
        return "Mixed"

    return "Other"