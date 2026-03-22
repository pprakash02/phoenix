# Module: `Problem 1 - Word Scores`

> This module provides utilities for calculating Scrabble‑style scores for words.  
> The primary function, **`getWordScore`**, computes a word’s score based on individual
> letter values, the word length, and an optional bonus when the word uses all
> tiles from a hand of size `n`. The module expects a global dictionary
> `SCRABBLE_LETTER_VALUES` that maps lowercase letters to their Scrabble point
> values.

## Functions

### `getWordScore(word, n)`

**Description**  
Calculates the total score for a given `word`. The score is the sum of the
Scrabble values of each letter, multiplied by the number of letters used, and
adds a 50‑point bonus if the word consumes exactly `n` letters (i.e., the entire
hand). The function assumes that `word` consists only of lowercase alphabetic
characters and that `n` is a non‑negative integer representing the hand size.

**Parameters**
- `word` (*str*): The word whose score is to be computed. Must contain only
  lowercase letters.
- `n` (*int*): The size of the hand (number of tiles originally available).  
  Used to determine whether the 50‑point bonus applies.

**Returns**  
`int` – The computed score (always ≥ 0). Returns `0` immediately if `word` is
empty.

**Examples**
```python
# Example 1: empty word (any hand size, even negative)
result = getWordScore('', -1)   # → 0

# The following examples raise NameError because SCRABBLE_LETTER_VALUES
# is not defined in the current context. They illustrate the expected
# behavior once the dictionary is provided.

# result = getWordScore('hello', 0)   # → NameError: name 'SCRABBLE_LETTER_VALUES' is not defined
# result = getWordScore('test', 1)    # → NameError: name 'SCRABBLE_LETTER_VALUES' is not defined
# result = getWordScore('a', 10)      # → NameError: name 'SCRABBLE_LETTER_VALUES' is not defined
```

**Edge Cases / Notes**
- **Empty word**: Returns `0` without consulting `SCRABBLE_LETTER_VALUES`.
- **Missing `SCRABBLE_LETTER_VALUES`**: If the global dictionary is not defined,
  the function raises a `NameError`. Ensure that the mapping is imported or
  defined before calling the function.
- **Bonus condition**: The 50‑point bonus is applied **only** when the number
  of letters used (`len(word)`) exactly equals `n`. If `n` is negative or zero,
  the bonus will never be awarded (unless `len(word)` is also zero, which is
  handled earlier).
- **Input validation**: The function does **not** validate that `word` contains
  only valid letters; passing an invalid character will also raise a
  `KeyError` from the missing entry in `SCRABBLE_LETTER_VALUES`.