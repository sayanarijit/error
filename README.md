errorhelpers
============

[![PyPI version](https://img.shields.io/pypi/v/errorhelpers.svg)](https://pypi.org/project/errorhelpers)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/errorhelpers.svg)](https://pypi.org/project/errorhelpers)
[![Maintainability](https://api.codeclimate.com/v1/badges/989e85c7a858c7696658/maintainability)](https://codeclimate.com/github/sayanarijit/errorhelpers/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/989e85c7a858c7696658/test_coverage)](https://codeclimate.com/github/sayanarijit/errorhelpers/test_coverage)


Helpers for handling Python errors.


### Example 1: Basic usage

```python
import pytest
import errorhelpers

@errorhelpers.expect_errors(ZeroDivisionError)
def sensitive_transaction(x, y):
    return int(x) / int(y)

assert sensitive_transaction(4, "2") == 2

# `ZeroDivisionError` will be re-raised.
with pytest.raises(ZeroDivisionError):
    sensitive_transaction(4, 0)

# In case of other exceptions, `errorhelpers.UnexpectedError("Unexpected error")`
# will be raised instead.
with pytest.raises(errorhelpers.UnexpectedError, match="Unexpected error"):
    sensitive_transaction("a", "b")
```

### Example 2: Default value

```python
import pytest
import errorhelpers

@errorhelpers.expect_errors(
    ZeroDivisionError, on_unexpected_error=lambda err_, args_, kwargs_: -1
)
def sensitive_transaction(x, y):
    return int(x) / int(y)

assert sensitive_transaction(4, "2") == 2

# `ZeroDivisionError` will be re-raised.
with pytest.raises(ZeroDivisionError):
    sensitive_transaction(4, 0)

# In case of other exceptions, -1 will be returned.
assert sensitive_transaction("a", "b") == -1
```

### Example 3: Custom error

```python
import pytest
import errorhelpers

class CustomError(Exception):
    @classmethod
    def raise_(cls, msg):
        def raiser(error, args, kwargs):
            print("Hiding error:", error, "with args:", args, "and kwargs: ", kwargs)
            raise cls(msg)

        return raiser

@errorhelpers.expect_errors(
    ZeroDivisionError, on_unexpected_error=CustomError.raise_("Custom error")
)
def sensitive_transaction(x, y):
    return int(x) / int(y)

assert sensitive_transaction(4, "2") == 2

# `ZeroDivisionError` will be re-raised.
with pytest.raises(ZeroDivisionError):
    sensitive_transaction(4, 0)

# In case of other exceptions, `CustomError` will be raised instead.
with pytest.raises(CustomError, match="Custom error"):
    sensitive_transaction("a", "b")

# Hiding error: invalid literal for int() with base 10: 'a' with args: ('a', 'b') and kwargs:  {}
```
