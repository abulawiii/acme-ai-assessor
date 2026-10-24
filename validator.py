ALLOWED_STATUSES = ["Met", "Partly met", "Gap", "Missing info", "Not applicable"]
EXPECTED_IDS = ["AI-001", "AI-002", "AI-003", "AI-004", "AI-005", "AI-006", "AI-007", "AI-008"]


def check_assessment(result, use_case_text):
    """Check the AI's assessment and return a list of problems (empty list = all good)."""
    problems = []
    requirements = result.get("requirements", [])

    # 1. Exactly 8 requirements
    if len(requirements) != 8:
        problems.append(f"Expected 8 requirements, but got {len(requirements)}.")

    # 2. IDs must be AI-001 to AI-008, with no duplicates
    found_ids = [item["id"] for item in requirements]
    for expected_id in EXPECTED_IDS:
        times_found = found_ids.count(expected_id)
        if times_found == 0:
            problems.append(f"{expected_id} is missing from the assessment.")
        elif times_found > 1:
            problems.append(f"{expected_id} appears {times_found} times.")

    for item in requirements:
        # 3. Status must be one of the 5 allowed words
        if item["status"] not in ALLOWED_STATUSES:
            problems.append(f"{item['id']} has an unknown status: {item['status']}.")

        # 4. Each evidence quote must really be in the use case, so the AI can't invent it.
        # An empty list means "Not mentioned", so there is nothing to check.
        for quote in item["evidence_quotes"]:
            if quote.lower() not in use_case_text.lower():
                problems.append(f"{item['id']} evidence was not found in the use case: \"{quote}\"")

    return problems
