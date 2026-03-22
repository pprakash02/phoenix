import pytest
import importlib.util
import pathlib
import sys

# Load the target module from its file path
_module_path = pathlib.Path(__file__).resolve().parents[0] / "Problem Set 4" / "Problem 1 - Word Scores.py"
_spec = importlib.util.spec_from_file_location("word_scores_module", _module_path)
_word_scores = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_word_scores)

# Export the function to be tested
getWordScore = _word_scores.getWordScore


def test_getWordScore_empty_word_returns_zero():
    """
    Verify that an empty word always yields a score of 0,
    regardless of the value of n (including negative values).
    """
    assert getWordScore('', -1) == 0
    assert getWordScore('', 0) == 0
    assert getWordScore('', 10) == 0


def test_getWordScore_raises_name_error_when_dict_missing():
    """
    The function relies on SCRABBLE_LETTER_VALUES. If this global
    dictionary is not defined, any non‑empty word should raise a NameError.
    """
    with pytest.raises(NameError):
        getWordScore('hello', 0)
    with pytest.raises(NameError):
        getWordScore('test', 1)
    with pytest.raises(NameError):
        getWordScore('a', 10)
    with pytest.raises(NameError):
        getWordScore('abcdef', 100)
    with pytest.raises(NameError):
        getWordScore('python', 0.5)


def test_getWordScore_correct_scoring_without_bonus(monkeypatch):
    """
    Provide a minimal SCRABBLE_LETTER_VALUES mapping and verify the
    calculated score when the word length does NOT equal n (no bonus).
    """
    monkeypatch.setattr(_word_scores, 'SCRABBLE_LETTER_VALUES', {
        'h': 4, 'e': 1, 'l': 1, 'o': 1
    })
    # word = "hello": sum = 4+1+1+1+1 = 8, length = 5 → 8 * 5 = 40
    assert getWordScore('hello', 6) == 40


def test_getWordScore_correct_scoring_with_bonus(monkeypatch):
    """
    Provide a minimal SCRABBLE_LETTER_VALUES mapping and verify the
    calculated score when the word uses all n letters (bonus of 50 points).
    """
    monkeypatch.setattr(_word_scores, 'SCRABBLE_LETTER_VALUES', {
        'a': 1, 'b': 3, 'c': 3
    })
    # word = "abc": sum = 1+3+3 = 7, length = 3 → 7 * 3 = 21, plus 50 bonus = 71
    assert getWordScore('abc', 3) == 71


def test_getWordScore_type_error_for_non_string_word():
    """
    Passing a non‑string (e.g., an integer) should raise a TypeError because
    the function attempts to iterate over the argument.
    """
    with pytest.raises(TypeError):
        getWordScore(12345, 5)


def test_getWordScore_key_error_for_unknown_letter(monkeypatch):
    """
    If SCRABBLE_LETTER_VALUES does not contain a needed letter, a KeyError
    should be raised when that letter is processed.
    """
    monkeypatch.setattr(_word_scores, 'SCRABBLE_LETTER_VALUES', {'a': 1})
    with pytest.raises(KeyError):
        getWordScore('ab', 2)


def test_getWordScore_negative_n_without_bonus(monkeypatch):
    """
    When n is negative and the word length does not equal n,
    the function should compute the normal score without adding the bonus.
    """
    monkeypatch.setattr(_word_scores, 'SCRABBLE_LETTER_VALUES', {
        'z': 10
    })
    # word = "z": sum = 10, length = 1 → 10 * 1 = 10, no bonus because lettersUsed != n
    assert getWordScore('z', -5) == 10


def test_getWordScore_zero_n_bonus_applies(monkeypatch):
    """
    If n is zero and the word length is also zero, the function returns 0
    (handled by early return). For a non‑empty word with n == 0,
    the bonus should not be applied because lettersUsed != n.
    """
    monkeypatch.setattr(_word_scores, 'SCRABBLE_LETTER_VALUES', {
        'x': 8
    })
    # Non‑empty word with n == 0 should not receive the bonus
    assert getWordScore('x', 0) == 8 * 1  # 8


def test_getWordScore_large_word_without_bonus(monkeypatch):
    """
    Test the function with a longer word to ensure multiplication
    by word length works correctly. No bonus is added because
    lettersUsed != n.
    """
    monkeypatch.setattr(_word_scores, 'SCRABBLE_LETTER_VALUES', {
        'p': 3, 'y': 4, 't': 1, 'h': 4, 'o': 1, 'n': 1
    })
    word = 'python'  # sum = 3+4+1+4+1+1 = 14, length = 6 → 14 * 6 = 84
    assert getWordScore(word, 10) == 84


def test_getWordScore_word_length_equals_n_zero_bonus(monkeypatch):
    """
    Verify that when the word length equals n, the bonus of 50 points is added.
    """
    monkeypatch.setattr(_word_scores, 'SCRABBLE_LETTER_VALUES', {
        'd': 2, 'a': 1, 't': 1, 'e': 1
    })
    word = 'date'  # sum = 2+1+1+1 = 5, length = 4 → 5 * 4 = 20, plus 50 = 70
    assert getWordScore(word, 4) == 70
