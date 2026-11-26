"""Training-only CV search; evaluates one selected candidate without touching production."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from xgboost import XGBClassifier
from app.intelligence import ROOT, ARTIFACTS
from ml.features import normalized
from ml.train import metrics
from ml.quality_gate import content_hash


def main():
    records = json.loads((ROOT / "data/career_profiles.json").read_text())
    split = json.loads((ARTIFACTS / "split.json").read_text())
    labels = sorted({r["career"] for r in records})
    y = np.array([labels.index(r["career"]) for r in records])
    texts = np.array([normalized(r["text"]) for r in records])
    train, test = split["train"], split["test"]
    contract = json.loads((ARTIFACTS / "quality_contract.json").read_text())
    if content_hash(ROOT / "data/career_profiles.json") != contract["dataset_sha256"] or content_hash(ARTIFACTS / "split.json") != contract["split_sha256"]:
        raise ValueError("The frozen evaluation data/split changed")
    if set(train) & set(test):
        raise ValueError("Train/test overlap")
    features = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)),
    ])
    pipeline = Pipeline([("features", features), ("classifier", LogisticRegression(max_iter=2000, random_state=42))])
    grid = [
        {"classifier": [LogisticRegression(max_iter=2000, random_state=42)],
         "classifier__C": [.1, 1, 10, 100], "classifier__class_weight": [None, "balanced"],
         "features__transformer_weights": [{"word": 1, "char": 0}, {"word": 1, "char": 1}, {"word": 0, "char": 1}]},
        {"classifier": [RandomForestClassifier(n_estimators=250, random_state=42, n_jobs=1)],
         "classifier__class_weight": [None, "balanced"], "classifier__min_samples_leaf": [1, 2],
         "features__transformer_weights": [{"word": 1, "char": 1}]},
        {"classifier": [XGBClassifier(n_estimators=150, objective="multi:softprob", num_class=len(labels), random_state=42, n_jobs=1)],
         "classifier__max_depth": [2, 4], "classifier__learning_rate": [.05, .15],
         "features__transformer_weights": [{"word": 1, "char": 1}]},
    ]
    search = GridSearchCV(pipeline, grid, scoring={"f1_macro": "f1_macro", "accuracy": "accuracy"},
        refit="f1_macro", cv=StratifiedKFold(5, shuffle=True, random_state=42), n_jobs=2)
    search.fit(texts[train], y[train])
    # Choose on CV only. One final evaluation of that candidate, not test-based search.
    prediction = search.predict_proba(texts[test])
    measured = metrics(y[test], prediction)
    best = {k: str(v) if k == "classifier" else v for k, v in search.best_params_.items()}
    result = {"evaluated_at": datetime.now(timezone.utc).isoformat(), "train_rows": len(train), "test_rows": len(test),
        "configurations": len(search.cv_results_["params"]), "selection": "Five-fold training-only macro F1; word and character features fitted inside every fold.",
        "best_cv_f1_macro": round(float(search.best_score_), 4), "best_parameters": best, "selected_candidate_test": measured,
        "required_macro_f1": .78, "target_pass": measured["f1_macro"] >= .78, "deployed": False,
        "limitations": ["This survey holdout was evaluated in earlier development; it is not fresh external validation.",
            "No test-based hyperparameter selection, data/split changes, or synthetic labeled training rows.",
            "A selected individual classifier is compared here; its result is not mislabeled as an ensemble result.",
            "This experiment never changes model weights, deployed evaluation, CI thresholds, or current production files."]}
    (ARTIFACTS / "model_improvement_experiment.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
