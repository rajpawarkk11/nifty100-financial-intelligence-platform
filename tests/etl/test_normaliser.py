from src.etl.normaliser import (
    normalize_year,
    normalize_ticker
)


# 20 YEAR TESTS

def test_year_1():
    assert normalize_year("2024") == 2024

def test_year_2():
    assert normalize_year("FY2023") == 2023

def test_year_3():
    assert normalize_year("2022") == 2022

def test_year_4():
    assert normalize_year(2021) == 2021

def test_year_5():
    assert normalize_year(None) is None

def test_year_6():
    assert normalize_year("") is None

def test_year_7():
    assert normalize_year("FY2020-21") == 2020

def test_year_8():
    assert normalize_year("2019") == 2019

def test_year_9():
    assert normalize_year("FY2018") == 2018

def test_year_10():
    assert normalize_year("2017") == 2017

def test_year_11():
    assert normalize_year("2016") == 2016

def test_year_12():
    assert normalize_year("2015") == 2015

def test_year_13():
    assert normalize_year("2014") == 2014

def test_year_14():
    assert normalize_year("2013") == 2013

def test_year_15():
    assert normalize_year("2012") == 2012

def test_year_16():
    assert normalize_year("2011") == 2011

def test_year_17():
    assert normalize_year("2010") == 2010

def test_year_18():
    assert normalize_year("2009") == 2009

def test_year_19():
    assert normalize_year("2008") == 2008

def test_year_20():
    assert normalize_year("2007") == 2007


# 15 TICKER TESTS

def test_ticker_1():
    assert normalize_ticker("tcs") == "TCS"

def test_ticker_2():
    assert normalize_ticker("infy.ns") == "INFY"

def test_ticker_3():
    assert normalize_ticker("reliance-eq") == "RELIANCE"

def test_ticker_4():
    assert normalize_ticker(" hdfcbank ") == "HDFCBANK"

def test_ticker_5():
    assert normalize_ticker(None) is None

def test_ticker_6():
    assert normalize_ticker("sbin") == "SBIN"

def test_ticker_7():
    assert normalize_ticker("lt.ns") == "LT"

def test_ticker_8():
    assert normalize_ticker("itc") == "ITC"

def test_ticker_9():
    assert normalize_ticker("asianpaint") == "ASIANPAINT"

def test_ticker_10():
    assert normalize_ticker("axisbank") == "AXISBANK"

def test_ticker_11():
    assert normalize_ticker("kotakbank") == "KOTAKBANK"

def test_ticker_12():
    assert normalize_ticker("nestleind") == "NESTLEIND"

def test_ticker_13():
    assert normalize_ticker("sunpharma") == "SUNPHARMA"

def test_ticker_14():
    assert normalize_ticker("tatamotors") == "TATAMOTORS"

def test_ticker_15():
    assert normalize_ticker("ultracemco") == "ULTRACEMCO"