import json
import logging
from collections import deque
from pathlib import Path
from typing import Any

from .messages import Message
from .tools import ToolCall, ToolResult

logger = logging.getLogger(__name__)


def _parse_other_object[T](obj: dict[str, Any] | None, otype: type[T]) -> T | None:
    if obj is not None:
        return otype(**obj)
    return None


def _message_from_dict(obj: dict[str, Any]) -> Message:
    obj["tool_call"] = _parse_other_object(obj.get("tool_call"), ToolCall)
    obj["tool_result"] = _parse_other_object(obj.get("tool_result"), ToolResult)

    return Message(**obj)


def message_from_json(json_str: str) -> Message:
    """Deserialize a JSON-formatted string into a Message instance.

    Args:
        json_str: A JSON-formatted string representing a Message.

    Returns:
        A Message instance created from the JSON data.
    """
    obj = json.loads(json_str)
    return _message_from_dict(obj)


def messages_from_json(json_str: str) -> list[Message] | None:
    try:
        messages: list[Message] = []
        objects = json.loads(json_str)
        for obj in objects:
            messages.append(_message_from_dict(obj))

        return messages

    except json.JSONDecodeError:
        logger.exception("Failed to decode JSON.")
        return None

    except (TypeError, ValueError):
        logger.exception("Failed to parse message from dict.")
        return None


def messages_from_jsonl(path: Path, limit: int) -> list[Message] | None:
    try:
        with path.open(encoding="utf-8") as fp:
            all_lines = fp.readlines()

        if not all_lines:
            return []

        lines: list[str] = list(deque(all_lines, maxlen=limit))

        return [message_from_json(line) for line in lines]

    except json.JSONDecodeError:
        logger.exception("Failed to decode JSON.")
        return None

    except (TypeError, ValueError):
        logger.exception("Failed to parse message from dict.")
        return None
