# Module: `Problem 4 - Hand Length`

> This module provides a utility function for determining the total number of letters currently available in a player's hand. The hand is represented as a dictionary where keys are single‑character strings (letters) and values are the counts of each letter.

## Functions

### `calculateHandlen(hand)`

**Description**:  
Computes the total length of the hand by summing the counts of all letters stored in the `hand` dictionary.

**Parameters**:
- `hand` (*dict[str, int]*): A mapping from each letter (as a one‑character string) to the number of times that letter appears in the hand.

**Returns**:  
`int` – the sum of all letter counts, i.e., the total number of letters in the hand.

**Examples**:
```python
# Based on observed runtime behavior (error cases)
result = calculateHandlen(0)   # → TypeError: 'int' object is not iterable
result = calculateHandlen(1)   # → TypeError: 'int' object is not iterable
result = calculateHandlen(-1)  # → TypeError: 'int' object is not iterable

# Typical successful usage
hand = {'a': 2, 'b': 1, 'c': 3}
result = calculateHandlen(hand)  # → 6
```

**Edge Cases / Notes**:
- The function expects an *iterable* dictionary. Passing a non‑dictionary (e.g., an `int`) raises `TypeError: 'int' object is not iterable`.
- An empty dictionary `{}` is a valid input and will correctly return `0`.
- All values in the dictionary should be integers; non‑integer values may cause unexpected results or errors during the summation.  

---