import json
from typing import Any

from litellm import Choices
from litellm.types.utils import ModelResponse

from ..messages import Message, ToolCall, assistant_message
from ..tools import Tool


def message_to_litellm(msg: Message) -> dict[str, Any]:
    """
    Convert an internal Message object into a LiteLLM-compatible dictionary.

    This function maps the Message roles and content into the structure
    expected by LiteLLM's chat/completions API. Supported roles:
    - "system", "user", "assistant": mapped directly with their content.
    - "tool": mapped to a "tool" role with an associated tool_call_id and content.

    Args:
        msg: The Message instance to convert.

    Returns:
        A dictionary representing the message in LiteLLM format.

    Raises:
        ValueError: If the message role is not recognized.
    """
    if msg.role == "user" and msg.content_type == "image":
        return {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": msg.content_data,
                }
            ],
        }
    if msg.role in {"system", "user", "assistant"}:
        return {
            "role": msg.role,
            "content": msg.content or "",
        }

    if msg.role == "tool" and msg.tool_result:
        return {
            "role": "tool",
            "tool_call_id": msg.tool_result.id,
            "content": msg.tool_result.data,
        }

    raise ValueError(f"Unknown message role: {msg.role}")


def tools_to_litellm(tools: list[Tool]) -> list[dict[str, Any]]:
    """
    Convert a list of Tool instances into LiteLLM-compatible tool definitions.

    Each Tool is mapped to a "function" type tool definition with a name,
    description, and JSON schema parameters, matching LiteLLM's expected
    tools format for function calling.

    Args:
        tools: A list of Tool objects to be converted.

    Returns:
        A list of dictionaries representing tools in LiteLLM format.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.schema,
            },
        }
        for tool in tools
    ]


def litellm_response_to_message(
    response: ModelResponse, meta_data: dict[str, Any]
) -> Message:
    """
    Convert a LiteLLM ModelResponse into an internal Message instance.

    This inspects the first choice in the response, reads its `message`,
    and returns either:
    - an assistant Message containing plain text content, or
    - an assistant Message containing a single ToolCall (if the model
      requested a tool invocation via `tool_calls`).

    Behavior:
    - Only the first element of `response.choices` is considered.
    - If `choice.message.tool_calls` is present and non-empty, only the
      first tool call is converted into a ToolCall and attached to the
      returned Message.
    - If there are no tool calls, the assistant's text content
      (`choice.message.content`) is used instead.
    - Any provided `meta_data` fields are forwarded to `assistant_message`.

    Args:
        response: LiteLLM ModelResponse with a `choices` list. The first
            choice must have a `message` attribute that may include
            `tool_calls` and/or `content`.
        meta_data: Additional metadata to attach to the internal Message
            (e.g., run IDs, timestamps, or other tracing information).

    Returns:
        An assistant Message representing the model reply,
        optionally including a ToolCall if the model requested a tool.
    """
    choice: Choices = response.choices[0]
    msg = choice.message

    if getattr(msg, "tool_calls", None):
        # Only one tool call per completion.
        tool_call = msg.tool_calls[0]

        return assistant_message(
            tool_call=ToolCall(
                id=tool_call.id,
                name=tool_call.function.name,
                args=json.loads(tool_call.function.arguments),
            ),
            **meta_data,
        )

    return assistant_message(text=msg.content, **meta_data)
