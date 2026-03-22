import pytest
import importlib.util
import os

# Dynamically load the target module because its path contains spaces
MODULE_PATH = os.path.abspath(
    "/home/pprakash/phoenix/generated_tests/PX-714DB47F/workspace/Midterm Exam/Problem 9.py"
)
spec = importlib.util.spec_from_file_location("problem_9", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

is_list_permutation = module.is_list_permutation


def test_is_list_permutation_basic_permutation_strings():
    """Two lists with the same string elements in different order should be permutations."""
    L1 = ["a", "a", "b"]
    L2 = ["b", "a", "a"]
    result = is_list_permutation(L1, L2)
    assert result == ("a", 2, str)


def test_is_list_permutation_basic_permutation_mixed():
    """Lists containing both ints and strings that are permutations should return the most common element."""
    L1 = [1, "b", 1, "c", "c", 1]
    L2 = ["c", 1, "b", 1, 1, "c"]
    result = is_list_permutation(L1, L2)
    assert result == (1, 3, int)


def test_is_list_permutation_not_permutation():
    """When the lists are not permutations, the function must return False."""
    L1 = ["a", "a", "b"]
    L2 = ["a", "b"]
    assert is_list_permutation(L1, L2) is False


def test_is_list_permutation_empty_lists():
    """Both empty lists should yield the sentinel tuple (None, None, None)."""
    assert is_list_permutation([], []) == (None, None, None)


def test_is_list_permutation_non_iterable_inputs_int():
    """Passing non‑iterable arguments (e.g., integers) should raise TypeError."""
    with pytest.raises(TypeError):
        is_list_permutation(0, 0)


def test_is_list_permutation_non_iterable_inputs_float():
    """Passing non‑iterable arguments (e.g., floats) should raise TypeError."""
    with pytest.raises(TypeError):
        is_list_permutation(1.5, 1.5)


def test_is_list_permutation_non_iterable_inputs_bool():
    """Passing non‑iterable arguments (e.g., booleans) should raise TypeError."""
    with pytest.raises(TypeError):
        is_list_permutation(True, True)


def test_is_list_permutation_non_iterable_inputs_negative_int():
    """Passing non‑iterable negative integers should raise TypeError."""
    with pytest.raises(TypeError):
        is_list_permutation(-1, -1)


def test_is_list_permutation_unhashable_elements():
    """Lists containing unhashable elements (e.g., inner lists) should raise a TypeError from Counter."""
    L1 = [[1, 2], [3, 4]]
    L2 = [[3, 4], [1, 2]]
    with pytest.raises(TypeError):
        is_list_permutation(L1, L2)


def test_is_list_permutation_bool_int_equivalence():
    """True and 1 are considered equal (both hash to the same key). The function should handle this correctly."""
    L1 = [True, True, False]
    L2 = [1, 1, 0]
    result = is_list_permutation(L1, L2)
    # The most common element could be either True or 1; both have count 2 and type bool or int respectively.
    assert result[1] == 2
    assert result[0] in (True, 1)
    assert result[2] in (bool, int)


def test_is_list_permutation_tie_between_elements():
    """When multiple elements share the highest frequency, any one may be returned."""
    L1 = ["a", "b"]
    L2 = ["b", "a"]
    result = is_list_permutation(L1, L2)
    assert result[0] in ("a", "b")
    assert result[1] == 1
    assert result[2] == str


def test_is_list_permutation_single_element_lists():
    """Lists with a single identical element should be permutations and return that element."""
    L1 = ["singleton"]
    L2 = ["singleton"]
    assert is_list_permutation(L1, L2) == ("singleton", 1, str)


def test_is_list_permutation_mixed_types_same_value():
    """Different types that compare equal (e.g., 1 and True) should be treated as the same element."""
    L1 = [1, True, 1]
    L2 = [True, 1, True]
    result = is_list_permutation(L1, L2)
    # The underlying key will be the first encountered type (int in this construction)
    assert result[0] == 1
    assert result[1] == 3
    assert result[2] == int

