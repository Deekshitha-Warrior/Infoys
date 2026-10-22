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
