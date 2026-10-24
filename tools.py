import re

from knowledge import load_requirements

# Keyword lists the scan tools look for in the use case text
SENSITIVE_DATA_KEYWORDS = [
    "customer names", "account", "financial", "personal", "HR",
    "performance", "employee", "salary", "security logs", "confidential",
]
THIRD_PARTY_KEYWORDS = [
    "third-party", "third party", "hosted", "API", "vendor", "external", "provider",
]
HUMAN_OVERSIGHT_KEYWORDS = [
    "review", "approve", "human", "analyst", "primary input", "automatically",
]


def find_keywords(keywords, use_case_text):
    """Return the keywords that appear in the text (case-insensitive)."""
    found = []
    for keyword in keywords:
        # Match only at the start of a word, so "HR" does not match inside
        # "three", but "approve" still matches "approved"
        pattern = r"\b" + re.escape(keyword)
        if re.search(pattern, use_case_text, re.IGNORECASE):
            found.append(keyword)
    return found


def get_requirements():
    return {"requirements": load_requirements()}


def scan_sensitive_data(use_case_text):
    return {"found": find_keywords(SENSITIVE_DATA_KEYWORDS, use_case_text)}


def scan_third_party(use_case_text):
    return {"found": find_keywords(THIRD_PARTY_KEYWORDS, use_case_text)}


def scan_human_oversight(use_case_text):
    return {"found": find_keywords(HUMAN_OVERSIGHT_KEYWORDS, use_case_text)}
