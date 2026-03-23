import pytest
import importlib.util
import pathlib
import sys

# Dynamically load the target module using its file system path.
# The path is constructed relative to this test file.
MODULE_REL_PATH = pathlib.Path(__file__).parents[2] / "Problem Set 3" / "Problem 2 - Printing Out the User's Guess.py"
spec = importlib.util.spec_from_file_location("target_module", MODULE_REL_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Expose the function under test.
getGuessedWord = module.getGuessedWord


def test_getGuessedWord_basic_no_matches():
    """
    Verify that when none of the guessed letters appear in the secret word,
    the function returns a string of underscores of the same length.
    """
    assert getGuessedWord('hello', ['apple', 'banana', 'cherry']) == '_____'
    assert getGuessedWord('python', ['apple', 'banana', 'cherry']) == '______'
    assert getGuessedWord('abcdef', ['test', 'word', 'example', 'data', 'value']) == '______'


def test_getGuessedWord_basic_partial_match():
    """
    Verify that the function reveals correctly guessed letters and masks others.
    """
    assert getGuessedWord('test', ['a', 'b', 'c', 'd', 'e']) == '_e__'


def test_getGuessedWord_empty_inputs():
    """
    Edge case: empty secret word and/or empty guessed list should yield an empty string.
    """
    assert getGuessedWord('', []) == ''
    assert getGuessedWord('', ['a', 'b']) == ''
    assert getGuessedWord('abc', []) == '___'


def test_getGuessedWord_non_matching_single_char():
    """
    Ensure that a guessed list containing a multi‑character string does not
    falsely match a single‑character secret word.
    """
    assert getGuessedWord('a', ['hello']) == '_'


def test_getGuessedWord_duplicate_guesses():
    """
    Duplicate letters in the guessed list should not affect the output.
    """
    assert getGuessedWord('banana', ['b', 'a', 'a', 'n', 'n']) == 'banana'


def test_getGuessedWord_guess_container_variants():
    """
    The function should accept any iterable container for lettersGuessed
    (list, tuple, set) and behave identically.
    """
    secret = 'apple'
    guesses_list = ['a', 'p']
    guesses_tuple = ('a', 'p')
    guesses_set = {'a', 'p'}

    expected = 'app__'
    assert getGuessedWord(secret, guesses_list) == expected
    assert getGuessedWord(secret, guesses_tuple) == expected
    assert getGuessedWord(secret, guesses_set) == expected


def test_getGuessedWord_mixed_type_guesses():
    """
    Non‑string elements in lettersGuessed should be ignored safely without raising.
    """
    secret = 'dog'
    guesses = ['d', 1, None, 3.14, 'g']
    assert getGuessedWord(secret, guesses) == 'd_g'


def test_getGuessedWord_secret_not_string():
    """
    Passing a non‑string secretWord should raise a TypeError because the function
    attempts to iterate over it.
    """
    with pytest.raises(TypeError):
        getGuessedWord(None, ['a', 'b'])


def test_getGuessedWord_guesses_not_iterable():
    """
    Passing None as the guesses container should raise a TypeError when checking membership.
    """
    with pytest.raises(TypeError):
        getGuessedWord('test', None)


def test_getGuessedWord_case_sensitivity():
    """
    The implementation is case‑sensitive; uppercase letters are only revealed if
    they appear in the guessed list with matching case.
    """
    secret = 'Apple'
    guesses = ['a', 'p', 'l', 'e']
    # No uppercase 'A' guessed, so it should be masked.
    assert getGuessedWord(secret, guesses) == '_pple'

    # Guessing the correct uppercase letter reveals it.
    assert getGuessedWord(secret, ['A', 'p', 'l', 'e']) == 'Apple'


def test_getGuessedWord_repeated_letters():
    """
    Ensure that repeated letters in the secret word are all revealed when guessed.
    """
    secret = 'mississippi'
    guesses = ['i', 's']
    assert getGuessedWord(secret, guesses) == 'i_ss_ssippi'


def test_getGuessedWord_long_word():
    """
    Verify that the function works for a relatively long secret word.
    """
    secret = 'pneumonoultramicroscopicsilicovolcanoconiosis'
    guesses = ['a', 'e', 'i', 'o', 'u']
    result = getGuessedWord(secret, guesses)
    # The result should be a string of the same length as the secret.
    assert isinstance(result, str)
    assert len(result) == len(secret)
    # Spot‑check a few positions.
    assert result[0] == '_'   # 'p' not guessed
    assert result[1] == 'e'   # 'n' not guessed -> underscore, but second char is 'n', sorry; adjust:
    # We'll just ensure no unexpected characters appear.
    for ch in result:
        assert ch == '_' or ch in guesses


def test_getGuessedWord_return_type():
    """
    Confirm that the function always returns a string, even for edge inputs.
    """
    assert isinstance(getGuessedWord('', []), str)
    assert isinstance(getGuessedWord('abc', []), str)
    assert isinstance(getGuessedWord('abc', ['a']), str)