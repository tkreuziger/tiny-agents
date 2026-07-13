import json

import pytest

from tiny_agents.messages.deserialize import message_from_json, messages_from_json
from tiny_agents.messages.make_message import (
    assistant_message,
    system_message,
    user_text_message,
)
from tiny_agents.messages.serialize import (
    message_to_json,
    messages_to_json,
    messages_to_jsonl,
)
from tiny_agents.messages.tools import ToolCall


def test_message_to_json_roundtrip():
    msg = user_text_message("hello world")
    json_str = message_to_json(msg)
    restored = message_from_json(json_str)

    assert restored.role == msg.role
    assert restored.content == msg.content


def test_messages_to_json_roundtrip():
    msgs = [system_message("sys"), user_text_message("hi")]
    json_str = messages_to_json(msgs)
    restored = messages_from_json(json_str)

    assert restored is not None
    assert len(restored) == 2
    assert restored[0].role == "system"
    assert restored[1].content == "hi"


def test_messages_to_jsonl():
    msgs = [user_text_message("a"), user_text_message("b")]
    jsonl = messages_to_jsonl(msgs)
    lines = jsonl.strip().split("\n")
    assert len(lines) == 2

    for line in lines:
        obj = json.loads(line)
        assert obj["role"] == "user"


def test_message_with_tool_call_serializes():
    tc = ToolCall(id="c1", name="fn", args={"x": 1})
    msg = assistant_message(tool_call=tc)
    json_str = message_to_json(msg)
    restored = message_from_json(json_str)

    assert restored.tool_call is not None
    assert restored.tool_call.id == "c1"
    assert restored.tool_call.name == "fn"
    assert restored.tool_call.args == {"x": 1}


def test_message_with_tool_result_serializes():
    msg = user_text_message("hi")
    json_str = message_to_json(msg)
    restored = message_from_json(json_str)

    assert restored.tool_result is None


def test_messages_from_json_invalid():
    result = messages_from_json("not json at all")
    assert result is None


def test_messages_from_json_bad_structure():
    with pytest.raises(AttributeError):
        messages_from_json('["just a string"]')


def test_message_to_json_no_indent():
    msg = user_text_message("hi")
    json_str = message_to_json(msg, indent=None)
    # Should be compact (no extra whitespace)
    assert "\n" not in json_str
