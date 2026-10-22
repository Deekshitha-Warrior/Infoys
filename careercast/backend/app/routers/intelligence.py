import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import User, Profile, Resume, Prediction
from ..intelligence import predict, model_report, resume_analysis, profile_hash
from .profile import _profile_to_out

router = APIRouter(prefix="/api/intelligence", tags=["career intelligence"])


@router.get("/models")
def models(user: User = Depends(get_current_user)):
    return model_report()


@router.post("/predict")
def prediction(
    k: int = Query(5, ge=1, le=10),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(Profile).filter_by(user_id=user.user_id).first()
    if not profile:
        raise HTTPException(422, "Complete your profile first.")
    try:
        result = predict(_profile_to_out(profile, user), k)
        result["profile_hash"] = profile_hash(_profile_to_out(profile, user))
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    db.add(Prediction(user_id=user.user_id, result=json.dumps(result)))
    db.commit()
    return result


@router.get("/history")
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(Profile).filter_by(user_id=user.user_id).first()
    current_hash = profile_hash(_profile_to_out(profile, user)) if profile else None
    version = model_report().get("version")
    reports = []
    for row in (
        db.query(Prediction)
        .filter_by(user_id=user.user_id)
        .order_by(Prediction.prediction_id.desc())
        .limit(20)
    ):
        report = json.loads(row.result)
        reports.append(
            {
                "id": row.prediction_id,
                "created_at": row.created_at,
                "report": report,
                "is_current": report.get("profile_hash") == current_hash
                and report.get("model_version") == version,
            }
        )
    return reports


@router.get("/resume-analysis")
def analysis(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    row = (
        db.query(Resume)
        .filter_by(user_id=user.user_id)
        .order_by(Resume.resume_id.desc())
        .first()
    )
    if not row:
        raise HTTPException(404, "Upload a resume to get feedback.")
    return {
        "filename": row.filename,
        **resume_analysis(
            row.extracted_text or "", json.loads(row.parsed_information or "{}")
        ),
    }
