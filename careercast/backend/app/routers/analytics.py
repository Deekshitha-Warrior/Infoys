"""Private cohort analysis and opt-in user acceptance feedback."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import User, RecommendationFeedback
from ..schemas import ProfileBase
from ..intelligence import profile_hash
from .recommendations import current_profile
from careercast_tools.batch import predict_batch, cohort_summary

router = APIRouter(prefix="/api/intelligence", tags=["cohort analytics and feedback"])


class CohortInput(BaseModel):
    profiles: list[ProfileBase] = Field(min_length=1, max_length=1000)


@router.post("/cohort")
def cohort(payload: CohortInput, user: User = Depends(get_current_user)):
    try:
        reports = predict_batch([profile.model_dump() for profile in payload.profiles])
        return cohort_summary(reports)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


class SatisfactionInput(BaseModel):
    profile_hash: str = Field(min_length=64, max_length=64)
    rating: int = Field(strict=True, ge=1, le=5)


@router.post("/recommendation-feedback")
def feedback(payload: SatisfactionInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    current = profile_hash(current_profile(user, db))
    if current != payload.profile_hash:
        raise HTTPException(409, "Your profile changed. Refresh the analysis before rating it.")
    row = db.query(RecommendationFeedback).filter_by(user_id=user.user_id, profile_hash=current).first()
    if row is None:
        row = RecommendationFeedback(user_id=user.user_id, profile_hash=current, rating=payload.rating)
        db.add(row)
    else:
        row.rating = payload.rating
    db.commit()
    return {"saved": True, "rating": row.rating}
