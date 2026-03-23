import pytest
import importlib.util
import pathlib
import sys

# Dynamically load the target module whose path contains spaces
module_path = (
    pathlib.Path(__file__).parent
    / "home"
    / "pprakash"
    / "phoenix"
    / "generated_tests"
    / "PX-767AE5BC"
    / "workspace"
    / "Problem Set 3"
    / "Problem 3 - Printing Out all Available Letters.py"
)

spec = importlib.util.spec_from_file_location("problem3_module", module_path)
problem3 = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None, "Unable to locate the module spec"
spec.loader.exec_module(problem3)

getAvailableLetters = problem3.getAvailableLetters


def test_get_available_letters_standard_case():
    """Regression test: typical list of guessed letters returns the remaining alphabet."""
    lettersGuessed = ['e', 'i', 'k', 'p', 'r', 's']
    expected = 'abcdfghjlmnoqtuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_non_letter_strings():
    """Regression test: list containing non‑single‑character strings should be ignored,
    resulting in the full alphabet being returned."""
    lettersGuessed = ['apple', 'banana', 'cherry']
    expected = 'abcdefghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_first_five_letters():
    """Regression test: when first five letters are guessed, the rest of the alphabet is returned."""
    lettersGuessed = ['a', 'b', 'c', 'd', 'e']
    expected = 'fghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_empty_list():
    """Regression test: empty guess list returns the full alphabet."""
    lettersGuessed = []
    expected = 'abcdefghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_single_non_letter():
    """Regression test: a single non‑letter string does not affect the result."""
    lettersGuessed = ['hello']
    expected = 'abcdefghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_multiple_non_letters():
    """Regression test: multiple non‑letter strings are ignored."""
    lettersGuessed = ['test', 'word', 'example', 'data', 'value']
    expected = 'abcdefghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_all_letters():
    """Edge case: when all letters are guessed, the function should return an empty string."""
    lettersGuessed = list('abcdefghijklmnopqrstuvwxyz')
    expected = ''
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_duplicate_letters():
    """Edge case: duplicate entries in the guessed list should not affect the output."""
    lettersGuessed = ['a', 'a', 'b', 'b', 'c']
    expected = 'defghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_uppercase_input():
    """Edge case: uppercase letters are treated as distinct from lowercase, so they are ignored."""
    lettersGuessed = ['A', 'B', 'C']
    expected = 'abcdefghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_mixed_case_input():
    """Edge case: mixed case input should only remove matching lowercase letters."""
    lettersGuessed = ['a', 'B', 'c']
    expected = 'defghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_input_as_string():
    """Edge case: passing a string instead of a list works because strings are iterable."""
    lettersGuessed = 'abc'
    expected = 'defghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_input_as_tuple():
    """Edge case: passing a tuple works similarly to a list."""
    lettersGuessed = ('x', 'y', 'z')
    expected = 'abcdefghijklmnopqrstuvw'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_none_input_raises_type_error():
    """Exception case: passing None should raise a TypeError because membership test fails."""
    with pytest.raises(TypeError):
        getAvailableLetters(None)


def test_get_available_letters_non_string_elements():
    """Edge case: list containing non‑string elements does not raise; those elements are ignored."""
    lettersGuessed = [1, 2, 3, 'a']
    expected = 'bcdefghijklmnopqrstuvwxyz'
    assert getAvailableLetters(lettersGuessed) == expected


def test_get_available_letters_large_input():
    """Stress test: a large list with many repeated letters still returns the correct remaining letters."""
    large_list = ['a'] * 1000 + ['b'] * 500 + list('cdefghijklmnopqrstuvwxyz')
    expected = ''
    assert getAvailableLetters(large_list) == expected

