import pytest
import importlib.util
import os
from pathlib import Path

# Dynamically load the target module using its file path.
# Adjust the relative path as needed based on the test file location.
module_path = Path(__file__).resolve().parents[2] / "Problem Set 4" / "Problem 3 - Valid Words.py"
spec = importlib.util.spec_from_file_location("valid_words_module", module_path)
valid_words_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(valid_words_module)

isValidWord = valid_words_module.isValidWord


def test_isValidWord_valid_word_in_hand():
    """
    Verify that a word present in the word list and fully constructible from the hand returns True.
    """
    hand = {"h": 1, "e": 1, "l": 2, "o": 1}
    word_list = ["hello", "world"]
    assert isValidWord("hello", hand, word_list) is True


def test_isValidWord_word_not_in_wordlist():
    """
    Verify that a word that can be constructed from the hand but is not in the word list returns False.
    """
    hand = {"h": 1, "e": 1, "l": 2, "o": 1}
    word_list = ["world"]
    assert isValidWord("hello", hand, word_list) is False


def test_isValidWord_insufficient_letters():
    """
    Verify that a word present in the word list but requiring more instances of a letter than the hand provides returns False.
    """
    hand = {"h": 1, "e": 1, "l": 1, "o": 1}
    word_list = ["hello"]
    assert isValidWord("hello", hand, word_list) is False


def test_isValidWord_letter_missing_from_hand():
    """
    Verify that a word present in the word list but containing a letter absent from the hand returns False.
    """
    hand = {"h": 1, "e": 1, "l": 2}
    word_list = ["hello"]
    assert isValidWord("hello", hand, word_list) is False


def test_isValidWord_empty_word():
    """
    Verify that the empty string is not considered a valid word, regardless of hand or word list.
    """
    hand = {"a": 1}
    word_list = ["a"]
    assert isValidWord("", hand, word_list) is False


def test_isValidWord_hand_unchanged():
    """
    Ensure that the original hand dictionary is not mutated after calling the function.
    """
    original_hand = {"h": 1, "e": 1, "l": 2, "o": 1}
    hand_copy = original_hand.copy()
    word_list = ["hello"]
    isValidWord("hello", original_hand, word_list)
    assert original_hand == hand_copy


def test_isValidWord_invalid_hand_type_int():
    """
    Passing a non-dictionary type for hand should raise an AttributeError because .copy() is missing.
    """
    hand = 123  # not a dict
    word_list = ["test"]
    with pytest.raises(AttributeError):
        isValidWord("test", hand, word_list)


def test_isValidWord_invalid_hand_type_none():
    """
    Passing None as hand should raise an AttributeError.
    """
    hand = None
    word_list = ["test"]
    with pytest.raises(AttributeError):
        isValidWord("test", hand, word_list)


def test_isValidWord_invalid_word_type_int():
    """
    Passing a non-string type for word should raise a TypeError when iterating.
    """
    hand = {"t": 1, "e": 1, "s": 1}
    word_list = ["test"]
    with pytest.raises(TypeError):
        isValidWord(1234, hand, word_list)


def test_isValidWord_invalid_wordlist_type_int():
    """
    Passing a non-iterable type for wordList should raise a TypeError during membership test.
    """
    hand = {"t": 1, "e": 1, "s": 1}
    word_list = 42  # not iterable
    with pytest.raises(TypeError):
        isValidWord("test", hand, word_list)


def test_isValidWord_hand_with_zero_counts():
    """
    Hand entries with zero count should not allow usage of that letter.
    """
    hand = {"a": 0, "b": 2}
    word_list = ["ab"]
    assert isValidWord("ab", hand, word_list) is False


def test_isValidWord_word_longer_than_hand():
    """
    A word longer than the total number of letters in the hand cannot be valid.
    """
    hand = {"a": 1, "b": 1}
    word_list = ["aba"]
    assert isValidWord("aba", hand, word_list) is False


def test_isValidWord_multiple_calls_same_hand():
    """
    Multiple successive calls with the same hand should yield consistent results and not mutate the hand.
    """
    hand = {"c": 1, "a": 1, "t": 1}
    word_list = ["cat", "act"]
    assert isValidWord("cat", hand, word_list) is True
    assert isValidWord("act", hand, word_list) is True
    # Hand should remain unchanged after both calls
    assert hand == {"c": 1, "a": 1, "t": 1}