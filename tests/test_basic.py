"""Basic tests for llmini package."""

from llmini import (
    Message,
    Role,
    Tool,
    ToolCall,
    assistant_message,
    execute_tool,
    get_tool_by_name,
    make_tool,
    system_message,
    user_message,
)


def test_imports():
    """Test that all public imports work."""
    assert Message is not None
    assert Role is not None
    assert Tool is not None


def test_role_literal():
    """Test Role is a Literal type with correct values."""
    from typing import get_args

    valid_roles = get_args(Role)
    assert "system" in valid_roles
    assert "user" in valid_roles
    assert "assistant" in valid_roles
    assert "tool" in valid_roles


def test_message_creation():
    """Test creating messages."""
    msg = user_message("hello")
    assert msg.role == "user"
    assert msg.content == "hello"

    sys_msg = system_message("be helpful")
    assert sys_msg.role == "system"

    asst_msg = assistant_message("hi there")
    assert asst_msg.role == "assistant"


def test_tool_creation():
    """Test creating a tool."""

    @make_tool()
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    assert isinstance(add, Tool)
    assert add.name == "add"


def test_tool_execution():
    """Test executing a tool."""

    @make_tool()
    def multiply(x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y

    tool_call = ToolCall(id="call-1", name="multiply", args={"x": 3, "y": 4})
    result = execute_tool(multiply, tool_call)
    assert result.role == "tool"
    assert result.tool_result is not None


def test_tool_lookup():
    """Test looking up a tool by name."""

    @make_tool()
    def greet(name: str) -> str:
        """Greet someone."""
        return f"Hello, {name}!"

    found = get_tool_by_name([greet], "greet")
    assert found is greet


def test_tool_lookup_not_found():
    """Test looking up a non-existent tool."""
    result = get_tool_by_name([], "nonexistent")
    assert result is None
