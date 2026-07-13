import logging
from typing import Any

from pydantic import BaseModel

from ..completion import complete
from ..config import ModelConfig
from ..messages import Message, assistant_message, system_message, user_text_message
from .coerce import coerce_to_model
from .schema import (
    generate_response_schema,
    generate_string_schema,
    pydantic_to_json_schema,
)

logger = logging.getLogger(__name__)


def _try_structured_output(
    model: ModelConfig,
    system_prompt: str,
    user_content: str,
    schema_model: type[BaseModel],
    json_schema: dict[str, Any],
) -> Message:
    response_schema = generate_response_schema(
        schema_model.__name__,
        json_schema,
    )

    messages = [
        system_message(system_prompt),
        user_text_message(user_content),
    ]

    return complete(
        model=model,
        messages=messages,
        additional_kwargs={
            "response_format": response_schema,
        },
    )


def _try_string_fallback(
    model: ModelConfig,
    system_prompt: str,
    user_content: str,
    json_schema: dict[str, Any],
) -> Message:
    response_str = generate_string_schema(json_schema)
    prompt_sys = (
        "---\n"
        "Follow this JSON schema precisely "
        "(field names, types, required fields):\n"
        f"{response_str}\n\n"
        "Rules:\n"
        "- Output a single JSON object.\n"
        "- No comments, no explanations, no Markdown.\n"
        "- Do not wrap in code fences.\n"
    )

    top_level_keys = list(json_schema.get("properties", {}).keys())
    priming = "{\n" + ",\n".join(f'  "{k}": ' for k in top_level_keys)

    messages = [
        system_message(system_prompt + "\n" + prompt_sys),
        user_text_message(user_content),
        assistant_message(priming),
    ]

    return complete(
        model=model,
        messages=messages,
    )


def complete_with_schema[T: BaseModel](
    model: ModelConfig,
    schema_model: type[T],
    system_prompt: str,
    user_content: str,
) -> T | None:
    json_schema = pydantic_to_json_schema(schema_model)

    try:
        response = _try_structured_output(
            model, system_prompt, user_content, schema_model, json_schema
        )

        if response.content is None:
            raise RuntimeError("Model returned no text content.")

        return coerce_to_model(schema_model, response.content)

    except (RuntimeError, ValueError, KeyError, TypeError):
        logger.exception("Failed to force structured output.")

    try:
        response = _try_string_fallback(model, system_prompt, user_content, json_schema)

        if response.content is None:
            logger.warning("Model returned no text content in string fallback.")
            return None

        return coerce_to_model(schema_model, response.content)

    except (ValueError, KeyError, TypeError):
        logger.exception("Could not execute string fallback for structured output.")
        return None
