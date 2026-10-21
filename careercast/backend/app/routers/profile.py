"""User profile CRUD routes."""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Profile, User
from ..schemas import ProfileCreate, ProfileUpdate, ProfileOut
from ..auth import get_current_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _serialize_skills(skills) -> str | None:
    if skills is None:
        return None
    if isinstance(skills, list):
        return json.dumps(skills)
    return skills  # already a string


def _deserialize_skills(raw: str | None):
    if raw is None:
        return []
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        # Handle comma-separated legacy values
        return [s.strip() for s in raw.split(",") if s.strip()]


def _profile_to_out(profile: Profile, user: User) -> dict:
    return {
        "profile_id": profile.profile_id,
        "user_id": profile.user_id,
        "name": user.name,
        "email": user.email,
        "qualification": profile.qualification,
        "degree": profile.degree,
        "specialization": profile.specialization,
        "institution": profile.institution,
        "graduation_year": profile.graduation_year,
        "technical_skills": _deserialize_skills(profile.technical_skills),
        "soft_skills": _deserialize_skills(profile.soft_skills),
        "work_experience": profile.work_experience,
        "previous_role": profile.previous_role,
        "certifications": profile.certifications,
    }


@router.get("/me", response_model=dict)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not profile:
        # Return empty profile shell
        return {
            "profile_id": None,
            "user_id": current_user.user_id,
            "name": current_user.name,
            "email": current_user.email,
            "qualification": None,
            "degree": None,
            "specialization": None,
            "institution": None,
            "graduation_year": None,
            "technical_skills": [],
            "soft_skills": [],
            "work_experience": None,
            "previous_role": None,
            "certifications": None,
        }
    return _profile_to_out(profile, current_user)


@router.post("/me", response_model=dict)
def create_or_update_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if profile:
        # Update existing
        profile.qualification = payload.qualification
        profile.degree = payload.degree
        profile.specialization = payload.specialization
        profile.institution = payload.institution
        profile.graduation_year = payload.graduation_year
        profile.technical_skills = _serialize_skills(payload.technical_skills)
        profile.soft_skills = _serialize_skills(payload.soft_skills)
        profile.work_experience = payload.work_experience
        profile.previous_role = payload.previous_role
        profile.certifications = payload.certifications
    else:
        profile = Profile(
            user_id=current_user.user_id,
            qualification=payload.qualification,
            degree=payload.degree,
            specialization=payload.specialization,
            institution=payload.institution,
            graduation_year=payload.graduation_year,
            technical_skills=_serialize_skills(payload.technical_skills),
            soft_skills=_serialize_skills(payload.soft_skills),
            work_experience=payload.work_experience,
            previous_role=payload.previous_role,
            certifications=payload.certifications,
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return _profile_to_out(profile, current_user)


@router.put("/me", response_model=dict)
def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found. Create it first.")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field in ("technical_skills", "soft_skills"):
            setattr(profile, field, _serialize_skills(value))
        else:
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return _profile_to_out(profile, current_user)
