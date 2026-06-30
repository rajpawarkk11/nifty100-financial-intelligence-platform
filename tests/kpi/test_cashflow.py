from src.analytics.cashflow_kpis import (
    free_cash_flow,
    cfo_quality_score,
    cfo_quality_label,
    capex_intensity,
    capex_label,
    fcf_conversion_rate,
    capital_allocation_pattern,
)


def test_free_cash_flow():
    assert free_cash_flow(500, -200) == 300


def test_cfo_quality_score():
    assert cfo_quality_score(120, 100) == 1.2


def test_cfo_quality_none():
    assert cfo_quality_score(100, 0) is None


def test_cfo_quality_label():
    assert cfo_quality_label(1.2) == "High Quality"


def test_capex_intensity():
    assert capex_intensity(-200, 1000) == 20.0


def test_capex_label():
    assert capex_label(2) == "Asset Light"
    assert capex_label(5) == "Moderate"
    assert capex_label(10) == "Capital Intensive"


def test_fcf_conversion():
    assert fcf_conversion_rate(300, 600) == 50.0


def test_fcf_conversion_none():
    assert fcf_conversion_rate(300, 0) is None


def test_reinvestor():
    assert capital_allocation_pattern(100, -50, -25) == "Reinvestor"


def test_shareholder_returns():
    assert capital_allocation_pattern(
        100,
        -50,
        -20,
        1.5,
    ) == "Shareholder Returns"


def test_liquidating_assets():
    assert capital_allocation_pattern(
        100,
        20,
        -10,
    ) == "Liquidating Assets"


def test_distress_signal():
    assert capital_allocation_pattern(
        -100,
        20,
        30,
    ) == "Distress Signal"


def test_growth_funded():
    assert capital_allocation_pattern(
        -100,
        -20,
        50,
    ) == "Growth Funded by Debt"


def test_cash_accumulator():
    assert capital_allocation_pattern(
        100,
        20,
        30,
    ) == "Cash Accumulator"


def test_pre_revenue():
    assert capital_allocation_pattern(
        -100,
        -20,
        -30,
    ) == "Pre-Revenue"


def test_mixed():
    assert capital_allocation_pattern(
        100,
        -20,
        50,
    ) == "Mixed"