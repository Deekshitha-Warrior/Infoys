"""Aggregate actual opt-in skill relevance ratings. Never synthesize pilot evidence."""
import json
from app.database import SessionLocal
from app.models import GapFeedback


def main():
    with SessionLocal() as db:
        rows = db.query(GapFeedback).all()
        ratings = [rating for row in rows for rating in json.loads(row.ratings).values()]
        participants = len({row.user_id for row in rows})
    proportion = sum(ratings) / len(ratings) if ratings else None
    print(json.dumps({"participants": participants, "rated_competencies": len(ratings),
        "relevance": proportion, "target": 0.78,
        "threshold_met": proportion >= 0.78 if proportion is not None else None,
        "limitations": "Self-selected pilot feedback; report cohort size and recruitment method. No ratings means unverified, not passed."}, indent=2))


if __name__ == "__main__":
    main()
