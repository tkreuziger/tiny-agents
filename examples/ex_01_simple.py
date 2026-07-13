from tiny_agents import ModelConfig, complete, system_message, user_message

model = ModelConfig(model="anthropic/claude-3-5-haiku-latest")

reply = complete(
    model=model,
    messages=[
        system_message("You are a helpful assistant."),
        user_message("What is the capital of France?"),
    ],
)

print(reply.content)
