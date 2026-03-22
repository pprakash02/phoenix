# Module: `Problem 1 - Is the Word Guessed`

> This module provides a single utility function that determines whether a secret word has been completely guessed based on a collection of letters (or strings) that have been guessed so far. It is intended for use in word‑guessing games such as Hangman.

## Functions

### `isWordGuessed(secretWord, lettersGuessed)`

**Description**:  
Checks each character in `secretWord` to see if it appears in the `lettersGuessed` collection. Returns `True` only when **every** character of the secret word is present in the list; otherwise returns `False`.

**Parameters**:
- `secretWord` (*str*): The word the user is trying to guess.
- `lettersGuessed` (*list*): A list containing the letters (or strings) that have been guessed so far. The function treats each element of the list as a possible match for a single character of `secretWord`.

**Returns**:  
`bool` – `True` if all characters of `secretWord` are found in `lettersGuessed`; `False` otherwise.

**Examples**:
```python
# Based on observed runtime behavior
result = isWordGuessed('hello', ['apple', 'banana', 'cherry'])
# → False (none of the single letters h, e, l, o are in the list)

result = isWordGuessed('test', ['a', 'b', 'c', 'd', 'e'])
# → False (t is missing)

result = isWordGuessed('', [])
# → True (an empty word is trivially guessed)

result = isWordGuessed('a', ['hello'])
# → False ('hello' is not the single letter 'a')

result = isWordGuessed('abcdef', ['test', 'word', 'example', 'data', 'value'])
# → False (none of the required letters are present)
```

**Edge Cases / Notes**:
- The function does **not** validate that elements of `lettersGuessed` are single‑character strings. Supplying multi‑character strings (e.g., `'apple'`) will almost always cause the function to return `False` because those strings do not match individual characters.
- An empty `secretWord` returns `True` regardless of the content of `lettersGuessed`, as there are no letters to guess.
- The function performs a linear scan of `secretWord`; its time complexity is O(n) where *n* is the length of `secretWord`.