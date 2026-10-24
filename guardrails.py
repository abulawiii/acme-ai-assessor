import re

MIN_LENGTH = 30
MAX_LENGTH = 3000

# Phrases that try to give the AI new orders instead of describing a use case
INJECTION_PHRASES = [
    "ignore previous instructions",
    "ignore all instructions",
    "disregard the above",
    "you are now",
    "system prompt",
    "mark all as met",
    "approve this use case",
    "forget your rules",
]

# Simple patterns, not perfect: they catch the common cases
# name@domain, then one or more ".part" (so a full stop after the email is not eaten)
EMAIL_PATTERN = r"[\w.+-]+@[\w-]+(\.[\w-]+)+"
LONG_NUMBER_PATTERN = r"\d{8,}"  # 8 or more digits in a row, like account or card numbers


def check_length(text):
    """Return an error message if the text is too short or too long, otherwise None."""
    length = len(text.strip())
    if length < MIN_LENGTH:
        return f"The use case is too short ({length} characters). Please write at least {MIN_LENGTH}."
    if length > MAX_LENGTH:
        return f"The use case is too long ({length} characters). Please keep it under {MAX_LENGTH}."
    return None


def find_injection(text):
    """Return the suspicious phrases found in the text (case-insensitive)."""
    found = []
    for phrase in INJECTION_PHRASES:
        if phrase in text.lower():
            found.append(phrase)
    return found


def mask_sensitive_data(text):
    """Replace emails and long numbers with placeholders.

    Returns the masked text and a list saying what was masked, never the real values.
    """
    # re.subn replaces every match and also tells us how many it replaced
    masked_text, email_count = re.subn(EMAIL_PATTERN, "[EMAIL]", text)
    masked_text, number_count = re.subn(LONG_NUMBER_PATTERN, "[NUMBER]", masked_text)

    masked_items = []
    if email_count == 1:
        masked_items.append("1 email")
    elif email_count > 1:
        masked_items.append(f"{email_count} emails")
    if number_count == 1:
        masked_items.append("1 number")
    elif number_count > 1:
        masked_items.append(f"{number_count} numbers")

    return masked_text, masked_items
