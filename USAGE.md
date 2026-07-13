# tiny-agents Usage Guide

A comprehensive guide to using the `tiny-agents` library with all options, defaults, and examples.

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
  - [ModelConfig](#modelconfig)
  - [TransportConfig](#transportconfig)
- [Messages](#messages)
  - [system_message](#system_messagetext-str---message)
  - [user_message](#user_messagetext-str---message)
  - [user_image_message](#user_image_messagetext-str-image_path-str---message)
  - [assistant_message](#assistant_messagetext-str-none-tool_call-toolcall-none---message)
  - [tool_message](#tool_messagetool_call_id-str-data-dict---message)
- [Completion](#completion)
  - [complete](#completemodel-messages---message)
- [Tools](#tools)
  - [make_tool](#make_tool-requires_approval-bool--false---tool)
  - [Tool](#tool-dataclass)
  - [execute_tool](#execute_tooltool-tool_call-toolcall---message)
  - [get_tool_by_name](#get_tool_by_nametools-name---tool--none)
  - [Error Types](#error-types)
- [Structured Output](#structured-output)
  - [complete_with_schema](#complete_with_schemamodel-schema_model-system_prompt-user_content---t--none)
- [Serialization](#serialization)
  - [message_to_json](#message_to_jsonmessage-indent--2---str)
  - [messages_to_json](#messages_to_jsonmessages-indent--2---str)
  - [messages_to_jsonl](#messages_to_jsonlmessages---str)
  - [messages_from_jsonl](#messages_from_jsonlpath-limit---listmessage--none)
- [Utilities](#utilities)
  - [append_messages](#append_messagesmessages-msgs---listmessage)

---

## Installation

```bash
# Using uv
uv add tiny-agents

# Using pip
pip install tiny-agents
```

**Requirements:** Python >= 3.12

**Dependencies:**
- `litellm >= 1.81.8` — unified LLM API
- `pillow >= 12.1.0` — image handling
- `pydantic >= 2.12.5` — structured output

---

## Configuration

### ModelConfig

```python
ModelConfig(model: str, temperature: float = 0.7)
```

| Parameter     | Type   | Default | Description                                                  |
|---------------|--------|---------|--------------------------------------------------------------|
| `model`       | `str`  | *required* | LiteLLM model identifier (e.g. `"anthropic/claude-3-5-haiku-latest"`, `"openai/gpt-4o"`) |
| `temperature` | `float`| `0.7`  | Sampling temperature. Higher values produce more random output, lower values are more deterministic. |

```python
from tiny_agents import ModelConfig

# Minimal — uses default temperature (0.7)
model = ModelConfig(model="anthropic/claude-3-5-haiku-latest")

# Custom temperature
model = ModelConfig(model="openai/gpt-4o", temperature=0.3)

# With OpenAI model
model = ModelConfig(model="openai/gpt-4o-mini", temperature=1.0)
```

### TransportConfig

```python
TransportConfig(api_key: str | None = None, base_url: str | None = None)
```

| Parameter   | Type           | Default | Description                                            |
|-------------|----------------|---------|--------------------------------------------------------|
| `api_key`   | `str \| None`  | `None`  | API key for authenticating requests. `None` uses the provider's default (e.g. `ANTHROPIC_API_KEY` env var). |
| `base_url`  | `str \| None`  | `None`  | Custom base URL for the API endpoint. `None` uses the provider's default URL. |

```python
from tiny_agents import TransportConfig

# Use default (env vars)
transport = TransportConfig()

# Explicit API key
transport = TransportConfig(api_key="sk-ant-...")

# Custom base URL (e.g. for local/proxy endpoints)
transport = TransportConfig(base_url="https://my-proxy.example.com/v1")

# Both
transport = TransportConfig(api_key="sk-ant-...", base_url="https://my-proxy.example.com/v1")
```

---

## Messages

### system_message(text: str) -> Message

Creates a system-role message. Used to set the assistant's behavior and personality.

| Parameter | Type   | Description                  |
|-----------|--------|------------------------------|
| `text`    | `str`  | The system prompt content.   |

```python
from tiny_agents import system_message

msg = system_message("You are a helpful coding assistant.")
```

### user_message(text: str) -> Message

Alias for `user_text_message`. Creates a user-role text message.

| Parameter | Type   | Description                |
|-----------|--------|----------------------------|
| `text`    | `str`  | The user's message content. |

```python
from tiny_agents import user_message

msg = user_message("What is the capital of France?")
```

### user_image_message(text: str, image_path: str) -> Message

Creates a user message containing an image. The image is base64-encoded and EXIF metadata is extracted.

| Parameter    | Type   | Description                          |
|--------------|--------|--------------------------------------|
| `text`       | `str`  | The text accompanying the image.     |
| `image_path` | `str`  | File path to the image on disk.      |

```python
from tiny_agents import user_image_message

msg = user_image_message("What's in this image?", "/path/to/photo.jpg")
```

### assistant_message(text: str | None = None, tool_call: ToolCall | None = None, **metadata_kwargs: str) -> Message

Creates an assistant-role message. Typically you don't construct these manually — the `complete()` function returns them. Useful when building custom agent loops.

| Parameter            | Type                      | Default | Description                                |
|----------------------|---------------------------|---------|--------------------------------------------|
| `text`               | `str \| None`             | `None`  | The assistant's text response.             |
| `tool_call`          | `ToolCall \| None`        | `None`  | A tool invocation requested by the model.  |
| `**metadata_kwargs`  | `str`                     | —       | Additional string key-value metadata.      |

```python
from tiny_agents import assistant_message

# Text-only response
msg = assistant_message(text="The capital is Paris.")

# With a tool call (typically built by the library)
msg = assistant_message(tool_call=some_tool_call)
```

### tool_message(tool_call_id: str, data: dict) -> Message

Creates a tool-result message. Used to send tool execution results back to the model.

| Parameter      | Type            | Description                                |
|----------------|-----------------|--------------------------------------------|
| `tool_call_id` | `str`           | ID of the originating `ToolCall`.          |
| `data`         | `dict[str, Any]`| Structured result data from the tool.      |

```python
from tiny_agents import tool_message

msg = tool_message(tool_call_id="call_abc123", data={"temperature": 22, "condition": "sunny"})
```

---

## Completion

### complete(model, messages, *, tools=None, transport=None, additional_kwargs=None) -> Message

Send a conversation to the LLM and get a single assistant response.

| Parameter            | Type                       | Default | Description                                    |
|----------------------|----------------------------|---------|------------------------------------------------|
| `model`              | `ModelConfig`              | *required* | Model configuration.                          |
| `messages`           | `list[Message]`            | *required* | Conversation history.                         |
| `tools`              | `list[Tool] \| None`       | `None`  | Tools the model may call. Sets `tool_choice="auto"` when provided. |
| `transport`          | `TransportConfig \| None`  | `None`  | API key / base URL override.                  |
| `additional_kwargs`  | `dict[str, Any] \| None`   | `None`  | Extra kwargs passed to LiteLLM (e.g. `response_format`). |

```python
from tiny_agents import ModelConfig, complete, system_message, user_message

model = ModelConfig(model="anthropic/claude-3-5-haiku-latest")

reply = complete(
    model=model,
    messages=[
        system_message("You are a helpful assistant."),
        user_message("What is the capital of France?"),
    ],
)

print(reply.content)       # "The capital of France is Paris."
print(reply.metadata)      # {"input_tokens": ..., "output_tokens": ..., "cost": ..., "duration": ..., "timestamp": ...}
print(reply.is_tool_call()) # False (text response)
```

**With tools:**

```python
from tiny_agents import ModelConfig, complete, system_message, user_message, make_tool

@make_tool()
def get_weather(location: str) -> str:
    """Get the current weather at a location."""
    return "Sunny, 22°C"

model = ModelConfig(model="anthropic/claude-3-5-haiku-latest")

reply = complete(
    model=model,
    messages=[
        system_message("You are a helpful assistant."),
        user_message("How's the weather in Paris?"),
    ],
    tools=[get_weather],
)

if reply.is_tool_call():
    print(reply.tool_call.name)  # "get_weather"
    print(reply.tool_call.args)  # {"location": "Paris"}
```

**With custom transport:**

```python
from tiny_agents import ModelConfig, TransportConfig, complete, user_message

model = ModelConfig(model="openai/gpt-4o")
transport = TransportConfig(api_key="sk-...")

reply = complete(
    model=model,
    messages=[user_message("Hello!")],
    transport=transport,
)
```

**With additional kwargs:**

```python
reply = complete(
    model=model,
    messages=[user_message("Say only 'hi'")],
    additional_kwargs={"max_tokens": 10},
)
```

---

## Tools

### make_tool(*, requires_approval: bool = False) -> Tool

Decorator factory that converts a Python function into a `Tool`. The JSON schema is auto-generated from the function's type annotations and Google-style docstring.

| Parameter           | Type   | Default | Description                                                |
|---------------------|--------|---------|------------------------------------------------------------|
| `requires_approval` | `bool` | `False` | If `True`, `execute_tool()` requires an `approve` callback to proceed. |

```python
from tiny_agents import make_tool

@make_tool()
def get_weather(location: str) -> str:
    """Get the current weather at a location."""
    return "Sunny, 22°C"

@make_tool(requires_approval=True)
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    return "Sent"
```

**Supported type annotations:**

| Python Type           | JSON Schema Type                              |
|-----------------------|-----------------------------------------------|
| `str`                 | `"string"`                                    |
| `int`                 | `"integer"`                                   |
| `float`               | `"number"`                                    |
| `bool`                | `"boolean"`                                   |
| `list[T]`             | `{"type": "array", "items": ...}`             |
| `dict[str, T]`        | `{"type": "object", "additionalProperties": ...}` |
| `Literal["a", "b"]`   | `{"type": "string", "enum": ["a", "b"]}`      |
| `Optional[T]`         | Same as `T`, marked as not required           |

**Advanced tool example with complex types:**

```python
from typing import Literal, Optional

@make_tool()
def create_task(
    title: str,
    priority: Literal["low", "medium", "high"],
    tags: list[str],
    description: Optional[str] = None,
) -> str:
    """Create a new task in the system.

    Args:
        title: The task title.
        priority: Task priority level.
        tags: List of tag names.
        description: Optional detailed description.
    """
    return f"Created: {title}"
```

### Tool dataclass

```python
@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    schema: dict[str, Any]
    handler: Callable[..., Any]
    requires_approval: bool = False
```

| Field                | Type                    | Description                                     |
|----------------------|-------------------------|-------------------------------------------------|
| `name`               | `str`                   | Unique identifier (auto-set to function `__name__`). |
| `description`        | `str`                   | Human-readable summary (auto-extracted from docstring). |
| `schema`             | `dict[str, Any]`        | JSON Schema for input parameters.               |
| `handler`            | `Callable[..., Any]`    | The original Python function.                   |
| `requires_approval`  | `bool`                  | Whether execution requires approval (default `False`). |

```python
# Access tool metadata
print(get_weather.name)                  # "get_weather"
print(get_weather.description)           # "Get the current weather at a location."
print(get_weather.requires_approval)     # False

# Call the handler directly
result = get_weather.handler(location="Paris")
```

### execute_tool(tool, tool_call, *, approve=None) -> Message

Execute a tool and return a `tool_message` with the result. Handles timing, error wrapping, and approval gating.

When a tool has `requires_approval=True`, the `approve` callback **must** be provided — otherwise execution is denied. If `requires_approval=False` (the default), execution proceeds without prompting.

| Parameter | Type                                         | Default | Description                                  |
|-----------|----------------------------------------------|---------|----------------------------------------------|
| `tool`    | `Tool`                                       | *required* | The tool to execute.                     |
| `tool_call`| `ToolCall`                                  | *required* | The tool call from the model.            |
| `approve` | `Callable[[Tool, ToolCall], bool] \| None`   | `None`  | Callback that gates execution. Returns `True` to proceed, `False` to deny. |

```python
from tiny_agents import execute_tool, get_tool_by_name, append_messages

tool = get_tool_by_name(tools, call.name)
if tool:
    result_msg = execute_tool(tool, call)
    append_messages(chat, reply, result_msg)
    reply = complete(model=model, messages=chat)
```

**With approval gating:**

```python
import json
from tiny_agents import make_tool, execute_tool

@make_tool(requires_approval=True)
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to a recipient."""
    return "Sent"

def approve(tool, call) -> bool:
    args = json.dumps(call.args)
    response = input(f"Approve {tool.name}({args})? [y/n] ")
    return response.strip().lower() in ("y", "yes")

result_msg = execute_tool(send_email, call, approve=approve)
```

**Error handling within tools:**

```python
from tiny_agents import make_tool, ToolError, ToolFatalError

@make_tool()
def divide(a: float, b: float) -> str:
    """Divide two numbers."""
    if b == 0:
        raise ToolError("Cannot divide by zero")
    return str(a / b)

@make_tool()
def critical_operation(input: str) -> str:
    """Perform a critical operation."""
    if not input:
        raise ToolFatalError("Input is empty — terminating agent")
    return "done"
```

- `ToolError` — recoverable; the error is returned to the model as a structured payload.
- `ToolFatalError` — unrecoverable; raises `RuntimeError` and terminates the agent.

### get_tool_by_name(tools, name) -> Tool | None

Look up a tool by name from a list.

| Parameter | Type             | Description                     |
|-----------|------------------|---------------------------------|
| `tools`   | `list[Tool]`     | List of tools to search.        |
| `name`    | `str \| None`    | Tool name to find. Returns `None` if `name` is `None`. |

```python
tool = get_tool_by_name(tools, "get_weather")
if tool:
    result = execute_tool(tool, call)
```

### Error Types

```python
from tiny_agents import ToolError, ToolFatalError
```

| Exception        | Behavior                                    |
|------------------|---------------------------------------------|
| `ToolError`      | Recoverable. Returned to the model as `{"error": {"type": "tool_error", "message": "..."}}` |
| `ToolFatalError` | Unrecoverable. Raises `RuntimeError`, terminates the agent. |

---

## Structured Output

### complete_with_schema(model, schema_model, system_prompt, user_content) -> T | None

Generate a response parsed into a Pydantic model. Tries native structured output first, falls back to prompt-based schema enforcement.

| Parameter      | Type              | Description                                    |
|----------------|-------------------|------------------------------------------------|
| `model`        | `ModelConfig`     | Model configuration.                           |
| `schema_model` | `type[T]`         | A Pydantic `BaseModel` subclass defining the expected output shape. |
| `system_prompt`| `str`             | System prompt.                                 |
| `user_content` | `str`             | User message content.                          |

Returns an instance of `T`, or `None` if both strategies fail.

```python
from pydantic import BaseModel
from tiny_agents import ModelConfig, complete_with_schema

class Forecast(BaseModel):
    location: str
    temperature: int
    summary: str

model = ModelConfig(model="anthropic/claude-3-5-haiku-latest")

result = complete_with_schema(
    model=model,
    schema_model=Forecast,
    system_prompt="You are a weather assistant.",
    user_content="What's the weather in Paris?",
)

if result:
    print(result.location)     # "Paris"
    print(result.temperature)  # 22
    print(result.summary)      # "Sunny"
```

**Nested models:**

```python
from pydantic import BaseModel

class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    age: int
    address: Address

result = complete_with_schema(
    model=model,
    schema_model=Person,
    system_prompt="You are a data extraction assistant.",
    user_content="Extract: John Doe, 30, lives at 123 Main St, Paris, France",
)

if result:
    print(result.name)              # "John Doe"
    print(result.address.city)      # "Paris"
```

---

## Serialization

### message_to_json(message, indent=2) -> str

Serialize a single `Message` to a JSON string.

| Parameter | Type            | Default | Description                |
|-----------|-----------------|---------|----------------------------|
| `message` | `Message`       | *required* | The message to serialize. |
| `indent`  | `int \| None`   | `2`     | JSON indentation level. `None` for compact output. |

```python
from tiny_agents import message_to_json, system_message

msg = system_message("You are helpful.")
print(message_to_json(msg))
# {
#   "role": "system",
#   "content_type": "text",
#   "content": "You are helpful.",
#   "content_data": null,
#   "metadata": {...},
#   "tool_call": null,
#   "tool_result": null
# }

# Compact output
print(message_to_json(msg, indent=None))
# {"role": "system", "content_type": "text", "content": "You are helpful.", ...}
```

### messages_to_json(messages, indent=2) -> str

Serialize a list of messages to a JSON array string.

| Parameter | Type              | Default | Description                    |
|-----------|-------------------|---------|--------------------------------|
| `messages`| `list[Message]`   | *required* | The messages to serialize.   |
| `indent`  | `int \| None`     | `2`     | JSON indentation level.        |

```python
from tiny_agents import messages_to_json, system_message, user_message

chat = [
    system_message("You are helpful."),
    user_message("Hello!"),
]
print(messages_to_json(chat))
```

### messages_to_jsonl(messages) -> str

Serialize messages to JSONL format (one JSON object per line).

| Parameter | Type              | Description                  |
|-----------|-------------------|------------------------------|
| `messages`| `list[Message]`   | The messages to serialize.   |

```python
from tiny_agents import messages_to_jsonl

jsonl = messages_to_jsonl(chat)
print(jsonl)
# {"role": "system", ...}\n{"role": "user", ...}\n
```

### messages_from_jsonl(path, limit) -> list[Message] | None

Deserialize the last `limit` lines from a JSONL file.

| Parameter | Type    | Description                                     |
|-----------|---------|-------------------------------------------------|
| `path`    | `Path`  | Path to the JSONL file.                         |
| `limit`   | `int`   | Maximum number of recent lines to read.         |

```python
from pathlib import Path
from tiny_agents import messages_from_jsonl

messages = messages_from_jsonl(Path("conversation.jsonl"), limit=50)
if messages:
    for msg in messages:
        print(msg.role, msg.content)
```

---

## Utilities

### append_messages(messages, *msgs) -> list[Message]

Extend a message list in-place with one or more messages. Returns the same list.

| Parameter | Type              | Description                          |
|-----------|-------------------|--------------------------------------|
| `messages`| `list[Message]`   | The list to extend.                  |
| `*msgs`   | `Message`         | One or more messages to append.      |

```python
from tiny_agents import append_messages, user_message, system_message

chat = [system_message("You are helpful.")]
append_messages(chat, user_message("Hello!"))
append_messages(chat, user_message("How are you?"), user_message("What time is it?"))
print(len(chat))  # 4
```

---

## Complete Example: Multi-Turn Conversation

```python
from tiny_agents import (
    ModelConfig,
    complete,
    system_message,
    user_message,
    append_messages,
)

model = ModelConfig(model="anthropic/claude-3-5-haiku-latest", temperature=0.5)

chat = [
    system_message("You are a helpful assistant."),
    user_message("What is the capital of France?"),
]

# First turn
reply = complete(model=model, messages=chat)
print(reply.content)  # "The capital of France is Paris."

# Append reply and follow-up
append_messages(chat, reply, user_message("How many people live there?"))

# Second turn
reply = complete(model=model, messages=chat)
print(reply.content)  # "Approximately 2.1 million people..."
```

---

## Complete Example: Manual Tool Execution

```python
from tiny_agents import (
    ModelConfig,
    complete,
    system_message,
    user_message,
    tool_message,
    append_messages,
    make_tool,
    execute_tool,
    get_tool_by_name,
)

@make_tool()
def get_weather(location: str) -> str:
    """Get the current weather at a location."""
    return "Sunny, 22°C"

@make_tool()
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))

model = ModelConfig(model="anthropic/claude-3-5-haiku-latest")
tools = [get_weather, calculate]

chat = [
    system_message("You are a helpful assistant."),
    user_message("What's 2+2 and the weather in Paris?"),
]

for _ in range(10):
    reply = complete(model=model, messages=chat, tools=tools)
    append_messages(chat, reply)

    if not reply.is_tool_call():
        break

    call = reply.tool_call
    if call is None:
        break

    tool = get_tool_by_name(tools, call.name)
    if tool is None:
        raise RuntimeError(f"Unknown tool: {call.name}")

    result_msg = execute_tool(tool, call)
    append_messages(chat, result_msg)

print(reply.content)
```

---

## Complete Example: Structured Data Extraction

```python
from pydantic import BaseModel
from typing import Literal
from tiny_agents import ModelConfig, complete_with_schema

class MovieReview(BaseModel):
    title: str
    year: int
    rating: Literal["poor", "average", "good", "excellent"]
    summary: str

model = ModelConfig(model="anthropic/claude-3-5-haiku-latest")

review = complete_with_schema(
    model=model,
    schema_model=MovieReview,
    system_prompt="You are a movie critic. Extract structured review data.",
    user_content="Inception was a 2010 masterpiece by Christopher Nolan. 9/10.",
)

if review:
    print(f"{review.title} ({review.year}) — {review.rating}")
    print(review.summary)
```

---

## Message Structure

Every `Message` has these fields:

| Field          | Type                          | Description                                |
|----------------|-------------------------------|--------------------------------------------|
| `role`         | `"system" \| "user" \| "assistant" \| "tool"` | Message author. |
| `content_type` | `"text" \| "image"`           | Content type (default: `"text"`).          |
| `content`      | `str \| None`                 | Text content of the message.               |
| `content_data` | `str \| None`                 | Encoded data (e.g. base64 image).          |
| `metadata`     | `dict[str, str] \| None`      | Token usage, cost, timing, etc.            |
| `tool_call`    | `ToolCall \| None`            | Tool invocation requested by the model.    |
| `tool_result`  | `ToolResult \| None`          | Result of a tool invocation.               |

**Methods:**

| Method           | Returns  | Description                                |
|------------------|----------|--------------------------------------------|
| `is_tool_call()` | `bool`   | `True` if role is `"assistant"` and `tool_call` is set. |
| `to_dict()`      | `dict`   | Converts to a plain dictionary.            |
