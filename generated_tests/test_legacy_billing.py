import math
import pytest
from legacy_billing import process_transaction


def test_process_transaction_100():
    assert process_transaction("100") == 105.0


def test_process_transaction_large_number():
    assert process_transaction("12345678901234567890") == 1.2962962846296295e+19


def test_process_transaction_whitespace():
    assert process_transaction("   42   ") == 44.1


def test_process_transaction_scientific_large():
    assert process_transaction("1e3") == 1050.0


def test_process_transaction_scientific_small():
    assert process_transaction("1e-3") == 0.0010500000000000002


def test_process_transaction_nan():
    result = process_transaction("NaN")
    assert math.isnan(result)


def test_process_transaction_negative():
    with pytest.raises(ValueError, match="Transaction amount cannot be negative."):
        process_transaction("-50")


def test_process_transaction_zero():
    with pytest.raises(ZeroDivisionError, match="division by zero"):
        process_transaction("0")


def test_process_transaction_non_numeric():
    with pytest.raises(ValueError, match="could not convert string to float: 'abc'"):
        process_transaction("abc")


def test_process_transaction_empty_string():
    with pytest.raises(ValueError, match="could not convert string to float: ''"):
        process_transaction("")
