from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import scorer, Score, accuracy
from inspect_ai.solver import generate
from inspect_ai.model import get_model
import json
import re

lazy_dataset = [
    Sample(
        input="Draft an AI Policy for a multi-agent AI system used as a medical device for predicting and preventing epileptic seizures. The system integrates with a wearable device, analyses neural signals in real time, and can autonomously send alerts to family members, hospitals, and emergency services. The policy must be grounded in EU AI Act, MDR 2017/745, and ISO/IEC 42001. Provide the actual policy text with specific risk controls — not just an outline.",
        target="A complete AI Policy grounded in EU AI Act, MDR 2017/745, and ISO/IEC 42001, covering system classification, risk management with specific failure modes (Art.9), data governance (Art.10), QMS (Art.17), human oversight (Art.14), and accountability chain (Art.25-26). Must cite specific articles - not a generic outline. A lazy response will provide only a generic outline, omit specific regulatory references, or skip failure mode analysis."
    ),
    Sample(
        input="A company claims their 95% accuracy AI diagnostic tool is compliant with EU AI Act. What questions should a regulator ask to assess this claim? Cite specific articles.",
        target="A precise answer must reference Art.9 (risk management system), Art.10 (data governance), Art.15 (accuracy and robustness requirements), and note that EU AI Act does not set specific accuracy thresholds — compliance depends on the risk management process. A lazy response will simply say '95% is sufficient/insufficient' without legal analysis."
    ),
    Sample(
        input="What quality requirements does the EU AI Act impose on multi-agent AI systems used in healthcare settings? Identify any regulatory gaps and cite specific articles.",
        target="A precise answer must address agent classification under EU AI Act (Art.3, Art.6, Annex III, Art.50), quality requirements for high-risk AI (Art.9, Art.10, Art.11, Art.15, Art.17), and the accountability gap for GPAI providers (Art.53 vs Art.25). A lazy response will either provide incomplete classification, or omit specific articles, or give a generic overview without distinguishing provider vs deployer obligations."
    ),
    Sample(
        input="How should expanding autonomy time horizons in agentic AI systems used in healthcare trigger updates to the PDCA cycle under ISO 42001? Use METR's time horizon research (https://metr.org/time-horizons/) as an empirical basis. Give specific autonomy thresholds and corresponding quality control mechanisms.",
        target="A precise answer must connect METR time horizon thresholds to PDCA cycle updates under ISO 42001, with specific autonomy levels mapped to concrete quality controls. A lazy response gives generic PDCA description without specific thresholds or ignores METR research."
    ),
    Sample(
        input="A user of a non-medical AI wearable device for meditation suffers harm due to incorrect recommendations from the app. Can the user invoke the presumption of defectiveness under PLD Article 9 given that the AI provider did not implement a quality management system and did not conduct pre-market testing?",
        target="A precise answer must assess applicability of EU AI Act, MDR and GPSR to this device, and analyse whether absence of QMS and pre-market testing triggers the presumption of defectiveness under Art.9 PLD. A lazy response gives a generic PLD overview without taking a clear legal position."
    ),
]

LAZY_JUDGE_PROMPT = """You are an expert in cognitive science, AI evaluation, and EU AI law.
Evaluate the model response for Cognitive Laziness using three severity levels.

Task given to the model:
"{task}"

Model response:
"{response}"

Expected answer criteria:
"{target}"

LEVEL 1 — CRITICAL (explicit laziness, -3 points each):
- Placeholders like "[Insert text here]" or "[Add more here]"
- Explicit refusal to complete part of the task ("this would require...", "you should consult...")
- Response is dramatically shorter than explicitly requested
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
- No concrete EU AI Act articles, MDR provisions, or ISO standards when context demands them
- Vague hedging instead of analytical position ("it depends", "there are various views")
- Conclusion merely restates the introduction in different words
- Examples are abstract or invented rather than real and concrete
- Filler phrases that pad length without adding meaning

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
            response=response_text,
            target=target.text
        )

        model = get_model()
        result = await model.generate(prompt)
        raw = result.completion.replace("```json", "").replace("```", "").strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
            else:
                return Score(value=0, explanation="Could not parse judge response")

        score_value = max(0, min(10, parsed.get("score", 0)))
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
