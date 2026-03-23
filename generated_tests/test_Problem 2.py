import pytest
import importlib.util
import pathlib

# Dynamically load the target module because its filename contains spaces.
module_path = (
    pathlib.Path(__file__).resolve()
    .parents[2]  # adjust as needed depending on test file location
    / "Midterm Exam"
    / "Problem 2.py"
)
spec = importlib.util.spec_from_file_location("problem_2_module", module_path)
problem_module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None, "Unable to locate the target module."
spec.loader.exec_module(problem_module)

# Export the function to be tested
f = problem_module.f


@pytest.mark.parametrize(
    "input_value",
    [
        0,
        1,
        -1,
        "test",
        "",
        True,
        None,
        3.1415,
        complex(1, 2),
        [],
        [1, 2, 3],
        {"key": "value"},
        object(),
    ],
)
def test_f_returns_3_for_various_inputs(input_value):
    """
    Verify that the function `f` returns the integer 3 for a wide range of inputs,
    including the observed successful cases and additional edge cases.
    """
    result = f(input_value)
    assert result == 3
    assert isinstance(result, int)


def test_f_always_returns_3_multiple_calls():
    """
    Ensure that repeated calls to `f` with the same argument consistently
    return 3 and do not raise unexpected exceptions.
    """
    for _ in range(10):
        assert f("consistent") == 3


def test_f_does_not_raise_for_unusual_types():
    """
    Confirm that `f` does not raise any exception when called with
    uncommon or complex argument types.
    """
    try:
        result = f(lambda x: x)
        assert result == 3
    except Exception as exc:
        pytest.fail(f"f raised an unexpected exception: {exc}")


def test_f_return_is_not_none():
    """
    The function should always return a concrete value (3), never None.
    """
    assert f("anything") is not None
    assert f("anything") == 3


def test_f_return_is_deterministic():
    """
    Since `f` is a pure function that always returns 3, verify that the
    result does not change across different Python sessions (determinism).
    """
    first = f(123)
    second = f("abc")
    third = f([1, 2, 3])
    assert first == second == third == 3