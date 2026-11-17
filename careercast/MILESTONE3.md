# Milestone 3 - Skill Gap Analysis, API and CI Integration

## Delivered features

- Account-scoped FastAPI prediction, read-only recommendation, career checklist,
  detailed skill-gap report, CSV export, and pilot relevance feedback endpoints.
- Skill gap plans include a concrete practice activity, portfolio evidence, and
  a learning-resource search link for every missing checklist competency.
- The main React Skill Analysis and Learning Path screens display these plans.
  Optional per-competency feedback is stored per account/profile/career; repeated
  ratings update the existing report instead of multiplying votes.
- MLflow tracks metrics and artifact hashes and registers each fitted classifier
  as a versioned model. Registration does not promote a failing model.
- GitHub Actions runs API tests and the frontend build, independently recomputes
  ensemble macro F1 on the frozen holdout, requires at least 0.78, and detects
  regression against the recorded baseline. A failing gate exits nonzero.
- A separate Streamlit review prototype logs into the same FastAPI service,
  shows Plotly probability bars, and exports prediction JSON and skill CSV/PDF.
- A Dockerfile prepares the Python API for hosting; a benchmark measures local
  concurrent HTTP latency. CORS_ORIGINS configures allowed deployed frontends.

## API additions

All endpoints require `Authorization: Bearer <token>` from the existing login.
Existing `POST /api/intelligence/predict` saves prediction history; the new
`GET /api/intelligence/recommend?k=5` does not write history.

| Method and endpoint | Purpose |
|---|---|
| GET /api/intelligence/careers | Supported checklist career names |
| GET /api/intelligence/recommend?k=5 | Current profile recommendations |
| GET /api/intelligence/gap-report?career=Backend%20Developer | JSON skill/practice plan |
| GET /api/intelligence/gap-report?career=Backend%20Developer&format=csv | CSV download |
| POST /api/intelligence/gap-feedback | Optional current-profile relevance ratings |

Feedback JSON contains `career`, the current gap report's `profile_hash`, and
`ratings` such as `{ "docker": true }`. False means not relevant. Only actual
missing skills are accepted. Stale profile hashes return HTTP 409. The pilot
summary command prints aggregate counts, not participant names or emails.

## Run locally

From `careercast/backend`, using a virtual environment:

```powershell
python -m pip install -r requirements-milestone3.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In a second terminal with the same environment:

```powershell
python -m streamlit run review_app.py --server.address 127.0.0.1
```

Open http://127.0.0.1:8501 and sign in using an existing CareerCast account.
Complete the profile in the React app first. Tokens remain in the Streamlit
server session; no cached shared account reports or stored plaintext passwords.
For another API host, set CAREERCAST_API_URL before starting Streamlit.

## MLflow registry

```powershell
python -m ml.registry
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```

The default registry uses local SQLite and local MLflow artifact storage. Set
MLFLOW_TRACKING_URI (and the server's own authentication configuration) for a
shared server. Never publish the local database or MLflow artifact directory.
Three registered model names are CareerCast-logistic_regression,
CareerCast-random_forest and CareerCast-xgboost. Each run stores measured ensemble
metrics, model bundle hash, split and evaluation contract; registration results
are written to artifacts/registry_result.json. No champion alias or production
promotion is assigned automatically. Runtime inference continues using the
included vetted joblib bundle; registry registration does not swap a live model.

## CI quality gate

```powershell
python -m ml.quality_gate
```

The command reloads model weights and recomputes probabilities, rather than
trusting edited metrics in evaluation.json. It checks hashes of the frozen
feature dataset and split, plus the 0.78 minimum and recorded baseline. The
current holdout is a previously evaluated survey sample, not a new external
benchmark. Changes to the evaluation contract require review; do not change
splits or labels to pass. There is no continue-on-error on the quality gate.

The workflow runs for pushes to main and pull requests. To block merges in
GitHub, repository administrators must make `model-quality-gate` a required
status check in branch protection/rulesets. Adding a workflow alone cannot
prevent an administrator bypass or a direct push. It does not automatically
block Vercel deployments without configuring deployment checks there.

## Load and pilot evaluation

Use a dedicated synthetic test account with a saved profile. Set its access
token in CAREERCAST_BENCHMARK_TOKEN in the process environment, then run:

```powershell
python -m ml.benchmark_api --requests 120 --concurrency 5
python -m ml.pilot_report
```

The benchmark warms the model and measures prediction, recommendation, and gap
HTTP requests including auth, database reads, and prediction-history writes.
It reports per-endpoint p50/p95 and errors. Do not benchmark a real user's
account: predictions add history. Cold starts, a public host, hardware capacity,
and larger concurrency are separate tests. Pilot feedback must come from actual
participants; tests use synthetic ratings only and are not pilot evidence.

## Deployment

Build from the careercast directory with `docker build -t careercast-api .`.
Run with port 8000 exposed, a private SECRET_KEY, and explicit CORS_ORIGINS,
for example `https://careercast.vercel.app`. The API's existing DATABASE_URL
supports a persistent SQLAlchemy database (install the selected DB driver).
Use a persistent volume for the local SQLite DB and backend/uploads, or deploy
with an external database and suitable persistent file storage. Do not use an
ephemeral container filesystem for real account/resume persistence.

The frontend's VITE_API_URL must point to the hosted HTTPS API before rebuilding.
A Dockerfile is deployment preparation, not proof of a public API deployment.
No hosting account, public backend URL, or paid service was provisioned here.

## Acceptance status

- Macro F1 >=78%: enforced by CI, but currently below threshold. The gate should
  fail until an improved, genuinely evaluated model meets it.
- Skill-gap relevance >=78%: unverified until a real pilot cohort rates reports.
- API p95 <=300ms: record the measured local benchmark separately; a local test
  does not establish the same latency on a deployed service.
- Streamlit and MLflow are local prototypes/workflows; the React app remains
  the primary user workspace. Earlier milestone data limitations still apply.

## Verification recorded 17 November 2026

- Backend suite: 11 tests passed, including account isolation, optional feedback,
  stale-profile rejection, CSV export, read-only recommendations, and model gates.
- Frontend production build passed; the Skill Analysis competency cards and
  controls were reviewed in the local browser using an isolated synthetic account.
- Streamlit AppTest exercised login, chart rendering, target-career plans and
  actual PDF/CSV downloads against the local FastAPI test server.
- Concurrent HTTP benchmark: 120 requests, concurrency 5, zero errors. Per-endpoint
  p95: prediction 222.11 ms, recommendation 185.66 ms, skill-gap report 102.40 ms.
  All passed the 300 ms local warm-inference criterion in this test only.
- Model gate recomputed macro F1 0.3697, no regression against the baseline;
  the required 0.78 gate failed as expected. Evidence: artifacts/quality_gate.json.
- MLflow registered all three model versions locally; reloaded probability
  outputs matched the original classifiers. No model was promoted.
  MLflow's local DB and binary artifact store remain outside the source archive.
- No real pilot users were surveyed and no public backend was deployed.

Evidence files are in artifacts/api_benchmark.json and registry_result.json.
The registry result records this machine's local run; reproduce registration to
create the corresponding models in a different environment.

Docker CLI is unavailable on this machine, so the container recipe was not
built here. Local service and dependency verification are reported above.

The mentor-requested dashboard now displays match scores, the arithmetic for
each profile/learning/resume measure, and separate model validation results.
Three additional JavaScript tests verify learning-score arithmetic and missing
data behavior. See SCORING.md for definitions and specification traceability.
