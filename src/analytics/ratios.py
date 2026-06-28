"""
Profitability Ratio Engine
Sprint 2 - Day 08
"""

from typing import Optional


def net_profit_margin(net_profit: float, sales: float) -> Optional[float]:
    """Net Profit Margin (%)"""
    if sales == 0:
        return None
    return (net_profit / sales) * 100


def operating_profit_margin(
    operating_profit: float,
    sales: float
) -> Optional[float]:
    """Operating Profit Margin (%)"""
    if sales == 0:
        return None
    return (operating_profit / sales) * 100


def roe(
    net_profit: float,
    equity_capital: float,
    reserves: float
) -> Optional[float]:
    """Return on Equity (%)"""

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def roce(
    ebit: float,
    equity_capital: float,
    reserves: float,
    borrowings: float
) -> Optional[float]:
    """Return on Capital Employed (%)"""

    capital = equity_capital + reserves + borrowings

    if capital <= 0:
        return None

    return (ebit / capital) * 100


def roa(
    net_profit: float,
    total_assets: float
) -> Optional[float]:
    """Return on Assets (%)"""

    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100


def opm_cross_check(
    calculated_opm: float,
    source_opm: float
) -> bool:
    """
    Returns True if difference >1%
    """

    return abs(calculated_opm - source_opm) > 1


def log_opm_mismatch(
    company_id: str,
    year: str,
    calculated_opm: float,
    source_opm: float
):
    """
    Print OPM mismatch if difference >1%.
    """

    if opm_cross_check(calculated_opm, source_opm):
        print(
            f"[WARNING] OPM mismatch | "
            f"{company_id} | {year} | "
            f"Calculated={calculated_opm:.2f} | "
            f"Source={source_opm:.2f}"
        )


def is_financial_company(
    broad_sector: str
) -> bool:
    """
    Returns True if company belongs to Financials sector.
    """

    return broad_sector.strip().lower() == "financials"


def roce_status(
    roce_value: float,
    broad_sector: str
) -> str:
    """
    ROCE interpretation.
    """

    if roce_value is None:
        return "N/A"

    if is_financial_company(broad_sector):
        return "Financial Sector Benchmark"

    if roce_value >= 15:
        return "Good"

    if roce_value >= 10:
        return "Average"

    return "Weak"
# ==============================
# DAY 09 - LEVERAGE & EFFICIENCY
# ==============================

def debt_to_equity(
    borrowings: float,
    equity_capital: float,
    reserves: float
):
    """
    Debt to Equity Ratio

    Return 0 if company is debt free.
    Return None if equity <= 0.
    """

    if borrowings == 0:
        return 0

    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return borrowings / equity


def high_leverage_flag(
    debt_equity: float,
    broad_sector: str
):
    """
    True if D/E > 5 and NOT Financials.
    """

    if debt_equity is None:
        return False

    if is_financial_company(broad_sector):
        return False

    return debt_equity > 5


def interest_coverage_ratio(
    operating_profit: float,
    other_income: float,
    interest: float
):
    """
    Interest Coverage Ratio
    """

    if interest == 0:
        return None

    return (operating_profit + other_income) / interest


def icr_label(
    interest: float
):
    """
    Debt Free label.
    """

    if interest == 0:
        return "Debt Free"

    return ""


def icr_warning(
    icr
):
    """
    Warning if ICR < 1.5
    """

    if icr is None:
        return False

    return icr < 1.5


def net_debt(
    borrowings: float,
    investments: float
):
    """
    Net Debt
    """

    return borrowings - investments


def asset_turnover(
    sales: float,
    total_assets: float
):
    """
    Asset Turnover
    """

    if total_assets == 0:
        return None

    return sales / total_assets