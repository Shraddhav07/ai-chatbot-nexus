"""
Multi-Persona Conditional AI Chatbot
Demonstrates dynamic system prompt switching using a while True loop:
  Choice 1: Teacher Assistant
  Choice 2: Text Summarizer
  Choice 3: Interview Coach
  Choice 4: Travel Guide
"""
import os
import sys
from dotenv import load_dotenv

# Ensure UTF-8 output encoding on Windows so special characters and emojis print cleanly
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load environment variables
load_dotenv()

# Check API credentials (supports Groq or OpenRouter)
api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("\n" + "=" * 60)
    print("[!] ERROR: No API Key found in .env file!")
    print("Please add your GROQ_API_KEY or OPENROUTER_API_KEY to .env.")
    print("=" * 60 + "\n")
    sys.exit(1)

# Initialize client (uses groq if available, fallback to requests)
try:
    from groq import Groq
    client = Groq(api_key=api_key)
    MODEL = "openai/gpt-oss-120b"
    USE_GROQ_CLIENT = True
except ImportError:
    import requests
    USE_GROQ_CLIENT = False
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    MODEL = os.getenv("CHATBOT_MODEL", "meta-llama/llama-3.2-3b-instruct:free")


# Define Personas with tailored dynamic system prompts
PERSONAS = {
    "1": {
        "title": "Teacher Assistant",
        "description": "Explains complex topics simply, step-by-step, with helpful analogies.",
        "prompt": (
            "You are an expert, patient, and encouraging Teacher Assistant. "
            "Your role is to help students learn effectively. Break down complex concepts into simple, "
            "digestible steps. Use clear analogies, concrete real-world examples, and check for understanding. "
            "Always maintain a supportive, polite, and academically rigorous tone."
        ),
        "welcome": "Hello! I am your Teacher Assistant. What topic or concept would you like me to explain?"
    },
    "2": {
        "title": "Text Summarizer",
        "description": "Condenses lengthy text, notes, or articles into structured, crisp summaries.",
        "prompt": (
            "You are a professional Executive Text Summarizer. "
            "Your job is to read user input and produce high-quality, dense summaries. "
            "Format your output with: "
            "1. TL;DR (1-2 sentences) "
            "2. Key Takeaways (bulleted list) "
            "3. Actionable Points or Important Details. "
            "Be concise, eliminate fluff, and never invent information not in the text."
        ),
        "welcome": "Welcome! I am your Text Summarizer. Paste any text or article, and I will summarize it for you."
    },
    "3": {
        "title": "Interview Coach",
        "description": "Conducts mock interviews, asks questions, and provides feedback using the STAR method.",
        "prompt": (
            "You are a veteran Senior Hiring Manager and Interview Coach with 20+ years of experience. "
            "Help the user prepare for job interviews. You can conduct mock interview rounds, "
            "ask behavioral (STAR method) or technical questions one at a time, critique their answers, "
            "and suggest stronger phrasing. Maintain a professional, constructive, and realistic interview environment."
        ),
        "welcome": "Greetings! I am your Interview Coach. Tell me what job role you're preparing for, or ask for a practice question!"
    },
    "4": {
        "title": "Travel Guide",
        "description": "Provides travel itineraries, local hidden gems, cultural tips, and budget advice.",
        "prompt": (
            "You are an experienced, enthusiastic Global Travel Guide and local explorer. "
            "You provide detailed travel recommendations, day-by-day itineraries, cultural etiquette, "
            "local culinary must-tries, hidden gems, and safety/budget tips for any city or country. "
            "Keep suggestions vibrant, well-organized, and practical."
        ),
        "welcome": "Bon voyage! I am your Travel Guide. Which city, country, or destination are you planning to visit?"
    }
}


def query_llm(system_prompt: str, user_message: str) -> str:
    """Sends prompt with dynamic system prompt to the LLM."""
    if USE_GROQ_CLIENT:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message.content
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
        res = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=20)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]


def main():
    print("=" * 65)
    print("       DYNAMIC MULTI-PERSONA AI CHATBOT APPLICATION")
    print("=" * 65)
    print("Model ready. System prompt switches dynamically based on your choice.")

    # Outer while True loop: Persona Selection Menu
    while True:
        print("\n" + "-" * 65)
        print("SELECT AN AI PERSONA:")
        print("  [1] Teacher Assistant  - Explains concepts step-by-step")
        print("  [2] Text Summarizer    - Condenses long text into key points")
        print("  [3] Interview Coach    - Mock interviews & STAR feedback")
        print("  [4] Travel Guide       - Itineraries, local gems & travel tips")
        print("  [5] Exit Application")
        print("-" * 65)

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "5" or choice.lower() in {"exit", "quit"}:
            print("\nExiting application. Thank you for using Multi-Persona Chatbot!")
            break

        if choice not in PERSONAS:
            print("\n[!] Invalid selection! Please enter a number between 1 and 5.")
            continue

        selected_persona = PERSONAS[choice]
        current_system_prompt = selected_persona["prompt"]
        persona_name = selected_persona["title"]

        print("\n" + "=" * 65)
        print(f"[*] ACTIVATED PERSONA: {persona_name.upper()}")
        print(f"[*] System Prompt loaded dynamically.")
        print("=" * 65)
        print(f"\n{persona_name}: {selected_persona['welcome']}")
        print("\nCommands:")
        print("  - Type 'back' or 'menu' to return to persona selection")
        print("  - Type 'exit' to quit the application")
        print("-" * 65 + "\n")

        # Inner while True loop: Chatting with the selected persona
        while True:
            try:
                user_input = input(f"You -> [{persona_name}]: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\nSession interrupted. Returning to main menu...")
                break

            # Handle empty input
            if not user_input:
                print("[!] Input cannot be empty. Please enter your text or question.\n")
                continue

            # Handle navigation commands
            if user_input.lower() in {"back", "menu"}:
                print("\n[<] Returning to Persona Menu...\n")
                break

            if user_input.lower() in {"exit", "quit"}:
                print("\nExiting application. Goodbye!")
                return

            print(f"[*] {persona_name} is thinking...")

            # Query the AI with the dynamically selected system prompt
            try:
                reply = query_llm(
                    system_prompt=current_system_prompt,
                    user_message=user_input
                )
                print(f"\n{persona_name}:\n{reply.strip()}\n")
                print("-" * 65)
            except Exception as err:
                print(f"\n[!] Error communicating with AI: {err}\n")
                print("-" * 65)


if __name__ == "__main__":
    main()
