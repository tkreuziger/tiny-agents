from dataclasses import asdict, dataclass
from typing import Any, Literal

from .tools import ToolCall, ToolResult

MessageContentType = Literal["text", "image"]
Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True, slots=True)
class Message:
    """Represents a single message in a conversation, including optional metadata and tool interactions.

    Attributes:
        role: The role of the message author (system, user, assistant, or tool).
        content: Natural language text content of the message, if any.
        metadata: Optional metadata for the message, represented as string key-value pairs.
        tool_call: Tool invocation requested by the assistant, if present.
        tool_result: Result of a tool invocation, typically sent by the tool.
    """

    role: Role
    content_type: MessageContentType = "text"
    content: str | None = None
    content_data: str | None = None
    metadata: dict[str, str] | None = None

    tool_call: ToolCall | None = None
    tool_result: ToolResult | None = None

    def is_tool_call(self) -> bool:
        return self.role == "assistant" and self.tool_call is not None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
