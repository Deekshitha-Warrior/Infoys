"""Evaluate full-profile semantic features without changing the live model or split.

Requires the existing locally trained sentence encoder and optional embedding deps.
Hyperparameters are selected exclusively by training-fold macro F1.
"""
import hashlib
import json
from datetime import datetime, timezone

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.svm import SVC

from app.intelligence import ROOT, ARTIFACTS
from ml.embeddings import encoder, MODEL_DIR
from ml.features import normalized
from ml.quality_gate import content_hash, required_f1
from ml.train import metrics


def main():
    contract = json.loads((ARTIFACTS / "quality_contract.json").read_text())
    for path, key in [(ROOT / "data/career_profiles.json", "dataset_sha256"),
                      (ARTIFACTS / "split.json", "split_sha256")]:
        if content_hash(path) != contract[key]:
            raise ValueError("Frozen benchmark changed")
    records = json.loads((ROOT / "data/career_profiles.json").read_text())
    split = json.loads((ARTIFACTS / "split.json").read_text())
    train, test = split["train"], split["test"]
    if set(train) & set(test) or sorted(train + test) != list(range(len(records))):
        raise ValueError("Invalid split")
    labels = sorted({row["career"] for row in records})
    y = np.array([labels.index(row["career"]) for row in records])
    # Encoder was trained on O*NET only, not this survey. No survey fitting here.
    x = encoder().encode([normalized(row["text"]) for row in records],
                         normalize_embeddings=True, show_progress_bar=False)
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    candidates = [
        ("logistic_regression", LogisticRegression(max_iter=3000, random_state=42),
         {"C": [.1, 1, 10, 100], "class_weight": [None, "balanced"]}),
        ("support_vector", SVC(probability=True, random_state=42),
         {"C": [.1, 1, 10, 100], "kernel": ["linear", "rbf"],
          "class_weight": [None, "balanced"]}),
    ]
    searches = []
    for name, model, grid in candidates:
        search = GridSearchCV(model, grid, cv=cv, scoring="f1_macro", n_jobs=2)
        search.fit(x[train], y[train])
        searches.append((name, search))
        print(f"{name}: training CV macro F1 {search.best_score_:.4f}", flush=True)
    # Select before looking at any held-out prediction.
    name, selected = max(searches, key=lambda item: item[1].best_score_)
    probabilities = selected.predict_proba(x[test])
    measured = metrics(y[test], probabilities)
    # SVC's calibrated probability argmax can differ from its decision prediction.
    # Use probability argmax consistently with the app's prediction contract.
    result = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "train_rows": len(train), "test_rows": len(test),
        "features": "Full-profile normalized embeddings from local O*NET fine-tuned MiniLM",
        "encoder_weights_sha256": hashlib.sha256((MODEL_DIR / "model.safetensors").read_bytes()).hexdigest(),
        "selection": "Five-fold training-only macro F1 across 24 configurations; one selected holdout evaluation",
        "cv_results": [{"classifier": n, "best_cv_f1_macro": round(float(s.best_score_), 4),
                        "best_parameters": s.best_params_} for n, s in searches],
        "selected_classifier": name, "selected_candidate_test": measured,
        "minimum_macro_f1": required_f1(contract),
        "target_pass": measured["f1_macro"] >= required_f1(contract), "deployed": False,
        "limitations": ["Previously evaluated small survey holdout, not fresh external validation.",
                        "No test labels used for fitting or hyperparameter selection.",
                        "Individual candidate, not the deployed three-model ensemble.",
                        "No production weights, thresholds, labels or split modified."]}
    (ARTIFACTS / "semantic_experiment.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
