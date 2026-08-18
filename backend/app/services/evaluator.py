from typing import Any, Dict, List, Optional, Callable
import json
import re

from pydantic import BaseModel, Field, ValidationError, validator


class EvaluationResult(BaseModel):
    score: int = Field(..., ge=0, le=10)
    correctness: int = Field(..., ge=0, le=10)
    technical_depth: int = Field(..., ge=0, le=10)
    relevance: int = Field(..., ge=0, le=10)
    reasoning: int = Field(..., ge=0, le=10)
    clarity: int = Field(..., ge=0, le=10)
    completeness: int = Field(..., ge=0, le=10)
    feedback: str
    missing_concepts: List[str] = []
    strengths: List[str] = []
    verdict: Optional[str] = None

    @validator("verdict", pre=True, always=True)
    def _set_verdict(cls, v, values):
        if v:
            return v
        sc = values.get("score", 0)
        if sc >= 8:
            return "correct"
        if sc >= 4:
            return "partially_correct"
        return "incorrect"


class Evaluator:
    """Evaluates a candidate's free-text answer against retrieved context.

    Optionally accepts an `llm` callable that takes a prompt string and
    returns a string. If provided, the LLM is asked to return a JSON object
    matching EvaluationResult. If the LLM returns invalid JSON or the
    validation fails, the evaluator falls back to a deterministic rule-based
    scorer.
    """

    def __init__(self, llm: Optional[Callable[[str], str]] = None):
        self.llm = llm

    def _extract_keywords(self, texts: List[str], min_len: int = 4) -> List[str]:
        words = {}
        for t in texts:
            for w in re.findall(r"\b[a-zA-Z]{%d,}\b" % min_len, (t or "").lower()):
                if w in ("the", "and", "for", "with", "that", "this", "have", "has"):
                    continue
                words[w] = words.get(w, 0) + 1
        # return top 10
        return [w for w, _ in sorted(words.items(), key=lambda x: -x[1])][:10]

    def _rule_based(self, answer: str, question: str, retrieved_context: Dict[str, Any]) -> EvaluationResult:
        chunks = []
        if isinstance(retrieved_context, dict):
            for c in retrieved_context.get("chunks", []):
                chunks.append(c.get("text", ""))

        keywords = self._extract_keywords(chunks + [question])
        ans_text = (answer or "").lower()

        # correctness/relevance: overlap of keywords
        if not ans_text.strip():
            return EvaluationResult(
                score=0,
                correctness=0,
                technical_depth=0,
                relevance=0,
                reasoning=0,
                clarity=0,
                completeness=0,
                feedback="No answer provided",
                missing_concepts=keywords,
                strengths=[],
            )

        overlap = 0
        for k in keywords:
            if k in ans_text:
                overlap += 1

        rel_score = min(10, int((overlap / max(1, len(keywords))) * 10)) if keywords else 5

        # technical depth: presence of examples, code tokens, metrics
        depth = 0
        if any(tok in ans_text for tok in ("example", "e.g.", "for example", "implementation", "code", "return", "complexity")):
            depth += 6
        # longer answers get a boost
        if len(ans_text) > 200:
            depth += 3
        depth = min(10, depth)

        # reasoning: presence of causal words
        reason = 0
        if any(tok in ans_text for tok in ("because", "therefore", "thus", "so", "hence", "because of")):
            reason = 8
        elif any(tok in ans_text for tok in ("approach", "steps", "plan", "method")):
            reason = 6
        else:
            reason = 3

        # clarity: sentence length heuristics
        clarity = 7 if len(ans_text.split()) < 200 else 5
        if len(ans_text.splitlines()) > 5:
            clarity = max(3, clarity - 1)

        # completeness: coverage of top keywords
        comp = rel_score

        # overall score: weighted
        overall = int(round((rel_score * 0.25 + depth * 0.25 + reason * 0.2 + clarity * 0.15 + comp * 0.15)))
        overall = max(0, min(10, overall))

        missing = [k for k in keywords if k not in ans_text]
        strengths = [k for k in keywords if k in ans_text][:5]

        feedback = "Auto-evaluated using rule-based evaluator."
        return EvaluationResult(
            score=overall,
            correctness=int(round(rel_score)),
            technical_depth=int(round(depth)),
            relevance=int(round(rel_score)),
            reasoning=int(round(reason)),
            clarity=int(round(clarity)),
            completeness=int(round(comp)),
            feedback=feedback,
            missing_concepts=missing,
            strengths=strengths,
        )

    def evaluate(self, answer: str, question: str, retrieved_context: Dict[str, Any]) -> EvaluationResult:
        # Try LLM path first if available
        if self.llm:
            prompt = {
                "instruction": "Evaluate the candidate answer against the provided retrieved context and question. Return a JSON object matching the schema: score, correctness, technical_depth, relevance, reasoning, clarity, completeness, feedback, missing_concepts, strengths, verdict.",
                "question": question,
                "retrieved_context": retrieved_context,
                "answer": answer,
            }
            try:
                raw = self.llm(json.dumps(prompt))
                # try parse JSON
                parsed = json.loads(raw)
                # validate via pydantic
                return EvaluationResult(**parsed)
            except (json.JSONDecodeError, ValidationError, TypeError) as e:
                # fall back to rule-based but include LLM error in feedback
                rb = self._rule_based(answer, question, retrieved_context)
                rb.feedback = f"LLM evaluation failed or returned invalid JSON; falling back to rule-based. Error: {e}. \n{rb.feedback}"
                return rb
            except Exception as e:
                rb = self._rule_based(answer, question, retrieved_context)
                rb.feedback = f"LLM evaluation error: {e}. \n{rb.feedback}"
                return rb

        # No LLM: rule-based
        return self._rule_based(answer, question, retrieved_context)


__all__ = ["Evaluator", "EvaluationResult"]
