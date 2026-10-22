"""
Response Cleaning Utility for Module 6 Chatbot.
Demonstrates Activity 7: Clean and Display the AI Response.
"""
import re


def clean_markdown(text: str, strip_formatting: bool = False) -> str:
    """
    Cleans and formats an AI-generated text response.
    
    Args:
        text (str): The raw text response from the AI model.
        strip_formatting (bool): If True, strips Markdown syntax (bold, headers, bullets)
                                 for clean plain-text terminal viewing.
    
    Returns:
        str: The sanitized, cleaned text.
    """
    if not text:
        return ""

    cleaned = text

    # Strip triple-backtick wrappers if the whole response was wrapped in a code block
    code_block_match = re.match(r"^```(?:markdown|text)?\s*\n([\s\S]*?)\n```$", cleaned.strip())
    if code_block_match:
        cleaned = code_block_match.group(1)

    if strip_formatting:
        # Strip header markers (e.g., "### Title" -> "Title")
        cleaned = re.sub(r"^#{1,6}\s+", "", cleaned, flags=re.MULTILINE)
        
        # Strip bold and italics: **text** or *text* -> text
        cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
        cleaned = re.sub(r"__([^_]+)__", r"\1", cleaned)
        cleaned = re.sub(r"_([^_]+)_", r"\1", cleaned)
        
        # Strip inline code formatting: `code` -> code
        cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
        
        # Clean bullet indicators: replace "* " or "- " with bullet symbol "• "
        cleaned = re.sub(r"^\s*[-*]\s+", "• ", cleaned, flags=re.MULTILINE)

    # Normalize excessive newlines (more than 2 consecutive newlines replaced with 2)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    # Trim leading and trailing whitespace
    return cleaned.strip()


def format_display_response(raw_text: str, strip_formatting: bool = False) -> str:
    """
    Prepares an AI response for polished display in the terminal or web application.
    """
    cleaned = clean_markdown(raw_text, strip_formatting=strip_formatting)
    return cleaned
