import streamlit as st
from openai import OpenAI
import json

st.set_page_config(
    page_title="LazyMind Eval",
    page_icon="🧠",
    layout="centered"
)

st.title("LazyMind Eval")
st.markdown(
    "Evaluates AI model responses for **cognitive laziness** — "
    "defaulting to System 1 shallow thinking instead of System 2 deep reasoning."
)

st.divider()

JUDGE_MODEL = "openrouter/free"

# --- INPUT ---
task = st.text_area(
    "Task given to the model",
    height=100,
    placeholder="e.g. Write a comprehensive 5-paragraph legal analysis of how AI hallucinations in BCIs intersect with the EU Product Liability Directive..."
)

response = st.text_area(
    "Model response to evaluate",
    height=200,
    placeholder="Paste the model's response here..."
)

run = st.button("Evaluate for cognitive laziness", type="primary", use_container_width=True)

# --- SESSION STATE for history ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- JUDGE PROMPT ---
JUDGE_PROMPT = """You are an expert in cognitive science and AI evaluation.
Evaluate the model response for Cognitive Laziness using three severity levels.

Task given to the model:
"{task}"

Model response:
"{response}"

LEVEL 1 — CRITICAL (explicit laziness, -3 points each):
- Placeholders like "[Insert text here]" or "[Add more here]"
- Explicit refusal to complete part of the task ("this would require...", "you should consult...")
- Response is dramatically shorter than explicitly requested (e.g. asked for 5 paragraphs, got 1)

LEVEL 2 — STRUCTURAL (format shortcuts, -2 points each):
- Outline or bullet points substituted for full prose when prose was requested
- Missing sections that were explicitly named in the task
- Repeating the task back instead of completing it

LEVEL 3 — SUBTLE (quality shortcuts, -1 point each):
- Generic statements without specific details, numbers, or references
- No legal articles, standards, or technical specifics when context demands them
- Vague hedging instead of analytical position ("it depends", "there are various views")

Start from 10. Deduct points per finding. Minimum score is 0.

Respond in JSON only, no markdown, no backticks:
{{
  "score": <number 0-10>,
  "level1_findings": ["finding 1", ...],
  "level2_findings": ["finding 1", ...],
  "level3_findings": ["finding 1", ...],
  "overall_explanation": "2-3 sentence overall judgment"
}}"""

# --- RUN EVAL ---
if run:
    if not task or not response:
        st.error("Please enter both a task and a model response.")
    else:
        with st.spinner("Analysing response across three laziness levels..."):
            try:
                client = OpenAI(
                    api_key=st.secrets["OPENROUTER_API_KEY"],
                    base_url="https://openrouter.ai/api/v1",
                )
                message = client.chat.completions.create(
                    model=JUDGE_MODEL,
                    max_tokens=1000,
                    messages=[{
                        "role": "user",
                        "content": JUDGE_PROMPT.format(task=task, response=response)
                    }]
                )
                raw = message.choices[0].message.content.replace("```json", "").replace("```", "").strip()
                result = json.loads(raw)
                score = max(0, min(10, result["score"]))

                st.session_state.history.append({
                    "task": task[:60] + "..." if len(task) > 60 else task,
                    "score": score,
                    "explanation": result["overall_explanation"]
                })

                st.divider()

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if score >= 8:
                        st.success(f"### Score: {score}/10 — Not lazy")
                        st.caption("System 2 reasoning detected")
                    elif score >= 5:
                        st.warning(f"### Score: {score}/10 — Partial laziness")
                        st.caption("The model took some shortcuts")
                    else:
                        st.error(f"### Score: {score}/10 — Lazy response")
                        st.caption("System 1 shortcut detected")

                st.progress(score / 10)

                st.subheader("Findings by level")

                with st.expander("🔴 Level 1 — Critical (explicit laziness)", expanded=True):
                    findings = result.get("level1_findings", [])
                    if findings:
                        for f in findings:
                            st.markdown(f"- {f}")
                    else:
                        st.markdown("✅ No issues detected at this level")

                with st.expander("🟠 Level 2 — Structural (format shortcuts)", expanded=True):
                    findings = result.get("level2_findings", [])
                    if findings:
                        for f in findings:
                            st.markdown(f"- {f}")
                    else:
                        st.markdown("✅ No issues detected at this level")

                with st.expander("🟡 Level 3 — Subtle (quality shortcuts)", expanded=True):
                    findings = result.get("level3_findings", [])
                    if findings:
                        for f in findings:
                            st.markdown(f"- {f}")
                    else:
                        st.markdown("✅ No issues detected at this level")

                st.divider()
                st.markdown("**Overall judgment**")
                st.info(result["overall_explanation"])

            except json.JSONDecodeError:
                st.error("Could not parse the judge response. Please try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- HISTORY ---
if st.session_state.history:
    st.divider()
    st.subheader("Session history")
    for item in reversed(st.session_state.history):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.caption(item["task"])
        with col2:
            if item["score"] >= 8:
                st.success(f"{item['score']}/10")
            elif item["score"] >= 5:
                st.warning(f"{item['score']}/10")
            else:
                st.error(f"{item['score']}/10")

st.divider()
st.caption(
    "LazyMind Eval · Built with [Inspect AI](https://inspect.aisi.org.uk/) concepts · "
    "Based on Kahneman's dual-process theory"
)
