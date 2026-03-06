import math
import pytest

from legacy_workspace.legacy_billing import process_transaction

@pytest.mark.parametrize(
    "input_val,expected",
    [
        ("100", 105.0),
        ("1e309", math.inf),
        ("9999999999", 10499999998.95),
        ("0.01", 0.0105),
        ("   20  ", 21.0),
        ("3.14159", 3.2986695),
    ],
)
def test_process_transaction_success(input_val, expected):
    """Test successful processing of transaction amounts."""
    result = process_transaction(input_val)
    if math.isinf(expected):
        assert math.isinf(result)
    else:
        assert result == expected

@pytest.mark.parametrize(
    "input_val,expected_exception,expected_message",
    [
        ("-50", ValueError, "Transaction amount cannot be negative."),
        ("0", ZeroDivisionError, "division by zero"),
        ("abc", ValueError, "could not convert string to float: 'abc'"),
        ("", ValueError, "could not convert string to float: ''"),
    ],
)
def test_process_transaction_exceptions(input_val, expected_exception, expected_message):
    """Test that invalid inputs raise the correct exceptions with expected messages."""
    with pytest.raises(expected_exception) as exc_info:
        process_transaction(input_val)
    # Verify that the exception message contains the expected substring
    assert expected_message in str(exc_info.value)
