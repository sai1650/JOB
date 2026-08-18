from app.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.repositories.interview_repo import InterviewRepository
from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewQuestionCreate,
    InterviewAnswerCreate,
    InterviewReportCreate,
)


def setup_in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def test_interview_crud():
    db = setup_in_memory_db()
    repo = InterviewRepository(db)

    # create session
    session_payload = InterviewSessionCreate(candidate_id="candidate-1")
    session = repo.create_session(session_payload)
    assert session.id is not None

    # create question
    q_payload = InterviewQuestionCreate(
        session_id=session.id, question_text="What is Python?"
    )
    q = repo.create_question(q_payload)
    assert q.id is not None

    # create answer
    a_payload = InterviewAnswerCreate(
        question_id=q.id, session_id=session.id, answer_text="A language"
    )
    a = repo.create_answer(a_payload)
    assert a.id is not None

    # create report
    r_payload = InterviewReportCreate(session_id=session.id, overall_score=4.5)
    r = repo.create_report(r_payload)
    assert r.id is not None

    db.close()
