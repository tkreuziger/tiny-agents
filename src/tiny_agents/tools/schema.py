import inspect
import logging
import types
from typing import Any, Literal, Union, get_args, get_origin

from .docstring import parse_google_docstring

logger = logging.getLogger(__name__)


def is_optional(annotation: Any) -> bool:
    origin = get_origin(annotation)

    if origin is Union or origin is types.UnionType:
        return type(None) in get_args(annotation)

    return False


def strip_optional(annotation: Any) -> Any:
    if is_optional(annotation):
        return next(a for a in get_args(annotation) if a is not type(None))

    return annotation


def python_type_to_schema(annotation: Any) -> dict[str, Any]:
    """
    Convert a Python type annotation into a JSON-schema fragment.
    Handles:
      - basic primitives
      - Optional[T]
      - list[T]
      - dict[str, T]
      - Literal[...]
    """
    annotation = strip_optional(annotation)
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Literal:
        return {
            "type": python_type_to_schema(type(args[0]))["type"],
            "enum": list(args),
        }

    if origin is list:
        item_type = args[0] if args else Any
        return {
            "type": "array",
            "items": python_type_to_schema(item_type),
        }

    if origin is dict:
        value_type = args[1] if len(args) == 2 else Any
        return {
            "type": "object",
            "additionalProperties": python_type_to_schema(value_type),
        }

    primitive_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
    }

    if annotation not in primitive_map:
        logger.warning("Unknown type annotation %s, defaulting to string.", annotation)

    return {"type": primitive_map.get(annotation, "string")}


def function_to_schema(func: Any) -> dict[str, Any]:
    sig = inspect.signature(func)
    doc = parse_google_docstring(func.__doc__)

    properties = {}
    required = []

    for name, param in sig.parameters.items():
        annotation = (
            param.annotation if param.annotation is not inspect.Parameter.empty else str
        )
        schema = python_type_to_schema(annotation)

        if name in doc["params"]:
            schema["description"] = doc["params"][name]

        properties[name] = schema

        is_required = param.default is inspect.Parameter.empty and not is_optional(
            param.annotation
        )
        if is_required:
            required.append(name)

    return {
        "name": func.__name__,
        "description": doc["description"],
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": required,
        },
    }
