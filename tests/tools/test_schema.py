from llmini.tools.schema import (
    function_to_schema,
    is_optional,
    python_type_to_schema,
    strip_optional,
)


def test_is_optional_with_optional():
    assert is_optional(int | None) is True


def test_is_optional_with_plain_type():
    assert is_optional(int) is False


def test_strip_optional():
    assert strip_optional(int | None) is int


def test_strip_optional_no_op():
    assert strip_optional(int) is int


def test_primitives():
    assert python_type_to_schema(str) == {"type": "string"}
    assert python_type_to_schema(int) == {"type": "integer"}
    assert python_type_to_schema(float) == {"type": "number"}
    assert python_type_to_schema(bool) == {"type": "boolean"}


def test_optional_strips_and_converts():
    assert python_type_to_schema(str | None) == {"type": "string"}


def test_list_type():
    result = python_type_to_schema(list[int])
    assert result == {"type": "array", "items": {"type": "integer"}}


def test_dict_type():
    result = python_type_to_schema(dict[str, int])
    assert result == {
        "type": "object",
        "additionalProperties": {"type": "integer"},
    }


def test_unknown_type_defaults_to_string():
    assert python_type_to_schema(object) == {"type": "string"}


def test_function_to_schema_basic():
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    schema = function_to_schema(add)
    assert schema["name"] == "add"
    assert schema["description"] == "Add two numbers."
    assert schema["parameters"]["required"] == ["a", "b"]
    assert schema["parameters"]["properties"]["a"] == {"type": "integer"}
    assert schema["parameters"]["properties"]["b"] == {"type": "integer"}


def greet(name: str, greeting: str = "Hello") -> str:
    """Greet someone.

    Args:
        name: The person's name.
        greeting: The greeting word.
    """
    return f"{greeting}, {name}!"


def test_function_to_schema_with_defaults():
    schema = function_to_schema(greet)
    assert schema["parameters"]["required"] == ["name"]
    assert "greeting" not in schema["parameters"]["required"]


def test_function_to_schema_with_optional_param():
    def notify(message: str, recipient: str | None = None) -> str:
        """Send a notification.

        Args:
            message: The message to send.
            recipient: Who to send to.
        """
        return "sent"

    schema = function_to_schema(notify)
    assert schema["parameters"]["required"] == ["message"]
    assert "recipient" not in schema["parameters"]["required"]
