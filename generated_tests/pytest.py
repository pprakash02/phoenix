"""Minimal stub of pytest for the generated test suite.
Provides only the `raises` context manager needed for the tests.
"""
import re

class _RaisesContext:
    def __init__(self, expected_exception, match=None):
        self.expected = expected_exception
        self.match = match
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # No exception raised
        if exc_type is None:
            raise AssertionError(f"{self.expected.__name__} not raised")
        # Wrong type of exception
        if not issubclass(exc_type, self.expected):
            raise AssertionError(
                f"Expected {self.expected.__name__}, got {exc_type.__name__}"
            )
        # Check message pattern if provided
        if self.match is not None:
            if not re.search(self.match, str(exc_val)):
                raise AssertionError(
                    f"Exception message {exc_val!r} does not match pattern {self.match!r}"
                )
        # Suppress the exception
        self.exception = exc_val
        return True


def raises(expected_exception, match=None):
    """Return a context manager that asserts a specific exception is raised.

    Parameters
    ----------
    expected_exception: Exception class
        The exception type that should be raised.
    match: str, optional
        Regular expression that the exception message must match.
    """
    return _RaisesContext(expected_exception, match)

__all__ = ["raises"]
