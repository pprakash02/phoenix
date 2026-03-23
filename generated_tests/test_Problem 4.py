import pytest
import importlib.util
import sys
from pathlib import Path

# Dynamically load the target module from its absolute path
MODULE_PATH = Path("/home/pprakash/phoenix/generated_tests/PX-767AE5BC/workspace/Midterm Exam/Problem 4.py")
spec = importlib.util.spec_from_file_location("problem_4", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
is_triangular = module.is_triangular


def test_is_triangular_zero():
    """Regression test: 0 should be considered triangular (observed behavior)."""
    assert is_triangular(0) is True


def test_is_triangular_one():
    """Regression test: 1 is a triangular number."""
    assert is_triangular(1) is True


def test_is_triangular_bool_true():
    """Regression test: bool True (treated as 1) returns True."""
    assert is_triangular(True) is True


def test_is_triangular_negative_raises():
    """Negative input should raise a ValueError due to sqrt of a negative number."""
    with pytest.raises(ValueError):
        is_triangular(-1)


def test_is_triangular_string_raises():
    """String input should raise a TypeError when concatenated with int."""
    with pytest.raises(TypeError):
        is_triangular("test")


def test_is_triangular_empty_string_raises():
    """Empty string input should raise a TypeError."""
    with pytest.raises(TypeError):
        is_triangular("")


def test_is_triangular_large_triangular_number():
    """A known large triangular number (55) should return True."""
    assert is_triangular(55) is True  # 10th triangular number


def test_is_triangular_non_triangular_number():
    """A non‑triangular integer (56) should return False."""
    assert is_triangular(56) is False


def test_is_triangular_float_integer_value():
    """Float that represents an integer triangular number should be recognized as triangular."""
    assert is_triangular(3.0) is True  # 3 is triangular (1+2)


def test_is_triangular_float_non_integer():
    """Non‑integer float should return False."""
    assert is_triangular(4.5) is False


def test_is_triangular_bool_false():
    """Bool False (treated as 0) should return True, matching observed behavior for 0."""
    assert is_triangular(False) is True


def test_is_triangular_none_raises():
    """None input should raise a TypeError."""
    with pytest.raises(TypeError):
        is_triangular(None)