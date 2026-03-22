# Module: `Problem 7`

> This module provides utility functions for dictionary manipulation. Currently it implements a single helper, `dict_invert`, which creates an inverted mapping of a dictionary’s values to the list of keys that originally mapped to each value.

## Functions

### `dict_invert(d)`

**Description**  
Returns a new dictionary that inverts the mapping of the input dictionary `d`. For each unique value in `d`, the returned dictionary contains that value as a key, and its associated value is a **sorted list** of all original keys that mapped to it.

**Parameters**  
- `d` (*dict*): The dictionary to be inverted. Keys can be any hashable type; values must also be hashable because they become keys in the resulting dictionary.

**Returns**  
- *dict*: An inverted dictionary where each key is a value from the original `d` and each value is a sorted list of the original keys that corresponded to that value.

**Examples**
```python
# Example based on observed runtime behavior (invalid input)
result = dict_invert('hello')   # → AttributeError: 'str' object has no attribute 'items'

# Correct usage example
original = {'a': 1, 'b': 2, 'c': 1}
result = dict_invert(original)
# result == {1: ['a', 'c'], 2: ['b']}
```

**Edge Cases / Notes**  
- **Non‑dictionary input**: If `d` is not a dictionary (e.g., a string, list, or any other type), the function will raise an `AttributeError` because it attempts to call `.items()` on the argument.  
- **Duplicate values**: All keys that share the same value are collected into a list and sorted alphabetically (or according to the natural order of the key type).  
- **Empty dictionary**: Passing an empty dictionary (`{}`) returns an empty dictionary (`{}`).