import json
import os
import uuid
from datetime import datetime, timezone

from ai_client import MODEL

LOG_FOLDER = "logs"
LOG_FILE = os.path.join(LOG_FOLDER, "audit_log.jsonl")


def write_line(entry):
    """Add one entry as one JSON line at the end of the log file."""
    os.makedirs(LOG_FOLDER, exist_ok=True)
    # "a" = append, so we never overwrite earlier entries
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def save_assessment(masked_text, masked_items, blocked, block_reason,
                    result=None, verdict=None, problems=None):
    """Log one assessment (or blocked attempt) and return its new assessment_id.

    Only the MASKED text is saved, never the original, so the log holds no
    emails or account numbers.
    """
    assessment_id = uuid.uuid4().hex[:8]  # short id, easy to read and quote

    # A blocked attempt never reached the AI, so these stay empty
    model = None
    human_decision = "Not needed"
    risk_level = None
    risk_reason = None
    requirement_rows = []
    follow_up_questions = []
    agent_steps = []
    if not blocked:
        model = MODEL
        human_decision = "Pending"
    if result:
        risk_level = result["risk_level"]
        risk_reason = result["risk_reason"]
        # Each row already has exactly id, status, evidence_quotes, reason, action
        requirement_rows = result["requirements"]
        follow_up_questions = result["follow_up_questions"]
        agent_steps = result["agent_steps"]

    write_line({
        "type": "assessment",
        "assessment_id": assessment_id,
        "timestamp": now_utc(),
        "model": model,
        "masked_input": masked_text,
        "masked_items": masked_items,
        "blocked": blocked,
        "block_reason": block_reason,
        "agent_steps": agent_steps,
        "risk_level": risk_level,
        "risk_reason": risk_reason,
        "requirements": requirement_rows,
        "follow_up_questions": follow_up_questions,
        "verdict": verdict,
        "validator_problems": problems,
        "human_decision": human_decision,
    })
    return assessment_id


def save_decision(assessment_id, decision, reviewer_name, comment):
    """Log the analyst's decision ("Accepted" or "Rejected") for an assessment."""
    write_line({
        "type": "decision",
        "assessment_id": assessment_id,
        "timestamp": now_utc(),
        "decision": decision,
        "reviewer_name": reviewer_name,
        "comment": comment,
    })
