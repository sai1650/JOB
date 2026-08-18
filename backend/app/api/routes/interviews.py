from datetime import datetime
import json
import math
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.candidate_repo import CandidateRepository
from app.repositories.interview_repo import InterviewRepository
from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewQuestionCreate,
    InterviewAnswerCreate,
    InterviewReportCreate,
)
from app.services.retrieval import Retriever
from app.services.question_generator import InterviewQuestionGenerator
from app.services.evaluator import Evaluator
from app.services.strategy import InterviewStrategy
from app.models.interview import InterviewQuestion, InterviewAnswer
from app.models.candidate import Candidate
from app.services.report_generator import generate_report

router = APIRouter()


class SimpleVectorStore:
    """Loads fallback vectors from knowledge_base/<role>/fallback_vectors.json and
    performs cosine similarity search.
    """

    def __init__(self, role_id: str, base_path: str = None):
        from pathlib import Path

        base = base_path or Path(__file__).resolve().parents[2]
        path = base / "knowledge_base" / role_id / "fallback_vectors.json"
        self.items = []
        if path.exists():
            try:
                self.items = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                self.items = []

    def _cosine(self, a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def search(self, q_vec, top_k=10):
        res = []
        for it in self.items:
            vec = it.get("vector")
            score = self._cosine(q_vec, vec) if vec else 0.0
            meta = it.get("metadata", {})
            res.append({
                "id": meta.get("chunk_id"),
                "text": meta.get("text"),
                "source": meta.get("source"),
                "page": meta.get("page"),
                "vector": vec,
                "score": score,
            })
        res.sort(key=lambda x: -x.get("score", 0.0))
        return res[:top_k]


def _simple_llm_generate(prompt: str) -> str:
    """Deterministic simple generator that creates one question per
    top chunk. Each question cites the chunk it was derived from.
    Returns JSON string as expected by InterviewQuestionGenerator.
    """
    try:
        # Parse the prompt which contains JSON payload
        prompt_text = prompt.replace(
            "Please generate JSON array of interview questions. Input: ",
            ""
        )
        prompt_payload = json.loads(prompt_text)
    except Exception:
        # If parsing fails, return empty array
        return json.dumps([])

    questions = []
    retrieved = prompt_payload.get("retrieved_context", {}) or {}
    chunks = retrieved.get("chunks", [])
    candidate = prompt_payload.get("candidate_profile", {}) or {}
    role = prompt_payload.get("selected_role", {}) or {}
    stage = prompt_payload.get("interview_stage", "")

    # For safety, only use up to 5 chunks
    for c in chunks[:5]:
        txt = c.get("text", "")
        topic = c.get("topic") or (role.get("title") if isinstance(
            role, dict) else "general") or "general"
        techs = (candidate.get("extracted_technologies", []) or [])[:3]
        role_title = (role.get("title") if isinstance(role, dict)
                      else role or "")
        qtext = (
            f"Based on the following context: '{txt[:200]}', "
            f"explain the key ideas and how they apply to {techs} "
            f"for the role {role_title}."
        )
        q = {
            "question": qtext,
            "topic": topic,
            "difficulty": "medium",
            "question_type": "applied",
            "reason": "grounded in retrieved chunk",
            "source_context": [
                {
                    "source": c.get("source"),
                    "page": c.get("page")
                }
            ],
        }
        questions.append(q)
    return json.dumps(questions)


@router.post("/interviews")
def create_interview(payload: InterviewSessionCreate, db: Session = Depends(get_db)):
    cand_repo = CandidateRepository(db)
    interview_repo = InterviewRepository(db)

    candidate = cand_repo.get(payload.candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Validate required fields
    if not payload.selected_role:
        raise HTTPException(
            status_code=400,
            detail="Role selection is required to start an interview"
        )

    # create session
    session_payload = InterviewSessionCreate(**payload.dict())
    try:
        session = interview_repo.create_session(session_payload)

        # identify candidate profile
        candidate_profile = {
            "extracted_skills": candidate.extracted_skills or [],
            "extracted_technologies": candidate.extracted_technologies or [],
            "extracted_domains": candidate.extracted_domains or [],
        }

        # initialize strategy state on session
        initial_state = {
            "asked_topics": [],
            "difficulty_history": [],
            "scores": [],
            "weak_topics": [],
            "strong_topics": [],
            "unanswered_areas": (candidate_profile.get("extracted_skills", []) or []) + (candidate_profile.get("extracted_technologies", []) or []),
        }
        session.strategy_state = initial_state

        # retrieval
        role_id = session.selected_role or payload.selected_role
        vector_store = SimpleVectorStore(role_id or "default")
        retriever = Retriever(vector_store=vector_store)
        retrieved = retriever.retrieve(
            selected_role={"title": role_id},
            candidate_profile=candidate_profile,
            interview_stage="screening",
            previous_answers=[],
            knowledge_gaps=[],
            top_k=5,
        )

        # generate first question
        q_gen = InterviewQuestionGenerator(llm=_simple_llm_generate)
        gen_out = q_gen.generate(
            candidate_profile=candidate_profile,
            selected_role={"title": role_id},
            retrieved_context=retrieved,
            interview_history=[],
            previous_answers=[],
            interview_stage="screening",
            num_questions=1,
        )

        questions = gen_out.get("questions", [])
        if questions:
            q = questions[0]
            source_refs = []
            for s in q.get("source_context", []):
                source = s.get("source") or "unknown"
                page = s.get("page") or "0"
                source_refs.append(f"{source}:{page}")
            q_payload = InterviewQuestionCreate(
                session_id=session.id,
                question_text=q["question"],
                question_type=q.get("question_type"),
                difficulty=q.get("difficulty"),
                topic=q.get("topic"),
                retrieved_context=retrieved,
                source_reference=",".join(source_refs),
                generation_metadata={"trace": retrieved.get("trace_id")},
            )
            interview_repo.create_question(q_payload)

        # update session status (object already added via repo.create_session)
        session.status = "IN_PROGRESS"
        session.started_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"session_id": session.id}


@router.get("/interviews/{session_id}")
def get_interview(session_id: str, db: Session = Depends(get_db)):
    repo = InterviewRepository(db)
    s = repo.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    # return session with questions and answers
    qs = repo.list_questions_for_session(session_id)
    questions = []
    for q in qs:
        questions.append(
            {
                "id": q.id,
                "text": q.question_text,
                "type": q.question_type,
                "difficulty": q.difficulty,
                "topic": q.topic,
                "created_at": q.created_at,
            }
        )
    return {
        "id": s.id,
        "candidate_id": s.candidate_id,
        "status": s.status,
        "started_at": s.started_at,
        "completed_at": s.completed_at,
        "questions": questions,
    }


@router.get("/interviews/{session_id}/current-question")
def get_current_question(session_id: str, db: Session = Depends(get_db)):
    repo = InterviewRepository(db)
    s = repo.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Interview already completed")
    qs = repo.list_questions_for_session(session_id)
    idx = s.current_question_index or 0
    if idx >= len(qs):
        raise HTTPException(status_code=404, detail="No current question")
    q = qs[idx]
    total = len(qs)
    return {
        "question": {
            "id": q.id,
            "text": q.question_text,
            "type": q.question_type,
            "difficulty": q.difficulty,
            "topic": q.topic,
            "number": idx + 1,
            "sources": [
                {"source": q.source_reference or "unknown", "page": "0"}
            ] if q.source_reference else [],
        },
        "progress": {
            "current": idx + 1,
            "total": total,
        },
    }


@router.post("/interviews/{session_id}/answer")
def submit_answer(session_id: str, payload: Dict[str, Any], db: Session = Depends(get_db)):
    # payload: {"question_id":..., "answer_text":...}
    repo = InterviewRepository(db)
    s = repo.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Interview already completed")

    qid = payload.get("question_id")
    answer_text = payload.get("answer_text")
    if not qid or answer_text is None:
        raise HTTPException(status_code=400, detail="question_id and answer_text required")

    # prevent duplicate answer
    existing = db.query(InterviewAnswer).filter(InterviewAnswer.question_id == qid).one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Answer already exists for this question")

    try:
        with db.begin():
            # simple evaluation: overlap with topic words
            q = db.query(InterviewQuestion).filter(InterviewQuestion.id == qid).one_or_none()
            if not q:
                raise HTTPException(status_code=404, detail="Question not found")

            # evaluate answer using Evaluator (LLM optional)
            evaluator = Evaluator()
            eval_res = evaluator.evaluate(answer_text, q.question_text, q.retrieved_context or {})

            ans_payload = InterviewAnswerCreate(
                question_id=qid,
                session_id=session_id,
                answer_text=answer_text,
                evaluation_score=float(eval_res.score),
                evaluation_feedback=eval_res.feedback,
                evaluation=eval_res.model_dump() if hasattr(eval_res, "model_dump") else eval_res.dict(),
            )
            ans = repo.create_answer(ans_payload)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"answer_id": ans.id, "evaluation_score": ans.evaluation_score}


@router.post("/interviews/{session_id}/next")
def next_question(session_id: str, db: Session = Depends(get_db)):
    repo = InterviewRepository(db)
    s = repo.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Interview already completed")

    try:
        # generate next question based on previous answers
        candidate = db.query(Candidate).filter(Candidate.id == s.candidate_id).one_or_none()
        candidate_profile = {
            "extracted_skills": candidate.extracted_skills or [],
            "extracted_technologies": candidate.extracted_technologies or [],
            "extracted_domains": candidate.extracted_domains or [],
        }

        # collect previous answers with scores
        prev_answers = []
        for a in s.answers:
            prev_answers.append({
                "question": a.question.question_text,
                "answer": a.answer_text,
                "score": (a.evaluation_score or 0.0),
            })

        # strategy decides next topic/difficulty/type
        strategy = InterviewStrategy(session_state=s.strategy_state or {})
        decision = strategy.decide_next(candidate_profile=candidate_profile, previous_answers=prev_answers)

        role_id = s.selected_role or "default"
        # retrieval: include topic hint
        vector_store = SimpleVectorStore(role_id)
        retriever = Retriever(vector_store=vector_store)
        retrieved = retriever.retrieve(
            selected_role={"title": role_id, "topic": decision.get("next_topic")},
            candidate_profile=candidate_profile,
            interview_stage=s.status,
            previous_answers=prev_answers,
            knowledge_gaps=[],
            top_k=5,
        )

        q_gen = InterviewQuestionGenerator(llm=_simple_llm_generate)
        gen_out = q_gen.generate(
            candidate_profile=candidate_profile,
            selected_role={"title": role_id, "topic": decision.get("next_topic")},
            retrieved_context=retrieved,
            interview_history=[],
            previous_answers=prev_answers,
            interview_stage=s.status,
            num_questions=1,
        )
        questions = gen_out.get("questions", [])
        if not questions:
            raise HTTPException(status_code=500, detail="No question generated")

        q = questions[0]
        source_refs = []
        for item in q.get("source_context", []):
            source = item.get("source") or "unknown"
            page = item.get("page") or "0"
            source_refs.append(f"{source}:{page}")
        q_payload = InterviewQuestionCreate(
            session_id=s.id,
            question_text=q["question"],
            question_type=q.get("question_type"),
            difficulty=q.get("difficulty"),
            topic=q.get("topic"),
            retrieved_context=retrieved,
            source_reference=",".join(source_refs),
            generation_metadata={"trace": retrieved.get("trace_id")},
        )
        repo.create_question(q_payload)

        # advance index
        s.current_question_index = (s.current_question_index or 0)
        s.current_question_index += 1
        db.commit()
        db.refresh(s)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"session_id": s.id, "current_question_index": s.current_question_index}


@router.post("/interviews/{session_id}/complete")
def complete_interview(session_id: str, db: Session = Depends(get_db)):
    repo = InterviewRepository(db)
    s = repo.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if s.status == "COMPLETED":
        raise HTTPException(status_code=400, detail="Interview already completed")

    try:
        with db.begin():
            # aggregate scores
            answers = s.answers
            if not answers:
                overall = 0.0
            else:
                total = sum((a.evaluation_score or 0.0) for a in answers)
                overall = total / max(1, len(answers))

            # generate structured report and persist it
            candidate = db.query(Candidate).filter(Candidate.id == s.candidate_id).one_or_none()
            qs = repo.list_questions_for_session(s.id)
            answers = list(s.answers)

            full_report = generate_report(s, candidate, qs, answers)

            report_payload = InterviewReportCreate(
                session_id=s.id,
                overall_score=overall,
                strengths=full_report.get('technical_strengths', []),
                weaknesses=full_report.get('technical_weaknesses', []),
                topic_scores=full_report.get('performance_by_topic', {}),
                recommendation=full_report.get('hiring_recommendation'),
                report=full_report,
            )
            repo.create_report(report_payload)

            s.status = "COMPLETED"
            s.completed_at = datetime.utcnow()
            db.add(s)
            db.commit()
            db.refresh(s)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {"session_id": s.id, "status": s.status}


@router.get("/interviews/{session_id}/report")
def get_interview_report(session_id: str, db: Session = Depends(get_db)):
    repo = InterviewRepository(db)
    s = repo.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    # Try to read stored report if available
    report = repo.get_report_for_session(session_id)

    # Build full report payload from stored data (answers + questions)
    qs = repo.list_questions_for_session(session_id)
    qmap = {q.id: q for q in qs}
    answers = []
    for a in s.answers:
        q = qmap.get(a.question_id)
        answers.append(
            {
                "question_id": a.question_id,
                "question_text": q.question_text if q else None,
                "topic": q.topic if q else None,
                "difficulty": q.difficulty if q else None,
                "answer_text": a.answer_text,
                "evaluation_score": a.evaluation_score,
                "evaluation_feedback": a.evaluation_feedback,
                "evaluation": a.evaluation,
                "created_at": a.created_at,
            }
        )

    num_questions = len(qs)

    # topic-wise aggregation
    topic_scores = {}
    topic_counts = {}
    difficulty_scores = {}
    difficulty_counts = {}
    score_progression = []

    for idx, a in enumerate(sorted(s.answers, key=lambda x: x.created_at)):
        score = float(a.evaluation_score or 0.0)
        q = qmap.get(a.question_id)
        topic = (q.topic or "general") if q else "general"
        diff = (q.difficulty or "unknown") if q else "unknown"

        topic_scores[topic] = topic_scores.get(topic, 0.0) + score
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

        difficulty_scores[diff] = difficulty_scores.get(diff, 0.0) + score
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1

        score_progression.append({"step": idx + 1, "score": score, "timestamp": a.created_at})

    topic_performance = {t: (topic_scores[t] / max(1, topic_counts[t])) for t in topic_scores}
    difficulty_performance = {d: (difficulty_scores[d] / max(1, difficulty_counts[d])) for d in difficulty_scores}

    # strengths/weaknesses from stored report, fallback to compute
    strengths = report.strengths if report and report.strengths else sorted(topic_performance.keys(), key=lambda x: -topic_performance.get(x,0))[:3]
    weaknesses = report.weaknesses if report and report.weaknesses else sorted(topic_performance.keys(), key=lambda x: topic_performance.get(x,0))[:3]

    overall_score = report.overall_score if report and report.overall_score is not None else (
        (sum((a.evaluation_score or 0.0) for a in s.answers) / max(1, len(s.answers))) if s.answers else 0.0
    )

    final = {
        "session_id": s.id,
        "candidate_id": s.candidate_id,
        "status": s.status,
        "started_at": s.started_at,
        "completed_at": s.completed_at,
        "overall_score": overall_score,
        "num_questions": num_questions,
        "topic_performance": topic_performance,
        "difficulty_performance": difficulty_performance,
        "score_progression": score_progression,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendation": report.recommendation if report else None,
        "questions": answers,
        "generated_report": report.report if report else None,
    }

    return final
