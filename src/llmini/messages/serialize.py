import datetime as dt
import json
from typing import Any

from .messages import Message


def _default_serializer(obj: Any) -> str | None:
    if isinstance(obj, (dt.date, dt.datetime)):
        return obj.isoformat()
    return None


def message_to_json(message: Message, indent: int | None = 2) -> str:
    """Serialize a Message instance to a JSON-formatted string.

    Args:
        message: The Message instance to serialize.

    Returns:
        A JSON-formatted string representing the message.
    """
    return json.dumps(message.to_dict(), indent=indent, default=_default_serializer)


def messages_to_json(messages: list[Message], indent: int | None = 2) -> str:
    obj = [message.to_dict() for message in messages]
    return json.dumps(obj, indent=indent, default=_default_serializer)


def messages_to_jsonl(messages: list[Message]) -> str:
    return (
        "\n".join(message_to_json(message, indent=None) for message in messages) + "\n"
    )
