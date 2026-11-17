"""Generate public API reference from the actual FastAPI schema (source checkout)."""
import json
from app.main import app
from app.intelligence import ROOT


def main():
    folder = ROOT / "docs"
    folder.mkdir(exist_ok=True)
    schema = app.openapi()
    (folder / "openapi.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")
    lines = ["# REST API reference", "", "Generated from FastAPI 0.4.0. Interactive Swagger: `/docs`; ReDoc: `/redoc`.", "", "Base URL is your running API, locally `http://127.0.0.1:8000`.", "Register/login take JSON, not OAuth form fields. Protected endpoints require", "`Authorization: Bearer <access_token>`. Tokens expire in 8 hours.", "", "| Method | Endpoint | Purpose | Authentication |", "|---|---|---|---|"]
    for path, methods in schema["paths"].items():
        for method, operation in methods.items():
            if method.upper() not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                continue
            lines.append(f"| {method.upper()} | `{path}` | {operation.get('summary', '')} | {'Bearer token' if operation.get('security') else 'Public'} |")
    lines += ["", "## Inputs and exports", "", "`POST /api/profile/me` accepts degree, specialization, institution, graduation_year,", "technical_skills and soft_skills arrays, qualification, work_experience, previous_role", "and certifications. A profile needs at least one skill for inference.", "", "`POST /api/intelligence/predict?k=5` saves account history; `GET /api/intelligence/recommend?k=5`", "returns current recommendations without saving. Both return career, confidence,", "ranking_score, alignment, matched_skills, missing_skills, model_scores and metadata.", "", "`GET /api/intelligence/gap-report?career=Software%20Developer&format=csv` downloads CSV;", "omit format for JSON. `/report.pdf` accepts `report_type=overview|careers|skills`", "and optional recommended `career`.", "", "`POST /api/intelligence/cohort` takes a `profiles` list with 1-1000 structured", "profiles and returns only aggregate distributions and gaps. It never queries", "other users or persists the uploaded cohort. Use deidentified input you may analyze.", "", "`POST /api/intelligence/recommendation-feedback` takes `profile_hash` and integer", "`rating` 1-5. Stale profile hashes return 409. `/gap-feedback` instead takes", "career, profile_hash and a map of missing skills to boolean relevance ratings.", "", "## Errors and privacy", "", "401: absent/invalid/expired token or incorrect login; 404: missing resource;", "409: duplicate account/stale feedback; 422: invalid input/missing profile.", "Resume uploads use multipart form field `file`, PDF/DOCX only, maximum 5 MB.", "Never send private access tokens in query strings. Local CLI commands do not", "need a bearer token; they process files you explicitly select.", "", "Full request/response types, constraints, parameters and status codes are in", "[openapi.json](openapi.json). Do not embed secrets in examples or publish user DBs."]
    (folder / "API.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
