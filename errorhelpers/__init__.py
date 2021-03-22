"""Helpers for handling Python errors."""

__version__ = "0.1.0"  # Also update pyproject.toml

from functools import wraps
from typing import Callable, TypeVar, Union, Sequence, Dict
from typing_extensions import Protocol

__all__ = ["UnexpectedError", "expect_errors"]

ExceptionType = TypeVar("ExceptionType", bound=BaseException)
FuncArgs = TypeVar("FuncArgs")
FuncKwArgs = TypeVar("FuncKwArgs")
FuncReturn = TypeVar("FuncReturn")
AlternateReturn = TypeVar("AlternateReturn")


class Func(Protocol):
    def __call__(
        self, *args: FuncArgs, **kwargs: FuncKwArgs
    ) -> FuncReturn:  # pragma: no cover
        ...


class AlternateFunc(Protocol):
    def __call__(
        self, *args: FuncArgs, **kwargs: FuncKwArgs
    ) -> Union[FuncReturn, AlternateReturn]:  # pragma: no cover
        ...


class UnexpectedError(BaseException):
    """This error is raised when something unexpected happens."""

    @classmethod
    def raise_(cls, _, __, ___) -> None:
        raise cls("Unexpected error")


def expect_errors(
    *errors: ExceptionType,
    on_unexpected_error: Callable[
        [ExceptionType, Sequence[FuncArgs], Dict[str, FuncKwArgs]], AlternateReturn
    ] = UnexpectedError.raise_
) -> AlternateFunc:
    """A decorator for handling the unexpected errors.

    Example 1: Basic usage

        >>> import pytest
        >>> import errorhelpers
        >>> 
        >>> @errorhelpers.expect_errors(ZeroDivisionError)
        ... def sensitive_transaction(x, y):
        ...     return int(x) / int(y)
        ... 
        >>> assert sensitive_transaction(4, "2") == 2
        >>> 
        >>> # `ZeroDivisionError` will be re-raised.
        >>> with pytest.raises(ZeroDivisionError):
        ...     sensitive_transaction(4, 0)
        ... 
        >>> # In case of other exceptions, `errorhelpers.UnexpectedError("Unexpected error")`
        >>> # will be raised instead.
        >>> with pytest.raises(errorhelpers.UnexpectedError, match="Unexpected error"):
        ...     sensitive_transaction("a", "b")

    Example 2: Default value

        >>> import pytest
        >>> import errorhelpers
        >>> 
        >>> @errorhelpers.expect_errors(
        ...     ZeroDivisionError, on_unexpected_error=lambda err_, args_, kwargs_: -1
        ... )
        ... def sensitive_transaction(x, y):
        ...     return int(x) / int(y)
        ... 
        >>> assert sensitive_transaction(4, "2") == 2
        >>> 
        >>> # `ZeroDivisionError` will be re-raised.
        >>> with pytest.raises(ZeroDivisionError):
        ...     sensitive_transaction(4, 0)
        ... 
        >>> # In case of other exceptions, -1 will be returned.
        >>> assert sensitive_transaction("a", "b") == -1

    Example 3: Custom error

        >>> import pytest
        >>> import errorhelpers
        >>> 
        >>> class CustomError(Exception):
        ...     @classmethod
        ...     def raise_(cls, msg):
        ...         def raiser(error, args, kwargs):
        ...             print("Hiding error:", error, "with args:", args, "and kwargs: ", kwargs)
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
        Hiding error: invalid literal for int() with base 10: 'a' with args: ('a', 'b') and kwargs:  {}
    """

    def wrapper(func: Func) -> AlternateFunc:
        @wraps(func)
        def wrapped(
            *args: FuncArgs, **kwargs: FuncKwArgs
        ) -> Union[FuncReturn, AlternateReturn]:
            try:
                return func(*args, **kwargs)
            except errors:
                raise
            except Exception as err:
                return on_unexpected_error(err, args, kwargs)

        return wrapped

    return wrapper
