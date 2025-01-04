from openai import OpenAI

client = OpenAI(api_key="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")

# Set your API key

try:
    response = client.chat.completions.create(model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the purpose of life?"}
    ])
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}") 