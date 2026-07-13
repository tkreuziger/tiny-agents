from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Tool:
    """Represents a callable tool with its metadata and input schema.

    Attributes:
        name: A unique identifier for the tool.
        description: A human-readable summary of what the tool does.
        schema: A dictionary (typically JSON Schema–like) describing the
            expected input parameters, their types, and any validation rules.
        handler: The callable that implements the tool's behavior. It should
            accept arguments matching the defined schema and return the tool's
            result.
    """

    name: str
    description: str
    schema: dict[str, Any]
    handler: Callable[..., Any]
