"""
Configuration and Environment Variable Loader for Module 6 Chatbot.
Demonstrates Activity 3: Securely Load and Validate the API Key.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output encoding on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Locate the .env file (check backend/ folder, then chatbot/ root, then parent directory)
current_dir = Path(__file__).resolve().parent
search_paths = [
    current_dir / ".env",
    current_dir.parent / ".env",
    current_dir.parent.parent / ".env"
]

env_loaded = False
loaded_env_path = None
for env_path in search_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)
        loaded_env_path = env_path
        env_loaded = True
        break

# Default configurations
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

DEFAULT_OPENROUTER_MODEL = os.getenv("CHATBOT_MODEL", "meta-llama/llama-3.2-3b-instruct:free")
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))


def get_api_credentials(require_key: bool = True):
    """
    Activity 3: Securely loads and validates the API key.
    Checks for OPENROUTER_API_KEY first, with fallback to GROQ_API_KEY if available.
    If require_key is True and no key is found, prints an error message and stops the application.
    """
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")

    # Filter out dummy placeholder values
    if openrouter_key and ("your_openrouter_api_key" in openrouter_key.lower() or openrouter_key.strip() == ""):
        openrouter_key = None
    if groq_key and ("your_groq_api_key" in groq_key.lower() or groq_key.strip() == ""):
        groq_key = None

    if openrouter_key:
        return {
            "provider": "openrouter",
            "api_key": openrouter_key,
            "api_url": OPENROUTER_API_URL,
            "model": DEFAULT_OPENROUTER_MODEL,
            "env_path": str(loaded_env_path) if loaded_env_path else "System Environment"
        }
    elif groq_key:
        return {
            "provider": "groq",
            "api_key": groq_key,
            "api_url": GROQ_API_URL,
            "model": DEFAULT_GROQ_MODEL,
            "env_path": str(loaded_env_path) if loaded_env_path else "System Environment"
        }

    if require_key:
        print("\n" + "=" * 60)
        print("[!] ERROR: API Key Missing or Not Configured!")
        print("=" * 60)
        print("The chatbot requires an API key to communicate with the AI model.")
        print("Please follow these steps to configure your API key:")
        print("  1. Copy '.env.example' to '.env' inside the 'backend' folder.")
        print("  2. Add your OpenRouter API key:")
        print("       OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx")
        print("  3. (Optional) Alternatively, provide a GROQ_API_KEY.")
        print("  4. Save the file and restart the application.")
        print("=" * 60 + "\n")
        sys.exit(1)

    return None
