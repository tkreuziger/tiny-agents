from tiny_agents.messages.make_message import (
    assistant_message,
    system_message,
    tool_message,
    user_text_message,
)
from tiny_agents.messages.tools import ToolCall


def test_user_text_message():
    msg = user_text_message("hello")
    assert msg.role == "user"
    assert msg.content == "hello"
    assert msg.metadata is not None
    assert "created_at" in msg.metadata


def test_system_message():
    msg = system_message("be helpful")
    assert msg.role == "system"
    assert msg.content == "be helpful"
    assert msg.metadata is not None


def test_assistant_message_text():
    msg = assistant_message("sure thing")
    assert msg.role == "assistant"
    assert msg.content == "sure thing"
    assert msg.tool_call is None


def test_assistant_message_with_tool_call():
    tc = ToolCall(id="c1", name="fn", args={"x": 1})
    msg = assistant_message(tool_call=tc)
    assert msg.role == "assistant"
    assert msg.tool_call is not None
    assert msg.tool_call.name == "fn"
    assert msg.content is None


def test_assistant_message_with_metadata():
    msg = assistant_message("ok", model="gpt-4")
    assert msg.metadata is not None
    assert msg.metadata["model"] == "gpt-4"


def test_tool_message():
    msg = tool_message("c1", {"result": 42})
    assert msg.role == "tool"
    assert msg.tool_result is not None
    assert msg.tool_result.id == "c1"
    assert msg.tool_result.data == {"result": 42}
    assert msg.metadata is not None
