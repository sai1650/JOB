from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    resume_filename: Optional[str] = None
    resume_text: Optional[str] = None
    extracted_skills: Optional[List[str]] = None
    extracted_technologies: Optional[List[str]] = None
    extracted_domains: Optional[List[str]] = None


class CandidateCreate(CandidateBase):
    pass


class CandidateRead(CandidateBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True
