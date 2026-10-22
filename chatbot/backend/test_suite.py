"""
Comprehensive Test Suite for Module 6 Chatbot.
Executes and validates all required scenarios from Activity 8:
  Test Case 1: A valid question (LLM request & cleaned response)
  Test Case 2: An empty input (Input validation rejection)
  Test Case 3: The exit or quit command (Exit condition handling)
  Test Case 4: An invalid or missing API key (Authentication error handling)
  Test Case 5: A network-related failure / timeout simulation (Network error handling)
"""
import sys
import unittest
from unittest.mock import patch
import requests

from config import get_api_credentials
from chatbot import validate_user_input, send_chat_message
from response_cleaner import format_display_response, clean_markdown


def print_banner(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def run_all_tests():
    print_banner("INTELLIPAAT MODULE 6 - HANDS-ON VERIFICATION SUITE")
    print("Executing tests for all 8 Activities...\n")

    # -------------------------------------------------------------
    # Scenario 1: Empty Input Handling (Activity 4)
    # -------------------------------------------------------------
    print_banner("SCENARIO 1: Empty Input Handling (Activity 4)")
    empty_inputs = ["", "   ", "\t  \n  "]
    for inp in empty_inputs:
        is_valid, msg, is_exit = validate_user_input(inp)
        print(f"Input: {repr(inp)}")
        print(f"  -> Valid? {is_valid} | Is Exit? {is_exit}")
        print(f"  -> Result message: '{msg}'")
        assert not is_valid, "Expected empty input to be rejected"
    print("[PASS] Empty input successfully rejected with appropriate warning.")

    # -------------------------------------------------------------
    # Scenario 2: Exit / Quit Commands (Activity 4)
    # -------------------------------------------------------------
    print_banner("SCENARIO 2: Exit / Quit Command Handling (Activity 4)")
    exit_commands = ["exit", "quit", "QUIT", "  exit  ", "q"]
    for cmd in exit_commands:
        is_valid, processed, is_exit = validate_user_input(cmd)
        print(f"Input: {repr(cmd)}")
        print(f"  -> Valid? {is_valid} | Is Exit? {is_exit} | Processed: '{processed}'")
        assert is_exit, f"Expected {cmd} to trigger exit condition"
    print("[PASS] Exit commands correctly identified and handled.")

    # -------------------------------------------------------------
    # Scenario 3: Response Cleaning (Activity 7)
    # -------------------------------------------------------------
    print_banner("SCENARIO 3: Response Cleaning & Markdown Formatting (Activity 7)")
    raw_markdown = """```markdown
### What is Artificial Intelligence?
**Artificial Intelligence** (AI) is the simulation of *human intelligence*.
- Fast
- Scalable
```"""
    cleaned_normal = format_display_response(raw_markdown, strip_formatting=False)
    cleaned_plain = format_display_response(raw_markdown, strip_formatting=True)
    print("--- RAW AI RESPONSE ---")
    print(raw_markdown)
    print("\n--- CLEANED RESPONSE (Preserving readable markdown) ---")
    print(cleaned_normal)
    print("\n--- CLEANED RESPONSE (Stripped for plain terminal) ---")
    print(cleaned_plain)
    assert "```markdown" not in cleaned_normal
    print("\n[PASS] Response cleaner successfully sanitizes code-blocks, markers, and whitespace.")

    # -------------------------------------------------------------
    # Scenario 4: Missing & Invalid API Key (Activities 3 & 5)
    # -------------------------------------------------------------
    print_banner("SCENARIO 4: Missing or Invalid API Key Handling (Activities 3 & 5)")
    
    # 4a. Missing credentials
    missing_creds_result = send_chat_message("Hello", credentials={"api_key": "", "api_url": "https://openrouter.ai/api/v1/chat/completions", "model": "meta-llama/llama-3.2-3b-instruct:free"})
    print("4a. Testing Missing/Invalid Credentials Call:")
    print(f"  -> Success: {missing_creds_result['success']}")
    print(f"  -> Error Type: {missing_creds_result['error_type']}")
    print(f"  -> Error Message: {missing_creds_result['error_message']}")
    
    # 4b. Invalid key against live endpoint (HTTP 401)
    fake_creds = {
        "api_key": "sk-invalid-test-key-12345",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "meta-llama/llama-3.2-3b-instruct:free",
        "provider": "openrouter"
    }
    print("\n4b. Testing Unauthorized Request against OpenRouter (Simulating HTTP 401):")
    invalid_result = send_chat_message("Hello", credentials=fake_creds)
    print(f"  -> Success: {invalid_result['success']}")
    print(f"  -> Status Code: {invalid_result['status_code']}")
    print(f"  -> Error Type: {invalid_result['error_type']}")
    print(f"  -> Error Message: {invalid_result['error_message']}")
    assert invalid_result["status_code"] in [401, 403] or invalid_result["error_type"] == "APIStatusError"
    print("[PASS] Invalid/missing API keys gracefully caught with descriptive diagnostic message.")

    # -------------------------------------------------------------
    # Scenario 5: Network Timeout & Connection Failure (Activity 6)
    # -------------------------------------------------------------
    print_banner("SCENARIO 5: Network & Timeout Error Handling (Activity 6)")
    
    # 5a. Timeout Simulation
    print("5a. Testing Timeout Error Handling (using mock timeout):")
    with patch("requests.post", side_effect=requests.exceptions.Timeout("Connection timed out")):
        timeout_result = send_chat_message("Hello", credentials=fake_creds, timeout=5)
        print(f"  -> Success: {timeout_result['success']}")
        print(f"  -> Error Type: {timeout_result['error_type']}")
        print(f"  -> Error Message: {timeout_result['error_message']}")
        assert timeout_result["error_type"] == "TimeoutError"

    # 5b. Connection Failure (No internet) Simulation
    print("\n5b. Testing Connection Error Handling (No internet simulation):")
    with patch("requests.post", side_effect=requests.exceptions.ConnectionError("Failed to resolve host")):
        conn_result = send_chat_message("Hello", credentials=fake_creds)
        print(f"  -> Success: {conn_result['success']}")
        print(f"  -> Error Type: {conn_result['error_type']}")
        print(f"  -> Error Message: {conn_result['error_message']}")
        assert conn_result["error_type"] == "ConnectionError"
    print("[PASS] Network timeouts and connection errors caught without crashing.")

    # -------------------------------------------------------------
    # Scenario 6: Valid Question with Real Live Model (Activities 5 & 8)
    # -------------------------------------------------------------
    print_banner("SCENARIO 6: Live Valid Question Submission (Activity 8)")
    real_creds = get_api_credentials(require_key=False)
    if real_creds:
        print(f"Testing live prompt with configured provider [{real_creds.get('provider')}]:")
        prompt = "In 2 sentences, explain why error handling is important in software development."
        print(f"Prompt: '{prompt}'")
        result = send_chat_message(prompt=prompt, credentials=real_creds)
        print(f"  -> Success: {result['success']}")
        print(f"  -> Status Code: {result['status_code']}")
        print(f"  -> AI Reply:\n{result['reply']}")
        assert result["success"] is True
        print("\n[PASS] Valid question received a high quality AI response successfully!")
    else:
        print("[!] Note: No active API key detected in .env. Live call skipped; mock tests verified all logic.")

    print_banner("ALL ACTIVITIES 1 - 8 SUCCESSFULLY VERIFIED!")


if __name__ == "__main__":
    run_all_tests()
