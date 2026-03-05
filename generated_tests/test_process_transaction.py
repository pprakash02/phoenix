import pytest
import math
from legacy_workspace.legacy_billing import process_transaction

@pytest.mark.parametrize(
    "input_value,expected",
    [
        ("100", 105.0),
        ("1e309", "Infinity"),
        ("1e-309", 1.050000000000004e-309),
        ("   200   ", 210.0),
        ("100.5", 105.525),
    ],
)
def test_process_transaction_success(input_value, expected):
    """Test successful executions of process_transaction."""
    result = process_transaction(input_value)
    if expected == "Infinity":
        assert math.isinf(result) and result > 0
    else:
        assert result == expected

@pytest.mark.parametrize(
    "input_value,expected_exception",
    [
        ("0", ZeroDivisionError),
        ("-50", ValueError),
        ("abc", ValueError),
        ("", ValueError),
        ("0.0", ZeroDivisionError),
    ],
)
def test_process_transaction_exceptions(input_value, expected_exception):
    """Test that process_transaction raises expected exceptions for invalid inputs."""
    with pytest.raises(expected_exception):
        process_transaction(input_value)
