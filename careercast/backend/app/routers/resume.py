"""Resume upload and parsing routes."""
import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Resume, User, Profile
from ..schemas import ApplyParsedData
from ..auth import get_current_user
from ..parser import extract_text, parse_resume

router = APIRouter(prefix="/api/resume", tags=["resume"])

UPLOAD_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate extension
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Only PDF and DOCX are allowed.",
        )

    # Read bytes and validate size
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 5 MB limit.",
        )

    # Save file with unique name to avoid collisions
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = UPLOAD_DIR / safe_name
    with open(dest, "wb") as f:
        f.write(file_bytes)

    # Extract text
    try:
        text = extract_text(file_bytes, file.filename)
    except ValueError as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(exc))

    if not text.strip():
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail=(
                "No readable text found in this file. "
                "It may be a scanned image PDF. Please upload a text-based document "
                "or enter your information manually."
            ),
        )

    # Parse with spaCy rules
    try:
        parsed = parse_resume(text)
    except Exception as exc:
        parsed = {
            "technical_skills": [],
            "education": [],
            "job_roles": [],
            "experience": [],
            "raw_text_preview": text[:500],
            "parse_error": str(exc),
        }

    # Persist to DB
    resume = Resume(
        user_id=current_user.user_id,
        filename=file.filename,
        extracted_text=text,
        parsed_information=json.dumps(parsed),
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return {
        "resume_id": resume.resume_id,
        "filename": resume.filename,
        "upload_date": resume.upload_date,
        "parsed_information": parsed,
    }


@router.get("/latest")
def get_latest_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.user_id)
        .order_by(Resume.upload_date.desc())
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="No resume uploaded yet.")

    parsed = None
    if resume.parsed_information:
        try:
            parsed = json.loads(resume.parsed_information)
        except json.JSONDecodeError:
            parsed = {}

    return {
        "resume_id": resume.resume_id,
        "filename": resume.filename,
        "upload_date": resume.upload_date,
        "parsed_information": parsed,
    }


@router.get("/all")
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.user_id)
        .order_by(Resume.upload_date.desc())
        .all()
    )
    result = []
    for r in resumes:
        result.append({
            "resume_id": r.resume_id,
            "filename": r.filename,
            "upload_date": r.upload_date,
        })
    return result


@router.post("/{resume_id}/apply")
def apply_parsed_to_profile(
    resume_id: int,
    payload: ApplyParsedData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save confirmed extracted resume data into the user's profile."""
    resume = (
        db.query(Resume)
        .filter(Resume.resume_id == resume_id, Resume.user_id == current_user.user_id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not profile:
        profile = Profile(user_id=current_user.user_id)
        db.add(profile)

    if payload.technical_skills is not None:
        profile.technical_skills = json.dumps(payload.technical_skills)
    if payload.soft_skills is not None:
        profile.soft_skills = json.dumps(payload.soft_skills)
    if payload.job_roles and not profile.previous_role:
        profile.previous_role = payload.job_roles[0]
    if payload.experience and not profile.work_experience:
        profile.work_experience = payload.experience[0]
    if payload.education and not profile.qualification:
        profile.qualification = payload.education[0]

    db.commit()
    return {"detail": "Profile updated with extracted resume data."}
