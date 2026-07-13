from llmini import ModelConfig, Message, complete, system_message, user_message, append_messages

model = ModelConfig(model="anthropic/claude-3-5-haiku-latest")

chat: list[Message] = [
    system_message("You are a helpful assistant."),
    user_message("What is the capital of France?"),
]

reply = complete(model=model, messages=chat)
print(reply.content)

append_messages(chat, reply, user_message("How many people live there?"))

reply = complete(model=model, messages=chat)
print(reply.content)
