import os
import sys
from dotenv import load_dotenv
from groq import Groq

# Ensure UTF-8 output encoding on Windows so special characters and emojis print without error
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file. Please add your key to .env.")

client = Groq(api_key=api_key)

# Supported chat models available in your Groq account:
# "openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"
MODEL = "openai/gpt-oss-120b"


# --- 1. Basic Greeting Test ---
print("--- 1. Simple Greeting ---")
chat = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "Hello",
        }
    ],
)
print(chat.choices[0].message.content)
print("\n" + "=" * 50 + "\n")


# --- 2. Basic Prompt - Zero Shot ---
print("--- 2. Zero-Shot Prompt ---")
prompt = "Explain what is an AI in short line"

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
)
print(response.choices[0].message.content)
print("\n" + "=" * 50 + "\n")


# --- 3. System Prompt (Comedian Persona) ---
print("--- 3. System Prompt (Comedian Persona) ---")
systemPrompt = (
    "You are a comedian and everything you answer will be a joke that is very funny, "
    "you have been doing comedy for 25 years now, you are updated with everything that is "
    "going on in the world, your talks have humor."
)
userPrompt = "Who is elon musk?"

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": systemPrompt,
        },
        {
            "role": "user",
            "content": userPrompt,
        },
    ],
)

print(response.choices[0].message.content)