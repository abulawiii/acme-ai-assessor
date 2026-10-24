import streamlit as st

from ai_client import assess_use_case
from audit_log import save_assessment, save_decision
from guardrails import check_length, find_injection, mask_sensitive_data
from knowledge import load_requirements
from validator import check_assessment
from verdict import get_verdict

st.title("Acme AI Use Case Assessor")

# The app is useless without the requirements, so stop here if they can't be loaded
try:
    requirements = load_requirements()
except RuntimeError as error:
    st.error(str(error))
    st.stop()

# Show the requirements in the sidebar so the user knows what the AI checks against
st.sidebar.header("Acme AI requirements")
for item in requirements:
    st.sidebar.markdown(f"**{item['id']}**: {item['requirement']}")

# Big text box so the user can paste a full use case description
use_case_text = st.text_area("Paste an AI use case here:", height=250)

if st.button("Assess"):
    # Forget the previous result, so it is never shown next to a new input
    st.session_state["saved"] = None

    # Guardrails run first, so bad input never reaches the AI

    # a. Length check (this also catches an empty box)
    length_error = check_length(use_case_text)
    if length_error:
        st.error(length_error)
        st.stop()

    # Mask right away, so even the log of a blocked attempt never holds the original text
    masked_text, masked_items = mask_sensitive_data(use_case_text)

    # b. Block text that tries to give the AI orders, and log the attempt
    injection_phrases = find_injection(use_case_text)
    if injection_phrases:
        phrase_list = ", ".join(f'"{phrase}"' for phrase in injection_phrases)
        save_assessment(masked_text, masked_items, blocked=True,
                        block_reason=f"Instructions aimed at the AI: {phrase_list}")
        st.error(f"Blocked: this text contains instructions aimed at the AI: {phrase_list}")
        st.stop()

    # d. The AI only ever sees the masked text.
    # The API call takes a few seconds, so show the user we are working.
    with st.spinner("Assessing..."):
        result = assess_use_case(masked_text)

    if "error" in result:
        st.error(result["error"])
        st.stop()

    verdict = get_verdict(result)
    # e. Validate against the masked text, because that is what the AI quoted from
    problems = check_assessment(result, masked_text)
    assessment_id = save_assessment(masked_text, masked_items, blocked=False, block_reason="",
                                    result=result, verdict=verdict, problems=problems)

    # Keep everything in session_state: Streamlit reruns the whole script on every
    # click, so without this the result would vanish when the analyst clicks Accept
    st.session_state["saved"] = {
        "assessment_id": assessment_id,
        "result": result,
        "verdict": verdict,
        "problems": problems,
        "masked_items": masked_items,
    }

saved = st.session_state.get("saved")
if saved:
    result = saved["result"]
    verdict = saved["verdict"]
    problems = saved["problems"]

    # c. Tell the user what was hidden before sending to the AI
    if saved["masked_items"]:
        st.info("Masked before sending to the AI: " + ", ".join(saved["masked_items"]))

    # Verdict at the top, coloured by how serious it is
    if verdict == "Approve":
        st.success(f"Verdict: {verdict}")
    elif verdict == "Approve with conditions":
        st.warning(f"Verdict: {verdict}")
    else:
        st.error(f"Verdict: {verdict}")
    st.caption("AI recommendation only. An analyst must review before use.")

    st.markdown(f"**Risk level: {result['risk_level']}**. {result['risk_reason']}")

    # Show validator problems so the user knows which parts to double-check
    if problems:
        problem_lines = "\n".join(f"- {problem}" for problem in problems)
        st.warning("Please double-check this assessment:\n\n" + problem_lines)

    st.subheader("Summary")
    st.write(result["use_case_summary"])

    st.subheader("Requirements")
    table_rows = []
    for item in result["requirements"]:
        # st.table reads cells as Markdown, where "two spaces + newline"
        # means a line break, so each quote gets its own line
        if item["evidence_quotes"]:
            evidence_text = "  \n".join(f'"{quote}"' for quote in item["evidence_quotes"])
        else:
            evidence_text = "Not mentioned"

        table_rows.append({
            "ID": item["id"],
            "Status": item["status"],
            "Evidence": evidence_text,
            "Reason": item["reason"],
            "Action": item["action"],
        })
    # st.table wraps long text, so the reasons stay readable
    st.table(table_rows)

    st.subheader("Follow-up questions")
    for question in result["follow_up_questions"]:
        st.markdown(f"- {question}")

    # Hidden by default: shows which tools the agent chose, in order
    with st.expander("Agent steps"):
        for step_number, step in enumerate(result["agent_steps"], start=1):
            st.markdown(f"{step_number}. **{step['tool']}**: {step['result']}")

    # A person makes the final call; the AI only recommends
    st.subheader("Analyst review")
    reviewer_name = st.text_input("Reviewer name")
    comment = st.text_area("Comment")

    decision = None
    if st.button("Accept assessment"):
        decision = "Accepted"
    if st.button("Reject assessment"):
        decision = "Rejected"

    if decision:
        if reviewer_name.strip() == "":
            st.error("Please enter your name before saving a decision.")
        else:
            save_decision(saved["assessment_id"], decision, reviewer_name, comment)
            st.success(f"Decision saved for assessment {saved['assessment_id']}")
