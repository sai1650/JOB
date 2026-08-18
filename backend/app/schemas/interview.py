from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InterviewSessionBase(BaseModel):
    candidate_id: str
    selected_role: Optional[str] = Field(None, alias="role")
    status: Optional[str] = "pending"

    class Config:
        populate_by_name = True  # Allow both field names


class InterviewSessionCreate(InterviewSessionBase):
    pass


class InterviewSessionRead(InterviewSessionBase):
    id: str
    current_question_index: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class InterviewQuestionBase(BaseModel):
    question_text: str
    question_type: Optional[str] = None
    difficulty: Optional[str] = None
    topic: Optional[str] = None
    retrieved_context: Optional[Dict[str, Any]] = None
    source_reference: Optional[str] = None
    generation_metadata: Optional[Dict[str, Any]] = None


class InterviewQuestionCreate(InterviewQuestionBase):
    session_id: str


class InterviewQuestionRead(InterviewQuestionBase):
    id: str
    session_id: str
    created_at: datetime

    class Config:
        orm_mode = True


class InterviewAnswerBase(BaseModel):
    answer_text: Optional[str] = None
    evaluation: Optional[dict] = None


class InterviewAnswerCreate(InterviewAnswerBase):
    question_id: str
    session_id: str
    evaluation_score: Optional[float] = None
    evaluation_feedback: Optional[str] = None


class InterviewAnswerRead(InterviewAnswerBase):
    id: str
    question_id: str
    session_id: str
    evaluation_score: Optional[float] = None
    evaluation_feedback: Optional[str] = None
    evaluation: Optional[dict] = None
    created_at: datetime

    class Config:
        orm_mode = True


class InterviewReportBase(BaseModel):
    overall_score: Optional[float] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    topic_scores: Optional[Dict[str, float]] = None
    recommendation: Optional[str] = None
    report: Optional[Dict[str, Any]] = None


class InterviewReportCreate(InterviewReportBase):
    session_id: str


class InterviewReportRead(InterviewReportBase):
    id: str
    session_id: str
    generated_at: datetime

    class Config:
        orm_mode = True
