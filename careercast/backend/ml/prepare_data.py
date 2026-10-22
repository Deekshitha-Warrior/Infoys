"""Download public sources; retain no names, gender, or individual identifiers."""

import csv
import hashlib
import io
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path
from app.intelligence import profile_text, canonical

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
SURVEY_URL = "https://huggingface.co/datasets/dyno7/career_recommender/resolve/72b6754/career_recommender.csv"
ONET_URL = (
    "https://www.onetcenter.org/dl_files/database/db_31_0_csv/software_skills.csv"
)
OCCUPATIONS_URL = (
    "https://www.onetcenter.org/dl_files/database/db_31_0_csv/occupation_data.csv"
)


def label_for(title):
    title = title.lower().strip()
    if any(x in title for x in ["mechanical", "production engineer", "manufacturing"]):
        return "Mechanical Engineer"
    if any(x in title for x in ["civil", "site engineer", "structural engineer"]):
        return "Civil Engineer"
    if any(x in title for x in ["teacher", "teaching", "professor", "lecturer"]):
        return "Educator"
    if any(
        x in title for x in ["financial analyst", "accountant", "accounting", "finance"]
    ):
        return "Finance Analyst"
    if any(x in title for x in ["marketing", "sales executive", "digital marketing"]):
        return "Marketing Specialist"
    if any(
        x in title
        for x in ["data scientist", "machine learning", "ai engineer", "data engineer"]
    ):
        return "Data Scientist"
    if any(
        x in title
        for x in ["data analyst", "business analyst", "business intelligence"]
    ):
        return "Business Intelligence Analyst"
    if any(
        x in title
        for x in ["front end", "frontend", "web developer", "web design", "full stack"]
    ):
        return "Web Developer"
    if any(
        x in title
        for x in ["software test", "qa engineer", "quality assurance", "test engineer"]
    ):
        return "Software QA Engineer"
    if any(x in title for x in ["cyber", "security analyst", "security engineer"]):
        return "Information Security Analyst"
    if any(x in title for x in ["project manager", "product manager", "it manager"]):
        return "IT Project Manager"
    if any(
        x in title
        for x in [
            "software",
            "developer",
            "programmer",
            "system engineer",
            "systems engineer",
        ]
    ):
        return "Software Developer"
    return None


def main(raw_survey=None):
    DATA.mkdir(exist_ok=True)
    survey_bytes = (
        Path(raw_survey).read_bytes()
        if raw_survey
        else urllib.request.urlopen(SURVEY_URL, timeout=90).read()
    )
    reader = list(csv.DictReader(io.StringIO(survey_bytes.decode("utf-8-sig"))))
    records = []
    seen = set()
    for row in reader:
        values = list(row.values())
        label = label_for(values[10])
        if not label:
            continue
        # No title, name, gender, interests, or employment-status inputs.
        profile = {
            "degree": values[2],
            "specialization": values[3],
            "technical_skills": [
                canonical(s) for s in re.split(r"[;,]", values[5]) if s.strip()
            ],
            "certifications": values[8],
        }
        text = re.sub(r"\s+", " ", profile_text(profile)).strip().lower()
        text = re.sub(r"[\w.+-]+@[\w.-]+\.[a-z]+|https?://\S+", "", text)
        key = hashlib.sha256(text.encode()).hexdigest()
        if len(text) < 12 or key in seen:
            continue
        seen.add(key)
        records.append(
            {
                "text": text,
                "technical_skills": profile["technical_skills"],
                "career": label,
                "source": "public_self_reported_first_job_survey",
            }
        )
    counts = Counter(r["career"] for r in records)
    records = [r for r in records if counts[r["career"]] >= 8]
    (DATA / "career_profiles.json").write_text(
        json.dumps(records, indent=2), encoding="utf-8"
    )
    onet_path = DATA / "onet_software_skills.csv"
    if not onet_path.exists():
        onet_path.write_bytes(urllib.request.urlopen(ONET_URL, timeout=90).read())
    occupations_path = DATA / "onet_occupations.csv"
    if not occupations_path.exists():
        occupations_path.write_bytes(
            urllib.request.urlopen(OCCUPATIONS_URL, timeout=90).read()
        )
    manifest = {
        "survey": {
            "url": SURVEY_URL,
            "license": "MIT (publisher metadata)",
            "sha256": hashlib.sha256(survey_bytes).hexdigest(),
            "raw_rows": len(reader),
            "retained_rows": len(records),
            "class_counts": dict(Counter(r["career"] for r in records)),
            "transformation": "Removed names, gender, interests and identifiers; mapped first job titles to broad categories; deduplicated feature text; removed categories with fewer than 8 rows.",
        },
        "onet": {
            "url": ONET_URL,
            "version": "31.0",
            "license": "CC BY 4.0",
            "sha256": hashlib.sha256(onet_path.read_bytes()).hexdigest(),
        },
        "limitations": [
            "Self-reported first-job survey, not longitudinal LinkedIn transitions.",
            "Small, imbalanced sample; broad label mappings are curated.",
            "No identified SemEval career benchmark; no claim of SemEval validation.",
        ],
    }
    manifest["onet_occupations"] = {
        "url": OCCUPATIONS_URL,
        "version": "31.0",
        "license": "CC BY 4.0",
        "sha256": hashlib.sha256(occupations_path.read_bytes()).hexdigest(),
    }
    (DATA / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest["survey"]["class_counts"], indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-survey")
    main(parser.parse_args().raw_survey)
