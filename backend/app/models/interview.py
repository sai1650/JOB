import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Float,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
from app.models.base import Base


def gen_uuid():
    return str(uuid.uuid4())


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    candidate_id = Column(String(36), ForeignKey("candidates.id"), nullable=False, index=True)
    selected_role = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    current_question_index = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    candidate = relationship("Candidate", backref="sessions")
    questions = relationship("InterviewQuestion", back_populates="session")
    answers = relationship("InterviewAnswer", back_populates="session")
    strategy_state = Column(JSON, nullable=True)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False, index=True)
    question_text = Column(String, nullable=False)
    question_type = Column(String(50), nullable=True)
    difficulty = Column(String(50), nullable=True)
    topic = Column(String(255), nullable=True, index=True)
    retrieved_context = Column(JSON, nullable=True)
    source_reference = Column(String(512), nullable=True)
    generation_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("InterviewSession", back_populates="questions")
    answers = relationship("InterviewAnswer", back_populates="question")


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    question_id = Column(String(36), ForeignKey("interview_questions.id"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False, index=True)
    answer_text = Column(String, nullable=True)
    evaluation_score = Column(Float, nullable=True)
    evaluation_feedback = Column(String, nullable=True)
    evaluation = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    question = relationship("InterviewQuestion", back_populates="answers")
    session = relationship("InterviewSession", back_populates="answers")


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    session_id = Column(String(36), ForeignKey("interview_sessions.id"), nullable=False, index=True)
    overall_score = Column(Float, nullable=True)
    strengths = Column(JSON, nullable=True)
    weaknesses = Column(JSON, nullable=True)
    topic_scores = Column(JSON, nullable=True)
    recommendation = Column(String, nullable=True)
    report = Column(JSON, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("InterviewSession")


Index("ix_session_candidate", InterviewSession.candidate_id)
