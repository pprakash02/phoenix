import importlib.util
import pathlib

import pytest


def load_module():
    """
    Dynamically load the target module using its file path.
    Returns the imported module object.
    """
    module_path = pathlib.Path(
        "/home/pprakash/phoenix/generated_tests/PX-714DB47F/workspace/Problem Set 5/Problem 4 - Decrypt a Story.py"
    )
    spec = importlib.util.spec_from_file_location("problem_4_decrypt_story", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_decrypt_story_raises_name_error():
    """
    Verify that calling ``decrypt_story`` without the required globals
    raises a ``NameError`` because ``CiphertextMessage`` is not defined.
    """
    mod = load_module()
    with pytest.raises(NameError):
        mod.decrypt_story()


def test_decrypt_story_success(monkeypatch):
    """
    Monkey‑patch the missing dependencies with dummy implementations
    and assert that ``decrypt_story`` returns the value produced by
    ``CiphertextMessage.decrypt_message`` and that the encrypted string
    is passed correctly.
    """
    mod = load_module()

    captured = {}

    class DummyCiphertextMessage:
        def __init__(self, text):
            captured["text"] = text

        def decrypt_message(self):
            return (42, "dummy decrypted story")

    def dummy_get_story_string():
        return "encrypted story content"

    monkeypatch.setattr(mod, "CiphertextMessage", DummyCiphertextMessage)
    monkeypatch.setattr(mod, "get_story_string", dummy_get_story_string)

    result = mod.decrypt_story()

    assert captured["text"] == "encrypted story content"
    assert result == (42, "dummy decrypted story")


def test_decrypt_story_empty_string(monkeypatch):
    """
    Ensure that ``decrypt_story`` works when the story string is empty.
    The dummy ``CiphertextMessage`` records the received text and returns
    a predictable tuple.
    """
    mod = load_module()

    captured = {}

    class DummyCiphertextMessage:
        def __init__(self, text):
            captured["text"] = text

        def decrypt_message(self):
            return (0, "")

    def dummy_get_story_string():
        return ""

    monkeypatch.setattr(mod, "CiphertextMessage", DummyCiphertextMessage)
    monkeypatch.setattr(mod, "get_story_string", dummy_get_story_string)

    result = mod.decrypt_story()

    assert captured["text"] == ""
    assert result == (0, "")


def test_decrypt_story_non_string_return(monkeypatch):
    """
    Test the behaviour when ``get_story_string`` returns a non‑string value.
    The dummy ``CiphertextMessage`` does not enforce type checking, so the
    function should still forward the value and return the dummy result.
    """
    mod = load_module()

    captured = {}

    class DummyCiphertextMessage:
        def __init__(self, text):
            captured["text"] = text

        def decrypt_message(self):
            return ("shift", ["list", "of", "words"])

    def dummy_get_story_string():
        return 12345  # non‑string input

    monkeypatch.setattr(mod, "CiphertextMessage", DummyCiphertextMessage)
    monkeypatch.setattr(mod, "get_story_string", dummy_get_story_string)

    result = mod.decrypt_story()

    assert captured["text"] == 12345
    assert result == ("shift", ["list", "of", "words"])