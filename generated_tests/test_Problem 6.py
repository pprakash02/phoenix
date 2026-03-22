import pytest
import importlib.util
import pathlib

# Dynamically load the target module since its path contains spaces
_module_path = pathlib.Path(
    "/home/pprakash/phoenix/generated_tests/PX-714DB47F/workspace/Midterm Exam/Problem 6.py"
)
_spec = importlib.util.spec_from_file_location("problem6", _module_path)
_problem6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_problem6)

largest_odd_times = _problem6.largest_odd_times


def test_largest_odd_times_basic_example():
    """Typical example from the docstring: largest odd-occurring element."""
    assert largest_odd_times([3, 9, 5, 3, 5, 3]) == 9


def test_largest_odd_times_no_odd_occurrences():
    """When no element occurs an odd number of times, function should return None."""
    assert largest_odd_times([2, 2, 4, 4]) is None


def test_largest_odd_times_single_odd_element():
    """Single element list should be returned (occurs once, which is odd)."""
    assert largest_odd_times([42]) == 42


def test_largest_odd_times_all_even_except_one():
    """Largest element occurs even times, fallback to next odd-occurring element."""
    assert largest_odd_times([5, 5, 3]) == 3


def test_largest_odd_times_recursive_case():
    """Recursive removal of the current max when it occurs an even number of times."""
    # 4 occurs twice (even), 2 occurs once (odd) -> should return 2
    assert largest_odd_times([2, 4, 4, 2]) == 2


def test_largest_odd_times_negative_numbers():
    """Function should handle negative integers correctly."""
    assert largest_odd_times([-1, -3, -1, -3, -5]) == -5


def test_largest_odd_times_mixed_positive_and_negative():
    """Mixed signs with odd occurrences."""
    assert largest_odd_times([-2, 1, -2, 3, 1, 3, 3]) == 3


def test_largest_odd_times_string_input():
    """String input is iterable; function should return the highest character occurring odd times."""
    assert largest_odd_times("hello") == "o"
    assert largest_odd_times("test") == "t"
    assert largest_odd_times("") is None


def test_largest_odd_times_list_of_strings():
    """List containing a single string behaves like a string input."""
    assert largest_odd_times(["hello"]) == "o"
    assert largest_odd_times(["test"]) == "t"
    assert largest_odd_times([""]) is None


def test_largest_odd_times_list_of_lists():
    """List of comparable items (e.g., lists) where max works."""
    assert largest_odd_times([[1, 2, 3]]) == [1, 2, 3]


def test_largest_odd_times_empty_list():
    """Explicit empty list should return None."""
    assert largest_odd_times([]) is None


def test_largest_odd_times_non_comparable_elements():
    """When elements cannot be compared, max() should raise a TypeError."""
    with pytest.raises(TypeError):
        largest_odd_times([1, "a"])


def test_largest_odd_times_none_input():
    """Passing None instead of a list should raise a TypeError."""
    with pytest.raises(TypeError):
        largest_odd_times(None)


def test_largest_odd_times_large_input():
    """Large input where an odd-occurring element exists; ensure function returns a value."""
    large_list = [i for i in range(1000)] + [500]  # 500 occurs twice (even), 999 occurs once (odd)
    assert largest_odd_times(large_list) == 999


def test_largest_odd_times_all_even_occurrences():
    """All elements occur an even number of times; should return None."""
    assert largest_odd_times([1, 1, 2, 2, 3, 3]) is None


def test_largest_odd_times_multiple_odd_occurrences():
    """Multiple elements occur odd times; should return the largest among them."""
    assert largest_odd_times([7, 7, 5, 5, 5, 3, 3, 3]) == 7


def test_largest_odd_times_single_element_even_times():
    """Single element occurring an even number of times should result in None."""
    assert largest_odd_times([10, 10]) is None


def test_largest_odd_times_duplicate_max_even_then_odd():
    """Max element appears even times, next max appears odd times."""
    assert largest_odd_times([8, 8, 7, 7, 7]) == 7


def test_largest_odd_times_unicode_characters():
    """String with Unicode characters; max should respect Unicode ordering."""
    assert largest_odd_times("áéíóú") == "ú"  # each char occurs once (odd) and 'ú' is max


def test_largest_odd_times_mixed_types_same_comparable():
    """Elements of same type that are comparable (e.g., tuples)."""
    assert largest_odd_times([(1, 2), (3, 4), (1, 2)]) == (3, 4)