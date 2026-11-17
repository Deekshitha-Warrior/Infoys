# Command-line reference

Install from the careercast folder with `python -m pip install .` (Python 3.14).
Use `careercast --help`, or `python -m careercast_tools --help`. Commands work
locally on your own files; they do not sign into the website or modify its DB.

Example profile JSON:

```json
{"degree": "B.Tech", "specialization": "Computer Science", "technical_skills": ["python", "sql", "git"], "soft_skills": ["communication"]}
```

| Command | Behavior |
|---|---|
| `careercast profile profile.json --output validated.json` | Validate and normalize the structured profile |
| `careercast parse resume.pdf --output parsed.json` | Parse a local PDF/DOCX; does not claim measured parser precision |
| `careercast predict profile.json --k 5 --output prediction.json` | Predict and rank careers |
| `careercast recommend profile.json --k 5 --output recommendations.json` | Recommendation alias for the same local ranking pipeline |
| `careercast gap-report profile.json --career "Backend Developer" --output gap.json` | Generate actionable competency plan |
| `careercast gap-report profile.json --career "Backend Developer" --format csv --output gap.csv` | Export gap CSV |
| `careercast export profile.json --output report.pdf` | Generate personalized PDF from current local inputs |
| `careercast batch cohort.json --output predictions.json` | Process a JSON list of 1-1,000 profiles, including gap plans |
| `careercast cohort cohort.json --output summary.json` | Aggregate career distribution and common gaps from supplied profiles |
| `careercast serve --host 127.0.0.1 --port 8000` | Start the authenticated FastAPI service |

Install the review extra with `python -m pip install ".[review]"`, then launch
`careercast review --api-url http://127.0.0.1:8000`. The installed review UI
includes comparison charts, private cohort uploads and PDF/CSV exports.

`--k` accepts 1-10. PDF export accepts optional `--career` when it is in the
returned Top-K. Existing output files are overwritten when explicitly selected.
Errors exit with code 2; successful commands exit with code 0. No credentials
are needed for local inference. Protect exported files if your inputs are private.

The installed wheel includes the trained model, compact vectors, public survey
features, model/dataset cards, and docs. It does not include a full Sentence-BERT
checkpoint, personal database, private resumes, MLflow DB or browser sessions.
Install `[review]` or `[registry]` extras for Streamlit or MLflow. The React
frontend remains a separate source-based app. Install the spaCy English model
with `python -m spacy download en_core_web_sm` for richer NER; the parser has a
rule-based fallback and does not silently claim benchmark-level accuracy.

Installed API state defaults to `~/.careercast`; source development retains
backend-local state. Set CAREERCAST_DATA_DIR for another writable runtime folder,
DATABASE_URL for a database, CORS_ORIGINS for allowed frontend origins, and a
private SECRET_KEY for a shared API. Model assets are read-only package resources.
