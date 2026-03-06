import math
import pytest
from legacy_workspace.legacy_billing import process_transaction


def test_process_transaction_success():
    result = process_transaction("100")
    assert result == 105.0


def test_process_transaction_negative_amount():
    with pytest.raises(ValueError) as exc_info:
        process_transaction("-50")
    assert "Transaction amount cannot be negative" in str(exc_info.value)


def test_process_transaction_zero_amount():
    with pytest.raises(ZeroDivisionError):
        process_transaction("0")


def test_process_transaction_invalid_input():
    with pytest.raises(ValueError) as exc_info:
        process_transaction("abc")
    assert "could not convert" in str(exc_info.value).lower()
