# Module: `Problem 2 - Dealing with Hands`

> This module provides utilities for manipulating a “hand” of letters in word‑game style applications.  
> A hand is represented as a dictionary that maps each letter (a single‑character string) to the count of how many times that letter is available.  
> The primary operation is to consume letters from a hand when a word is played, returning a new hand without mutating the original.

## Functions

### `updateHand(hand, word)`

**Description**:  
Creates a new hand dictionary that reflects the consumption of the letters required to form `word`.  
For each character in `word`, the corresponding count in the hand is decremented; if a count reaches zero, that entry is removed from the hand.  
The original `hand` dictionary is left unchanged (no side effects).

**Parameters**:
- `hand` (*dict[str, int]*): A mapping of letters to their available counts. The function assumes that the hand contains at least as many of each letter as appears in `word`.
- `word` (*str*): The word whose letters should be removed from the hand.

**Returns**:  
`dict[str, int]` – a new hand dictionary with the used letters removed (or reduced in count).

**Examples**:
```python
# Crash examples observed during testing
result = updateHand(0, 'hello')   # → AttributeError: 'int' object has no attribute 'copy'
result = updateHand(1, 'test')    # → AttributeError: 'int' object has no attribute 'copy'
result = updateHand(-1, '')       # → AttributeError: 'int' object has no attribute 'copy'
```

**Edge Cases / Notes**:
- **Invalid `hand` type**: Passing a non‑dictionary (e.g., an `int`) for `hand` triggers an `AttributeError` because the implementation calls `hand.copy()`. Ensure `hand` is a dictionary before invoking the function.
- **Missing letters**: If `word` contains a letter not present in `hand` (or more occurrences than available), a `KeyError` will be raised when the code attempts to decrement a non‑existent entry.
- **Empty word**: An empty string results in the hand being returned unchanged, provided `hand` is a valid dictionary.
- **No side effects**: The original `hand` object is never modified; a shallow copy is created and returned.