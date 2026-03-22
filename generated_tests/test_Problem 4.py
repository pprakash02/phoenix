import pytest
import importlib.util
import pathlib

# Dynamically load the target module because its path contains spaces.
module_path = pathlib.Path(__file__).parent / "Midterm Exam" / "Problem 4.py"
spec = importlib.util.spec_from_file_location("problem_4", module_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

is_triangular = mod.is_triangular


def test_is_triangular_zero():
    """Regression test: input 0 should return True (observed behavior)."""
    assert is_triangular(0) is True


def test_is_triangular_one():
    """Regression test: input 1 should return True (observed behavior)."""
    assert is_triangular(1) is True


def test_is_triangular_true_bool():
    """Regression test: boolean True is treated as 1 and should return True."""
    assert is_triangular(True) is True


def test_is_triangular_negative_raises():
    """The function should raise ValueError for negative integers (math domain error)."""
    with pytest.raises(ValueError):
        is_triangular(-1)


def test_is_triangular_string_raises():
    """Passing a non‑numeric string should raise a TypeError."""
    with pytest.raises(TypeError):
        is_triangular("test")


def test_is_triangular_empty_string_raises():
    """Passing an empty string should raise a TypeError."""
    with pytest.raises(TypeError):
        is_triangular("")


def test_is_triangular_none_raises():
    """Passing None should raise a TypeError."""
    with pytest.raises(TypeError):
        is_triangular(None)


def test_is_triangular_list_raises():
    """Passing a list should raise a TypeError."""
    with pytest.raises(TypeError):
        is_triangular([1, 2, 3])


def test_is_triangular_non_triangular_small():
    """Small non‑triangular number (2) should return False."""
    assert is_triangular(2) is False


def test_is_triangular_triangular_small():
    """Small triangular numbers (3, 6, 10) should return True."""
    assert is_triangular(3) is True
    assert is_triangular(6) is True
    assert is_triangular(10) is True


def test_is_triangular_large_triangular():
    """A larger triangular number (n=100 => 5050) should return True."""
    n = 100
    triangular = n * (n + 1) // 2
    assert is_triangular(triangular) is True


def test_is_triangular_large_non_triangular():
    """A large non‑triangular number should return False."""
    assert is_triangular(5051) is False


def test_is_triangular_float_triangular():
    """A float representing a triangular integer (3.0) should return True."""
    assert is_triangular(3.0) is True


def test_is_triangular_float_non_triangular():
    """A float representing a non‑triangular integer (2.5) should return False."""
    assert is_triangular(2.5) is False


def test_is_triangular_negative_float_raises():
    """Negative float should raise ValueError (math domain error)."""
    with pytest.raises(ValueError):
        is_triangular(-2.0)