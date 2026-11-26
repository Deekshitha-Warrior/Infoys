# Milestone 4 - Packaging, Testing and Finalization

## Delivered implementation

- pip-installable `careercast-intelligence` 0.4.0 source distribution and wheel
  configuration, including compact trained models and public metadata/assets.
- Public Python API and `careercast` CLI commands for profile validation, resume
  parsing, prediction/recommendation, gaps, PDF/CSV export, batch inference,
  cohort summaries and starting the authenticated REST service.
- Regression tests for batch/single-profile parity, validation, CLI output,
  account isolation, cohort privacy, and feedback alongside previous API tests.
- Streamlit side-by-side career comparisons, cohort distribution/gap analytics,
  aggregate downloads, existing PDF exports and optional relevance satisfaction.
- OpenAPI schema, endpoint and CLI references, release/testing documentation,
  and model/dataset cards with Hugging Face-style metadata.
- A cold-process 1,000-profile CLI benchmark and an actual-user satisfaction
  report workflow. Source and wheel acceptance evidence is recorded separately.

## Install and run

From this careercast directory, in Python 3.14:

```powershell
python -m pip install .
careercast --help
careercast serve
```

For the source review app and registry:

```powershell
python -m pip install ".[review,registry]"
cd backend
python -m streamlit run review_app.py
```

The main React frontend still runs from frontend with `npm ci` and `npm run dev`.
The Streamlit prototype uses the configured CAREERCAST_API_URL and the same
CareerCast account/profile. Local CLI commands run on explicit input files and
do not access other accounts or website history.

For distributions and checks:

```powershell
python -m pip install ".[dev]"
python -m build
python -m twine check dist/*
cd backend
python -m pytest -q
python -m ml.benchmark_batch
python -m ml.uat_report
```

See docs/CLI.md, docs/API.md and docs/RELEASE.md for details. Package extras are
optional; core inference does not need MLflow, Streamlit, or a full transformer.
Installed model assets are read-only; writable account state lives separately.

## Acceptance limits

- A successful local pip/wheel installation is not a publication to PyPI.
- The batch test uses 1,000 synthetic structured profiles for throughput. It
  includes file ingestion, validation, feature extraction, models, ranking,
  gap plans and JSON write; it does not measure parsing 1,000 resume documents.
- Satisfaction is measured only from actual optional account feedback. Ratings
  4 or 5 out of 5 count as satisfied, using one latest response per account.
  Zero responses means unverified, not 0% satisfaction or a passed 82% target.
- GitHub publication of docs/cards is not publication or endorsement on the
  Hugging Face Hub. Mixed upstream licenses and source limitations are retained.
- Prior model/parser accuracy targets and real cohort validation remain unmet
  or unverified; no trained weights or benchmark labels were altered here.
- No public backend, package-index upload, or paid service is provisioned by
  these source changes.

## Verification (latest rerun: 26 November 2026)

- Backend integration/regression suite: 16 tests passed.
- Existing frontend scoring checks: 3 tests; unchanged React production UI.
- Batch CLI: 1,000 synthetic structured profiles completed in 20.741 seconds,
  including a cold Python process and JSON output. Four-minute local target passed.
- Wheel and source metadata checks passed with twine. The wheel was installed
  to an isolated target and exercised outside the source tree; API, CLI, model
  assets, public dataset and API docs loaded successfully from that installation.
- Streamlit AppTest passed login, career comparison, probability charts, personalized
  PDF/CSV export and cohort analytics against a dedicated local synthetic API.
  Its upload widget value was supplied by the test; actual cohort HTTP validation
  and aggregation still executed on the API. This is test evidence, not pilot feedback.
- No real-user UAT responses exist in this evaluation: 82% satisfaction is unverified.
- Prior quality gate remains below 78% macro F1; no benchmark thresholds were relaxed.

See artifacts/batch_benchmark.json for exact measurement scope. CI now builds and
checks distributions and runs the batch benchmark in addition to prior tests.
The produced wheel is a local distribution; no package-index upload was performed.

The Desktop launcher now supports `-Review` and waits for the API before starting
the frontend. Its normal setup installs the project package (and review extra
when requested), making the command-line entry point available as well.
