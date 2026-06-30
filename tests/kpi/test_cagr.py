from src.analytics.cagr import calculate_cagr


def test_cagr_normal():
    value, flag = calculate_cagr(100, 200, 5)
    assert round(value, 2) == 14.87
    assert flag == "OK"


def test_decline_to_loss():
    value, flag = calculate_cagr(100, -50, 5)
    assert value is None
    assert flag == "DECLINE_TO_LOSS"


def test_turnaround():
    value, flag = calculate_cagr(-100, 100, 5)
    assert value is None
    assert flag == "TURNAROUND"


def test_both_negative():
    value, flag = calculate_cagr(-100, -50, 5)
    assert value is None
    assert flag == "BOTH_NEGATIVE"


def test_zero_base():
    value, flag = calculate_cagr(0, 100, 5)
    assert value is None
    assert flag == "ZERO_BASE"


def test_invalid_period():
    value, flag = calculate_cagr(100, 200, 0)
    assert value is None
    assert flag == "INVALID_PERIOD"


def test_growth():
    value, flag = calculate_cagr(100, 150, 3)
    assert flag == "OK"


def test_same_value():
    value, flag = calculate_cagr(100, 100, 5)
    assert round(value, 2) == 0
    assert flag == "OK"


def test_large_growth():
    value, flag = calculate_cagr(100, 1000, 10)
    assert flag == "OK"


def test_small_growth():
    value, flag = calculate_cagr(100, 110, 5)
    assert flag == "OK"