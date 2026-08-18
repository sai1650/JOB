import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.models.base import Base


def gen_uuid():
    return str(uuid.uuid4())


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    resume_filename = Column(String(512), nullable=True)
    resume_text = Column(String, nullable=True)
    extracted_skills = Column(JSON, nullable=True)
    extracted_technologies = Column(JSON, nullable=True)
    extracted_domains = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


Index("ix_candidate_email", Candidate.email)
