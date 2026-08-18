from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from starlette.responses import JSONResponse
import logging
import os
from app.core.security_utils import (
    secure_filename,
    allowed_file,
    validate_name_email,
    MAX_UPLOAD_BYTES,
)
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.resume_parser import ResumeParser
from app.repositories.candidate_repo import CandidateRepository
from app.schemas.candidate import CandidateCreate
import uuid

router = APIRouter()
logger = logging.getLogger("candidate_screening.upload")

PDF_CONTENT_TYPES = {"application/pdf"}
TEXT_CONTENT_TYPES = {"text/plain"}
GENERIC_CONTENT_TYPES = {"application/octet-stream", "binary/octet-stream", ""}


def _is_allowed_content_type(filename: str, content_type: str) -> bool:
    ext = os.path.splitext((filename or "").lower())[1]
    ct = (content_type or "").lower().strip()
    if ext == ".pdf":
        return ct in PDF_CONTENT_TYPES or ct in GENERIC_CONTENT_TYPES
    if ext == ".txt":
        return ct in TEXT_CONTENT_TYPES or ct in GENERIC_CONTENT_TYPES
    return False


@router.post("/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    name: str = None,
    email: str = None,
):
    # basic validations
    if not file.filename or not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF or TXT file.",
        )
    if not _is_allowed_content_type(file.filename, file.content_type or ""):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid PDF or TXT file.",
        )

    # stream read but ensure size limit
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File size must be less than 5 MB.",
        )

    # sanitize provided name/email
    name_sanitized, email_sanitized = validate_name_email(name, email)
    name = name_sanitized
    email = email_sanitized

    # safe filename
    filename = secure_filename(file.filename)
    logger.info("Received resume upload: %s size=%d", filename, len(contents))

    parser = ResumeParser(contents, filename)
    try:
        raw_text = parser.extract_text()
    except RuntimeError as exc:
        logger.warning("Resume extraction failed: %s", str(exc))
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception("Resume extraction failed")
        raise HTTPException(status_code=500, detail="Extraction error")

    text = parser.clean_text(raw_text)
    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Unable to process this resume.",
        )

    sections = parser.extract_sections(text)
    skills = parser.extract_skills(text)
    techs = parser.extract_technologies(text)
    domains = parser.extract_domains(text)

    # create candidate record
    if not name:
        name = "Unknown"
    if not email:
        email = f"{uuid.uuid4().hex[:8]}@example.com"

    payload = CandidateCreate(
        name=name,
        email=email,
        resume_filename=filename,
        resume_text=text,
        extracted_skills=skills,
        extracted_technologies=techs,
        extracted_domains=domains,
    )
    repo = CandidateRepository(db)
    try:
        obj = repo.create(payload)
        db.commit()
        db.refresh(obj)
    except Exception:
        db.rollback()
        logger.exception("DB error while creating candidate")
        raise HTTPException(status_code=500, detail="DB error")

    return JSONResponse(
        {
            "candidate_id": obj.id,
            "filename": os.path.basename(file.filename),
            "message": "Resume processed successfully",
            "profile": {
                "skills": skills,
                "technologies": techs,
                "domains": domains,
                "projects": [],
            },
            "skills": skills,
            "technologies": techs,
            "domains": domains,
            "sections": sections,
            "resume_text": text,
        }
    )
