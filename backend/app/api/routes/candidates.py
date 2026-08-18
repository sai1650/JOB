from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.candidate_repo import CandidateRepository
from app.schemas.candidate import CandidateRead

router = APIRouter()


@router.get("/candidates/{candidate_id}", response_model=CandidateRead)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    repo = CandidateRepository(db)
    obj = repo.get(candidate_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return obj
