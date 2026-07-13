import json

from tiny_agents.completion.utils import (
    litellm_response_to_message,
    message_to_litellm,
    tools_to_litellm,
)
from tiny_agents.messages.make_message import assistant_message, system_message, tool_message, user_text_message
from tiny_agents.messages.tools import ToolCall, ToolResult
from tiny_agents.tools.types import Tool


def test_message_to_litellm_user():
    msg = user_text_message("hi")
    result = message_to_litellm(msg)
    assert result["role"] == "user"
    assert result["content"] == "hi"


def test_message_to_litellm_system():
    msg = system_message("be helpful")
    result = message_to_litellm(msg)
    assert result["role"] == "system"
    assert result["content"] == "be helpful"


def test_message_to_litellm_assistant():
    msg = assistant_message("ok")
    result = message_to_litellm(msg)
    assert result["role"] == "assistant"
    assert result["content"] == "ok"


def test_message_to_litellm_tool():
    msg = tool_message("c1", {"result": 42})
    result = message_to_litellm(msg)
    assert result["role"] == "tool"
    assert result["tool_call_id"] == "c1"
    assert result["content"] == {"result": 42}


def test_message_to_litellm_image():
    from tiny_agents.messages.messages import Message

    msg = Message(
        role="user",
        content_type="image",
        content="describe this",
        content_data="data:image/png;base64,abc123",
    )
    result = message_to_litellm(msg)
    assert result["role"] == "user"
    assert isinstance(result["content"], list)
    assert result["content"][0]["type"] == "image_url"


def test_message_to_litellm_unknown_role():
    from tiny_agents.messages.messages import Message

    msg = Message(role="user", content="hi")  # type: ignore[arg-type]
    # Patch role to an invalid value after construction
    object.__setattr__(msg, "role", "unknown")  # type: ignore[arg-type]
    try:
        message_to_litellm(msg)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown message role" in str(e)


def test_tools_to_litellm():
    tool = Tool(
        name="add",
        description="Add numbers",
        schema={"type": "object", "properties": {"a": {"type": "integer"}}},
        handler=lambda a: a,
    )
    result = tools_to_litellm([tool])
    assert len(result) == 1
    assert result[0]["type"] == "function"
    assert result[0]["function"]["name"] == "add"
    assert result[0]["function"]["description"] == "Add numbers"


def test_tools_to_litellm_empty():
    assert tools_to_litellm([]) == []


class _FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class _FakeChoice:
    def __init__(self, message):
        self.message = message


class _FakeResponse:
    def __init__(self, choice):
        self.choices = [choice]


def test_litellm_response_to_message_text():
    fake_msg = _FakeMessage(content="hello from llm")
    resp = _FakeResponse(_FakeChoice(fake_msg))
    msg = litellm_response_to_message(resp, {"model": "test"})

    assert msg.role == "assistant"
    assert msg.content == "hello from llm"
    assert msg.tool_call is None
    assert msg.metadata["model"] == "test"


def test_litellm_response_to_message_tool_call():
    fake_tc = type("obj", (), {"id": "tc1", "function": type("fn", (), {"name": "add", "arguments": '{"x":1}'})})()
    fake_msg = _FakeMessage(tool_calls=[fake_tc])
    resp = _FakeResponse(_FakeChoice(fake_msg))
    msg = litellm_response_to_message(resp, {})

    assert msg.tool_call is not None
    assert msg.tool_call.id == "tc1"
    assert msg.tool_call.name == "add"
    assert msg.tool_call.args == {"x": 1}
    assert msg.content is None
