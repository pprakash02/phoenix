import pytest
from .home.pprakash.phoenix.generated_tests.PX-714DB47F.workspace.Midterm Exam.Problem 5 import print_without_vowels


def test_print_without_vowels_basic_hello(capsys):
    """Verify that vowels are removed from a simple lowercase word."""
    print_without_vowels("hello")
    captured = capsys.readouterr()
    assert captured.out == "hll"


def test_print_without_vowels_basic_test(capsys):
    """Verify removal of vowels from another simple word."""
    print_without_vowels("test")
    captured = capsys.readouterr()
    assert captured.out == "tst"


def test_print_without_vowels_empty_string(capsys):
    """An empty input should result in no output (empty string)."""
    print_without_vowels("")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_print_without_vowels_abcde(capsys):
    """String containing both vowels and consonants should return only consonants."""
    print_without_vowels("abcde")
    captured = capsys.readouterr()
    assert captured.out == "bcd"


def test_print_without_vowels_all_vowels(capsys):
    """A string consisting solely of vowels should produce an empty output."""
    print_without_vowels("aeiouAEIOU")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_print_without_vowels_mixed_case(capsys):
    """Mixed case letters should have vowels removed regardless of case."""
    print_without_vowels("HeLLo WoRLd")
    captured = capsys.readouterr()
    assert captured.out == "HLL WRLd"


def test_print_without_vowels_non_ascii(capsys):
    """Non‑ASCII characters (e.g., emojis) should be preserved."""
    print_without_vowels("😀a😀e😀")
    captured = capsys.readouterr()
    # Only the emojis remain; vowels are stripped
    assert captured.out == "😀😀😀"


def test_print_without_vowels_newline_and_spaces(capsys):
    """Whitespace and newline characters are not vowels and should be retained."""
    input_str = "a b\nc d e"
    print_without_vowels(input_str)
    captured = capsys.readouterr()
    # Expected: spaces and newline stay, vowels removed
    assert captured.out == " b\nc d "


def test_print_without_vowels_type_error():
    """Passing a non‑iterable (e.g., integer) should raise a TypeError."""
    with pytest.raises(TypeError):
        print_without_vowels(12345)


def test_print_without_vowels_none_input():
    """Passing None should raise a TypeError because None is not iterable."""
    with pytest.raises(TypeError):
        print_without_vowels(None)