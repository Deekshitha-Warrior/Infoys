"""Transparent competency checklist and practice plan, independent of classifier labels."""
import csv
import io
from urllib.parse import quote
from .intelligence import CAREERS, canonical, profile_hash
from .pdf_report import PRACTICE


def gap_report(profile, career):
    if career not in CAREERS:
        raise ValueError("Choose a career from the supported career checklist.")
    skills = {canonical(s) for s in (profile.get("technical_skills") or []) + (profile.get("soft_skills") or [])}
    if not skills:
        raise ValueError("Add at least one skill to your profile first.")
    required = CAREERS[career]
    matched = [s for s in required if s in skills]
    missing = [s for s in required if s not in skills]
    actions = []
    for i, skill in enumerate(missing):
        actions.append({
            "skill": skill, "sequence": i + 1,
            "practice": PRACTICE.get(skill, f"Study the fundamentals of {skill}, complete a practical exercise, and explain the result to a peer."),
            "evidence": f"Add a portfolio example demonstrating {skill}, with a short explanation and feedback from a reviewer.",
            "resource_url": "https://www.google.com/search?q=" + quote(skill + " course tutorial"),
        })
    return {"career": career, "alignment": round(100 * len(matched) / len(required)),
        "matched_skills": matched, "missing_skills": missing, "actions": actions,
        "profile_hash": profile_hash(profile),
        "method": "Equal-weight curated core-skill checklist; sequence follows checklist order, not measured importance. Matching means listed in the profile, not independently assessed proficiency.",
        "relevance_status": "Pilot relevance has not been validated."}


def gap_csv(report):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["career", "skill", "status", "practice", "evidence", "resource_url"])
    for skill in report["matched_skills"]:
        writer.writerow([report["career"], skill, "listed in profile", "", "", ""])
    for action in report["actions"]:
        writer.writerow([report["career"], action["skill"], "to develop", action["practice"], action["evidence"], action["resource_url"]])
    return output.getvalue()

