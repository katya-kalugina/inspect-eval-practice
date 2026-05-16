# LazyMind Eval: Measuring Cognitive Laziness in Large Language Models

## Overview

An evaluation built with [Inspect AI](https://inspect.aisi.org.uk/) that measures cognitive laziness in large language models — the tendency to default to shallow, System 1 thinking instead of deep, System 2 analytical reasoning.

## Hypothesis

Based on Kahneman's dual-process theory, LLMs exhibit a systematic bias toward low-effort responses even when tasks explicitly require comprehensive analysis. This eval operationalises "cognitive laziness" as a measurable behavioural pattern.

In high-stakes domains such as law, medicine, and AI governance, this pattern constitutes a robustness defect under the EU AI Act Article 9 requirements for accuracy and reliability.

## Relevance to AI Safety

When AI systems act as proxy agents in high-risk contexts (healthcare, Brain-Computer Interfaces, legal analysis), cognitive laziness transfers cognitive load back to the human operator — undermining the reliability of the system and creating accountability gaps across the AI value chain.

## Eval Design

| Component | Implementation |
|-----------|---------------|
| Dataset | 3 tasks requiring deep legal and technical analysis |
| Solver | generate() |
| Scorer | model_graded_qa() with custom laziness detection prompt |

## Laziness Indicators

The AI judge evaluates responses for the following signals:

1. Response length significantly shorter than explicitly req
