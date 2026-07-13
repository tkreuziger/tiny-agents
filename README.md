# llmini

A minimal, ergonomic Python library for interacting with LLMs. Built on top of [LiteLLM](https://github.com/BerriAI/litellm).

## Features

- **Unified LLM access** — works with Anthropic, OpenAI, and any LiteLLM-supported provider
- **Tool calling** — define tools as Python functions, schemas are auto-generated from type hints and docstrings
- **Structured output** — parse LLM responses into Pydantic models
- **Image support** — send images in messages with automatic base64 encoding
- **Approval gating** — mark tools as requiring approval before execution
- **Message serialization** — export conversations as JSON or JSONL
- **Zero config** — works out of the box with environment variables for API keys

## Installation

```bash
uv add llmini

# or
pip install llmini
```

## Quick Start

```python
from llmini import ModelConfig, complete, system_message, user_message

reply = complete(
    model=ModelConfig(model="anthropic/claude-3-5-haiku-latest"),
    messages=[
        system_message("You are a helpful assistant."),
        user_message("What is the capital of France?"),
    ],
)

print(reply.content)  # "The capital of France is Paris."
```

**With tools:**

```python
from llmini import ModelConfig, complete, system_message, user_message, make_tool

@make_tool()
def get_weather(location: str) -> str:
    """Get the current weather at a location."""
    return "Sunny, 22°C"

reply = complete(
    model=ModelConfig(model="anthropic/claude-3-5-haiku-latest"),
    messages=[
        system_message("You are a helpful assistant."),
        user_message("How's the weather in Paris?"),
    ],
    tools=[get_weather],
)
```

**Building a tool-using agent loop:** see [examples/test_04_agent.py](examples/test_04_agent.py).

## Documentation

- **[USAGE.md](USAGE.md)** — full API reference with all parameters, defaults, and detailed examples
- **[examples/](examples/)** — runnable example scripts

## License

MIT
