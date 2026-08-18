from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.interview import (
    InterviewSession,
    InterviewQuestion,
    InterviewAnswer,
    InterviewReport,
)
from app.schemas.interview import (
    InterviewSessionCreate,
    InterviewQuestionCreate,
    InterviewAnswerCreate,
    InterviewReportCreate,
)


class InterviewRepository:
    def __init__(self, db: Session):
        self.db = db

    # Sessions
    def create_session(self, payload: InterviewSessionCreate) -> InterviewSession:
        obj = InterviewSession(**payload.dict())
        self.db.add(obj)
        return obj

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.db.query(InterviewSession).filter(InterviewSession.id == session_id).one_or_none()

    def list_sessions_for_candidate(self, candidate_id: str) -> List[InterviewSession]:
        return (
            self.db.query(InterviewSession)
            .filter(InterviewSession.candidate_id == candidate_id)
            .all()
        )

    # Questions
    def create_question(self, payload: InterviewQuestionCreate) -> InterviewQuestion:
        obj = InterviewQuestion(**payload.dict())
        self.db.add(obj)
        return obj

    def list_questions_for_session(self, session_id: str) -> List[InterviewQuestion]:
        return (
            self.db.query(InterviewQuestion).filter(InterviewQuestion.session_id == session_id).all()
        )

    # Answers
    def create_answer(self, payload: InterviewAnswerCreate) -> InterviewAnswer:
        obj = InterviewAnswer(**payload.dict())
        self.db.add(obj)
        return obj

    # Reports
    def create_report(self, payload: InterviewReportCreate) -> InterviewReport:
        obj = InterviewReport(**payload.dict())
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def get_report_for_session(self, session_id: str) -> Optional[InterviewReport]:
        return (
            self.db.query(InterviewReport)
            .filter(InterviewReport.session_id == session_id)
            .order_by(InterviewReport.generated_at.desc())
            .first()
        )
