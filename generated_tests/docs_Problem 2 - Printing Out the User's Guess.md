# Module: `Problem 2 - Printing Out the User's Guess`

> This module contains a utility function used in Hangman‑style games to display the current state of a secret word based on the letters the player has guessed so far. The function returns a string where correctly guessed letters are shown in their original positions and all other characters are represented by underscores.

## Functions

### `getGuessedWord(secretWord, lettersGuessed)`

**Description**  
Constructs a visual representation of `secretWord` by revealing the letters that appear in `lettersGuessed` and replacing all other characters with underscores (`'_'`). The order of characters in the returned string matches the order in `secretWord`.

**Parameters**

- `secretWord` (*str*): The word that the user is trying to guess.
- `lettersGuessed` (*list of str*): A collection of letters that have been guessed so far.  
  *Typical usage expects each element to be a single‑character string (e.g., `['a', 'e', 'i']`).*

**Returns**  
`result` (*str*): A string composed of the correctly guessed letters and underscores for the remaining letters. The length of the string equals `len(secretWord)`.

**Examples**
```python
# Example 1 – no guessed letters match
result = getGuessedWord('hello', ['apple', 'banana', 'cherry'])
# → '_____'

# Example 2 – one matching letter ('e')
result = getGuessedWord('test', ['a', 'b', 'c', 'd', 'e'])
# → '_e__'

# Example 3 – empty secret word
result = getGuessedWord('', [])
# → ''

# Example 4 – guessed list contains a multi‑character string; no match
result = getGuessedWord('a', ['hello'])
# → '_'

# Example 5 – none of the guessed strings match any character
result = getGuessedWord('abcdef', ['test', 'word', 'example', 'data', 'value'])
# → '______'
```

**Edge Cases / Notes**
- The function does **not** validate that items in `lettersGuessed` are single characters. If the list contains multi‑character strings (as shown in the examples), the membership test `l in lettersGuessed` will fail, resulting in an underscore for that position.
- An empty `secretWord` returns an empty string (`''`).
- The function performs a simple linear scan; its time complexity is **O(n × m)** where *n* is the length of `secretWord` and *m* is the length of `lettersGuessed`. For typical Hangman usage (small word lengths and short guess lists) this is negligible.