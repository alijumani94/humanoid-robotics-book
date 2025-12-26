"""Input validation and sanitization utilities."""

import re
import html
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Patterns for detecting prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+(instructions?|prompts?|rules?)",
    r"system\s*prompt",
    r"you\s+are\s+(now|a)\s+",
    r"forget\s+(everything|all|previous)",
    r"<\s*script\s*>",
    r"javascript:",
    r"on\w+\s*=",  # Event handlers like onclick=
]


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing HTML and dangerous characters.

    Args:
        text: Input text

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Unescape HTML entities
    text = html.unescape(text)

    # Remove null bytes
    text = text.replace('\x00', '')

    # Normalize whitespace
    text = ' '.join(text.split())

    return text.strip()


def detect_prompt_injection(text: str) -> bool:
    """
    Detect potential prompt injection attempts.

    Args:
        text: Input text

    Returns:
        bool: True if injection detected
    """
    text_lower = text.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            logger.warning(f"Potential prompt injection detected: pattern '{pattern}' matched")
            return True

    return False


def validate_question_length(text: str, max_length: int = 500) -> bool:
    """
    Validate question length.

    Args:
        text: Question text
        max_length: Maximum allowed length

    Returns:
        bool: True if valid
    """
    return len(text) <= max_length


def validate_selected_text(text: Optional[str], max_length: int = 5000) -> bool:
    """
    Validate selected text length.

    Args:
        text: Selected text
        max_length: Maximum allowed length

    Returns:
        bool: True if valid
    """
    if text is None:
        return True

    return len(text) <= max_length


def validate_input(question: str, selected_text: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """
    Validate and sanitize all user input.

    Args:
        question: User question
        selected_text: Optional selected text

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Sanitize inputs
    question = sanitize_input(question)

    if selected_text:
        selected_text = sanitize_input(selected_text)

    # Check length
    if not validate_question_length(question):
        return False, "Question exceeds maximum length of 500 characters"

    if not validate_selected_text(selected_text):
        return False, "Selected text exceeds maximum length of 5000 characters"

    # Check for empty question
    if not question or len(question.strip()) == 0:
        return False, "Question cannot be empty"

    # Detect prompt injection
    if detect_prompt_injection(question):
        return False, "Invalid question format detected"

    if selected_text and detect_prompt_injection(selected_text):
        return False, "Invalid selected text format detected"

    return True, None
