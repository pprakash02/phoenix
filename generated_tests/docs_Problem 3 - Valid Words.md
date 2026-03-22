# Module: `Problem 3 - Valid Words`

> This module provides utilities for validating whether a candidate word can be formed from a given hand of letters and appears in a supplied word list. The primary function, `isValidWord`, checks both membership in the word list and availability of required letters without mutating the input hand.

## Functions

### `isValidWord(word, hand, wordList)`

**Description**:  
Determines if `word` is a valid entry by confirming two conditions: (1) the word exists in `wordList`, and (2) every character of the word can be taken from `hand` with sufficient quantity. The function works on a copy of `hand`, leaving the original dictionary unchanged.

**Parameters**:
- `word` (*str*): The candidate word to validate. Must be a non‑empty string.
- `hand` (*dict[str, int]*): Mapping of letters to the number of times each letter is available. Each value should be a non‑negative integer.
- `wordList` (*list[str]*): A list containing lowercase strings representing the allowed vocabulary.

**Returns**: *bool* – `True` if `word` satisfies both conditions; `False` otherwise.

**Examples**:
```python
# Valid usage
hand = {'h': 1, 'e': 1, 'l': 2, 'o': 1}
wordList = ['hello', 'world']
result = isValidWord('hello', hand, wordList)   # → True

# Word not in wordList
result = isValidWord('test', hand, wordList)   # → False

# Not enough letters in hand
hand = {'h': 1, 'e': 1, 'l': 1, 'o': 1}
result = isValidWord('hello', hand, wordList)  # → False

# Based on observed runtime behavior (invalid `hand` type)
result = isValidWord('hello', 0, ['apple', 'banana', 'cherry'])
# → AttributeError: 'int' object has no attribute 'copy'

result = isValidWord('test', 1, ['a', 'b', 'c', 'd', 'e'])
# → AttributeError: 'int' object has no attribute 'copy'

result = isValidWord('', -1, [])
# → AttributeError: 'int' object has no attribute 'copy'
```

**Edge Cases / Notes**:
- An empty string (`word == ''`) is considered invalid and the function returns `False` without checking the hand or word list.
- The function expects `hand` to be a dictionary; passing any other type (e.g., an integer) triggers an `AttributeError` because the implementation calls `hand.copy()`.
- The function does **not** modify the original `hand` dictionary; it operates on a shallow copy.
- All letter counts are decremented on the temporary copy as characters are matched; if a required letter is missing or its count reaches zero, the validation fails.