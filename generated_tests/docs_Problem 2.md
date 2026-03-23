# Module: `Problem 2`

> This module defines a single utility function that returns a constant integer value. The implementation does not depend on the input argument, making the function behave identically for any provided value.

## Functions

### `f(x)`

**Description**:  
Returns the integer `3` irrespective of the argument supplied. The function ignores its parameter and always produces the same constant output.

**Parameters**:
- `x` (*Any*): The input value is accepted but not used in any computation. It can be of any type (e.g., `int`, `float`, `str`, etc.).

**Returns**:  
`int` – the constant value `3`.

**Examples**:
```python
# Based on observed runtime behavior
result = f(0)        # → 3
result = f(1)        # → 3
result = f(-1)       # → 3
result = f('test')   # → 3
result = f('')       # → 3
```

**Edge Cases / Notes**:
- No crashes or exceptions were observed for any input type during testing.
- The function’s behavior is deterministic and does not depend on the value or type of `x`.