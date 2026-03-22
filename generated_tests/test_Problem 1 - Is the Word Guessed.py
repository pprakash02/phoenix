import pytest
import importlib.util
import os

# Load the target module from the given absolute path
MODULE_PATH = "/home/pprakash/phoenix/generated_tests/PX-714DB47F/workspace/Problem Set 3/Problem 1 - Is the Word Guessed.py"
MODULE_NAME = "problem_is_word_guessed"

spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Export the function to be tested
isWordGuessed = module.isWordGuessed


def test_isWordGuessed_observed_case_hello():
    """
    Verify observed behavior: secretWord 'hello' with a list of unrelated words returns False.
    """
    secret = "hello"
    guessed = ["apple", "banana", "cherry"]
    assert isWordGuessed(secret, guessed) is False


def test_isWordGuessed_observed_case_test():
    """
    Verify observed behavior: secretWord 'test' with letters that do not cover all characters returns False.
    """
    secret = "test"
    guessed = ["a", "b", "c", "d", "e"]
    assert isWordGuessed(secret, guessed) is False


def test_isWordGuessed_observed_case_empty_secret():
    """
    Verify observed behavior: empty secretWord should be considered guessed (True) regardless of lettersGuessed.
    """
    assert isWordGuessed("", []) is True
    assert isWordGuessed("", ["any", "list"]) is True


def test_isWordGuessed_observed_case_single_letter():
    """
    Verify observed behavior: secretWord 'a' with a non-matching guess list returns False.
    """
    assert isWordGuessed("a", ["hello"]) is False


def test_isWordGuessed_observed_case_long_word():
    """
    Verify observed behavior: secretWord 'abcdef' with unrelated word list returns False.
    """
    assert isWordGuessed("abcdef", ["test", "word", "example", "data", "value"]) is False


def test_isWordGuessed_observed_case_python():
    """
    Verify observed behavior: secretWord 'python' with unrelated word list returns False.
    """
    assert isWordGuessed("python", ["apple", "banana", "cherry"]) is False


def test_isWordGuessed_all_letters_present():
    """
    Edge case: all unique letters of secretWord are present in lettersGuessed, should return True.
    """
    secret = "dog"
    guessed = ["d", "o", "g", "x", "y"]
    assert isWordGuessed(secret, guessed) is True


def test_isWordGuessed_repeated_letters():
    """
    Edge case: secretWord contains repeated letters; a single occurrence in lettersGuessed suffices.
    """
    secret = "letter"
    guessed = ["l", "e", "t", "r"]
    assert isWordGuessed(secret, guessed) is True


def test_isWordGuessed_missing_one_letter():
    """
    Edge case: all but one letter are guessed; should return False.
    """
    secret = "banana"
    guessed = ["b", "a", "n"]
    # Missing 'a' after the first occurrence is irrelevant, but all letters are present, so True
    assert isWordGuessed(secret, guessed) is True
    guessed_missing = ["b", "n"]
    assert isWordGuessed(secret, guessed_missing) is False


def test_isWordGuessed_case_sensitivity():
    """
    Verify that the function is case-sensitive; mismatched case leads to False.
    """
    secret = "Apple"
    guessed = ["a", "p", "l", "e"]
    assert isWordGuessed(secret, guessed) is False


def test_isWordGuessed_extra_letters_in_guess():
    """
    Having extra letters in lettersGuessed does not affect the result; should still return True if all needed letters are present.
    """
    secret = "cat"
    guessed = ["c", "a", "t", "x", "y", "z"]
    assert isWordGuessed(secret, guessed) is True


def test_isWordGuessed_non_string_secret_raises():
    """
    Passing a non-string secretWord should raise a TypeError because it is not iterable.
    """
    with pytest.raises(TypeError):
        isWordGuessed(12345, ["1", "2", "3"])


def test_isWordGuessed_non_iterable_lettersGuessed_raises():
    """
    Passing a non-iterable (e.g., None) for lettersGuessed should raise a TypeError when using 'in'.
    """
    with pytest.raises(TypeError):
        isWordGuessed("test", None)


def test_isWordGuessed_lettersGuessed_with_non_string_elements():
    """
    lettersGuessed may contain non-string elements; the function should handle them without error,
    returning False if characters are not found.
    """
    secret = "abc"
    guessed = [1, 2, 3]  # integers, not matching any letters
    assert isWordGuessed(secret, guessed) is False


def test_isWordGuessed_unicode_characters():
    """
    Verify behavior with Unicode characters in both secretWord and lettersGuessed.
    """
    secret = "café"
    guessed = ["c", "a", "f", "é"]
    assert isWordGuessed(secret, guessed) is True


def test_isWordGuessed_empty_lettersGuessed_nonempty_secret():
    """
    If lettersGuessed is empty but secretWord is non-empty, result should be False.
    """
    assert isWordGuessed("nonempty", []) is False


def test_isWordGuessed_large_input_performance():
    """
    Stress test with a long secretWord and a large lettersGuessed list.
    Ensure function returns quickly and correctly.
    """
    secret = "a" * 1000
    guessed = [chr(i) for i in range(97, 123)]  # all lowercase letters
    assert isWordGuessed(secret, guessed) is True


def test_isWordGuessed_mixed_type_lettersGuessed():
    """
    lettersGuessed contains a mix of strings and other types; function should ignore non-matching types.
    """
    secret = "dog"
    guessed = ["d", 0, "o", None, "g"]
    assert isWordGuessed(secret, guessed) is True

