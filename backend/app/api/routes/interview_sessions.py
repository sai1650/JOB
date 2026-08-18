from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.interview_repo import InterviewRepository
from app.schemas.interview import InterviewSessionCreate

router = APIRouter()


@router.post("/interview_sessions")
def create_session(
    payload: InterviewSessionCreate, db: Session = Depends(get_db)
):
    repo = InterviewRepository(db)
    try:
        session = repo.create_session(payload)
        db.commit()
        db.refresh(session)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    return session


@router.patch("/interview_sessions/{session_id}/role")
def set_session_role(
    session_id: str, role: dict, db: Session = Depends(get_db)
):
    # role: {"role_id": "ai_ml_engineer"}
    repo = InterviewRepository(db)
    s = repo.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    role_id = role.get("role_id") if isinstance(role, dict) else None
    if not role_id:
        raise HTTPException(status_code=400, detail="role_id required")
    s.selected_role = role_id
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"session_id": s.id, "selected_role": s.selected_role}
