import datetime as dt
import logging
import time
from typing import Any

from litellm import (
    completion as litellm_completion,  # pyright: ignore[reportUnknownVariableType]
)
from litellm.exceptions import APIError, AuthenticationError, RateLimitError
from litellm.types.utils import ModelResponse

from ..config import ModelConfig, TransportConfig
from ..messages import Message
from ..tools import Tool
from .tracking import get_tokens_and_cost
from .utils import litellm_response_to_message, message_to_litellm, tools_to_litellm

logger = logging.getLogger(__name__)


def complete(
    model: ModelConfig,
    messages: list[Message],
    *,
    tools: list[Tool] | None = None,
    transport: TransportConfig | None = None,
    additional_kwargs: dict[str, Any] | None = None,
) -> Message:
    """
    Generate a single assistant message completion.

    This function converts internal `Message` and `Tool` objects into the
    LiteLLM-compatible format, forwards the request with the configured
    model and transport settings, and converts the LiteLLM response back into a
    `Message`.

    Args:
        model: The model configuration (name, temperature, etc.) to use for
            the completion.
        messages: The list of prior messages in the conversation, including
            system, user, assistant, and tool messages.
        tools: Optional list of tools that the model may call during
            completion. When provided, tool usage is set to automatic.
        transport: Optional transport configuration (e.g. API key, base URL)
            for the underlying model provider.
        additional_kwargs: Optional more kwargs that are passed through to
            LiteLLM.

    Returns:
        A `Message` representing the assistant's reply produced by the model.
    """
    llm_messages = [message_to_litellm(m) for m in messages]

    kwargs: dict[str, Any] = {
        "model": model.model,
        "messages": llm_messages,
        "temperature": model.temperature,
        **(additional_kwargs or {}),
    }

    if tools:
        kwargs["tools"] = tools_to_litellm(tools)
        kwargs["tool_choice"] = "auto"

    if transport:
        if transport.api_key:
            kwargs["api_key"] = transport.api_key
        if transport.base_url:
            kwargs["base_url"] = transport.base_url

    start_time = time.time()

    try:
        response: ModelResponse = litellm_completion(**kwargs)

        input_tokens, output_tokens, cost = get_tokens_and_cost(model.model, response)
        meta_data = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "duration": time.time() - start_time,
            "timestamp": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return litellm_response_to_message(response, meta_data)

    except AuthenticationError as e:
        logger.exception("Authentication failed: %s", e)
        raise e

    except RateLimitError as e:
        logger.exception("Rate limited: %s", e)
        raise e

    except APIError as e:
        logger.exception("API error: %s", e)
        raise e
