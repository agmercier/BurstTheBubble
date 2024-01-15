# from openai import OpenAI

# client = OpenAI(api_key="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")
# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#   ]
# )

# print(completion.choices[0].message)
from openai import OpenAI
import gradio as gr

client = OpenAI(api_key="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")

messages = [
    {"role": "system", "content": "You are a helpful and kind AI Assistant."},
]


def chatbot(input):
    if input:
        messages.append({"role": "user", "content": input})
        chat = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0,  # temperature dictates how random gpt will be. How closly will it follow the prompts.
        )
        reply = chat.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        return reply


inputs = gr.components.Textbox(
    lines=7,
    label="Chat with AI",
)
outputs = gr.components.Textbox(label="Reply")

gr.Interface(
    fn=chatbot,
    inputs=inputs,
    outputs=outputs,
    title="AI Chatbot",
    description="Ask anything you want",
    theme="compact",
).launch(share=True)
