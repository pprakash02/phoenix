import pytest
import importlib.util
import os

# Dynamically load the target module since its path contains spaces and is not a valid import name.
MODULE_PATH = os.path.join(
    "/home/pprakash/phoenix/generated_tests/PX-714DB47F/workspace",
    "Midterm Exam",
    "Problem 2.py",
)

spec = importlib.util.spec_from_file_location("problem_2", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None, "Failed to locate module spec"
spec.loader.exec_module(module)

# Export the function to be tested
f = module.f


def test_f_returns_three_for_integer_zero():
    """Verify that f returns 3 when called with integer 0."""
    assert f(0) == 3


def test_f_returns_three_for_integer_one():
    """Verify that f returns 3 when called with integer 1."""
    assert f(1) == 3


def test_f_returns_three_for_negative_one():
    """Verify that f returns 3 when called with integer -1."""
    assert f(-1) == 3


def test_f_returns_three_for_string():
    """Verify that f returns 3 when called with a non‑empty string."""
    assert f("test") == 3


def test_f_returns_three_for_empty_string():
    """Verify that f returns 3 when called with an empty string."""
    assert f("") == 3


def test_f_returns_three_for_boolean_true():
    """Verify that f returns 3 when called with True (bool is a subclass of int)."""
    assert f(True) == 3


def test_f_returns_three_for_none():
    """Verify that f returns 3 when called with None."""
    assert f(None) == 3


def test_f_returns_three_for_list():
    """Verify that f returns 3 when called with a list object."""
    assert f([1, 2, 3]) == 3


def test_f_returns_three_for_dict():
    """Verify that f returns 3 when called with a dictionary object."""
    assert f({"key": "value"}) == 3


def test_f_raises_type_error_when_no_arguments():
    """Calling f without arguments should raise a TypeError."""
    with pytest.raises(TypeError):
        f()


def test_f_raises_type_error_when_too_many_arguments():
    """Calling f with more than one argument should raise a TypeError."""
    with pytest.raises(TypeError):
        f(1, 2)


def test_f_is_pure_and_ignores_input():
    """Ensure that f consistently returns 3 regardless of the input type."""
    diverse_inputs = [
        42,
        -999,
        0.0,
        3.1415,
        "random string",
        b"bytes",
        (1, 2),
        {1, 2, 3},
        object(),
    ]
    for inp in diverse_inputs:
        assert f(inp) == 3, f"f({inp!r}) did not return 3"


def test_f_return_type_is_int():
    """The return value of f should always be of type int."""
    result = f("any")
    assert isinstance(result, int)
    assert result == 3

