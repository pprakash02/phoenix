# Module: `Problem 4`

> This module provides a utility function for determining whether a given integer (or integer‑compatible value) is a triangular number. A triangular number *Tₙ* can be expressed as *n(n+1)/2* for some positive integer *n*. The implementation uses the inverse triangular‑number formula and checks if the resulting index is an integer.

## Functions

### `is_triangular(k)`

**Description**:  
Determines whether the argument `k` represents a triangular number. The function computes  

\[
x = \frac{\sqrt{8k + 1} - 1}{2}
\]

and returns `True` if `x` is an integer (i.e., `k` fits the triangular‑number formula), otherwise `False`.

**Parameters**:
- `k` (*int or float or bool*): The value to test. The docstring states it should be a positive integer, but the implementation accepts any numeric type that can be used in arithmetic with `math.sqrt`. Non‑numeric arguments will raise a `TypeError`.

**Returns**:  
`bool` – `True` if `k` is triangular, `False` otherwise.

**Examples**:
```python
# Based on observed runtime behavior
result = is_triangular(0)      # → True  (0 is treated as triangular by this implementation)
result = is_triangular(1)      # → True
result = is_triangular(True)   # → True  (True is interpreted as 1)
```

**Edge Cases / Notes**:
- The function does **not** validate that `k` is positive. Supplying a negative integer (e.g., `-1`) triggers `math.sqrt` on a negative argument, raising `ValueError: math domain error`.
- Passing non‑numeric types (e.g., strings) causes a `TypeError` because the expression `8*k + 1` attempts to concatenate a string with an integer.
- `bool` values are subclasses of `int`; therefore `True` is treated as `1` and returns `True`.
- Mathematically, the triangular sequence starts at `1` (`T₁ = 1`). The current implementation incorrectly returns `True` for `k = 0`. Users may need to add an explicit check if `0` should be excluded.