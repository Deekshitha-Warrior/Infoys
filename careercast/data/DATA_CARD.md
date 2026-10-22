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
