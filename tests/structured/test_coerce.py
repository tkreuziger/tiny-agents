import pytest
from pydantic import BaseModel

from llmini.structured.coerce import coerce_to_model


class Person(BaseModel):
    name: str
    age: int


def test_coerce_valid_json():
    raw = '{"name": "Alice", "age": 30}'
    result = coerce_to_model(Person, raw)
    assert result.name == "Alice"
    assert result.age == 30


def test_coerce_json_with_surrounding_text():
    raw = 'Here is the result: {"name": "Bob", "age": 25} hope that helps!'
    result = coerce_to_model(Person, raw)
    assert result.name == "Bob"
    assert result.age == 25


def test_coerce_invalid_raises():
    with pytest.raises(RuntimeError, match="Could not coerce"):
        coerce_to_model(Person, "not json at all")


def test_coerce_validates_types():
    with pytest.raises(RuntimeError, match="Could not coerce"):
        coerce_to_model(Person, '{"name": "Alice", "age": "not a number"}')
