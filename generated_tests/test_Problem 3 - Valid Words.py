import os
import pytest
import importlib.util

# Load the target module from its file path
MODULE_PATH = "/home/pprakash/phoenix/generated_tests/PX-6DC06898/workspace/Problem Set 4/Problem 3 - Valid Words.py"
spec = importlib.util.spec_from_file_location("valid_words_module", MODULE_PATH)
valid_words_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(valid_words_module)

# Expose the function under test
isValidWord = valid_words_module.isValidWord


def test_isValidWord_valid_simple():
    """Word is in wordList and hand has sufficient letters."""
    hand = {'h': 1, 'e': 1, 'l': 2, 'o': 1}
    wordList = ['hello', 'world']
    assert isValidWord('hello', hand, wordList) is True


def test_isValidWord_invalid_not_in_wordlist():
    """Word is not present in the supplied word list."""
    hand = {'h': 1, 'e': 1, 'l': 2, 'o': 1}
    wordList = ['world']
    assert isValidWord('hello', hand, wordList) is False


def test_isValidWord_invalid_insufficient_letters():
    """Hand lacks enough copies of a needed letter."""
    hand = {'h': 1, 'e': 1, 'l': 1, 'o': 1}
    wordList = ['hello']
    assert isValidWord('hello', hand, wordList) is False


def test_isValidWord_invalid_missing_letter():
    """Hand is missing a required letter entirely."""
    hand = {'h': 1, 'e': 1, 'l': 2}
    wordList = ['hello']
    assert isValidWord('hello', hand, wordList) is False


def test_isValidWord_empty_word():
    """An empty string is never a valid word."""
    hand = {'a': 1}
    wordList = ['a']
    assert isValidWord('', hand, wordList) is False


def test_isValidWord_hand_not_mutated():
    """The function must not modify the original hand dictionary."""
    hand = {'h': 1, 'e': 1, 'l': 2, 'o': 1}
    original_hand = hand.copy()
    wordList = ['hello']
    isValidWord('hello', hand, wordList)
    assert hand == original_hand


def test_isValidWord_non_dict_hand_raises():
    """Passing a non‑dict as hand should raise AttributeError due to missing .copy()."""
    with pytest.raises(AttributeError):
        isValidWord('test', 123, ['test'])

    with pytest.raises(AttributeError):
        isValidWord('test', 1.5, ['test'])


def test_isValidWord_non_iterable_wordlist_raises():
    """Passing a non‑iterable as wordList should raise TypeError when using 'in'."""
    hand = {'t': 1, 'e': 1, 's': 1}
    with pytest.raises(TypeError):
        isValidWord('test', hand, None)


def test_isValidWord_word_not_string():
    """Providing a non‑string word should raise TypeError when iterating."""
    hand = {'1': 1}
    wordList = ['1']
    with pytest.raises(TypeError):
        isValidWord(123, hand, wordList)


def test_isValidWord_word_with_repeating_and_extra_hand():
    """Word uses repeated letters but hand provides sufficient counts."""
    hand = {'a': 3, 'b': 1}
    wordList = ['aba']
    assert isValidWord('aba', hand, wordList) is True


def test_isValidWord_word_with_extra_hand_letters():
    """Hand contains extra letters not needed for the word."""
    hand = {'a': 2, 'b': 2, 'c': 5}
    wordList = ['ab']
    assert isValidWord('ab', hand, wordList) is True


def test_isValidWord_empty_wordlist():
    """An empty word list should cause any word to be invalid."""
    hand = {'a': 1}
    assert isValidWord('a', hand, []) is False


def test_isValidWord_empty_hand():
    """Empty hand cannot form any non‑empty word."""
    hand = {}
    wordList = ['a']
    assert isValidWord('a', hand, wordList) is False


def test_isValidWord_case_sensitivity():
    """The function does not perform case conversion; mismatched case fails."""
    hand = {'H': 1, 'e': 1, 'l': 2, 'o': 1}
    wordList = ['hello']
    assert isValidWord('Hello', hand, wordList) is False


def test_isValidWord_word_longer_than_hand():
    """Word longer than total letters in hand should be invalid."""
    hand = {'a': 2, 'b': 1}
    wordList = ['aba']
    assert isValidWord('aba', hand, wordList) is True  # exact match
    assert isValidWord('abaa', hand, wordList) is False  # exceeds hand size


def test_isValidWord_hand_with_zero_counts():
    """Letters with zero count in hand cannot be used."""
    hand = {'a': 0, 'b': 1}
    wordList = ['ab']
    assert isValidWord('ab', hand, wordList) is False


def test_isValidWord_word_not_in_wordlist_but_hand_ok():
    """Even if hand can form the word, missing from word list makes it invalid."""
    hand = {'c': 1, 'a': 1, 't': 1}
    wordList = ['dog', 'mouse']
    assert isValidWord('cat', hand, wordList) is False


def test_isValidWord_multiple_calls_same_hand():
    """Repeated calls should not affect subsequent validations."""
    hand = {'h': 1, 'e': 1, 'l': 2, 'o': 1}
    wordList = ['hello', 'hell']
    assert isValidWord('hell', hand, wordList) is True
    # hand should remain unchanged, allowing the next call
    assert isValidWord('hello', hand, wordList) is True