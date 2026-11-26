# Release and reproducibility guide

Version 0.4.0 packages the API/CLI and existing model weights. The React source
is distributed separately in the full-project ZIP. No private resume, DB, token,
MLflow store, virtual environment or node_modules should enter the wheel/ZIP.

1. Run backend integration/regression tests and frontend scoring tests/build.
2. Run `python -m ml.quality_gate` from backend. A current nonzero result is
   expected: the 78% macro F1 target remains unmet. Never weaken the gate to
   label a release as model-quality approved.
3. Run `python -m ml.export_docs` to regenerate the API schema/reference.
4. Build source/wheel with `python -m build` from careercast, then check metadata
   with `python -m twine check dist/*`.
5. Install the wheel into an isolated location and invoke its CLI from outside
   the source tree. Confirm model inference and public assets load from the wheel.
6. Run the cold-process 1,000-profile batch benchmark; preserve evidence/scope.
7. Publish source documentation/cards to the project repository. PyPI and
   Hugging Face uploads require separate publishing accounts and authorization.

The dataset card describes anonymized public survey fields, transformations,
class counts, splits, licenses, intended use, privacy and limitations. The model
card documents architecture, input assumptions, training/evaluation, measured
metrics, bias, exclusions and upstream notices. Neither implies external review.

The source ZIP contains the GitHub workflow as well as source docs. The workflow
runs tests, validates the wheel and records package artifacts; the separate model
quality check remains required for any claim of meeting its F1 threshold.
No deployment or model production alias is changed by package installation.

Source regeneration uses Python 3.14 and versions in backend/requirements.txt.
Model weights are untrusted-code-capable Python serialization: load only the
bundled, reviewed artifact; do not replace it with arbitrary uploaded joblib files.

CI installs the English spaCy model before parser tests. Frozen evaluation
contracts use canonical JSON hashes, preserving value/array-order integrity
without rejecting equivalent Windows/Linux line endings.

## Safe training and candidate evaluation

From backend, `python -m ml.train --semantic` writes a timestamped directory
under artifacts/candidates. It does not overwrite the active model/evaluation.
Use `--output-dir` for a new explicit candidate directory. `--promote` requires
baseline accuracy >=65%, ensemble macro F1 >=80%, ranking Top-5 recall >=90%,
embedding synonym cosine >=85%, no F1 regression and the unchanged split.
Restart the API after an approved promotion. Other external/pilot acceptance
criteria still need separate evidence; passing a model gate does not prove them.

`python -m ml.improve_model` reproduces the 32-configuration training-only CV
comparison and saves model_improvement_experiment.json without deploying a model.
The holdout was used in previous development and is not independent validation.
