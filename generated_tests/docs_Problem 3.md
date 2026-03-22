# Module: `Problem 3`

> This module provides utility functions for processing strings. Currently it includes a function that extracts all numeric characters from a string and returns their arithmetic sum. The function validates that the input contains at least one digit and raises an exception otherwise.

## Functions

### `sum_digits(string)`

**Description**:  
Scans the supplied string for decimal digit characters (`0`‑`9`). If any digits are found, it converts each digit to an integer and returns the total sum of those integers. If the string contains no digits, a `ValueError` is raised.

**Parameters**:
- `string` (*str*): The input text to be examined for digit characters.

**Returns**:  
- *int*: The sum of all digit characters found in `string`.

**Examples**:
```python
# Example raising an error (observed runtime behavior)
result = sum_digits('hello')   # → ValueError: No digits in input

# Example raising an error (observed runtime behavior)
result = sum_digits('test')    # → ValueError: No digits in input

# Example raising an error (observed runtime behavior)
result = sum_digits('')        # → ValueError: No digits in input

# Typical successful usage (inferred from implementation)
result = sum_digits('a1b2c3')  # → 6
```

**Edge Cases / Notes**:
- The function **crashes** (raises `ValueError`) when the input string contains no digit characters, as demonstrated by the inputs `'hello'`, `'test'`, and `''`.
- Only characters that are individually recognized as digits by `str.isdigit()` are summed; multi‑digit numbers are treated as separate digits (e.g., `'12'` contributes `1 + 2 = 3`).
- Non‑numeric characters are ignored.