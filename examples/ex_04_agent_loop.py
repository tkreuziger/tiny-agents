from llmini import (
    Message,
    ModelConfig,
    Tool,
    append_messages,
    complete,
    execute_tool,
    make_tool,
    system_message,
    user_message,
)


def run_agent(
    *,
    model: ModelConfig,
    task: str,
    system_prompt: str | None = None,
    tools: list[Tool] | None = None,
    max_steps: int = 20,
) -> Message:
    messages: list[Message] = []

    if system_prompt:
        append_messages(messages, system_message(system_prompt))

    append_messages(messages, user_message(task))

    tools_by_name: dict[str, Tool] = {tool.name: tool for tool in tools or []}

    for _ in range(max_steps):
        reply = complete(model=model, messages=messages, tools=tools)
        append_messages(messages, reply)

        if not reply.is_tool_call():
            return reply

        call = reply.tool_call
        if call is None:
            return reply

        tool = tools_by_name.get(call.name)

        if tool is None:
            raise RuntimeError(f"Unknown tool: {call.name}")

        tool_result = execute_tool(tool, call)
        append_messages(messages, tool_result)

    raise RuntimeError("Agent exceeded max_steps without producing a final answer.")



@make_tool()
def get_weather(location: str) -> str:
    """Get the current weather at a location."""
    return f"Weather in {location}: Sunny, 22°C"


reply = run_agent(
    model=ModelConfig(model="anthropic/claude-3-5-haiku-latest"),
    task="How is the weather in Paris?",
    system_prompt="You are a helpful assistant.",
    tools=[get_weather],
)

print(reply.content)
