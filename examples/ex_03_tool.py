from llmini import ModelConfig, Message, complete, system_message, user_message, tool_message, append_messages, make_tool

model = ModelConfig(model="anthropic/claude-3-5-haiku-latest")


@make_tool()
def get_weather(location: str) -> str:
    """Get the current weather at a location."""
    return "Sunny, 22°C"


chat: list[Message] = [
    system_message("You are a helpful assistant."),
    user_message("How is the weather in Paris?"),
]

reply = complete(model=model, messages=chat, tools=[get_weather])

if reply.is_tool_call() and reply.tool_call:
    call = reply.tool_call
    result = get_weather.handler(**call.args)
    append_messages(chat, reply, tool_message(tool_call_id=call.id, data=result))

    reply = complete(model=model, messages=chat)
    print(reply.content)
