# CareerCast

A career exploration workspace with a navy sidebar, lavender surfaces, purple
actions, profile-driven dashboards, and transparent model evaluation.

## Features

- Registration, JWT login, protected pages, and validated profile editing.
- PDF/DOCX resume upload, spaCy NER plus rules, aliases, extraction review,
  profile import, and eight transparent resume completeness checks.
- Logistic Regression, Random Forest, and XGBoost classifiers with stratified
  cross-validated hyperparameter tuning and a separate held-out split.
- TF-IDF, multi-hot skills, and averaged fine-tuned Sentence-BERT skill vectors.
- Top-K ranking, individual model probabilities, core-skill alignment, skill
  gaps, prediction history, personalized PDF report export, and a learning roadmap.
- Evaluation page showing actual metrics, acceptance gates, and data limits.

The UI follows the supplied visual references. Placement feeds, mock interviews,
live market statistics, and ATS/grammar vendor scores are not fabricated.

## Authentication

CareerCast uses email/password authentication built with **FastAPI**, **JWT**,
and **bcrypt**.

| Component | Technology and behavior |
|---|---|
| Registration and login | FastAPI JSON endpoints: `POST /api/auth/register` and `POST /api/auth/login` |
| Password storage | Passlib with bcrypt hashes; plaintext passwords are not stored |
| Access tokens | `python-jose` signs JWTs with HS256; tokens expire after 8 hours and identify the user through the `sub` claim |
| Protected API requests | FastAPI `OAuth2PasswordBearer` extracts `Authorization: Bearer <token>`; the backend verifies the token and loads its user from the database |
| Account data | SQLAlchemy with SQLite by default; profiles, resumes, and prediction history are scoped to the authenticated account |
| Frontend session | React AuthContext stores the token as `cc_token` and user details as `cc_user` in browser localStorage; an Axios interceptor attaches the token |
| Protected pages and logout | React protected routes require a signed-in user; logout clears the local session; API 401 responses clear it and redirect to login |

Registration rejects duplicate email addresses. Login checks the supplied
password against the stored bcrypt hash before issuing a token. Both successful
registration and login return an access token and basic user details.

The current implementation uses bearer tokens in localStorage, rather than
HttpOnly cookies. Logout removes the browser's token; it does not revoke an
already issued token on the server. There is no refresh-token flow, email
verification, password-reset flow, social login, or multi-factor authentication.
Set a strong private `SECRET_KEY` in the backend process environment before a
shared deployment; the source includes a development fallback key.

Implementation: `backend/app/auth.py`, `backend/app/routers/auth.py`,
`frontend/src/context/AuthContext.jsx`, and `frontend/src/api.js`.

## Dashboard score explanations

The dashboard now shows career match indices, individual model probabilities,
skill match/gap ratios, learning-task completion, roadmap coverage, profile and
resume completeness, and model validation results, with formulas.
See [score definitions and PDF traceability](SCORING.md).

## Progress through Milestones 1, 2 and 3

The implementation below is delivered. **Feature completion and benchmark
acceptance are different:** several model/data targets are still unmet.

### Milestone 1 - Profile ingestion, resume parsing and baseline prediction

- Built validated profile forms for education, technical/soft skills,
  certifications, and work experience.
- Added account registration/login, protected pages, and account-scoped data.
- Implemented PDF/DOCX resume upload and spaCy NER with skill/role/education
  rules, alias normalization, extraction review, and confirmed profile import.
- Added eight structural resume completeness checks and improvement suggestions.
- Trained Logistic Regression with cross-validated parameter tuning; saved the
  trained model and connected it to career prediction.
- Added prediction reports, vocabulary coverage, and persisted prediction history.

**Results:** 359 anonymized public survey profiles, 269 training profiles and
90 held-out profiles across 10 career categories. Logistic Regression accuracy
is **55.56%**, below the required 65%. An additional 48-configuration tuning
experiment scored 52.22% on the same holdout, so it did not replace the better
baseline. Parser precision on 200 independently annotated resumes is unverified.

### Milestone 2 - Advanced ML, semantic features and recommendations

- Added Random Forest and XGBoost with cross-validated hyperparameter tuning.
- Combined TF-IDF, canonical multi-hot skills, and fine-tuned Sentence-BERT skill
  embeddings. Fine-tuning used 480 pairs from 240 O*NET occupation descriptions.
- Implemented Top-K ranking using 80% mean classifier probability and 20% curated
  skill alignment, with individual model scores, matching and missing skills.
- Added Career Intelligence, Skill Analysis, a learning roadmap with device-local
  progress, and 10 Google courses plus 10 certificate/certification pathways.
- Added separate personalized Career Intelligence and Skill Analysis PDF reports,
  model evaluation, and stale-profile/model detection for saved reports.
- Standardized dashboard, authentication pages, and workspace UI in navy/violet.

| Model or ranking | Accuracy | Macro F1 | Top-5 recall |
|---|---:|---:|---:|
| Logistic Regression | 55.56% | 43.25% | 88.89% |
| Random Forest | 37.78% | 28.44% | 86.67% |
| XGBoost | 48.89% | 30.20% | 88.89% |
| Mean ensemble | 53.33% | 36.97% | 90.00% |
| Final career ranking | 53.33% | 37.53% | 90.00% |

**Acceptance:** Top-5 recall reaches 90% on this survey split. Ensemble macro F1
remains below the 80% Milestone 2 target. Mean synonym cosine similarity is
71.68%, below 85%. No SemEval or curated LinkedIn transition validation was
performed; the collected survey is not presented as either benchmark.

### Milestone 3 - Skill gaps, APIs, registry, CI and review UI

- Added authenticated read-only recommendations, supported-career queries,
  detailed skill-gap reports, and CSV downloads alongside the prediction API.
- Added actionable practice activities, portfolio evidence suggestions, and
  resource links to Skill Analysis and Learning Path.
- Added optional per-skill relevance feedback with account isolation and
  stale-profile checks, plus an aggregate pilot-report command.
- Configured MLflow experiment tracking and versioned registration of all three
  classifiers. Registered models were reloaded and their probability outputs
  matched the original models. No failing model was promoted.
- Added GitHub Actions for API tests, frontend scoring tests/build, and an
  independently recomputed macro F1 gate of at least 78%, with regression checks.
- Built a Streamlit review prototype using authenticated FastAPI requests,
  Plotly career probability charts, and JSON/CSV/PDF downloads.
- Added a Docker deployment recipe and configurable backend CORS origins.
- Added dashboard match indices, confidence, skill match/gap, learning progress,
  roadmap coverage, profile/resume completeness, vocabulary coverage, and model
  validation metrics, with visible formulas and honest unavailable states.

**Verification:** 11 backend tests and 3 JavaScript scoring tests passed; the
production frontend build passed. Streamlit login, charts, plans and exports
were checked against an isolated test API. A local HTTP test of 120 requests
at concurrency 5 had zero errors, with p95 latencies of **222.11 ms prediction,
185.66 ms recommendation, and 102.40 ms gap report**. These pass 300 ms locally
with a warm model, not a public-host performance guarantee.

**Remaining acceptance:** the 78% CI macro F1 gate correctly fails at the current
36.97%. GitHub administrators must require the status check to enforce merge
blocking. Real pilot skill-gap relevance of at least 78% is unverified. No
public backend was provisioned; the Docker recipe was not built here because
Docker CLI was unavailable. Frontend deployment alone does not host the API.

### Score interpretation and data limits

Career match indices are ranking heuristics; model probabilities are
uncalibrated and do not measure hiring success. Checklist matches and
self-reported learning progress are not assessed proficiency. Confidence
intervals, live market-demand scores, and trained experience-recency weighting
are not available and are not replaced with invented percentages. The test
split has been evaluated previously; it is not fresh external validation.

Detailed evidence: [Milestones 1-2](MILESTONES.md),
[Milestone 3 setup](MILESTONE3.md), [dashboard formulas](SCORING.md), and
[measured model evaluation](artifacts/evaluation.json).

## Run on Windows

Tested with Python 3.14 and Node.js 26. Use the exact ML versions in
`backend/requirements.txt` when loading the included model bundle.

From the project directory:

```powershell
.\Start-CareerCast.ps1
```

The script creates a local virtual environment, installs dependencies, downloads
the spaCy English model, and starts both services. Use the local URL Vite prints.
The backend listens on `http://127.0.0.1:8000`. Ports 5173 and 5174 are allowed
for local frontend development. Stop the script with Ctrl+C.

Alternatively use two terminals:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m spacy download en_core_web_sm
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

The included classifier contains the compact skill embedding table. Normal
inference does not download a transformer or require torch. The full fine-tuned
encoder is a training artifact excluded from Git and the source ZIP; it can be
recreated with the commands below.

## Use the workspace

1. Create an account and complete My Profile. Press Enter to add each skill tag.
2. Optionally upload a resume, review extracted fields, and save confirmed data.
3. Choose **Analyze my profile** on Dashboard or Career Intelligence.
4. Compare paths, open Skill Analysis, and choose a target career.
5. Use Learning Path to open resources and mark progress on this device.
6. After changing profile inputs, generate a fresh analysis. Stale reports stay
   in account-scoped history but are not displayed as current recommendations.
7. Open Model Evaluation before interpreting confidence or acceptance status.

## Reproduce data and training

Run from `backend` after installing training dependencies:

```powershell
python -m pip install -r requirements-training.txt
python -m ml.prepare_data
python -m ml.embeddings
python -m ml.train --semantic
```

`prepare_data` downloads a version-pinned public survey, removes names, gender,
URLs and email addresses, maps first-job labels to broad career categories,
deduplicates feature text, and records hashes. O*NET software skills and
occupational descriptions supply the embedding fine-tuning corpus. Read
`../data/DATA_CARD.md` and `../data/manifest.json` for provenance.

Fine-tuning uses 240 O*NET descriptions and 480 positive/negative pairs, separate
from the survey validation set. Compact 384-dimensional embeddings are exported
for the curated skill vocabulary; inference averages known skill vectors. New
unknown skills are reported through vocabulary coverage. This is not an
unrestricted semantic encoder for arbitrary unseen resume text.

The classifier split is stratified 75/25 with seed 42; TF-IDF is fitted inside
every CV fold. Hyperparameters use three-fold macro-F1 optimization. Reports
include accuracy, macro precision/recall/F1, and Top-5 recall. The ranking is
80% mean model probability and 20% curated skill alignment. Probabilities are
uncalibrated and are not probabilities of hiring success.

## Tests

```powershell
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest -q
cd ../frontend
npm run build
```

Tests use a fresh in-memory database and synthetic documents. They cover auth,
profile validation, predictions, account isolation, stale history detection,
resume upload/review, corrupt and oversized files, and spaCy fallback behavior.

To evaluate a real independently annotated parser corpus:

```powershell
python -m ml.evaluate_parser path/to/gold_resumes.json --output parser_report.json
```

The expected annotation schema is documented in that module. At least 200
independent resumes and 90% measured precision are required for its gate.

## API

Interactive API docs: `http://127.0.0.1:8000/docs`.

| Endpoint | Purpose |
|---|---|
| `POST /api/auth/register`, `/api/auth/login` | Account and JWT session |
| `GET/POST/PUT /api/profile/me` | Validated profile |
| `POST /api/resume/upload` | Parse PDF/DOCX, maximum 5 MB |
| `GET /api/resume/latest`, `/api/resume/all` | Account resume history |
| `POST /api/resume/{id}/apply` | Apply confirmed data |
| `POST /api/intelligence/predict?k=5` | Predict and save Top-K ranking |
| `GET /api/intelligence/history` | Last 20 account-scoped reports |
| `GET /api/intelligence/models` | Measured evaluation and acceptance gates |
| `GET /api/intelligence/resume-analysis` | Latest resume structural checks |

SQLite creates `users`, `profiles`, `resumes`, and `predictions`. Set
`DATABASE_URL` to configure another SQLAlchemy database (install its driver).
Set `SECRET_KEY` in the server environment before any shared deployment.
Set `VITE_API_URL` when the frontend uses a different API origin.
Local databases, uploaded resumes, environments, caches, and dependencies are
excluded from Git and the source archive.

## Data and model notices

- O*NET 31.0, USDOL/ETA, CC BY 4.0; transformed for skill intelligence.
  https://www.onetcenter.org/license_db.html
- dyno7 career_recommender, publisher MIT metadata, anonymized feature subset.
  https://huggingface.co/datasets/dyno7/career_recommender
- sentence-transformers/all-MiniLM-L6-v2, Apache 2.0; fine-tuned on O*NET.
  https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

No source organization endorses CareerCast or its recommendations.

## Deploy the frontend on Vercel

Set Root Directory to `careercast/frontend`, Framework Preset to **Vite**,
Install Command to `npm ci`, Build Command to `npm run build`, and Output
Directory to `dist`. Redeploy after changing these settings. The included
frontend `vercel.json` handles React Router deep links such as `/login`.
The repository-root `vercel.json` also supports leaving Root Directory at the
repository root. Production HTML should reference `/assets/`, not `/src/main.jsx`.

Set `VITE_API_URL` to your deployed FastAPI backend's public HTTPS address before
building. The default `http://localhost:8000` only works on your computer.
Deploying this frontend does not start the Python backend. The current backend
CORS list allows local origins only; include `https://careercast.vercel.app`
when deploying the backend. Use a private `SECRET_KEY`, a persistent database,
and persistent storage for uploaded resumes on that backend.
