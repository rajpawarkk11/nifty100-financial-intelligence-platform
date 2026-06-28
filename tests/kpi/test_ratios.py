from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    roe,
    roce,
    roa,
    opm_cross_check,
)


def test_net_profit_margin_normal():
    assert round(net_profit_margin(200, 1000), 2) == 20.00


def test_net_profit_margin_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_roe_normal():
    assert round(roe(100, 200, 300), 2) == 20.00


def test_roe_negative_equity():
    assert roe(100, -100, 50) is None


def test_roa_normal():
    assert round(roa(120, 600), 2) == 20.00


def test_roa_zero_assets():
    assert roa(120, 0) is None


def test_opm_cross_check_match():
    calculated = operating_profit_margin(200, 1000)
    assert opm_cross_check(calculated, 20.5) is False


def test_opm_cross_check_mismatch():
    calculated = operating_profit_margin(200, 1000)
    assert opm_cross_check(calculated, 22.5) is True

from src.analytics.ratios import (
    debt_to_equity,
    high_leverage_flag,
    interest_coverage_ratio,
    icr_label,
    icr_warning,
    net_debt,
    asset_turnover
)


def test_debt_to_equity_normal():
    assert debt_to_equity(100, 50, 50) == 1


def test_debt_to_equity_debt_free():
    assert debt_to_equity(0, 50, 50) == 0


def test_interest_coverage_normal():
    assert interest_coverage_ratio(100, 20, 20) == 6


def test_interest_coverage_zero_interest():
    assert interest_coverage_ratio(100, 20, 0) is None


def test_icr_label():
    assert icr_label(0) == "Debt Free"


def test_high_leverage_flag():
    assert high_leverage_flag(6, "Healthcare") is True


def test_net_debt():
    assert net_debt(500, 120) == 380


def test_asset_turnover():
    assert asset_turnover(1000, 500) == 2