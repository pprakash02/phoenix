import pytest
from .home.pprakash.phoenix.generated_tests.PX-714DB47F.workspace.Problem Set 3.Problem 3 - Printing Out all Available Letters import getAvailableLetters

def test_get_available_letters_basic_success():
    """Regression test: typical usage with a list of single-character guesses."""
    letters = ['a', 'b', 'c', 'd', 'e']
    expected = 'fghijklmnopqrstuvwxyz'
    assert getAvailableLetters(letters) == expected

def test_get_available_letters_no_guesses():
    """Regression test: empty guesses should return the full alphabet."""
    assert getAvailableLetters([]) == 'abcdefghijklmnopqrstuvwxyz'

def test_get_available_letters_non_letter_strings():
    """Regression test: strings that are not single letters are ignored."""
    guesses = ['apple', 'banana', 'cherry']
    assert getAvailableLetters(guesses) == 'abcdefghijklmnopqrstuvwxyz'

def test_get_available_letters_single_non_letter():
    """Regression test: a single non-letter string does not affect output."""
    assert getAvailableLetters(['hello']) == 'abcdefghijklmnopqrstuvwxyz'

def test_get_available_letters_mixed_strings():
    """Regression test: mix of non-letter strings should still return full alphabet."""
    guesses = ['test', 'word', 'example', 'data', 'value']
    assert getAvailableLetters(guesses) == 'abcdefghijklmnopqrstuvwxyz'

def test_get_available_letters_all_letters_guessed():
    """Edge case: all letters guessed should return an empty string."""
    all_letters = list('abcdefghijklmnopqrstuvwxyz')
    assert getAvailableLetters(all_letters) == ''

def test_get_available_letters_duplicate_letters():
    """Edge case: duplicate entries in guesses should not cause errors."""
    guesses = ['a', 'a', 'b', 'b', 'c']
    expected = 'defghijklmnopqrstuvwxyz'
    assert getAvailableLetters(guesses) == expected

def test_get_available_letters_uppercase_and_symbols():
    """Edge case: uppercase letters and symbols are treated as distinct strings."""
    guesses = ['A', '1', '!', 'z']
    # Only lowercase 'z' matches, so it should be removed; 'a' remains because 'A' != 'a'
    expected = 'abcdefghijklmnopqrstuvwxy'
    assert getAvailableLetters(guesses) == expected

def test_get_available_letters_mixed_length_strings():
    """Edge case: strings longer than one character do not match single letters."""
    guesses = ['ab', 'c']
    # Only 'c' matches a single lowercase letter
    expected = 'abdefghijklmnopqrstuvwxyz'
    assert getAvailableLetters(guesses) == expected

def test_get_available_letters_none_in_list():
    """Edge case: list containing None should be ignored for letter matching."""
    guesses = [None, 'a']
    expected = 'bcdefghijklmnopqrstuvwxyz'
    assert getAvailableLetters(guesses) == expected

def test_get_available_letters_input_is_string():
    """Edge case: passing a string (iterable of characters) works like a list of guesses."""
    guesses = 'abc'
    expected = 'defghijklmnopqrstuvwxyz'
    assert getAvailableLetters(guesses) == expected

def test_get_available_letters_input_is_tuple():
    """Edge case: passing a tuple of guesses works identically to a list."""
    guesses = ('x', 'y', 'z')
    expected = 'abcdefghijklmnopqrstuvw'
    assert getAvailableLetters(guesses) == expected

def test_get_available_letters_input_not_iterable():
    """Exception case: passing a non-iterable (e.g., None) should raise TypeError."""
    with pytest.raises(TypeError):
        getAvailableLetters(None)

def test_get_available_letters_return_type():
    """General sanity check: function should always return a string."""
    result = getAvailableLetters(['a', 'b'])
    assert isinstance(result, str)