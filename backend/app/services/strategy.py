from typing import Any, Dict, List, Optional


class InterviewStrategy:
    """Adaptive interview strategy engine.

    Tracks asked topics, difficulty history, scores, weak/strong topics,
    and decides the next topic, difficulty and question type.
    """

    DIFFICULTY_ORDER = ["easy", "medium", "hard"]

    def __init__(self, session_state: Optional[Dict[str, Any]] = None):
        # session_state is a JSON-serializable dict persisted on the session
        self.state = session_state or {}
        self.state.setdefault("asked_topics", [])
        self.state.setdefault("difficulty_history", [])
        self.state.setdefault("scores", [])
        self.state.setdefault("weak_topics", [])
        self.state.setdefault("strong_topics", [])
        self.state.setdefault("unanswered_areas", [])

    def _last_difficulty(self) -> Optional[str]:
        dh = self.state.get("difficulty_history")
        return dh[-1] if dh else None

    def _bump_difficulty(self, last: Optional[str], direction: int) -> str:
        # direction: +1 to increase, -1 to decrease, 0 to keep
        if not last:
            return "medium"
        try:
            idx = self.DIFFICULTY_ORDER.index(last)
        except ValueError:
            return "medium"
        idx = max(0, min(len(self.DIFFICULTY_ORDER) - 1, idx + direction))
        return self.DIFFICULTY_ORDER[idx]

    def update_with_answer(self, question_topic: Optional[str], difficulty: Optional[str], score: float):
        if question_topic:
            if question_topic not in self.state["asked_topics"]:
                self.state["asked_topics"].append(question_topic)

        if difficulty:
            self.state["difficulty_history"].append(difficulty)

        self.state["scores"].append(score)

        # update weak/strong topics heuristics
        if question_topic:
            if score >= 8:
                if question_topic not in self.state["strong_topics"]:
                    self.state["strong_topics"].append(question_topic)
                if question_topic in self.state["weak_topics"]:
                    self.state["weak_topics"].remove(question_topic)
            elif score <= 4:
                if question_topic not in self.state["weak_topics"]:
                    self.state["weak_topics"].append(question_topic)

    def decide_next(self, candidate_profile: Dict[str, Any], previous_answers: List[Dict[str, Any]]) -> Dict[str, Any]:
        # determine candidate areas
        skills = (candidate_profile.get("extracted_skills") or []) + (candidate_profile.get("extracted_technologies") or [])
        skills = [s for s in skills if s]

        # choose next topic not asked yet
        next_topic = None
        for s in skills:
            if s not in self.state["asked_topics"]:
                next_topic = s
                break
        if not next_topic:
            # fallback: use last strong topic or general
            if self.state["weak_topics"]:
                # test foundational understanding of a weak topic
                next_topic = self.state["weak_topics"][0]
            elif self.state["strong_topics"]:
                next_topic = self.state["strong_topics"][0]
            else:
                next_topic = skills[0] if skills else "general"

        # determine difficulty based on last score
        last_score = (self.state.get("scores") or [])[-1] if self.state.get("scores") else None
        last_diff = self._last_difficulty()
        if last_score is None:
            # start medium
            next_diff = "medium"
        else:
            if last_score >= 8:
                next_diff = self._bump_difficulty(last_diff, +1)
            elif last_score >= 4:
                next_diff = self._bump_difficulty(last_diff, 0)
            else:
                next_diff = self._bump_difficulty(last_diff, -1)

        # choose question type
        if (self.state.get("scores") and self.state["scores"][-1] >= 8) or (previous_answers and any(a.get("score", 0) >= 8 for a in previous_answers)):
            q_type = "applied"
        elif self.state.get("scores") and self.state["scores"][-1] >= 4:
            q_type = "clarification"
        else:
            q_type = "conceptual"

        # avoid repeated topics
        if next_topic in self.state["asked_topics"]:
            # pick related technology or general
            alt = next((s for s in skills if s not in self.state["asked_topics"]), None)
            if alt:
                next_topic = alt

        # update unanswered areas
        self.state["unanswered_areas"] = [s for s in skills if s not in self.state["asked_topics"]]

        return {
            "next_topic": next_topic,
            "next_difficulty": next_diff,
            "next_question_type": q_type,
            "retrieval_query": {"topic": next_topic, "techs": candidate_profile.get("extracted_technologies", [])},
            "updated_state": self.state,
        }


__all__ = ["InterviewStrategy"]
