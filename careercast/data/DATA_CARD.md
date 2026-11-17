---
license: other
license_name: upstream-license-notices
license_link: https://github.com/Deekshitha-Warrior/Infoys/blob/main/careercast/data/DATA_CARD.md#licenses-and-publication
language: en
task_categories:
- text-classification
size_categories:
- n<1K
tags:
- anonymized-survey
- career-exploration
- onet
---

# Data sources and scope

The O*NET® 31.0 Database by the U.S. Department of Labor, Employment and
Training Administration (USDOL/ETA) supplies the software-skill taxonomy.
Used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Source: https://www.onetcenter.org/database.html
License: https://www.onetcenter.org/license_db.html
CareerCast normalizes skill aliases and selects career categories. USDOL/ETA
has not approved, endorsed, or tested these modifications.

The public career survey is published by dyno7 under MIT metadata:
https://huggingface.co/datasets/dyno7/career_recommender
The import removes names, gender and identifiers and retains education,
skills, certifications and mapped first-job labels. Raw personal records are
not redistributed. See manifest.json for checksums and exact transformations.

This is a first-job survey, not a LinkedIn transition dataset. No specific
SemEval career benchmark was identified from the project specification.
Evaluation results must not be described as SemEval or LinkedIn results.
An independently annotated set of 200 resumes is still needed to validate
the parser precision requirement. Synthetic fixtures test behavior only.

## Sentence encoder

The all-MiniLM-L6-v2 base model by Sentence Transformers is Apache 2.0:
https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
CareerCast fine-tunes this model using O*NET descriptions and software lists.
The compact skill embedding table is derived from that fine-tuned model.
The base model's license is included at `../artifacts/LICENSE-MiniLM.txt`.

## Dataset structure and processing

The distributed career_profiles.json contains 359 records with text,
technical_skills, mapped career and source fields. Text combines selected skills,
education and certification fields; target job titles are excluded from features.
There are 10 broad curated target classes. Exact feature-text duplicates and
classes with fewer than eight rows were removed. There may still be correlated
or near-duplicate survey responses; anonymity is not a formal privacy guarantee.

The stratified seed-42 split has 269 training and 90 test records. Split indices,
source URLs and byte hashes are distributed in artifacts/split.json and manifest.json.
No user-uploaded resumes or local CareerCast accounts are part of this dataset.
No raw personal identifiers, email/URL fields, gender or survey names are included.
Education and unusual skill combinations can remain indirect identifiers; do not
attempt reidentification or combine this subset with private identity records.

The observed first job is not proof of ideal career fit or future success.
The small self-selected sample is not representative of all users, labor markets,
career transitions or demographic groups. Mechanical/civil/education/finance
labels are hand-mapped and can lose detail. Suitable use is educational pipeline
experimentation; unsuitable use includes hiring, eligibility or automated life
opportunity decisions. Unknown/unsupported careers are not evaluated as classifiers.

## Licenses and publication

The survey publisher lists MIT metadata; O*NET material is CC BY 4.0, and the
base sentence encoder is Apache 2.0. These are distinct upstream licenses, not a
new blanket license for every project component. Source attribution is preserved.
The card is available in the public GitHub source; no separate Hugging Face dataset
upload, third-party approval or independent benchmark validation is claimed.
