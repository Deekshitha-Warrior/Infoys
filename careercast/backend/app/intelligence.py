"""Reproducible career inference. Model probabilities are not hiring probabilities."""

import json
import re
import hashlib
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts"
ALIASES = {
    "js": "javascript",
    "reactjs": "react",
    "react.js": "react",
    "nodejs": "node.js",
    "node": "node.js",
    "py": "python",
    "postgres": "postgresql",
    "sklearn": "scikit-learn",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "amazon web services": "aws",
    "gcp": "google cloud",
    "k8s": "kubernetes",
    "cplusplus": "c++",
}
CAREERS = {
    "Mechanical Engineer": [
        "autocad",
        "solidworks",
        "matlab",
        "mechanical design",
        "manufacturing",
        "problem solving",
    ],
    "Civil Engineer": [
        "autocad",
        "structural analysis",
        "project management",
        "excel",
        "civil engineering",
        "communication",
    ],
    "Educator": [
        "teaching",
        "communication",
        "research",
        "presentation",
        "leadership",
        "curriculum design",
    ],
    "Finance Analyst": [
        "excel",
        "accounting",
        "financial analysis",
        "sql",
        "statistics",
        "communication",
    ],
    "Marketing Specialist": [
        "digital marketing",
        "communication",
        "seo",
        "excel",
        "data analysis",
        "content creation",
    ],
    "Software Developer": ["python", "java", "javascript", "git", "sql", "rest api"],
    "Data Scientist": [
        "python",
        "sql",
        "machine learning",
        "pandas",
        "statistics",
        "scikit-learn",
    ],
    "Web Developer": ["javascript", "html", "css", "react", "node.js", "git"],
    "Database Administrator": [
        "sql",
        "postgresql",
        "mysql",
        "linux",
        "database design",
        "python",
    ],
    "Information Security Analyst": [
        "linux",
        "network security",
        "python",
        "cybersecurity",
        "firewalls",
        "cryptography",
    ],
    "Computer Systems Analyst": [
        "sql",
        "systems analysis",
        "business analysis",
        "communication",
        "python",
        "agile",
    ],
    "Network Administrator": [
        "linux",
        "networking",
        "tcp/ip",
        "network security",
        "powershell",
        "azure",
    ],
    "Software QA Engineer": [
        "python",
        "selenium",
        "testing",
        "sql",
        "git",
        "javascript",
    ],
    "IT Project Manager": [
        "agile",
        "scrum",
        "project management",
        "communication",
        "leadership",
        "jira",
    ],
    "Business Intelligence Analyst": [
        "sql",
        "tableau",
        "power bi",
        "excel",
        "python",
        "data analysis",
    ],
    "Backend Developer": [
        "python",
        "java",
        "rest api",
        "sql",
        "docker",
        "git",
    ],
    "Frontend Developer": [
        "javascript",
        "html",
        "css",
        "react",
        "accessibility",
        "git",
    ],
    "Mobile App Developer": [
        "kotlin",
        "swift",
        "react native",
        "mobile development",
        "rest api",
        "git",
    ],
    "Cloud Engineer": [
        "aws",
        "azure",
        "google cloud",
        "linux",
        "docker",
        "networking",
    ],
    "DevOps Engineer": [
        "linux",
        "docker",
        "kubernetes",
        "ci/cd",
        "python",
        "aws",
    ],
    "Machine Learning Engineer": [
        "python",
        "machine learning",
        "scikit-learn",
        "tensorflow",
        "pandas",
        "docker",
    ],
    "Data Analyst": [
        "sql",
        "excel",
        "data analysis",
        "statistics",
        "tableau",
        "python",
    ],
    "UX Designer": [
        "figma",
        "user research",
        "wireframing",
        "prototyping",
        "usability testing",
        "communication",
    ],
    "Product Manager": [
        "product strategy",
        "roadmapping",
        "user research",
        "agile",
        "communication",
        "data analysis",
    ],
    "Business Analyst": [
        "business analysis",
        "requirements gathering",
        "sql",
        "excel",
        "communication",
        "data analysis",
    ],
    "Accountant": [
        "accounting",
        "bookkeeping",
        "financial reporting",
        "excel",
        "tax preparation",
        "attention to detail",
    ],
    "Human Resources Specialist": [
        "recruiting",
        "employee relations",
        "human resources",
        "communication",
        "organization",
        "conflict resolution",
    ],
    "Sales Representative": [
        "sales",
        "negotiation",
        "communication",
        "customer relationship management",
        "presentation",
        "customer service",
    ],
    "Graphic Designer": [
        "adobe photoshop",
        "adobe illustrator",
        "graphic design",
        "typography",
        "figma",
        "creativity",
    ],
    "Operations Analyst": [
        "process improvement",
        "excel",
        "sql",
        "data analysis",
        "project management",
        "problem solving",
    ],
}


def canonical(skill):
    value = re.sub(r"\s+", " ", skill.strip().lower())
    return ALIASES.get(value, value)


def profile_text(profile):
    skills = [
        canonical(s)
        for s in (profile.get("technical_skills") or [])
        + (profile.get("soft_skills") or [])
    ]
    # Exclude target titles from training and inference to avoid label leakage.
    return " ".join(
        skills
        + [
            profile.get(k) or ""
            for k in ("degree", "specialization", "qualification", "certifications")
        ]
    )


def profile_hash(profile):
    return hashlib.sha256(profile_text(profile).encode()).hexdigest()


@lru_cache(maxsize=1)
def load_bundle():
    import joblib

    path = ARTIFACTS / "career_models.joblib"
    return joblib.load(path) if path.exists() else None


def model_report():
    path = ARTIFACTS / "evaluation.json"
    return (
        json.loads(path.read_text(encoding="utf-8"))
        if path.exists()
        else {
            "status": "not_trained",
            "models": {},
            "limitations": ["Run python -m ml.train from backend first."],
        }
    )


def predict(profile, k=5):
    import numpy as np

    bundle = load_bundle()
    if bundle is None:
        raise ValueError(
            "Career models are not trained yet. Run python -m ml.train in backend."
        )
    text = profile_text(profile)
    skills = {
        canonical(s)
        for s in (profile.get("technical_skills") or [])
        + (profile.get("soft_skills") or [])
    }
    if not skills:
        raise ValueError(
            "Add at least one skill to your profile before predicting careers."
        )
    x = bundle["vectorizer"].transform([text])
    probabilities = {
        name: model.predict_proba(x)[0] for name, model in bundle["models"].items()
    }
    ensemble = np.mean(list(probabilities.values()), axis=0)
    labels = bundle["labels"]
    ranked = []
    for index, label in enumerate(labels):
        required = CAREERS.get(label, [])
        matched = [s for s in required if s in skills]
        missing = [s for s in required if s not in skills]
        alignment = len(matched) / max(len(required), 1)
        confidence = float(ensemble[index])
        ranked.append(
            {
                "career": label,
                "confidence": round(confidence * 100, 1),
                "alignment": round(alignment * 100),
                "ranking_score": round((0.8 * confidence + 0.2 * alignment) * 100, 1),
                "matched_skills": matched,
                "missing_skills": missing,
                "model_scores": {
                    n: round(float(p[index]) * 100, 1) for n, p in probabilities.items()
                },
            }
        )
    ranked.sort(key=lambda r: r["ranking_score"], reverse=True)
    ranked_labels = {row["career"] for row in ranked}
    skill_careers = ranked + [
        {
            "career": label,
            "alignment": round(
                sum(skill in skills for skill in required)
                / max(len(required), 1)
                * 100
            ),
            "matched_skills": [skill for skill in required if skill in skills],
            "missing_skills": [skill for skill in required if skill not in skills],
        }
        for label, required in CAREERS.items()
        if label not in ranked_labels
    ]
    known = set(bundle["vectorizer"].vocabulary_)
    covered = [s for s in skills if any(t in known for t in s.split())]
    return {
        "recommendations": ranked[:k],
        "skill_careers": skill_careers,
        "skill_count": len(skills),
        "coverage": round(len(covered) / len(skills) * 100),
        "unrecognized_skills": sorted(skills - set(covered)),
        "model_version": bundle["version"],
        "method": "Mean LR/RF/XGBoost probability (80%) + curated skill alignment (20%). No live market signals.",
        "data_scope": bundle["data_scope"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def resume_analysis(text, parsed):
    """Transparent structural checks, not an ATS vendor or grammar model score."""
    lower = text.lower()
    checks = [
        (
            "contact",
            bool(re.search(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}", lower)),
            "Add a contact email address.",
        ),
        (
            "education",
            bool(parsed.get("education")),
            "Include your degree and institution.",
        ),
        (
            "skills",
            len(parsed.get("technical_skills", [])) >= 4,
            "List at least four relevant technical skills.",
        ),
        (
            "experience",
            bool(parsed.get("experience") or parsed.get("job_roles")),
            "Describe internships, work experience, or relevant roles.",
        ),
        (
            "projects",
            "project" in lower,
            "Add practical projects and describe your contribution.",
        ),
        (
            "impact",
            bool(re.search(r"\d+\s*(%|percent|users|customers)", lower)),
            "Quantify your impact with measurable outcomes.",
        ),
        (
            "portfolio",
            any(s in lower for s in ["github.com", "linkedin.com", "portfolio"]),
            "Include a GitHub, LinkedIn, or portfolio link.",
        ),
        (
            "summary",
            any(s in lower for s in ["summary", "objective", "about me"]),
            "Add a concise professional summary.",
        ),
    ]
    return {
        "score": round(sum(ok for _, ok, _ in checks) / len(checks) * 100),
        "checks": [{"name": n, "passed": ok} for n, ok, _ in checks],
        "suggestions": [tip for _, ok, tip in checks if not ok],
        "word_count": len(text.split()),
        "method": "Eight equally weighted resume completeness checks. Not an ATS or grammar score.",
    }
