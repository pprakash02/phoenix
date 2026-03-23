import pytest
import importlib.util
import pathlib

# Dynamically load the target module because its path contains spaces and unconventional characters
def _load_target_module():
    base_path = pathlib.Path(__file__).parent
    module_path = (
        base_path
        / "home"
        / "pprakash"
        / "phoenix"
        / "generated_tests"
        / "PX-6DC06898"
        / "workspace"
        / "Midterm Exam"
        / "Problem 6.py"
    )
    spec = importlib.util.spec_from_file_location("problem6", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module

_mod = _load_target_module()
largest_odd_times = _mod.largest_odd_times

def test_largest_odd_times_string_hello():
    """Regression test: the function should return the largest character occurring odd times for a string."""
    result = largest_odd_times("hello")
    assert result == "o"

def test_largest_odd_times_string_test():
    """Regression test: observed behavior for the string 'test' where the result should be 's'."""
    result = largest_odd_times("test")
    assert result == "s"

def test_largest_odd_times_empty_string():
    """Edge case: an empty string should yield None because there are no elements to evaluate."""
    result = largest_odd_times("")
    assert result is None

def test_largest_odd_times_list_of_ints():
    """Regression test: a simple list of ints should return the maximum when it appears an odd number of times."""
    result = largest_odd_times([1, 2, 3])
    assert result == 3

def test_largest_odd_times_all_even_counts():
    """Edge case: when every element appears an even number of times, the function should return None."""
    result = largest_odd_times([2, 2, 4, 4])
    assert result is None

def test_largest_odd_times_example_from_docstring():
    """Regression test using the example provided in the docstring."""
    result = largest_odd_times([3, 9, 5, 3, 5, 3])
    assert result == 9

def test_largest_odd_times_empty_list():
    """Edge case: an explicitly empty list should return None."""
    result = largest_odd_times([])
    assert result is None

def test_largest_odd_times_multiple_odd_occurrences():
    """When several numbers occur odd times, the largest such number should be returned."""
    result = largest_odd_times([1, 1, 2, 3, 3])
    assert result == 3

def test_largest_odd_times_max_even_then_odd():
    """The max element occurs an even number of times, requiring recursive filtering."""
    result = largest_odd_times([5, 5, 4, 4, 3])
    assert result == 3

def test_largest_odd_times_negative_numbers():
    """Function should correctly handle negative integers."""
    result = largest_odd_times([-1, -2, -2, -3, -3, -3])
    # -1 occurs once (odd), -2 occurs twice (even), -3 occurs three times (odd)
    # Largest odd-occurring element is -1
    assert result == -1

def test_largest_odd_times_max_even_others_odd():
    """When the maximum element occurs an even number of times, the next lower odd-occurring element is returned."""
    result = largest_odd_times([7, 7, 5])
    assert result == 5

def test_largest_odd_times_single_element():
    """A single-element list should return that element."""
    result = largest_odd_times([42])
    assert result == 42

def test_largest_odd_times_type_error_none():
    """Passing None should raise a TypeError because max() cannot operate on None."""
    with pytest.raises(TypeError):
        largest_odd_times(None)

def test_largest_odd_times_type_error_mixed_types():
    """Passing a list with mixed incomparable types should raise a TypeError."""
    with pytest.raises(TypeError):
        largest_odd_times([1, "a", 2])

def test_largest_odd_times_large_input_performance():
    """Large input sanity check: ensure the function returns a result (not None) for a sizable list."""
    large_list = [i % 10 for i in range(1000)]  # many repetitions, some odd counts
    result = largest_odd_times(large_list)
    assert result is not None

def test_largest_odd_times_unicode_string():
    """Unicode characters should be handled correctly; the max character with odd count is returned."""
    result = largest_odd_times("áéíóúáéí")
    # Characters: á (2), é (2), í (2), ó (1), ú (1) -> max odd-occurring = 'ú' (unicode point > 'ó')
    assert result == "ú"
