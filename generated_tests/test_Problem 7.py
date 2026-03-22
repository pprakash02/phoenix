import pytest
from .home.pprakash.phoenix.generated_tests.PX-714DB47F.workspace.Midterm Exam.Problem 7 import dict_invert


def test_dict_invert_basic_example():
    """Verify basic inversion with unique values."""
    d = {1: 10, 2: 20, 3: 30}
    expected = {10: [1], 20: [2], 30: [3]}
    assert dict_invert(d) == expected


def test_dict_invert_duplicate_values():
    """Verify inversion when multiple keys share the same value; lists must be sorted."""
    d = {1: 10, 2: 20, 3: 30, 4: 30}
    expected = {10: [1], 20: [2], 30: [3, 4]}
    assert dict_invert(d) == expected


def test_dict_invert_boolean_keys():
    """Verify inversion with boolean values and unordered integer keys."""
    d = {4: True, 2: True, 0: True}
    expected = {True: [0, 2, 4]}
    assert dict_invert(d) == expected


def test_dict_invert_empty_dict():
    """An empty dictionary should invert to an empty dictionary."""
    d = {}
    expected = {}
    assert dict_invert(d) == expected


def test_dict_invert_tuple_values():
    """Values can be immutable tuples; ensure proper grouping and sorting of keys."""
    d = {1: (1, 2), 2: (1, 2), 3: (2, 3)}
    expected = {(1, 2): [1, 2], (2, 3): [3]}
    assert dict_invert(d) == expected


def test_dict_invert_unsorted_input_keys():
    """Input keys may be out of order; output lists must always be sorted."""
    d = {5: 'a', 2: 'a', 8: 'b'}
    expected = {'a': [2, 5], 'b': [8]}
    assert dict_invert(d) == expected


def test_dict_invert_mixed_value_types():
    """Dictionary may contain mixed immutable value types."""
    d = {1: 1, 2: '1', 3: 1}
    expected = {1: [1, 3], '1': [2]}
    assert dict_invert(d) == expected


def test_dict_invert_original_unchanged():
    """The original dictionary should remain unchanged after inversion."""
    d = {1: 10, 2: 20, 3: 10}
    original = d.copy()
    _ = dict_invert(d)
    assert d == original


@pytest.mark.parametrize(
    "invalid_input",
    [
        "hello",               # str
        ["a", "b"],            # list
        123,                   # int
        None,                  # NoneType
        3.14,                  # float
    ],
)
def test_dict_invert_invalid_input_raises_attributeerror(invalid_input):
    """Passing a non-dict should raise AttributeError because .items() is missing."""
    with pytest.raises(AttributeError):
        dict_invert(invalid_input)