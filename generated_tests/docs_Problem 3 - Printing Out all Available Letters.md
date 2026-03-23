# Module: `Problem 3 - Printing Out all Available Letters`

> This module provides a utility for determining which letters of the English alphabet have **not** been guessed yet. It is primarily useful in word‑guessing games (e.g., Hangman) where the program needs to display the remaining possible letters to the player.

## Functions

### `getAvailableLetters(lettersGuessed)`

**Description**:  
Returns a string containing all lowercase English letters (`a`‑`z`) that are **not** present in the supplied `lettersGuessed` list. The function iterates through the alphabet in order and builds a result string with each letter that has not been guessed.

**Parameters**:
- `lettersGuessed` (*list of str*): A list representing the letters that have been guessed so far. Elements are expected to be single‑character lowercase strings, but the function does not enforce this.

**Returns**:  
- *str*: A concatenated string of the remaining unguessed letters, ordered from `a` to `z`.

**Examples**:
```python
# Based on observed runtime behavior
result = getAvailableLetters(['apple', 'banana', 'cherry'])
# → 'abcdefghijklmnopqrstuvwxyz'

result = getAvailableLetters(['a', 'b', 'c', 'd', 'e'])
# → 'fghijklmnopqrstuvwxyz'

result = getAvailableLetters([])
# → 'abcdefghijklmnopqrstuvwxyz'

result = getAvailableLetters(['hello'])
# → 'abcdefghijklmnopqrstuvwxyz'

result = getAvailableLetters(['test', 'word', 'example', 'data', 'value'])
# → 'abcdefghijklmnopqrstuvwxyz'
```

**Edge Cases / Notes**:
- The function treats the `lettersGuessed` list as a collection of exact characters; any entry longer than one character (e.g., `'apple'`) will **not** match any single alphabet letter and therefore has no effect on the output.
- Only lowercase letters `a`‑`z` are considered. Uppercase letters or non‑alphabetic characters are ignored because they do not appear in the reference string `'abcdefghijklmnopqrstuvwxyz'`.
- No validation or error handling is performed; passing a non‑list argument will raise a `TypeError` when the function attempts to iterate over it.
- The returned string is always sorted alphabetically, regardless of the order of elements in `lettersGuessed`.

---