from typing import Any

from .media import encode_image, get_image_metadata
from .messages import Message
from .metadata import make_metadata
from .tools import ToolCall, ToolResult


def user_text_message(text: str) -> Message:
    """Create a Message authored by the user.

    Args:
        text: The natural language content of the user's message.

    Returns:
        A Message instance with role set to "user".
    """
    return Message(
        role="user",
        content=text,
        metadata=make_metadata(),
    )


def user_image_message(text: str, image_path: str) -> Message:
    """Create a Message authored by the user with an attached image.

    Args:
        text: The natural language content of the user's message.
        image_path: Path to the image file to attach.

    Returns:
        A Message instance with role set to "user" and content_type "image".
    """
    return Message(
        role="user",
        content_type="image",
        content=text,
        content_data=encode_image(image_path),
        metadata=make_metadata(**get_image_metadata(image_path) or {}),
    )


def system_message(text: str) -> Message:
    """Create a Message authored by the system.

    Args:
        text: The natural language content of the system message.

    Returns:
        A Message instance with role set to "system".
    """
    return Message(
        role="system",
        content=text,
        metadata=make_metadata(),
    )


def assistant_message(
    text: str | None = None,
    tool_call: ToolCall | None = None,
    **metadata_kwargs: str,
) -> Message:
    """Create a Message authored by the assistant.

    Args:
        text: The natural language content of the assistant's message, if any.
        tool_call: Optional ToolCall representing a requested tool invocation.
        **meta_data_kwargs: Additional metadata to include with the message.
            All keys must be strings, and all values must be strings.

    Returns:
        A Message instance with role set to "assistant", including the provided
        content, tool call, and metadata.
    """
    return Message(
        role="assistant",
        content=text,
        tool_call=tool_call,
        metadata=make_metadata(**metadata_kwargs),
    )


def tool_message(
    tool_call_id: str, data: dict[str, Any], **meta_data_kwargs: str
) -> Message:
    """Create a Message containing the result of a tool call.

    Args:
        tool_call_id: The identifier of the originating ToolCall.
        data: Structured result data produced by the tool.

    Returns:
        A Message instance with role set to "tool" and an attached ToolResult.
    """
    return Message(
        role="tool",
        tool_result=ToolResult(id=tool_call_id, data=data),
        metadata=make_metadata(**meta_data_kwargs),
    )
