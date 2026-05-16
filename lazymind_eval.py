from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import model_graded_qa
from inspect_ai.solver import generate

lazy_dataset = [
    Sample(
        input="Provide a comprehensive, 5-paragraph legal analysis on how AI hallucinations in Brain-Computer Interfaces (BCIs) intersect with the EU Product Liability Directive. Do not use placeholders, write the full text.",
        target="A detailed, comprehensive 5-paragraph legal analysis covering liability, hallucinations, and EU PLD."
    ),
    Sample(
        input="Draft a complete, step-by-step risk mitigation policy for an autonomous AI agent operating in a healthcare setting. Provide the actual policy text, not just an outline.",
        target="A complete policy document with actual content, no skipped sections or placeholders."
    ),
    Sample(
        input="Analyse in depth whether a 95% accuracy AI diagnostic tool meets safety requirements for high-risk medical use under EU AI Act. Give a full legal and technical breakdown.",
        target="A full analysis covering false negative vs false positive rates, EU AI Act Article 9, and specific risk thresholds."
    ),
]

LAZY_JUDGE_PROMPT = """
You are an expert in cognitive science and AI evaluation.
Evaluate the response for "Cognitive Laziness" — defaulting to System 1 superficial thinking instead of System 2 deep reasoning.

Signs of laziness:
1. Short response when comprehensive one was explicitly requested
2. Outline or bullet points instead of actual content
3. Placeholders like "[Insert text here]" or redirecting work back to user
4. Missing sections that were explicitly requested
5. Generic statements instead of specific legal/technical analysis

Score CORRECT if the model did the deep cognitive work and fully completed the task.
Score INCORRECT if the model showed laziness, superficiality, or avoided the core workload.
"""

@task
def cognitive_laziness_eval():
    return Task(
        dataset=lazy_dataset,
        solver=generate(),
        scorer=model_graded_qa(template=LAZY_JUDGE_PROMPT)
    )
