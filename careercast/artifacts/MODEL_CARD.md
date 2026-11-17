---
license: other
license_name: upstream-license-notices
license_link: https://github.com/Deekshitha-Warrior/Infoys/blob/main/careercast/data/DATA_CARD.md#licenses-and-publication
language: en
library_name: scikit-learn
tags:
- career-exploration
- skill-gap-analysis
- ensemble
- educational-prototype
datasets:
- dyno7/career_recommender
metrics:
- accuracy
- f1
- recall
model-index:
- name: CareerCast mean ensemble
  results:
  - task:
      type: text-classification
      name: Broad career category prediction
    dataset:
      type: dyno7/career_recommender
      name: Anonymized survey subset
      split: held-out 90-profile survey split
    metrics:
    - type: accuracy
      value: 0.5333
    - type: f1
      name: Macro F1
      value: 0.3697
---

# CareerCast model card

Version: career-survey-semantic-v2. Trained: 2026-10-22T17:06:28.521968+00:00.

Intended use: career exploration for self-directed users. Not a hiring,
admissions, lending or eligibility decision system. Model class probabilities
are uncalibrated and do not measure the chance of getting a job.

Inputs: canonical technical/soft skills, degree, specialization, qualification,
certifications. Previous job title is excluded to reduce label leakage.
Experience/recency is not modeled without reliable training labels.

Three CV-tuned classifiers use TF-IDF plus curated multi-hot skills and mean
fine-tuned skill embeddings. Unknown skill vectors are zero; canonical aliases
are normalized. Core-skill alignment is a curated checklist, not an employer
requirement. Ranking: 80% mean classifier probability, 20% alignment.

Training data: 269 anonymized first-job survey records.
Held-out test: 90 records, stratified split seed 42. See
split.json for indices. TF-IDF is fit within each cross-validation fold.

Measured ranking accuracy 53.33%, macro F1
37.53%, Top-5 recall 90.00%.
Results apply only to this split, not LinkedIn or SemEval benchmarks.
Small/imbalanced self-reported data, broad hand-mapped classes, and English
inputs limit generalization. Near-duplicate or correlated survey entries may
remain despite exact-text deduplication. No external cohort validation exists.

The base MiniLM model is Apache 2.0. Fine-tuning uses licensed O*NET data;
source attribution and license copies are distributed with the artifacts.
The full encoder checkpoint can be reproduced but is excluded from Git and ZIP.
The compact vectors and classifier bundle are included for offline inference.

Acceptance details: ../MILESTONES.md. Dataset details: ../data/DATA_CARD.md.

## Bias, evaluation and release notes

The survey is self-selected, small and imbalanced: Software Developer has 138
examples while Software QA Engineer has eight. Removing names and gender does
not remove proxies in education/skills, guarantee demographic fairness, or
establish coverage across geography, language, disability or socioeconomic groups.
No demographic subgroup validation, calibrated probabilities or causal career
outcome study has been performed. English-only taxonomy matching may miss novel
skills and interdisciplinary paths. Checklists are curated rather than empirical
employer requirements. There are no live market signals or confidence intervals.

The frozen holdout has been examined in previous development. A separate fresh
external cohort is needed for independent validation. MLflow/CI adds traceability;
it does not raise the measured model quality or validate SemEval/LinkedIn claims.
Artifact distribution contains compact trained vectors, not the complete encoder.

For reproduction see ../README.md and ../docs/RELEASE.md. Code version 0.4.0 keeps
model version career-survey-semantic-v2. The API/CLI expose scores as exploration
heuristics; users should review suggestions with context and qualified guidance.
Hugging Face-style metadata is included for portability; this card is published
in GitHub, not claimed as independently reviewed or hosted on the Hub.
