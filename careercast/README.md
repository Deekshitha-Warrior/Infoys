# CareerCast

A career exploration workspace with a navy sidebar, lavender surfaces, purple
actions, profile-driven dashboards, and transparent model evaluation.

## Features

- Registration, JWT login, protected pages, and validated profile editing.
- PDF/DOCX resume upload, spaCy NER plus rules, aliases, extraction review,
  profile import, and eight transparent resume completeness checks.
- Logistic Regression, Random Forest, and XGBoost classifiers with stratified
  cross-validated hyperparameter tuning and an untouched held-out split.
- TF-IDF, multi-hot skills, and averaged fine-tuned Sentence-BERT skill vectors.
- Top-K ranking, individual model probabilities, core-skill alignment, skill
  gaps, prediction history, personalized PDF report export, and a learning roadmap.
- Evaluation page showing actual metrics, acceptance gates, and data limits.

The UI follows the supplied visual references. Placement feeds, mock interviews,
live market statistics, and ATS/grammar vendor scores are not fabricated.

## Milestone status

Milestone 1 and 2 **implementation workflows are present**, but the PDF's complete
acceptance criteria are **not all achieved**. See `MILESTONES.md` and
`artifacts/evaluation.json` for the actual results. A public first-job survey is
not a LinkedIn transition benchmark. No specific SemEval career dataset could
be identified from the specification. Parser precision still requires 200
independently annotated resumes. Do not present test fixtures as that benchmark.

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
