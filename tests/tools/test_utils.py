import pytest

from llmini.messages import ToolCall
from llmini.tools.errors import ToolError, ToolFatalError
from llmini.tools.types import Tool
from llmini.tools.utils import execute_tool, get_tool_by_name


def _make_tool(name: str = "echo") -> Tool:
    return Tool(
        name=name,
        description="Echo input",
        schema={"type": "object", "properties": {"text": {"type": "string"}}},
        handler=lambda text="": text,
    )


def test_get_tool_by_name_found():
    tool = _make_tool("echo")
    assert get_tool_by_name([tool], "echo") is tool


def test_get_tool_by_name_not_found():
    tool = _make_tool("echo")
    assert get_tool_by_name([tool], "other") is None


def test_get_tool_by_name_none_name():
    tool = _make_tool("echo")
    assert get_tool_by_name([tool], None) is None


def test_execute_tool_success():
    tool = _make_tool("echo")
    call = ToolCall(id="c1", name="echo", args={"text": "hi"})
    result = execute_tool(tool, call)

    assert result.role == "tool"
    assert result.tool_result is not None
    assert result.tool_result.id == "c1"


def test_execute_tool_denied_by_approval():
    tool = _make_tool("echo")
    tool_with_approval = Tool(
        name=tool.name,
        description=tool.description,
        schema=tool.schema,
        handler=tool.handler,
        requires_approval=True,
    )
    call = ToolCall(id="c2", name="echo", args={"text": "hi"})

    def deny(_tool: Tool, _call: ToolCall) -> bool:
        return False

    result = execute_tool(tool_with_approval, call, approve=deny)
    assert result.role == "tool"
    assert "error" in result.tool_result.data


def test_execute_tool_error():
    def failing(**kwargs: object) -> str:
        raise ToolError("bad input")

    tool = Tool(name="fail", description="Fails", schema={}, handler=failing)
    call = ToolCall(id="c3", name="fail", args={})
    result = execute_tool(tool, call)

    assert "error" in result.tool_result.data
    assert result.tool_result.data["error"]["type"] == "tool_error"


def test_execute_tool_fatal_error_raises():
    def fatal(**kwargs: object) -> str:
        raise ToolFatalError("unrecoverable")

    tool = Tool(name="fatal", description="Fatal", schema={}, handler=fatal)
    call = ToolCall(id="c4", name="fatal", args={})

    with pytest.raises(RuntimeError, match="Agent terminated"):
        execute_tool(tool, call)


def test_execute_tool_unexpected_error_raises():
    def boom(**kwargs: object) -> str:
        raise ValueError("oops")

    tool = Tool(name="boom", description="Boom", schema={}, handler=boom)
    call = ToolCall(id="c5", name="boom", args={})

    with pytest.raises(RuntimeError, match="Unexpected tool failure"):
        execute_tool(tool, call)
