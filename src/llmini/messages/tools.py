from dataclasses import dataclass
from typing import Any

__all__ = ["ToolCall", "ToolResult"]


@dataclass(frozen=True, slots=True)
class ToolCall:
    """Represents a request from the assistant to invoke a tool.

    Attributes:
        id: Unique identifier for this tool call, used to match results.
        name: Name of the tool to be invoked.
        args: Arguments to pass to the tool, encoded as a dictionary.
    """

    id: str
    name: str
    args: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Represents the result returned by a tool invocation.

    Attributes:
        id: Identifier of the originating tool call (matches ToolCall.id).
        data: Arbitrary structured data produced by the tool.
    """

    id: str
    data: dict[str, Any]
