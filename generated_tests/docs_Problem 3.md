# Module: `Problem 3`

> This module provides utility functions for simple string analysis.  
> Currently it contains a single function that extracts and sums all numeric
> characters present in a given string, raising an error when the string does
> not contain any digits.

## Functions

### `sum_digits(string)`

**Description**:  
Scans the supplied string for digit characters (`0`‑`9`). If at least one digit
is found, it converts each digit to an integer and returns the sum of those
integers. If the string contains no digits, a `ValueError` is raised.

**Parameters**:
- `string` (*str*): The input text to be examined for numeric characters.

**Returns**:  
- *int*: The sum of all digit characters found in `string`.  
  (Returned only when at least one digit is present.)

**Examples**:
```python
# Observed runtime behavior – error cases
result = sum_digits('hello')   # → raises ValueError: No digits in input
result = sum_digits('test')    # → raises ValueError: No digits in input
result = sum_digits('')        # → raises ValueError: No digits in input

# Typical successful usage (not observed but inferred from implementation)
result = sum_digits('a1b2c3')  # → 6
```

**Edge Cases / Notes**:
- The function **crashes** (raises `ValueError`) when the input string contains
  no digit characters, as demonstrated by the inputs `'hello'`, `'test'`, and
  `''`.
- Only single‑character digits are summed; multi‑digit numbers are treated as
  separate characters (e.g., `'12'` yields `1 + 2 = 3`).
- Non‑string inputs will cause an `AttributeError` because the implementation
  assumes the argument supports the `str` methods `isdigit` and iteration.  
  Users should ensure that `string` is indeed a string before calling the
  function.