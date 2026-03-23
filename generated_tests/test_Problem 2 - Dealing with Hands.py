import pytest
import importlib.util
import pathlib
import copy

# Load the target module using its absolute path
MODULE_PATH = pathlib.Path(
    "/home/pprakash/phoenix/generated_tests/PX-6DC06898/workspace/Problem Set 4/Problem 2 - Dealing with Hands.py"
)

spec = importlib.util.spec_from_file_location("dealing_hands", MODULE_PATH)
dealing_hands = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dealing_hands)

updateHand = dealing_hands.updateHand


def test_updateHand_basic_example():
    """
    Verify that updateHand correctly removes used letters and does not mutate the original hand.
    """
    original_hand = {'a': 1, 'q': 1, 'l': 2, 'm': 1, 'u': 1, 'i': 1}
    hand_copy = copy.deepcopy(original_hand)
    result = updateHand(original_hand, "quail")
    assert result == {'l': 1, 'm': 1}
    # original hand must stay unchanged
    assert original_hand == hand_copy


def test_updateHand_multiple_occurrences():
    """
    Test a word that uses the same letter more than once.
    """
    hand = {'a': 3, 'b': 2}
    result = updateHand(hand, "aba")
    assert result == {'a': 1, 'b': 1}
    # ensure original hand unchanged
    assert hand == {'a': 3, 'b': 2}


def test_updateHand_empty_word_returns_copy():
    """
    An empty word should result in a shallow copy of the hand (no letters removed).
    """
    hand = {'x': 2, 'y': 1}
    result = updateHand(hand, "")
    assert result == hand
    # verify that a new dict object is returned
    assert result is not hand


def test_updateHand_empty_hand_and_word():
    """
    Empty hand with empty word should return an empty dict.
    """
    hand = {}
    result = updateHand(hand, "")
    assert result == {}


def test_updateHand_missing_letter_raises_keyerror():
    """
    Attempting to use a letter not present in the hand should raise a KeyError.
    """
    hand = {'a': 1, 'b': 1}
    with pytest.raises(KeyError):
        updateHand(hand, "c")


def test_updateHand_empty_hand_nonempty_word_raises_keyerror():
    """
    Using any word with an empty hand must raise a KeyError.
    """
    hand = {}
    with pytest.raises(KeyError):
        updateHand(hand, "test")


def test_updateHand_non_dict_hand_raises_attributeerror():
    """
    Passing a non-dictionary as the hand should raise AttributeError due to missing .copy().
    """
    for bad_hand in [0, 1, -1, 10, 100, 0.5]:
        with pytest.raises(AttributeError):
            updateHand(bad_hand, "hello")


def test_updateHand_non_string_word_raises_typeerror():
    """
    Passing a non-iterable (non-string) word should raise a TypeError.
    """
    hand = {'a': 1}
    with pytest.raises(TypeError):
        updateHand(hand, 123)  # int is not iterable


def test_updateHand_hand_with_zero_counts():
    """
    Hand may contain zero counts; decrementing a missing letter leads to negative count.
    Ensure function does not delete the key unless count becomes exactly zero.
    """
    hand = {'a': 0, 'b': 1}
    result = updateHand(hand, "b")
    assert result == {'a': 0}
    # key 'a' with zero count remains because it was never decremented


def test_updateHand_unused_letters_stay():
    """
    Letters in the hand that are not used in the word must remain unchanged.
    """
    hand = {'c': 2, 'd': 1, 'e': 3}
    result = updateHand(hand, "ced")
    # 'c' used once, 'e' used once, 'd' used once
    assert result == {'c': 1, 'e': 2}
    # original hand unchanged
    assert hand == {'c': 2, 'd': 1, 'e': 3}