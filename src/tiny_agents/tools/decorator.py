from collections.abc import Callable
from typing import TypeVar

from .schema import function_to_schema
from .types import Tool

F = TypeVar("F", bound=Callable[..., object])


def make_tool() -> Callable[[F], Tool]:
    """Create a decorator that turns a function into a `Tool`.

    This factory returns a decorator which, when applied to a function,
    will inspect the function's signature and docstring via `function_to_schema`,
    construct a JSON-schema-like `parameters` specification, and return a
    `Tool` instance with the function's name, description, schema, and handler.

    Returns:
        A decorator that converts a function into a `Tool` instance.
    """

    def wrap(fn: F) -> Tool:
        """Wrap the given function and return it as a `Tool` instance."""
        schema = function_to_schema(fn)

        return Tool(
            name=fn.__name__,
            description=schema["description"] or "",
            schema=schema["parameters"],
            handler=fn,
        )

    return wrap
