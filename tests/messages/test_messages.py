from tiny_agents.messages.messages import Message
from tiny_agents.messages.tools import ToolCall, ToolResult


def test_message_basic():
    msg = Message(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"
    assert msg.tool_call is None
    assert msg.tool_result is None


def test_message_is_tool_call_false():
    msg = Message(role="user", content="hello")
    assert msg.is_tool_call() is False


def test_message_is_tool_call_true():
    tc = ToolCall(id="c1", name="fn", args={})
    msg = Message(role="assistant", tool_call=tc)
    assert msg.is_tool_call() is True


def test_message_is_tool_call_wrong_role():
    tc = ToolCall(id="c1", name="fn", args={})
    msg = Message(role="user", tool_call=tc)
    assert msg.is_tool_call() is False


def test_message_to_dict():
    msg = Message(role="system", content="be helpful")
    d = msg.to_dict()
    assert d["role"] == "system"
    assert d["content"] == "be helpful"
    assert isinstance(d, dict)


def test_message_frozen():
    msg = Message(role="user", content="hi")
    try:
        msg.content = "bye"  # type: ignore[misc]
        raise AssertionError("Should be frozen")
    except AttributeError:
        pass


def test_tool_call_dataclass():
    tc = ToolCall(id="c1", name="fn", args={"x": 1})
    assert tc.id == "c1"
    assert tc.name == "fn"
    assert tc.args == {"x": 1}


def test_tool_result_dataclass():
    tr = ToolResult(id="c1", data={"result": 42})
    assert tr.id == "c1"
    assert tr.data == {"result": 42}
