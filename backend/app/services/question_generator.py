import json
from typing import Any, Dict, List, Optional, Tuple

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
ALLOWED_TYPES = {
    "conceptual",
    "applied",
    "scenario",
    "resume",
    "debugging",
    "system_design",
}


class QuestionValidationError(Exception):
    pass


class InterviewQuestionGenerator:
    """Generates interview questions given profile, role, and retrieved context.

    The generator relies on an LLM-like callable that returns a JSON array
    of question objects. Validation ensures citations are only from
    retrieved chunks and enforces schema rules.
    """

    def __init__(self, llm: Optional[Any] = None):
        # llm: callable(prompt: str) -> str (JSON)
        self.llm = llm

    def _validate_question(self, q: Dict[str, Any], retrieved_chunks: List[Dict[str, Any]]) -> Tuple[bool, Optional[str]]:
        # Required fields
        for field in ("question", "topic", "difficulty", "question_type", "source_context"):
            if field not in q:
                return False, f"missing field {field}"

        text = q["question"].strip()
        if len(text) < 20:
            return False, "question too short"

        if q["difficulty"].lower() not in ALLOWED_DIFFICULTIES:
            return False, "invalid difficulty"

        if q["question_type"] not in ALLOWED_TYPES:
            return False, "invalid question_type"

        # Validate citations: each entry in source_context must match a retrieved chunk
        valid_sources = set((c.get("source"), c.get("page")) for c in retrieved_chunks)
        for cite in q.get("source_context", []):
            s = cite.get("source")
            p = cite.get("page")
            if (s, p) not in valid_sources:
                return False, f"unsupported citation {s}:{p}"

        return True, None

    def _dedupe(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        seen = set()
        out = []
        for q in questions:
            key = q.get("question", "").strip().lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(q)
        return out

    def generate(
        self,
        candidate_profile: Dict[str, Any],
        selected_role: Dict[str, Any],
        retrieved_context: Dict[str, Any],
        interview_history: List[Dict[str, Any]],
        previous_answers: List[Dict[str, Any]],
        interview_stage: str,
        num_questions: int = 5,
    ) -> Dict[str, Any]:
        if not self.llm:
            raise RuntimeError("LLM callable not provided")

        prompt_payload = {
            "candidate_profile": candidate_profile,
            "selected_role": selected_role,
            "retrieved_context": retrieved_context,
            "interview_history": interview_history,
            "previous_answers": previous_answers,
            "interview_stage": interview_stage,
            "num_questions": num_questions,
        }

        prompt = "Please generate JSON array of interview questions. Input: " + json.dumps(prompt_payload)

        raw = self.llm(prompt)

        try:
            parsed = json.loads(raw)
        except Exception as e:
            raise QuestionValidationError(f"LLM returned invalid JSON: {e}")

        if not isinstance(parsed, list):
            raise QuestionValidationError("LLM must return a JSON array of question objects")

        # Validate and filter
        retrieved_chunks = retrieved_context.get("chunks", []) if isinstance(retrieved_context, dict) else []
        validated = []
        rejected = []
        for q in parsed:
            ok, reason = self._validate_question(q, retrieved_chunks)
            if ok:
                validated.append(q)
            else:
                rejected.append({"question": q.get("question"), "reason": reason})

        # Deduplicate and limit
        validated = self._dedupe(validated)
        validated = validated[:num_questions]

        return {"questions": validated, "rejected": rejected}


__all__ = ["InterviewQuestionGenerator", "QuestionValidationError"]
