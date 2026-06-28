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