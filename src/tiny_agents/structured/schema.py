import json
from typing import Any

from pydantic import BaseModel


def pydantic_to_json_schema(model: type[BaseModel]) -> dict[str, Any]:
    return model.model_json_schema()


def generate_response_schema(name: str, model: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": name,
            "schema": model,
        },
        "strict": True,
    }


def generate_string_schema(model: dict[str, Any]) -> str:
    return json.dumps(model, indent=2, ensure_ascii=False)
