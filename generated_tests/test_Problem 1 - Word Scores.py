import pytest
import importlib.util
import pathlib
import sys

# Dynamically load the target module using its file system path.
MODULE_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "Problem Set 4"
    / "Problem 1 - Word Scores.py"
)

spec = importlib.util.spec_from_file_location("word_scores_module", MODULE_PATH)
word_scores_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(word_scores_module)

# Expose the function under test.
getWordScore = word_scores_module.getWordScore


def _set_scrabble_values(values=None):
    """
    Helper to inject a SCRABBLE_LETTER_VALUES dictionary into the target module.
    If `values` is None, a standard Scrabble scoring table is used.
    """
    if values is None:
        values = {
            "a": 1,
            "b": 3,
            "c": 3,
            "d": 2,
            "e": 1,
            "f": 4,
            "g": 2,
            "h": 4,
            "i": 1,
            "j": 8,
            "k": 5,
            "l": 1,
            "m": 3,
            "n": 1,
            "o": 1,
            "p": 3,
            "q": 10,
            "r": 1,
            "s": 1,
            "t": 1,
            "u": 1,
            "v": 4,
            "w": 4,
            "x": 8,
            "y": 4,
            "z": 10,
        }
    setattr(word_scores_module, "SCRABBLE_LETTER_VALUES", values)


def test_getWordScore_empty_string_negative_n():
    """
    Regression test for the observed successful case:
    An empty word should always return a score of 0,
    even when `n` is negative.
    """
    assert getWordScore("", -1) == 0


@pytest.mark.parametrize(
    "word,n",
    [
        ("hello", 0),
        ("test", 1),
        ("a", 10),
        ("abcdef", 100),
        ("python", 0.5),
    ],
)
def test_getWordScore_raises_NameError_when_values_missing(word, n):
    """
    The original implementation expects a global SCRABBLE_LETTER_VALUES dict.
    When it is absent, a NameError should be raised.
    """
    # Ensure the global is NOT present
    if hasattr(word_scores_module, "SCRABBLE_LETTER_VALUES"):
        delattr(word_scores_module, "SCRABBLE_LETTER_VALUES")
    with pytest.raises(NameError):
        getWordScore(word, n)


def test_getWordScore_basic_scoring_without_bonus():
    """
    Verify correct score calculation when the word does NOT use all `n` letters.
    """
    _set_scrabble_values()
    word = "hello"
    n = 10  # larger than word length, so no bonus
    # h=4, e=1, l=1, l=1, o=1 => sum = 8, letters =5 => 8*5 = 40
    expected = 40
    assert getWordScore(word, n) == expected


def test_getWordScore_basic_scoring_with_bonus():
    """
    Verify correct score calculation when the word uses exactly `n` letters,
    triggering the 50‑point bonus.
    """
    _set_scrabble_values()
    word = "hello"
    n = 5  # exactly the length of "hello"
    # base score = 8 * 5 = 40, plus 50 bonus = 90
    expected = 90
    assert getWordScore(word, n) == expected


def test_getWordScore_zero_n_no_bonus():
    """
    Edge case where `n` is zero. No bonus should be added regardless of word length.
    """
    _set_scrabble_values()
    word = "abc"
    n = 0
    # a=1,b=3,c=3 => sum =7, letters=3 => 7*3=21
    expected = 21
    assert getWordScore(word, n) == expected


def test_getWordScore_negative_n_no_bonus():
    """
    Edge case where `n` is negative. Bonus should never be applied.
    """
    _set_scrabble_values()
    word = "dog"
    n = -5
    # d=2, o=1, g=2 => sum=5, letters=3 => 5*3=15
    expected = 15
    assert getWordScore(word, n) == expected


def test_getWordScore_non_string_word_raises_type_error():
    """
    Passing a non‑string as the word should raise a TypeError because the
    function attempts to iterate over the input.
    """
    _set_scrabble_values()
    with pytest.raises(TypeError):
        getWordScore(12345, 5)


def test_getWordScore_n_as_string_no_bonus():
    """
    When `n` is a string, the equality check fails, so no bonus is added.
    The function should still return the correct base score.
    """
    _set_scrabble_values()
    word = "cat"
    n = "3"  # string, not int
    # c=3, a=1, t=1 => sum=5, letters=3 => 5*3=15
    expected = 15
    assert getWordScore(word, n) == expected


def test_getWordScore_n_as_float_no_bonus():
    """
    When `n` is a float, the equality check fails (int vs float),
    therefore no bonus is applied.
    """
    _set_scrabble_values()
    word = "quiz"
    n = 4.0  # float, not int
    # q=10, u=1, i=1, z=10 => sum=22, letters=4 => 22*4=88
    expected = 88
    assert getWordScore(word, n) == expected


def test_getWordScore_all_letters_used_with_float_n_no_bonus():
    """
    Even if the numeric value of `n` equals the word length,
    a type mismatch prevents the bonus from being added.
    """
    _set_scrabble_values()
    word = "test"
    n = 4.0  # float, length is 4
    # t=1, e=1, s=1, t=1 => sum=4, letters=4 => 4*4=16, no bonus
    expected = 16
    assert getWordScore(word, n) == expected


def test_getWordScore_custom_letter_values():
    """
    Verify that the function respects a custom SCRABBLE_LETTER_VALUES mapping.
    """
    custom_values = {"x": 5, "y": 7, "z": 9}
    _set_scrabble_values(custom_values)
    word = "xyz"
    n = 3
    # x=5, y=7, z=9 => sum=21, letters=3 => 21*3=63, plus bonus 50 = 113
    expected = 113
    assert getWordScore(word, n) == expected


def test_getWordScore_very_long_word_no_error():
    """
    Ensure the function can handle a long word without raising exceptions.
    The exact score is not asserted; we only verify that a result is returned.
    """
    _set_scrabble_values()
    long_word = "pneumonoultramicroscopicsilicovolcanoconiosis"
    n = len(long_word)  # use all letters to trigger bonus
    result = getWordScore(long_word, n)
    assert result is not None
    assert isinstance(result, int) and result > 0