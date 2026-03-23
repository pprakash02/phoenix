# Module: `Problem 2 - Printing Out the User's Guess`

> This module implements a helper routine used in word‑guessing games (e.g., Hangman).  
> The core function builds a visual representation of the secret word, revealing the letters that have already been guessed and masking the rest with underscores.

## Functions

### `getGuessedWord(secretWord, lettersGuessed)`

**Description**  
Constructs a string that shows which characters of `secretWord` have been guessed.  
For each character in `secretWord`, the function appends the character itself if it appears in the `lettersGuessed` list; otherwise it appends an underscore (`'_'`). The resulting string reflects the current state of the game board.

**Parameters**

- `secretWord` (*str*): The target word the user is trying to guess.
- `lettersGuessed` (*list of str*): A collection of letters (or strings) that have been guessed so far. Membership is tested **exactly**; only single‑character strings that match a character in `secretWord` will be revealed.

**Returns**  
- *str*: A string of the same length as `secretWord` composed of correctly guessed letters and underscores for unknown letters.

**Examples**
```python
# Example 1 – no guessed letters match
result = getGuessedWord('hello', ['apple', 'banana', 'cherry'])
# → '_____'

# Example 2 – one matching letter
result = getGuessedWord('test', ['a', 'b', 'c', 'd', 'e'])
# → '_e__'

# Example 3 – empty secret word
result = getGuessedWord('', [])
# → ''

# Example 4 – guessed entry is a whole word, not a single letter
result = getGuessedWord('a', ['hello'])
# → '_'

# Example 5 – list contains only multi‑character strings
result = getGuessedWord('abcdef', ['test', 'word', 'example', 'data', 'value'])
# → '______'
```

**Edge Cases / Notes**
- The function does **not** validate that items in `lettersGuessed` are single characters; any string longer than one character will never match a single character in `secretWord`.
- An empty `secretWord` yields an empty string regardless of `lettersGuessed`.
- Duplicate entries in `lettersGuessed` have no additional effect because membership testing is idempotent.
- The function assumes iterable inputs; passing non‑iterable types will raise a `TypeError`.