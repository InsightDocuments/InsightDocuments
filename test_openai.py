from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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