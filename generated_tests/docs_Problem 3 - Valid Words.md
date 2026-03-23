# Module: `Problem 3 - Valid Words`

> This module provides a utility to verify whether a given word is both present in a supplied dictionary of valid words and can be formed using the letters available in a player's hand. The core function performs the check without mutating its inputs.

## Functions

### `isValidWord(word, hand, wordList)`

**Description**:  
Determines if `word` is a valid entry (i.e., it exists in `wordList`) **and** can be constructed entirely from the letters available in `hand`. The function does **not** modify `hand` or `wordList`. It returns `True` only when both conditions are satisfied; otherwise it returns `False`.

**Parameters**:
- `word` (*str*): The candidate word to validate. Expected to be a non‑empty string of lowercase letters.
- `hand` (*dict[str, int]*): Mapping of letters to the number of times each letter is available. Example: `{'a': 2, 'b': 1}`.
- `wordList` (*list[str]*): A list containing all permissible lowercase words.

**Returns**:  
`bool` – `True` if `word` is in `wordList` **and** can be assembled from `hand`; `False` otherwise.

**Examples**:
```python
# Based on observed runtime behavior
# Example 1 – hand is an int, causing an AttributeError
result = isValidWord('hello', 0, ['apple', 'banana', 'cherry'])
# → AttributeError: 'int' object has no attribute 'copy'

# Example 2 – hand is an int, causing an AttributeError
result = isValidWord('test', 1, ['a', 'b', 'c', 'd', 'e'])
# → AttributeError: 'int' object has no attribute 'copy'

# Example 3 – empty word, valid hand but returns False
result = isValidWord('', -1, [])
# → AttributeError: 'int' object has no attribute 'copy' (hand is not a dict)
```

**Edge Cases / Notes**:
- **Non‑dict `hand`**: The function assumes `hand` implements the `.copy()` method. Passing a non‑dictionary (e.g., an `int`) raises `AttributeError: 'int' object has no attribute 'copy'`.
- **Empty string**: If `word` is `''`, the function immediately returns `False`.
- **Word not in `wordList`**: Returns `False` without checking the hand.
- **Insufficient letters**: If any character in `word` is missing from `hand` or appears more times than allowed, the function returns `False`.
- **Case sensitivity**: The implementation does not alter case; it expects lowercase inputs consistent with `wordList`.