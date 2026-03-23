import pytest
import importlib.util

# Dynamically load the target module because its path contains spaces
MODULE_FILE = "/home/pprakash/phoenix/generated_tests/PX-DC297CB5/workspace/Final Exam/Problem 3.py"
spec = importlib.util.spec_from_file_location("problem3_module", MODULE_FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Export the function to be tested
sum_digits = module.sum_digits


def test_sum_digits_mixed_characters():
    """
    Verify that sum_digits correctly sums numeric characters
    embedded within non‑numeric characters.
    """
    assert sum_digits("a;35d4") == 12  # 3 + 5 + 4
    assert sum_digits("abc123xyz") == 6  # 1 + 2 + 3
    assert sum_digits("0a1b2c3") == 6   # 0 + 1 + 2 + 3
    assert sum_digits("9") == 9
    assert sum_digits("abc9def0") == 9  # 9 + 0


def test_sum_digits_all_digits():
    """
    Ensure that a string consisting solely of digits returns the correct total.
    """
    assert sum_digits("1234567890") == 45
    assert sum_digits("0012") == 3  # 0+0+1+2
    assert sum_digits("99999") == 45


def test_sum_digits_no_digits_raises():
    """
    Confirm that a ValueError is raised when the input contains no digit characters.
    """
    for input_str in ["hello", "test", "", "a", "abcdef", "python"]:
        with pytest.raises(ValueError, match="No digits in input"):
            sum_digits(input_str)


def test_sum_digits_invalid_type_raises_type_error():
    """
    Passing a non‑string (e.g., int, list, None) should raise a TypeError
    because the implementation expects an iterable of characters.
    """
    for invalid_input in [123, ["1", "2"], None, 3.14, {"a": 1}]:
        with pytest.raises(TypeError):
            sum_digits(invalid_input)


def test_sum_digits_unicode_digit_characters():
    """
    Unicode characters that are considered digits by str.isdigit() will be
    identified, but int() conversion may fail, leading to a ValueError.
    """
    # The circled numbers are Unicode digits; int conversion raises ValueError.
    unicode_input = "①②3"
    with pytest.raises(ValueError):
        sum_digits(unicode_input)


def test_sum_digits_large_input():
    """
    Stress test with a long mixed string to ensure performance and correctness.
    """
    long_str = "a" * 1000 + "12345" + "b" * 500 + "67890" + "c" * 200
    # Expected sum: 1+2+3+4+5+6+7+8+9+0 = 45
    assert sum_digits(long_str) == 45

def test_sum_digits_boundary_empty_string():
    """
    An explicitly empty string should raise the same ValueError as any
    string without digits.
    """
    with pytest.raises(ValueError, match="No digits in input"):
        sum_digits("")

def test_sum_digits_boundary_single_non_digit():
    """
    A single-character string that is not a digit should raise ValueError.
    """
    with pytest.raises(ValueError):
        sum_digits("z")