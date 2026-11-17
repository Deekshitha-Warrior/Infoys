# REST API reference

Generated from FastAPI 0.4.0. Interactive Swagger: `/docs`; ReDoc: `/redoc`.

Base URL is your running API, locally `http://127.0.0.1:8000`.
Register/login take JSON, not OAuth form fields. Protected endpoints require
`Authorization: Bearer <access_token>`. Tokens expire in 8 hours.

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| POST | `/api/auth/register` | Register | Public |
| POST | `/api/auth/login` | Login | Public |
| PUT | `/api/auth/me` | Update My Name | Bearer token |
| GET | `/api/profile/me` | Get My Profile | Bearer token |
| PUT | `/api/profile/me` | Update Profile | Bearer token |
| POST | `/api/profile/me` | Create Or Update Profile | Bearer token |
| POST | `/api/resume/upload` | Upload Resume | Bearer token |
| GET | `/api/resume/latest` | Get Latest Resume | Bearer token |
| GET | `/api/resume/all` | List Resumes | Bearer token |
| POST | `/api/resume/{resume_id}/apply` | Apply Parsed To Profile | Bearer token |
| GET | `/api/intelligence/report.pdf` | Export Pdf | Bearer token |
| GET | `/api/intelligence/models` | Models | Bearer token |
| POST | `/api/intelligence/predict` | Prediction | Bearer token |
| GET | `/api/intelligence/history` | History | Bearer token |
| GET | `/api/intelligence/resume-analysis` | Analysis | Bearer token |
| GET | `/api/intelligence/careers` | Careers | Bearer token |
| GET | `/api/intelligence/recommend` | Recommendations | Bearer token |
| GET | `/api/intelligence/gap-report` | Gaps | Bearer token |
| POST | `/api/intelligence/gap-feedback` | Feedback | Bearer token |
| POST | `/api/intelligence/cohort` | Cohort | Bearer token |
| POST | `/api/intelligence/recommendation-feedback` | Feedback | Bearer token |
| GET | `/` | Root | Public |
| GET | `/health` | Health | Public |

## Inputs and exports

`POST /api/profile/me` accepts degree, specialization, institution, graduation_year,
technical_skills and soft_skills arrays, qualification, work_experience, previous_role
and certifications. A profile needs at least one skill for inference.

`POST /api/intelligence/predict?k=5` saves account history; `GET /api/intelligence/recommend?k=5`
returns current recommendations without saving. Both return career, confidence,
ranking_score, alignment, matched_skills, missing_skills, model_scores and metadata.

`GET /api/intelligence/gap-report?career=Software%20Developer&format=csv` downloads CSV;
omit format for JSON. `/report.pdf` accepts `report_type=overview|careers|skills`
and optional recommended `career`.

`POST /api/intelligence/cohort` takes a `profiles` list with 1-1000 structured
profiles and returns only aggregate distributions and gaps. It never queries
other users or persists the uploaded cohort. Use deidentified input you may analyze.

`POST /api/intelligence/recommendation-feedback` takes `profile_hash` and integer
`rating` 1-5. Stale profile hashes return 409. `/gap-feedback` instead takes
career, profile_hash and a map of missing skills to boolean relevance ratings.

## Errors and privacy

401: absent/invalid/expired token or incorrect login; 404: missing resource;
409: duplicate account/stale feedback; 422: invalid input/missing profile.
Resume uploads use multipart form field `file`, PDF/DOCX only, maximum 5 MB.
Never send private access tokens in query strings. Local CLI commands do not
need a bearer token; they process files you explicitly select.

Full request/response types, constraints, parameters and status codes are in
[openapi.json](openapi.json). Do not embed secrets in examples or publish user DBs.
