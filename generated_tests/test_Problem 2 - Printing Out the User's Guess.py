import pytest
import importlib.util
import os

# Load the target module from its absolute path
MODULE_PATH = "/home/pprakash/phoenix/generated_tests/PX-714DB47F/workspace/Problem Set 3/Problem 2 - Printing Out the User's Guess.py"

spec = importlib.util.spec_from_file_location("problem2_module", MODULE_PATH)
problem2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(problem2)

getGuessedWord = problem2.getGuessedWord


def test_getGuessedWord_all_underscores_due_to_non_char_guesses():
    """
    Verify that when lettersGuessed contains strings longer than a single character,
    none of the characters in secretWord are considered guessed, resulting in all underscores.
    """
    secret = "hello"
    guesses = ["apple", "banana", "cherry"]
    assert getGuessedWord(secret, guesses) == "_____"


def test_getGuessedWord_partial_match():
    """
    Verify that a single correctly guessed character appears in the output,
    while other characters remain underscores.
    """
    secret = "test"
    guesses = ["a", "b", "c", "d", "e"]
    assert getGuessedWord(secret, guesses) == "_e__"


def test_getGuessedWord_empty_inputs():
    """
    When both secretWord and lettersGuessed are empty, the result should be an empty string.
    """
    assert getGuessedWord("", []) == ""


def test_getGuessedWord_no_match_single_letter_secret():
    """
    Secret word of length 1 with a non-matching guess list should return a single underscore.
    """
    assert getGuessedWord("a", ["hello"]) == "_"


def test_getGuessedWord_all_underscores_complex_guess_list():
    """
    Verify that even with a list of various words, none matching the secretWord characters,
    the function returns only underscores.
    """
    secret = "abcdef"
    guesses = ["test", "word", "example", "data", "value"]
    assert getGuessedWord(secret, guesses) == "______"


def test_getGuessedWord_all_underscores_another_case():
    """
    Another example confirming that unrelated guess strings yield underscores only.
    """
    secret = "python"
    guesses = ["apple", "banana", "cherry"]
    assert getGuessedWord(secret, guesses) == "______"


def test_getGuessedWord_full_match_single_char_guesses():
    """
    All characters guessed correctly with single-character entries should be revealed.
    """
    secret = "apple"
    guesses = ["a", "p", "l", "e"]
    assert getGuessedWord(secret, guesses) == "apple"


def test_getGuessedWord_partial_match_mixed_order():
    """
    Characters guessed out of order should still appear in their correct positions.
    """
    secret = "banana"
    guesses = ["b", "n"]
    assert getGuessedWord(secret, guesses) == "b_n_n_"


def test_getGuessedWord_duplicate_guesses():
    """
    Duplicate entries in lettersGuessed should not affect the output.
    """
    secret = "test"
    guesses = ["t", "e", "t", "s", "e"]
    assert getGuessedWord(secret, guesses) == "test"


def test_getGuessedWord_non_string_guess_items():
    """
    Non-string items in lettersGuessed are ignored for matching characters,
    resulting in underscores for those positions.
    """
    secret = "abc"
    guesses = [1, 2, "b"]
    assert getGuessedWord(secret, guesses) == "_b_"


def test_getGuessedWord_secret_word_non_string_raises():
    """
    Passing a non-string secretWord should raise a TypeError when iterated.
    """
    with pytest.raises(TypeError):
        getGuessedWord(12345, ["1", "2", "3"])


def test_getGuessedWord_lettersGuessed_not_iterable_raises():
    """
    Passing a non-iterable for lettersGuessed should raise a TypeError.
    """
    with pytest.raises(TypeError):
        getGuessedWord("test", None)


def test_getGuessedWord_case_sensitivity():
    """
    The function is case-sensitive; uppercase letters in secretWord are not matched
    by lowercase guesses.
    """
    secret = "Apple"
    guesses = ["a", "p", "l", "e"]
    # Only the lowercase 'p', 'l', 'e' match positions; 'A' remains underscore
    assert getGuessedWord(secret, guesses) == "_pple"


def test_getGuessedWord_long_secret_word():
    """
    Ensure function handles a long secretWord without error and returns correct pattern.
    """
    secret = "abcdefghijklmnopqrstuvwxyz" * 10  # 260 characters
    guesses = list("aeiou")
    result = getGuessedWord(secret, guesses)
    # Verify length matches and only vowels are revealed
    assert len(result) == len(secret)
    for ch, out in zip(secret, result):
        if ch in guesses:
            assert out == ch
        else:
            assert out == "_"


def test_getGuessedWord_return_type_is_string():
    """
    The function should always return a string, even for edge cases.
    """
    assert isinstance(getGuessedWord("", []), str)
    assert isinstance(getGuessedWord("a", []), str)
    assert isinstance(getGuessedWord("test", ["t"]), str)