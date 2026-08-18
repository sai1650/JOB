from sqlalchemy.orm import Session
from typing import Optional
from app.models.candidate import Candidate
from app.schemas.candidate import CandidateCreate


class CandidateRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, payload: CandidateCreate) -> Candidate:
        obj = Candidate(**payload.dict())
        self.db.add(obj)
        return obj

    def get(self, candidate_id: str) -> Optional[Candidate]:
        return self.db.query(Candidate).filter(Candidate.id == candidate_id).one_or_none()

    def get_by_email(self, email: str) -> Optional[Candidate]:
        return self.db.query(Candidate).filter(Candidate.email == email).one_or_none()

    def list(self, limit: int = 100):
        return self.db.query(Candidate).limit(limit).all()
