# Module: `Problem 5`

> This module provides a simple utility function for removing all vowel characters from a given string while preserving the original order of the remaining characters. The resulting string is printed to standard output; the function does not return a value.

## Functions

### `print_without_vowels(s)`

**Description**:  
Creates a version of the input string `s` that contains no vowel characters (`a, e, i, o, u` in either lower‑ or upper‑case). The characters that remain retain their original order. The function prints this vowel‑free string and returns `None`.

**Parameters**:
- `s` (*str*): The source string from which vowels will be removed.

**Returns**:  
`None` – the function prints the processed string but does not return it.

**Examples**:
```python
# Based on observed runtime behavior
result = print_without_vowels('hello')   # → None (prints "hll")
result = print_without_vowels('test')    # → None (prints "tst")
result = print_without_vowels('')        # → None (prints "")
result = print_without_vowels('abcde')   # → None (prints "bcd")
```

**Edge Cases / Notes**:
- The function handles empty strings gracefully, printing nothing and returning `None`.
- Vowel removal is case‑insensitive; both uppercase and lowercase vowels are omitted.
- The function does **not** raise exceptions for any string input; it always returns `None`.