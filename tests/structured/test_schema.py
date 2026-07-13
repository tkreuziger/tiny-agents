from pydantic import BaseModel

from tiny_agents.structured.schema import (
    generate_response_schema,
    generate_string_schema,
    pydantic_to_json_schema,
)


class Person(BaseModel):
    name: str
    age: int


def test_pydantic_to_json_schema():
    schema = pydantic_to_json_schema(Person)
    assert "properties" in schema
    assert "name" in schema["properties"]
    assert "age" in schema["properties"]


def test_generate_response_schema():
    inner = {"type": "object", "properties": {"x": {"type": "integer"}}}
    result = generate_response_schema("MyModel", inner)
    assert result["type"] == "json_schema"
    assert result["json_schema"]["name"] == "MyModel"
    assert result["json_schema"]["schema"] == inner
    assert result["strict"] is True


def test_generate_string_schema():
    inner = {"type": "object", "properties": {"x": {"type": "integer"}}}
    result = generate_string_schema(inner)
    assert isinstance(result, str)
    assert '"type"' in result
    assert '"object"' in result
