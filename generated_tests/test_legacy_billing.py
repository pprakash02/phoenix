import math
import pytest
from legacy_workspace.legacy_billing import process_transaction


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("100", 105.0),
        ("99.99", 104.98949999999999),
        ("1e10", 10500000000.0),
        ("00100", 105.0),
    ],
)
def test_successful_mappings(inp, expected):
    assert process_transaction(inp) == expected


@pytest.mark.parametrize(
    "inp,exc_type,msg",
    [
        ("-5", ValueError, "Transaction amount cannot be negative."),
        ("0", ZeroDivisionError, "division by zero"),
        ("abc", ValueError, "could not convert string to float: 'abc'"),
        ("", ValueError, "could not convert string to float: ''"),
        ("   ", ValueError, "could not convert string to float: '   '"),
    ],
)
def test_crashes(inp, exc_type, msg):
    with pytest.raises(exc_type, match=msg):
        process_transaction(inp)
