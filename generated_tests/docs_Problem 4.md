# Module: `Problem 4`

> This module provides a single utility function that determines whether a given positive integer (or an integer‑compatible value) is a triangular number. A triangular number *Tₙ* satisfies the formula *Tₙ = n(n+1)/2*. The implementation uses the inverse quadratic formula to test the property.

## Functions

### `is_triangular(k)`

**Description**:  
Evaluates whether the argument `k` corresponds to a triangular number. The function computes  

\[
x = \frac{\sqrt{8k + 1} - 1}{2}
\]

and returns `True` if `x` is an integer (i.e., `k` can be expressed as *n(n+1)/2* for some integer *n*), otherwise `False`.

**Parameters**:
- `k` (*int* or *bool*): The value to test. Expected to be a non‑negative integer; booleans are accepted because they are subclasses of `int` in Python.

**Returns**:  
`bool` – `True` if `k` is triangular, `False` otherwise.

**Examples**:
```python
# Observed runtime behavior
result = is_triangular(0)      # → True  (note: 0 is not a standard triangular number)
result = is_triangular(1)      # → True
result = is_triangular(True)   # → True
```

**Edge Cases / Notes**:
- **Negative inputs**: `is_triangular(-1)` raises `ValueError: math domain error` because the expression under the square root becomes negative.
- **Non‑numeric inputs**: Passing a string such as `'test'` or `''` triggers `TypeError: can only concatenate str (not "int") to str`. This arises from the attempt to perform arithmetic with a non‑numeric type.
- **Zero handling**: The function returns `True` for `k = 0`, even though 0 is not traditionally considered a triangular number. Users may need to add an explicit check if a strict definition is required.
- **Missing import**: The function relies on `math.sqrt`; ensure `import math` is present in the module before calling the function.