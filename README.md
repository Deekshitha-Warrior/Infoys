# Infoys / CareerCast

CareerCast is the AI-powered career exploration application in
[`careercast/`](careercast/). Start with the [project guide](careercast/README.md).

## Progress through Milestones 1, 2, 3 and 4

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

### Milestone 4 - Packaging, testing and finalization

- Added a pip-installable Python library with bundled model assets and a public
  API, plus CLI commands for validation, resume parsing, predictions, gaps,
  PDF/CSV exports, batches, cohort summaries and the API/Streamlit servers.
- Expanded integration/regression coverage to 20 backend tests, including
  batch/single prediction parity, CLI output, cohort privacy and feedback.
- Added Streamlit career comparisons, uploaded-cohort distribution/skill-gap
  analytics, aggregate exports and optional recommendation-satisfaction ratings.
- Published CLI documentation, generated OpenAPI/REST reference, release guide,
  and enriched model/dataset cards with Hugging Face-style metadata.
- Built and checked wheel/source distributions, verified installed-wheel inference
  outside the source checkout, and added packaging/batch checks to GitHub Actions.

**Measured result:** the 1,000-profile structured-input CLI batch completed in
**20.741 seconds**, under four minutes on this Windows machine. The test covers
validation, feature extraction, all models, ranking, gap analysis and JSON output;
it does not benchmark parsing 1,000 resumes or deployed-host performance.
**82% user satisfaction remains unverified** without real participants. Packages
and cards are available in the source release; no PyPI/Hugging Face upload or
public-backend deployment is claimed. See the Milestone 4 guide for setup.

### Score interpretation and data limits

Career match indices are ranking heuristics; model probabilities are
uncalibrated and do not measure hiring success. Checklist matches and
self-reported learning progress are not assessed proficiency. Confidence
intervals, live market-demand scores, and trained experience-recency weighting
are not available and are not replaced with invented percentages. The test
split has been evaluated previously; it is not fresh external validation.

Further details: [Milestones 1-2 evidence](careercast/MILESTONES.md),
[Milestone 3 setup](careercast/MILESTONE3.md), and
[dashboard formulas](careercast/SCORING.md).

`careercast.zip` is the updated source distribution. It excludes personal
resume uploads, local databases, dependencies, and large training checkpoints.

## Authentication

CareerCast uses **FastAPI email/password authentication**, **bcrypt password
hashing through Passlib**, and **HS256 JWT access tokens through python-jose**.
Tokens expire after eight hours. React AuthContext manages the browser session,
and Axios sends bearer tokens to protected API endpoints. Account data is scoped
to the signed-in user through SQLAlchemy (SQLite by default).

See the [authentication details](careercast/README.md#authentication) for the
login flow, token storage, logout behavior, and current limitations.

[Milestone 4 installation, CLI and acceptance evidence](careercast/MILESTONE4.md).

## Latest verification - 26 November 2026

All four milestone implementation workflows were rechecked: 20 backend tests,
3 frontend scoring tests, the frontend build, isolated installed-wheel inference,
and Streamlit login/comparison/cohort/export checks passed. The latest cold-process
1,000-profile batch completed in 20.741 seconds. See [readiness evidence](careercast/artifacts/readiness.json).

Run the main app with `Start-CareerCast.ps1`; add `-Review` to start the Streamlit
review UI too. The launcher installs the pip package, waits for API readiness,
and uses fixed local ports 5173, 8000 and 8501. `-SkipSetup` is for an already
prepared environment; `-PythonExecutable` selects an explicit environment.

Implementation readiness is not full benchmark acceptance: baseline accuracy,
macro F1, independent parser validation and real-user feedback targets remain
unmet/unverified. The CI F1 gate is intentionally retained, not bypassed.

## Model quality follow-up - 26 November 2026

A training-only five-fold macro-F1 search compared 32 configurations of Logistic
Regression, Random Forest and XGBoost with word/character text features. The
CV-selected candidate achieved 36.67% held-out macro F1, below the current
ensemble's 36.97%; it was not deployed. The existing model and 78% CI requirement
remain unchanged. See the improvement experiment artifact for exact parameters.

Training now writes to a new candidate folder by default instead of overwriting
the running model. Explicit promotion requires all measurable model targets and
no F1 regression on the fixed split. Every candidate gets a distinct version.
The CI job now adds a clear summary/annotation showing actual F1, required F1 and
regression status, and never accepts a configured threshold below 78%.

### Model failure diagnostics

The CI quality summary now lists training/test support, predicted counts, precision, recall and F1 for every career. The downloadable `model-quality-evidence` artifact also contains a labeled confusion matrix and aggregate error counts, without profile text. The measured macro F1 remains 36.97%, below 78%; this reporting change does not claim a passing model. Software QA has only 6 training and 2 test profiles and no correct predictions in the frozen holdout. More representative, independently labeled data and renewed validation are needed before acceptance can be claimed.
