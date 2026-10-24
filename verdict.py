def get_verdict(result):
    """Decide the final verdict with a simple fixed rule, not the AI.

    We decide in Python so the verdict is predictable and easy to explain.
    """
    statuses = {}
    for item in result["requirements"]:
        statuses[item["id"]] = item["status"]

    # No human oversight on AI-driven decisions is a blocker
    if statuses.get("AI-003") == "Gap":
        return "Do not approve"

    # Approve only when nothing is open
    all_clear = True
    for status in statuses.values():
        if status not in ["Met", "Not applicable"]:
            all_clear = False
    if all_clear:
        return "Approve"

    return "Approve with conditions"
