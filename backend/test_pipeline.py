import os
from dotenv import load_dotenv
from groq import Groq  # 1. Switched from google.genai

# Load environment variables from .env file
load_dotenv()

# 2. Initialize the Groq client
# Ensure GROQ_API_KEY is defined in your .env
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 3. Request a chat completion
# Using llama-3.3-70b-versatile for high-quality text output
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Say hello in one short sentence.",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print("Response:")
# 4. Access the text content from the response object
print(chat_completion.choices[0].message.content)