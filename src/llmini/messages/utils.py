from .messages import Message


def append_messages(messages: list[Message], *msgs: Message) -> list[Message]:
    """Append one or more messages to an existing message list.

    Args:
        messages: The list of existing messages to extend.
        *msgs: One or more Message instances to append.

    Returns:
        The updated list of messages.
    """
    messages.extend(msgs)
    return messages
