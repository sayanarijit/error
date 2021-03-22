"""Helpers for handling Python errors."""

__version__ = "0.2.0"  # Also update pyproject.toml
__all__ = ["UnexpectedError", "expect_errors"]

from contextlib import contextmanager
from functools import wraps
from typing import Callable, Dict, Sequence, TypeVar, Union

from typing_extensions import Protocol

ExceptionType = TypeVar("ExceptionType", bound=BaseException)
FuncArgs = TypeVar("FuncArgs")
FuncKwArgs = TypeVar("FuncKwArgs")
FuncReturn = TypeVar("FuncReturn")


class Func(Protocol):
    def __call__(
        self, *args: FuncArgs, **kwargs: FuncKwArgs
    ) -> FuncReturn:  # pragma: no cover
        ...


class UnexpectedError(Exception):
    """This error is raised when something unexpected happens."""

    @classmethod
    def raise_(cls, _) -> None:
        raise cls("Unexpected error")


@contextmanager
def expect_errors(
    *errors: ExceptionType,
    on_unexpected_error: Callable[
        [ExceptionType], FuncReturn
    ] = UnexpectedError.raise_
) -> Func:
    """A decorator for handling the unexpected errors.

    Usage: ::

        # As a decorator
        @errorhelpers.expect_error(*errors, on_unexpected_error=handler)
        def some_error_prone_funcion():
            ...

        # Using with statement
        with errorhelpers.expect_error(*errors, on_unexpected_error=handler):
            # Some error prone operation
            ...


    Example 1: Basic usage

        >>> import pytest
        >>> import errorhelpers
        >>>
        >>> with errorhelpers.expect_errors(ZeroDivisionError):
        ...     assert 4 / 2 == 2
        ...
        >>> # `ZeroDivisionError` will be re-raised.
        >>> with pytest.raises(ZeroDivisionError):
        ...     with errorhelpers.expect_errors(ZeroDivisionError):
        ...         4 / 0
        ...
        >>> # In case of other exceptions, `errorhelpers.UnexpectedError("Unexpected error")`
        >>> # will be raised instead.
        >>> with pytest.raises(errorhelpers.UnexpectedError, match="Unexpected error"):
        ...     with errorhelpers.expect_errors(ZeroDivisionError):
        ...         "a" / "b"


    Example 2: Custom error

        >>> import pytest
        >>> import errorhelpers
        >>>
        >>> class CustomError(Exception):
        ...     @classmethod
        ...     def raise_(cls, msg):
        ...         def raiser(error):
        ...             print("Hiding error:", error)
        ...             raise cls(msg)
        ...
        ...         return raiser
        ...
        >>> @errorhelpers.expect_errors(
        ...     ZeroDivisionError, on_unexpected_error=CustomError.raise_("Custom error")
        ... )
        ... def sensitive_transaction(x, y):
        ...     return int(x) / int(y)
        >>>
        >>> assert sensitive_transaction(4, "2") == 2
        >>>
        >>> # `ZeroDivisionError` will be re-raised.
        >>> with pytest.raises(ZeroDivisionError):
        ...     sensitive_transaction(4, 0)
        ...
        >>> # In case of other exceptions, `CustomError` will be raised instead.
        >>> with pytest.raises(CustomError, match="Custom error"):
        ...     sensitive_transaction("a", "b")
        ...
        Hiding error: invalid literal for int() with base 10: 'a'
    """

    try:
        yield
    except errors as err:
        raise err
    except Exception as err:
        raise on_unexpected_error(err)
