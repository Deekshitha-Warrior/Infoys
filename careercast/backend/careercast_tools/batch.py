"""Validated batch inference with no user database or upload side effects."""
from collections import Counter
from app.schemas import ProfileBase
from app.intelligence import predict
from app.gaps import gap_report


def predict_batch(profiles, k=5):
    if not isinstance(profiles, list) or not 1 <= len(profiles) <= 1000:
        raise ValueError("Supply a JSON list containing 1 to 1000 structured profiles.")
    # Validate every row before expensive inference, avoiding partial success.
    validated = []
    for index, profile in enumerate(profiles):
        try:
            value = ProfileBase.model_validate(profile).model_dump()
            if not (value.get("technical_skills") or value.get("soft_skills")):
                raise ValueError("at least one skill is required")
            validated.append(value)
        except ValueError as exc:
            raise ValueError(f"Invalid profile at row {index + 1}: {exc}") from exc
    results = []
    for index, profile in enumerate(validated):
        report = predict(profile, k)
        report["row"] = index + 1
        report["gap_report"] = gap_report(profile, report["recommendations"][0]["career"])
        results.append(report)
    return results


def cohort_summary(results):
    if not results:
        raise ValueError("A cohort needs at least one prediction")
    careers, gaps = Counter(), Counter()
    for row in results:
        top = row["recommendations"][0]
        careers[top["career"]] += 1
        gaps.update(top["missing_skills"])
    return {"profile_count": len(results),
        "career_distribution": [{"career": career, "count": count, "percentage": round(count / len(results) * 100, 2)} for career, count in careers.most_common()],
        "common_skill_gaps": [{"skill": skill, "count": count} for skill, count in gaps.most_common(10)],
        "average_skill_alignment": round(sum(r["recommendations"][0]["alignment"] for r in results) / len(results), 2),
        "scope": "Only the cohort supplied in this request; no other accounts, profile identifiers or stored history are included. Model predictions are not ground-truth career outcomes."}
