# Module: `Problem 2`

> This module defines a single utility function that always returns the integer `3`, irrespective of the argument supplied. It can be used wherever a constant value of `3` is required without performing any computation on the input.

## Functions

### `f(x)`

**Description**: Returns the constant integer `3` for any provided argument. The input is ignored, making the function effectively a constant generator.

**Parameters**:
- `x` (*Any*): The value passed to the function. Its type is not used in the computation; examples include integers, strings, or any other Python object.

**Returns**: `int` – always the value `3`.

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
- The function does not raise exceptions for any input type; it consistently returns `3`.