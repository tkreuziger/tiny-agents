import time
from collections.abc import Callable
from typing import Any

from ..messages import Message, ToolCall, tool_message
from .errors import ToolError, ToolFatalError
from .types import Tool


def get_tool_by_name(tools: list[Tool], name: str | None) -> Tool | None:
    """Retrieve a tool from the provided list by its name.

    Args:
        tools: A list of Tool instances to search through.
        name: The name of the tool to look for. If None, the function
            immediately returns None.

    Returns:
        The Tool instance with the matching name, or None if no such tool
        is found or if name is None.
    """
    if name is None:
        return None

    for tool in tools:
        if tool.name == name:
            return tool

    return None


def execute_tool(
    tool: Tool,
    tool_call: ToolCall,
    *,
    approve: Callable[[Tool, ToolCall], bool] | None = None,
) -> Message:
    """Execute a tool with the provided ToolCall and wrap the result in a Message.

    This function invokes the tool's handler using the arguments specified in
    the ToolCall, measures execution time, and returns a tool_message that
    includes the result and duration. It normalizes known tool-related errors
    into a structured error payload, and escalates fatal or unexpected errors.

    Args:
        tool: The Tool instance to execute.
        tool_call: The ToolCall containing the arguments and metadata for the
            tool invocation.
        approve: Optional callback that gates execution. Called with the tool
            and tool_call; returns True to proceed, False to deny. When None,
            execution proceeds without gating.

    Returns:
        A Message instance produced by tool_message containing the tool's
        result or a structured error, along with execution duration.

    Raises:
        RuntimeError: If a ToolFatalError occurs (indicating the agent should
            terminate) or if any unexpected exception is raised during tool
            execution.
    """
    start_time = time.time()

    if tool.requires_approval:
        if approve:
            approved = approve(tool, tool_call)
        else:
            approved = False
    else:
        approved = True

    result: Any = None

    try:
        if approved:
            result = tool.handler(**tool_call.args)
        else:
            result = {
                "error": {
                    "type": "user_approval",
                    "message": "The user did not approve the use of the call.",
                }
            }

    except ToolError as ex:
        result = {
            "error": {
                "type": "tool_error",
                "message": str(ex),
            }
        }

    except ToolFatalError as ex:
        raise RuntimeError(f"Agent terminated: {ex}") from ex

    except Exception as ex:
        raise RuntimeError("Unexpected tool failure.") from ex

    return tool_message(
        tool_call_id=tool_call.id,
        data=result,
        duration=f"{time.time() - start_time:.2f}",
    )
