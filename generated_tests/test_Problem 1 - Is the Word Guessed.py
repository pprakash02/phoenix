import pytest
import importlib.util
import pathlib

# Dynamically load the target module from its file path.
# The file is located at:
# /home/pprakash/phoenix/generated_tests/PX-6DC06898/workspace/Problem Set 3/Problem 1 - Is the Word Guessed.py
module_path = pathlib.Path(__file__).parent.parent / "Problem Set 3" / "Problem 1 - Is the Word Guessed.py"
spec = importlib.util.spec_from_file_location("is_word_guessed_module", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

isWordGuessed = module.isWordGuessed


def test_isWordGuessed_observed_hello():
    """Regression test: secretWord='hello' with unrelated guessed letters should return False."""
    assert isWordGuessed('hello', ['apple', 'banana', 'cherry']) is False


def test_isWordGuessed_observed_test():
    """Regression test: secretWord='test' with letters that do not cover all characters should return False."""
    assert isWordGuessed('test', ['a', 'b', 'c', 'd', 'e']) is False


def test_isWordGuessed_observed_empty():
    """Regression test: empty secretWord should be considered guessed (True) regardless of guesses."""
    assert isWordGuessed('', []) is True


def test_isWordGuessed_observed_single_letter():
    """Regression test: secretWord='a' with unrelated guessed letters should return False."""
    assert isWordGuessed('a', ['hello']) is False


def test_isWordGuessed_observed_long_word():
    """Regression test: secretWord='abcdef' with unrelated guessed letters should return False."""
    assert isWordGuessed('abcdef', ['test', 'word', 'example', 'data', 'value']) is False


def test_isWordGuessed_observed_python():
    """Regression test: secretWord='python' with unrelated guessed letters should return False."""
    assert isWordGuessed('python', ['apple', 'banana', 'cherry']) is False


def test_isWordGuessed_all_letters_present():
    """Positive case: all letters of secretWord are present in lettersGuessed, should return True."""
    assert isWordGuessed('apple', ['a', 'p', 'l', 'e']) is True


def test_isWordGuessed_repeated_letters():
    """Edge case: secretWord contains repeated letters; each distinct letter only needs to appear once."""
    assert isWordGuessed('letter', ['l', 'e', 't', 'r']) is True


def test_isWordGuessed_case_sensitivity():
    """Edge case: function is case‑sensitive; mismatched case should result in False."""
    assert isWordGuessed('Apple', ['a', 'p', 'l', 'e']) is False


def test_isWordGuessed_empty_guesses_nonempty_word():
    """Edge case: non‑empty secretWord with empty guesses should return False."""
    assert isWordGuessed('nonempty', []) is False


def test_isWordGuessed_non_string_secret_word():
    """Exception case: passing a non‑string as secretWord should raise a TypeError."""
    with pytest.raises(TypeError):
        isWordGuessed(12345, ['1', '2', '3'])


def test_isWordGuessed_non_iterable_lettersGuessed():
    """Exception case: passing a non‑iterable as lettersGuessed should raise a TypeError."""
    with pytest.raises(TypeError):
        isWordGuessed('test', 123)


def test_isWordGuessed_none_inputs():
    """Exception case: passing None for either argument should raise a TypeError."""
    with pytest.raises(TypeError):
        isWordGuessed(None, ['a'])
    with pytest.raises(TypeError):
        isWordGuessed('a', None)


def test_isWordGuessed_mixed_type_lettersGuessed():
    """Edge case: lettersGuessed contains non‑string elements; containment check should still work."""
    assert isWordGuessed('abc', ['a', 1, None, 'b', 'c']) is True


def test_isWordGuessed_unicode_characters():
    """Edge case: secretWord and guesses contain Unicode characters."""
    assert isWordGuessed('café', ['c', 'a', 'f', 'é']) is True
    assert isWordGuessed('café', ['c', 'a', 'f']) is False

