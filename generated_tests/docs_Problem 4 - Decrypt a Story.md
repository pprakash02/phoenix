# Module: `Problem 4 - Decrypt a Story`

> This module provides a single utility function that attempts to decrypt an encoded story using the `CiphertextMessage` class. The story text is obtained via `get_story_string()`. The function is intended to return the plaintext version of the story, but it currently fails due to a missing import/definition of `CiphertextMessage`.

## Functions

### `decrypt_story()`

**Description**:  
Retrieves an encrypted story string with `get_story_string()`, wraps it in a `CiphertextMessage` object, and returns the result of its `decrypt_message()` method, which should be the decrypted story text.

**Parameters**:  
- *(none)* – the function does not accept any arguments.

**Returns**:  
- `str` – the decrypted story text (expected when `CiphertextMessage` is properly defined).

**Examples**:
```python
# Based on observed runtime behavior
result = decrypt_story()  # → NameError: name 'CiphertextMessage' is not defined
```

**Edge Cases / Notes**:
- **Crash**: Calling the function as is raises a `NameError` because `CiphertextMessage` is not imported or defined within the module's scope.
- To use this function successfully, ensure that `CiphertextMessage` (and its dependency `get_story_string`) are correctly imported from the appropriate library or module before invoking `decrypt_story()`.