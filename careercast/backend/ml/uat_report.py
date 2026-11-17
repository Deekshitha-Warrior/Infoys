"""Aggregate actual satisfaction ratings; one latest response per participant."""
import json
from app.database import SessionLocal
from app.models import RecommendationFeedback


def summarize(ratings):
    count = len(ratings)
    satisfied = sum(rating >= 4 for rating in ratings)
    return {"participants": count, "satisfied": satisfied,
        "satisfaction": satisfied / count if count else None,
        "target": 0.82, "target_met": satisfied / count >= .82 if count else None,
        "definition": "Latest recorded response per account; ratings 4 or 5 out of 5 count as satisfied.",
        "limitations": "Self-selected account responses; cohort recruitment and representativeness must be documented. No responses means unverified, not passed."}


def main():
    with SessionLocal() as db:
        rows = db.query(RecommendationFeedback).order_by(RecommendationFeedback.updated_at.desc(), RecommendationFeedback.feedback_id.desc()).all()
        latest = {}
        for row in rows:
            latest.setdefault(row.user_id, row.rating)
    print(json.dumps(summarize(list(latest.values())), indent=2))


if __name__ == "__main__":
    main()
