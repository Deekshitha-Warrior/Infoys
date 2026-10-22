# Milestones 1 and 2: implementation and acceptance

Updated 22 October 2026. This report distinguishes working implementation from
the benchmark thresholds in the supplied project specification.

## Delivered implementation

| Area | Implementation |
|---|---|
| Profile ingestion | Validated education, skills, certifications, experience; authenticated CRUD |
| Resume parsing | PDF/DOCX, spaCy NER plus skill entity rules, role/education patterns, aliases, review and import |
| Baseline | Trained Logistic Regression, three-fold CV tuning, held-out report |
| Advanced models | Trained Random Forest and XGBoost, three-fold macro-F1 optimization |
| Vectorization | TF-IDF, multi-hot skills, averaged fine-tuned 384-dimensional skill embeddings |
| Ranking | Top-K with individual and ensemble confidence, 80/20 probability/alignment scoring |
| Workspace | Dashboard, career comparison, skill analysis, learning roadmap, resume feedback, profile and evaluation |
| Persistence | Account-scoped prediction history; stale profile/model detection |
| Export | Downloadable JSON profile/prediction/evaluation report |

## Public data collected

- 1195 public survey rows inspected; 359 anonymized profiles retained across 10 classes.
- 269 training and 90 held-out profiles. Exact feature duplicates removed before splitting.
- Source: [dyno7 career survey](https://huggingface.co/datasets/dyno7/career_recommender), publisher MIT metadata.
- [O*NET 31.0](https://www.onetcenter.org/database.html) software skills and occupation descriptions, CC BY 4.0.
- Sentence-BERT fine-tuned on 480 positive/negative pairs from 240 O*NET occupations. Survey validation rows are excluded from fine-tuning.
- Names, gender, raw personal identifiers, email addresses and URLs are not included in the distributed feature data.

The survey records broad first-job categories. It is not a curated longitudinal
LinkedIn career-transition dataset. No identifiable SemEval career benchmark
was specified or located. These datasets are not relabeled as those benchmarks.

## Measured validation results

| Method | Top-1 accuracy | Macro F1 | Top-5 recall |
|---|---:|---:|---:|
| Logistic Regression | 55.56% | 43.25% | 88.89% |
| Random Forest | 37.78% | 28.44% | 86.67% |
| XGBoost | 48.89% | 30.20% | 88.89% |
| Mean ensemble | 53.33% | 36.97% | 90.00% |
| Final career ranking | 53.33% | 37.53% | 90.00% |

Skill synonym evaluation: mean raw cosine similarity
**71.68%** on ten manually curated pairs;
40.00% of pairs individually reach 0.85.
Canonical aliases are also normalized explicitly, separately from this raw
embedding test. Do not count alias lookup as measured embedding quality.

## Acceptance status: not fully complete

| PDF criterion | Actual status |
|---|---|
| Parser precision at least 90% on 200 held-out resumes | Not verified: no independently annotated 200-resume corpus |
| Logistic Regression Top-1 at least 65% | 55.56%: below target |
| XGBoost ensemble macro F1 at least 80% | 36.97%: below target |
| Top-5 recall at least 90% | 90.00%: passed on this survey split |
| Mean synonym cosine at least 85% | 71.68%: below target |
| SemEval and curated LinkedIn validation | Not performed: the named data is unavailable/unidentified |

The UI and implementation workflows are delivered; **milestones 1 and 2 must
not be presented as meeting every acceptance criterion**. A larger, representative,
appropriately licensed career-transition dataset and independently annotated
resume corpus are required. The current sample is small and imbalanced, with
only eight QA profiles. More tuning on the same held-out split would not be
a valid substitute for improved data and a fresh external evaluation.

## Verification and limits

- Production frontend build: passed.
- API integration suite: authentication, validation, upload, extraction review,
  account isolation, prediction history, stale reports, semantic feature shape,
  train/test separation, invalid files, and spaCy fallback.
- Browser visual review: blocked by the local-preview browser approval gate;
  desktop/mobile CSS is implemented but not visually verified in this session.
- Resume scores are eight structural completeness checks, not vendor ATS or
  grammar scores. Live market demand, placement feeds and mock interviews are
  outside this milestone implementation.
- Experience is captured in the profile, but recency/seniority weighting is not
  trained because this survey lacks reliable longitudinal experience labels.
- Learning progress is saved per account in this browser, not synchronized
  across devices. Analyzed resume text and private data remain in the local DB.

Read `artifacts/evaluation.json`, `artifacts/embedding_evaluation.json`,
`artifacts/split.json`, and `data/manifest.json` for machine-readable evidence.
