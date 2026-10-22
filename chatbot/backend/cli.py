"""
Interactive Chatbot CLI for Module 6.
Demonstrates:
  - Activity 3: API Key Verification at startup
  - Activity 4: Continuous loop with input validation & exit handling
  - Activity 5: Response & error status handling
  - Activity 6: Network and timeout safety
  - Activity 7: Clean response display
"""
import sys
from config import get_api_credentials
from chatbot import validate_user_input, send_chat_message


def run_cli():
    print("=" * 65)
    print("      INTELLIPAAT MODULE 6 - AI CHATBOT APPLICATION")
    print("=" * 65)

    # Activity 3: Securely load and validate API credentials at startup
    print("[*] Validating API configuration...")
    credentials = get_api_credentials(require_key=True)
    provider_name = credentials.get("provider", "openrouter").upper()
    model_name = credentials.get("model", "default")
    env_source = credentials.get("env_path", ".env")
    print(f"[+] Loaded successfully from: {env_source}")
    print(f"[+] Provider: {provider_name} | Model: {model_name}")
    print("=" * 65)
    print("Type your message and press Enter.")
    print("Type 'exit' or 'quit' to terminate the session.")
    print("=" * 65 + "\n")

    # Activity 4: Continuous Chatbot Loop
    while True:
        try:
            raw_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\n[!] Session interrupted. Goodbye!")
            break

        # Activity 4: Validate user input (whitespace trim, empty check, exit check)
        is_valid, processed_text, is_exit = validate_user_input(raw_input)

        if is_exit:
            print("\nChatbot: Goodbye! Have a wonderful day ahead!")
            break

        if not is_valid:
            # Activity 4: Inform user about empty or invalid input
            print(f"[!] Warning: {processed_text}\n")
            continue

        print("[*] Thinking...")

        # Activities 5, 6, 7: Send request, catch errors/timeouts, clean response
        result = send_chat_message(
            prompt=processed_text,
            credentials=credentials,
            strip_markdown=False
        )

        if result["success"]:
            print(f"\nChatbot:\n{result['reply']}\n")
            print("-" * 65)
        else:
            print(f"\n[Error - {result['error_type']}]: {result['error_message']}\n")
            print("-" * 65)


if __name__ == "__main__":
    run_cli()
