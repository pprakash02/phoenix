import pytest
import importlib.util
import os

# Dynamically load the target module because its path contains spaces.
MODULE_PATH = "/home/pprakash/phoenix/generated_tests/PX-767AE5BC/workspace/Problem Set 6/Problem 5.py"
spec = importlib.util.spec_from_file_location("problem_5_module", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

search = module.search
newsearch = module.newsearch


def test_search_negative_number_not_in_list():
    """search should return False when the element is not present (negative number)."""
    assert search([1, 2, 3], -1) is False


def test_search_string_not_in_list():
    """search should return False when a string element is not present."""
    assert search(['a', 'b', 'c'], 'test') is False


def test_search_empty_string_not_in_singleton():
    """search should return False when searching for an empty string in a list of non‑empty strings."""
    assert search(['test'], '') is False


def test_search_bool_true_in_int_list():
    """search should treat True as 1 and return True when 1 is in the list."""
    assert search([1, 2, 3], True) is True


def test_search_type_error_str_vs_int():
    """search should raise TypeError when comparing a string list element with an int."""
    with pytest.raises(TypeError):
        search(['a', 'b', 'c'], 0)


def test_search_type_error_str_vs_int_singleton():
    """search should raise TypeError when comparing a single string element with an int."""
    with pytest.raises(TypeError):
        search(['test'], 1)


def test_search_empty_list():
    """search should return False for any element when the list is empty."""
    assert search([], 5) is False
    assert search([], 'anything') is False


def test_search_single_element_present():
    """search should return True when the single element matches the target."""
    assert search([42], 42) is True


def test_search_single_element_smaller():
    """search should return False when the single element is greater than the target."""
    assert search([10], 5) is False


def test_search_multiple_elements_target_present():
    """search should correctly find an element that exists in a longer list."""
    assert search([1, 3, 5, 7, 9], 5) is True


def test_search_multiple_elements_target_absent():
    """search should return False when the element is not in the list."""
    assert search([1, 3, 5, 7, 9], 4) is False


def test_search_strings_sorted():
    """search should work with sorted string lists."""
    assert search(['a', 'b', 'c'], 'b') is True
    assert search(['a', 'b', 'c'], 'd') is False


def test_newsearch_negative_number_not_in_list():
    """newsearch should return False when the element is not present (negative number)."""
    assert newsearch([1, 2, 3], -1) is False


def test_newsearch_string_not_in_list():
    """newsearch should return False when a string element is not present."""
    assert newsearch(['a', 'b', 'c'], 'test') is False


def test_newsearch_empty_string_not_in_singleton():
    """newsearch should return False when searching for an empty string in a list of non‑empty strings."""
    assert newsearch(['test'], '') is False


def test_newsearch_bool_true_in_int_list():
    """newsearch should treat True as 1 and return True when 1 is in the list."""
    assert newsearch([1, 2, 3], True) is True


def test_newsearch_type_error_str_vs_int():
    """newsearch should raise TypeError when comparing a string list element with an int."""
    with pytest.raises(TypeError):
        newsearch(['a', 'b', 'c'], 0)


def test_newsearch_type_error_str_vs_int_singleton():
    """newsearch should raise TypeError when comparing a single string element with an int."""
    with pytest.raises(TypeError):
        newsearch(['test'], 1)


def test_newsearch_empty_list():
    """newsearch should return False for any element when the list is empty."""
    assert newsearch([], 5) is False
    assert newsearch([], 'anything') is False


def test_newsearch_single_element_present():
    """newsearch should return True when the single element matches the target."""
    assert newsearch([42], 42) is True


def test_newsearch_single_element_smaller():
    """newsearch should return False when the single element is greater than the target."""
    assert newsearch([10], 5) is False


def test_newsearch_multiple_elements_target_present():
    """newsearch should correctly find an element that exists in a longer list."""
    assert newsearch([1, 3, 5, 7, 9], 5) is True


def test_newsearch_multiple_elements_target_absent():
    """newsearch should return False when the element is not in the list."""
    assert newsearch([1, 3, 5, 7, 9], 4) is False


def test_newsearch_strings_sorted_mismatch():
    """newsearch may differ from search on string lists; verify its actual behavior."""
    # For a sorted string list, newsearch returns False for an element that exists.
    assert newsearch(['a', 'b', 'c'], 'b') is False
    # It still returns False for an element not present.
    assert newsearch(['a', 'b', 'c'], 'd') is False


def test_search_and_newsearch_agree_on_length_0_1_2():
    """Both functions should give the same result for lists of length 0, 1, or 2."""
    test_cases = [
        ([], 5),
        ([1], 1),
        ([1], 2),
        ([1, 2], 1),
        ([1, 2], 2),
        ([1, 2], 3),
    ]
    for lst, elem in test_cases:
        assert search(lst, elem) == newsearch(lst, elem)


def test_search_and_newsearch_disagree_on_length_3():
    """Demonstrate a case where search and newsearch differ for length >=3."""
    lst = [1, 2, 3]
    elem = 2
    assert search(lst, elem) is True
    assert newsearch(lst, elem) is False


def test_newsearch_boundary_condition_last_element():
    """newsearch should find the element when it is the last element of the list."""
    lst = [5, 10, 15]
    assert newsearch(lst, 15) is True


def test_newsearch_boundary_condition_first_element():
    """newsearch should find the element when it is the first element of the list."""
    lst = [5, 10, 15]
    assert newsearch(lst, 5) is True


def test_newsearch_target_greater_than_all():
    """newsearch should return False when the target is greater than all elements."""
    lst = [1, 2, 3]
    assert newsearch(lst, 10) is False


def test_newsearch_target_smaller_than_all():
    """newsearch should return False when the target is smaller than all elements."""
    lst = [5, 6, 7]
    assert newsearch(lst, 1) is False

