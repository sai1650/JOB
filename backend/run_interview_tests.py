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


def main():
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        repo = InterviewRepository(db)
        session_payload = InterviewSessionCreate(candidate_id="candidate-1")
        session = repo.create_session(session_payload)
        assert session.id is not None

        q_payload = InterviewQuestionCreate(
            session_id=session.id, question_text="What is Python?"
        )
        q = repo.create_question(q_payload)
        assert q.id is not None

        a_payload = InterviewAnswerCreate(
            question_id=q.id, session_id=session.id, answer_text="A language"
        )
        a = repo.create_answer(a_payload)
        assert a.id is not None

        r_payload = InterviewReportCreate(session_id=session.id, overall_score=4.5)
        r = repo.create_report(r_payload)
        assert r.id is not None

    except AssertionError as e:
        print("Interview repo tests failed:", e)
        raise
    finally:
        db.close()

    print("Interview repository smoke tests passed")


if __name__ == "__main__":
    main()
