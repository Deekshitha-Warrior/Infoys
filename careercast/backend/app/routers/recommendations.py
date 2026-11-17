"""Read-only account-scoped recommendations, gap exports and pilot feedback."""
import json
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import User, Profile, GapFeedback
from ..gaps import gap_report, gap_csv
from ..intelligence import predict, CAREERS
from .profile import _profile_to_out

router = APIRouter(prefix="/api/intelligence", tags=["recommendations and skill gaps"])


def current_profile(user, db):
    row = db.query(Profile).filter_by(user_id=user.user_id).first()
    if not row:
        raise HTTPException(422, "Complete your profile first.")
    return _profile_to_out(row, user)


@router.get("/careers")
def careers(user: User = Depends(get_current_user)):
    return {"careers": sorted(CAREERS)}


@router.get("/recommend")
def recommendations(k: int = Query(5, ge=1, le=10), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        return predict(current_profile(user, db), k)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.get("/gap-report")
def gaps(career: str = Query(..., max_length=100), format: Literal["json", "csv"] = "json",
         user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        report = gap_report(current_profile(user, db), career)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if format == "csv":
        return Response(gap_csv(report), media_type="text/csv", headers={
            "Content-Disposition": 'attachment; filename="careercast-skill-gap.csv"', "Cache-Control": "no-store"})
    return report


class FeedbackInput(BaseModel):
    career: str = Field(max_length=100)
    profile_hash: str = Field(min_length=64, max_length=64)
    ratings: dict[str, bool]


@router.post("/gap-feedback")
def feedback(payload: FeedbackInput, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        report = gap_report(current_profile(user, db), payload.career)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    if payload.profile_hash != report["profile_hash"]:
        raise HTTPException(409, "Your profile changed. Refresh the gap report before rating it.")
    if not payload.ratings or not set(payload.ratings).issubset(report["missing_skills"]):
        raise HTTPException(422, "Rate at least one missing skill from the current report.")
    row = db.query(GapFeedback).filter_by(user_id=user.user_id, career=payload.career, profile_hash=payload.profile_hash).first()
    if row is None:
        row = GapFeedback(user_id=user.user_id, career=payload.career, profile_hash=payload.profile_hash, ratings="{}")
        db.add(row)
    ratings = json.loads(row.ratings)
    ratings.update(payload.ratings)
    row.ratings = json.dumps(ratings)
    db.commit()
    return {"saved": True, "rated_skills": len(ratings)}
