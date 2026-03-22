# Module: `Problem 3 - Printing Out all Available Letters`

> This module provides a utility for the classic Hang‑man style games.  
> It computes which letters of the English alphabet have **not** been guessed yet, based on a list of previously guessed characters. The function operates only on lowercase letters `'a'`‑`'z'` and returns the remaining letters as a concatenated string.

## Functions

### `getAvailableLetters(lettersGuessed)`

**Description**  
Returns a string containing all lowercase English letters that are **not** present in the supplied `lettersGuessed` list. The function iterates through the alphabet in order and appends each letter that has not been guessed.

**Parameters**  
- `lettersGuessed` (*list of str*): A collection of characters (or strings) that have been guessed so far. The function expects each element to be a single lowercase letter, but it will treat any non‑matching entry as “not guessed”.

**Returns**  
- *str*: A string of the remaining (available) letters, ordered from `'a'` to `'z'`.

**Examples**
```python
# Example 1 – no letters guessed yet
result = getAvailableLetters([])                     # → 'abcdefghijklmnopqrstuvwxyz'

# Example 2 – some letters guessed
result = getAvailableLetters(['a', 'b', 'c', 'd', 'e'])  # → 'fghijklmnopqrstuvwxyz'

# Example 3 – input contains whole words (treated as non‑letters)
result = getAvailableLetters(['apple', 'banana', 'cherry'])  # → 'abcdefghijklmnopqrstuvwxyz'

# Example 4 – single‑character list inside another list (as observed in tests)
result = getAvailableLetters([['a', 'b', 'c']][0])   # → 'defghijklmnopqrstuvwxyz'

# Example 5 – mixed valid and invalid entries
result = getAvailableLetters(['t', 'e', 's', 't', 'word'])  # → 'abcdfghijklmnopqruvwxyz'
```

**Edge Cases / Notes**
- **Non‑letter entries**: Elements that are not single lowercase letters (e.g., full words like `'hello'`) are ignored, so the full alphabet is returned.
- **Case sensitivity**: The function only checks against lowercase `'a'`‑`'z'`. Uppercase letters will be considered “not guessed”.
- **Duplicate guesses**: Re‑guessing the same letter has no effect; the letter remains excluded from the result.
- **Empty input**: An empty `lettersGuessed` list yields the complete alphabet.
- **Performance**: The implementation runs in O(26 + n) time, where *n* is the length of `lettersGuessed`, which is negligible for typical game use.