import pytest
import importlib.util
import pathlib

# Load the target module dynamically using its absolute path.
_MODULE_PATH = pathlib.Path(
    "/home/pprakash/phoenix/generated_tests/PX-6DC06898/workspace/Problem Set 5/Problem 4 - Decrypt a Story.py"
)
_spec = importlib.util.spec_from_file_location(
    "problem4_decrypt_story", _MODULE_PATH
)
_problem4 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_problem4)


def test_decrypt_story_raises_name_error():
    """
    Verify that calling decrypt_story without the required globals
    (CiphertextMessage and get_story_string) raises a NameError.
    """
    # Ensure the module does NOT have the required names.
    for name in ("CiphertextMessage", "get_story_string"):
        if hasattr(_problem4, name):
            delattr(_problem4, name)

    with pytest.raises(NameError):
        _problem4.decrypt_story()


def test_decrypt_story_returns_expected_tuple(monkeypatch):
    """
    Monkey‑patch the missing globals with dummy implementations and verify
    that decrypt_story returns the tuple produced by CiphertextMessage.decrypt_message().
    """
    # Dummy get_story_string returns a known encrypted string.
    dummy_encrypted = "abcde"
    monkeypatch.setattr(_problem4, "get_story_string", lambda: dummy_encrypted)

    # Dummy CiphertextMessage records the input and returns a fixed tuple.
    class DummyCiphertextMessage:
        def __init__(self, text):
            # Verify that the constructor receives the exact string from get_story_string.
            assert text == dummy_encrypted
            self.text = text

        def decrypt_message(self):
            # Return a deterministic shift and the reversed string.
            return (5, self.text[::-1])

    monkeypatch.setattr(_problem4, "CiphertextMessage", DummyCiphertextMessage)

    result = _problem4.decrypt_story()
    expected = (5, dummy_encrypted[::-1])
    assert result == expected


def test_decrypt_story_with_empty_string(monkeypatch):
    """
    Ensure decrypt_story works when get_story_string returns an empty string.
    The dummy CiphertextMessage should handle it gracefully.
    """
    monkeypatch.setattr(_problem4, "get_story_string", lambda: "")

    class DummyCiphertextMessage:
        def __init__(self, text):
            assert text == ""
            self.text = text

        def decrypt_message(self):
            return (0, self.text)  # No change for empty input.

    monkeypatch.setattr(_problem4, "CiphertextMessage", DummyCiphertextMessage)

    result = _problem4.decrypt_story()
    assert result == (0, "")


def test_decrypt_story_propagates_exception(monkeypatch):
    """
    If CiphertextMessage.decrypt_message raises an exception,
    decrypt_story should propagate that exception unchanged.
    """
    monkeypatch.setattr(_problem4, "get_story_string", lambda: "data")

    class DummyCiphertextMessage:
        def __init__(self, text):
            self.text = text

        def decrypt_message(self):
            raise ValueError("decryption failed")

    monkeypatch.setattr(_problem4, "CiphertextMessage", DummyCiphertextMessage)

    with pytest.raises(ValueError, match="decryption failed"):
        _problem4.decrypt_story()