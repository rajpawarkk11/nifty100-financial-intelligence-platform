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