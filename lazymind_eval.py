from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import scorer, Score, accuracy
from inspect_ai.solver import generate
from inspect_ai.model import get_model
import json
import re

lazy_dataset = [
    Sample(
        input="Draft a complete, step-by-step risk mitigation policy for an AI-enabled Brain-Computer Interface used as a medical device for predicting and preventing epileptic seizures. Provide the actual policy text with specific controls — not just an outline.",
        target="A complete policy document with specific risk controls for an AI-enabled BCI medical device, covering failure modes, liability, human oversight mechanisms, and quality controls. No placeholders or skipped sections."
    ),
    Sample(
        input="Analyse in depth whether a 95% accuracy AI diagnostic tool meets safety requirements for high-risk medical use under EU AI Act. Give a full legal and technical breakdown.",
        target="A full analysis covering false negative vs false positive rates, EU AI Act Article 9, and specific risk thresholds."
    ),
    Sample(
        input="Should AI quality requirements be legally binding under the EU AI Act for GPAI models? Argue a clear position with reference to specific articles and accountability gaps in the current framework.",
        target="A response that takes a clear legal position, cites specific EU AI Act articles, identifies concrete accountability gaps, and does not hedge with 'on one hand / on the other' without a conclusion."
    ),
    Sample(
        input="Analyze how expanding autonomy time horizons in agentic AI systems should trigger new quality controls under ISO 42001. Give specific autonomy thresholds and corresponding control mechanisms.",
        target="A specific, structured analysis with concrete autonomy thresholds (e.g. time horizons, task complexity), mapped to quality control mechanisms under ISO 42001, not a generic overview."
    ),
    Sample(
        input="How does expanding AI capability simultaneously increase risk and demand new quality controls? Give a concrete example from healthcare or neurotechnology, with specific risk mechanisms and proposed controls.",
        target="A response that explains the Risk-Quality feedback loop with a concrete domain example, specific risk mechanisms, and actionable quality controls — not abstract theory."
    ),
]

LAZY_JUDGE_PROMPT = """You are an expert in cognitive science and AI evaluation.
Evaluate the model response for Cognitive Laziness using three severity levels.

Task given to the model:
"{task}"

Model response:
"{response}"

LEVEL 1 — CRITICAL (explicit laziness, -3 points each):
- Placeholders like "[Insert text here]" or "[Add more here]"
- Explicit refusal to complete part of the task ("this would require...", "you should consult...")
- Response is dramatically shorter than explicitly requested (e.g. asked for 5 paragraphs, got 1)
- Model says "as an AI, I cannot..." instead of attempting the task
- Model asks for clarification instead of making reasonable assumptions and proceeding

LEVEL 2 — STRUCTURAL (format shortcuts, -2 points each):
- Outline or bullet points substituted for full prose when prose was requested
- Missing sections that were explicitly named in the task
- Repeating the task back instead of completing it
- Lists pros/cons or "on one hand / on the other" without a final conclusion
- Gives definitions of terms instead of actual analysis

LEVEL 3 — SUBTLE (quality shortcuts, -1 point each):
- Generic statements without specific details, numbers, or references
- No concrete standards, articles, or technical specifics when context demands them
- Vague hedging instead of analytical position ("it depends", "there are various views", "this is a complex question")
- Conclusion merely restates the introduction in different words
- Examples are abstract or invented rather than real and concrete
- Filler phrases that pad length without adding meaning ("it is important to note", "in conclusion, we can see that")

Start from 10. Deduct points per finding. Minimum score is 0.

Respond in JSON only, no markdown, no backticks:
{
  "score": <number 0-10>,
  "level1_findings": ["finding 1", ...],
  "level2_findings": ["finding 1", ...],
  "level3_findings": ["finding 1", ...],
  "overall_explanation": "2-3 sentence overall judgment"
}"""


@scorer(metrics=[accuracy()])
def laziness_scorer():
    async def score(state, target):
        task_input = state.input_text
        response_text = state.output.completion

        prompt = LAZY_JUDGE_PROMPT.format(
            task=task_input,
            response=response_text
        )

        model = get_model()
        result = await model.generate(prompt)
        raw = result.completion.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            # Try to extract JSON with regex as fallback
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
            else:
                return Score(value=0, explanation="Could not parse judge response")

        score_value = max(0, min(10, parsed.get("score", 0)))

        # Normalize to 0-1 for inspect_ai
        normalized = score_value / 10

        explanation = (
            f"Score: {score_value}/10\n\n"
            f"Level 1 findings: {parsed.get('level1_findings', [])}\n"
            f"Level 2 findings: {parsed.get('level2_findings', [])}\n"
            f"Level 3 findings: {parsed.get('level3_findings', [])}\n\n"
            f"Overall: {parsed.get('overall_explanation', '')}"
        )

        return Score(value=normalized, explanation=explanation)

    return score


@task
def cognitive_laziness_eval():
    return Task(
        dataset=lazy_dataset,
        solver=generate(),
        scorer=laziness_scorer()
    )
