import json

# Relative path: start the app from the project folder (see README)
REQUIREMENTS_FILE = "data/acme_requirements.json"


def load_requirements():
    """Read the 8 Acme requirements from the JSON file and return them as a list."""
    # Raise a clear message so the app can show it, instead of a long traceback
    try:
        with open(REQUIREMENTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        raise RuntimeError(f"Could not read {REQUIREMENTS_FILE}")
