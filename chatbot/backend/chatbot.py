"""
Core Chatbot Module for Module 6 First AI Application.
Implements:
  - Activity 4: Validate User Input and Handle Exit Conditions
  - Activity 5: Handle API Errors and Validate Responses
  - Activity 6: Handle Network and Timeout Errors
  - Activity 7: Clean and Display the AI Response
"""
import json
import requests
from typing import Dict, Any, Tuple, Optional
from config import get_api_credentials, REQUEST_TIMEOUT
from response_cleaner import format_display_response

EXIT_COMMANDS = {"exit", "quit", "q", "bye"}


def validate_user_input(user_input: str) -> Tuple[bool, Optional[str], bool]:
    """
    Activity 4: Validate User Input and Handle Exit Conditions.

    Returns:
        (is_valid, processed_text_or_error_message, is_exit)
    """
    if user_input is None:
        return False, "Input cannot be empty. Please ask a question.", False

    # Remove unnecessary leading/trailing whitespace
    trimmed = user_input.strip()

    # Check for exit commands
    if trimmed.lower() in EXIT_COMMANDS:
        return True, trimmed, True

    # Check for empty input
    if len(trimmed) == 0:
        return False, "Input cannot be empty. Please ask a question.", False

    return True, trimmed, False


def send_chat_message(
    prompt: str,
    credentials: Optional[Dict[str, Any]] = None,
    timeout: int = REQUEST_TIMEOUT,
    strip_markdown: bool = False,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Activity 5 & 6 & 7: Sends user input to the OpenRouter / LLM API with
    comprehensive error handling, timeout management, response validation,
    and output cleaning. Supports dynamic system prompts.
    """
    # Activity 3 check: obtain credentials
    if credentials is None:
        credentials = get_api_credentials(require_key=False)
        if not credentials:
            return {
                "success": False,
                "reply": None,
                "error_type": "AuthenticationError",
                "error_message": "Missing API Key! Please configure OPENROUTER_API_KEY in your .env file.",
                "status_code": 401,
                "raw_response": None
            }

    api_url = credentials["api_url"]
    api_key = credentials["api_key"]
    model = credentials["model"]
    provider = credentials.get("provider", "openrouter")

    # Construct request headers
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # OpenRouter recommended headers
    if provider == "openrouter":
        headers["HTTP-Referer"] = "https://nexus-ai.local"
        headers["X-Title"] = "Nexus AI Chatbot"

    # Default or dynamic system prompt
    sys_content = system_prompt or "You are a helpful, courteous, and knowledgeable AI assistant."

    # Construct payload
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_content},
            {"role": "user", "content": prompt}
        ]
    }

    # Activity 6: Handle Network and Timeout Errors
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=payload,
            timeout=timeout
        )
    except requests.exceptions.Timeout:
        # Activity 6: Timeout handling
        return {
            "success": False,
            "reply": None,
            "error_type": "TimeoutError",
            "error_message": f"Request timed out after {timeout} seconds. The API server took too long to respond. Please try again later.",
            "status_code": 408,
            "raw_response": None
        }
    except requests.exceptions.ConnectionError:
        # Activity 6: No internet connection or host unreachable
        return {
            "success": False,
            "reply": None,
            "error_type": "ConnectionError",
            "error_message": "Unable to connect to the server. Please verify your internet connection and network settings.",
            "status_code": 503,
            "raw_response": None
        }
    except requests.exceptions.RequestException as req_err:
        # Activity 6: General network/HTTP exceptions
        return {
            "success": False,
            "reply": None,
            "error_type": "NetworkError",
            "error_message": f"A network error occurred while communicating with the API: {str(req_err)}",
            "status_code": None,
            "raw_response": None
        }
    except Exception as unexp_err:
        # Activity 6: Unexpected runtime exceptions
        return {
            "success": False,
            "reply": None,
            "error_type": "UnexpectedError",
            "error_message": f"An unexpected error occurred: {str(unexp_err)}",
            "status_code": None,
            "raw_response": None
        }

    # Activity 5: Check API response status
    status_code = response.status_code

    if status_code != 200:
        # Attempt to parse detailed error from response JSON
        error_detail = "Unknown API Error"
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                if "error" in error_data:
                    err_obj = error_data["error"]
                    if isinstance(err_obj, dict):
                        error_detail = err_obj.get("message", str(err_obj))
                    else:
                        error_detail = str(err_obj)
                elif "message" in error_data:
                    error_detail = str(error_data["message"])
                else:
                    error_detail = response.text
        except Exception:
            error_detail = response.text or f"HTTP Status {status_code}"

        # Categorize known HTTP status codes for clear reporting
        if status_code == 401:
            friendly_msg = f"Authentication Failed (401): Invalid or missing API key. Details: {error_detail}"
        elif status_code == 403:
            friendly_msg = f"Forbidden (403): You don't have permission to access this model. Details: {error_detail}"
        elif status_code == 404:
            friendly_msg = f"Model Not Found (404): The requested model '{model}' was not found. Details: {error_detail}"
        elif status_code == 429:
            friendly_msg = f"Rate Limit Exceeded (429): You have sent too many requests. Details: {error_detail}"
        elif status_code >= 500:
            friendly_msg = f"API Provider Server Error ({status_code}): The upstream AI service is temporarily unavailable. Details: {error_detail}"
        else:
            friendly_msg = f"API Request Failed ({status_code}): {error_detail}"

        return {
            "success": False,
            "reply": None,
            "error_type": "APIStatusError",
            "error_message": friendly_msg,
            "status_code": status_code,
            "raw_response": None
        }

    # Activity 5: Validate response structure
    try:
        data = response.json()
    except json.JSONDecodeError:
        return {
            "success": False,
            "reply": None,
            "error_type": "ResponseParsingError",
            "error_message": "Failed to decode response as valid JSON from API.",
            "status_code": 200,
            "raw_response": None
        }

    if not isinstance(data, dict):
        return {
            "success": False,
            "reply": None,
            "error_type": "InvalidResponseStructure",
            "error_message": "Expected JSON object in API response, received a different data type.",
            "status_code": 200,
            "raw_response": str(data)
        }

    choices = data.get("choices")
    if not isinstance(choices, list) or len(choices) == 0:
        return {
            "success": False,
            "reply": None,
            "error_type": "InvalidResponseStructure",
            "error_message": "API response missing 'choices' list or returned an empty choices array.",
            "status_code": 200,
            "raw_response": data
        }

    first_choice = choices[0]
    message = first_choice.get("message")
    if not isinstance(message, dict) or "content" not in message:
        return {
            "success": False,
            "reply": None,
            "error_type": "InvalidResponseStructure",
            "error_message": "API response choice is missing message content.",
            "status_code": 200,
            "raw_response": data
        }

    raw_reply = message.get("content") or ""

    # Activity 7: Clean and Display the AI Response
    cleaned_reply = format_display_response(raw_reply, strip_formatting=strip_markdown)

    return {
        "success": True,
        "reply": cleaned_reply,
        "error_type": None,
        "error_message": None,
        "status_code": 200,
        "raw_response": data
    }
