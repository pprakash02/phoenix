# Module: `Problem 1 - Word Scores`

> This module provides utilities for calculating Scrabble‑style scores for words.  
> The primary function, `getWordScore`, computes the base letter values, scales the sum by the word length, and awards a bonus when the word uses all tiles from a hand of size `n`. The implementation assumes the constant `SCRABBLE_LETTER_VALUES` (a mapping of letters to their Scrabble points) is defined elsewhere in the project.

## Functions

### `getWordScore(word, n)`

**Description**:  
Calculates the total score for a given `word`. The score is the sum of the Scrabble point values for each letter in the word, multiplied by the number of letters used, plus an additional 50 points if the word consumes exactly `n` letters (i.e., the entire hand) on the first turn. The function expects `word` to be a non‑empty string of lowercase alphabetic characters; an empty string yields a score of `0`.

**Parameters**:
- `word` (*str*): The word whose score is to be calculated. Expected to contain only lowercase letters.
- `n` (*int*): The hand size that determines whether the 50‑point bonus is applied.

**Returns**:  
`int` – The computed score (always non‑negative). Returns `0` immediately if `word` is empty.

**Examples**:
```python
# Example 1: empty word (edge case)
result = getWordScore('', -1)      # → 0

# Example 2: normal usage (requires SCRABBLE_LETTER_VALUES to be defined)
# Assuming SCRABBLE_LETTER_VALUES = {'h': 4, 'e': 1, 'l': 1, 'o': 1, ...}
result = getWordScore('hello', 7)  # → (4+1+1+1+1) * 5 = 40  (no bonus)

# Example 3: using all tiles (bonus applied)
# Assuming SCRABBLE_LETTER_VALUES = {'a': 1}
result = getWordScore('a', 1)      # → (1) * 1 + 50 = 51
```

**Edge Cases / Notes**:
- **Missing Constant**: The function relies on a global dictionary `SCRABBLE_LETTER_VALUES`. If this constant is not defined, a `NameError` is raised (e.g., inputs `['hello', 0]`, `['test', 1]`, `['a', 10]` all trigger this error).
- **Negative Hand Size**: When `n` is negative (as in `['', -1]`), the function still returns `0` for an empty word because the early‑return check (`if len(word) == 0`) bypasses any further logic.
- **Zero Hand Size**: If `n` is `0` and the word is non‑empty, the bonus will never be applied because `lettersUsed` cannot be `0`. The function will still compute the regular score, provided `SCRABBLE_LETTER_VALUES` exists.
- **Observed Crashes**: The test suite reported 5 crashes, all stemming from the undefined `SCRABBLE_LETTER_VALUES` constant. Ensure this mapping is imported or defined before invoking `getWordScore`.