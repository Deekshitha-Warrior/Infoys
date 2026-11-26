"""Train three classifiers with CV only inside the training split."""

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from app.intelligence import ROOT, ARTIFACTS, CAREERS, canonical
from .features import SkillFeatures


def metrics(y, p):
    precision, recall, f1, _ = precision_recall_fscore_support(
        y, p.argmax(1), average="macro", zero_division=0
    )
    top = np.argsort(p, axis=1)[:, -min(5, p.shape[1]) :]
    return {
        "accuracy": round(float(accuracy_score(y, p.argmax(1))), 4),
        "precision_macro": round(float(precision), 4),
        "recall_macro": round(float(recall), 4),
        "f1_macro": round(float(f1), 4),
        "top5_recall": round(
            float(np.mean([label in row for label, row in zip(y, top)])), 4
        ),
    }


def promotion_errors(report):
    """Preserve specification thresholds when manually promoting a candidate."""
    checks = {
        "baseline accuracy >=65%": report["models"]["logistic_regression"]["accuracy"] >= .65,
        "ensemble macro F1 >=80%": report["ensemble"]["f1_macro"] >= .8,
        "ranking Top-5 recall >=90%": report["ranking"]["top5_recall"] >= .9,
        "embedding synonym cosine >=85%": report.get("embedding", {}).get("mean_synonym_cosine", 0) >= .85,
    }
    return [name for name, passed in checks.items() if not passed]


def main(semantic=False, output_dir=None, promote=False):
    records = json.loads(
        (ROOT / "data/career_profiles.json").read_text(encoding="utf-8")
    )
    encoder = LabelEncoder()
    y = encoder.fit_transform([r["career"] for r in records])
    texts = np.array([r["text"] for r in records])
    indices = np.arange(len(records))
    train, test = train_test_split(indices, test_size=0.25, random_state=42, stratify=y)
    candidates = {
        "logistic_regression": (
            LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42),
            {"classifier__C": [0.5, 2.0, 8.0]},
        ),
        "random_forest": (
            RandomForestClassifier(
                n_estimators=150, class_weight="balanced", random_state=42, n_jobs=1
            ),
            {
                "classifier__max_depth": [8, None],
                "classifier__min_samples_leaf": [1, 2],
            },
        ),
        "xgboost": (
            XGBClassifier(
                n_estimators=100,
                objective="multi:softprob",
                num_class=len(encoder.classes_),
                eval_metric="mlogloss",
                random_state=42,
                n_jobs=2,
            ),
            {
                "classifier__max_depth": [2, 4],
                "classifier__learning_rate": [0.05, 0.15],
            },
        ),
    }
    candidate_dir = Path(output_dir) if output_dir else ARTIFACTS / "candidates" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    candidate_dir.mkdir(parents=True, exist_ok=False)
    models, report, probabilities = {}, {}, []
    vectorizer = None
    for name, (model, grid) in candidates.items():
        pipeline = Pipeline(
            [("features", SkillFeatures(semantic=semantic)), ("classifier", model)]
        )
        search = GridSearchCV(
            pipeline,
            grid,
            scoring="f1_macro",
            cv=StratifiedKFold(3, shuffle=True, random_state=42),
            n_jobs=1,
        )
        fit_parameters = {}
        if name == "xgboost":
            from sklearn.utils.class_weight import compute_sample_weight

            fit_parameters["classifier__sample_weight"] = compute_sample_weight(
                "balanced", y[train]
            )
        search.fit(texts[train], y[train], **fit_parameters)
        p = search.predict_proba(texts[test])
        probabilities.append(p)
        report[name] = {
            **metrics(y[test], p),
            "cv_f1_macro": round(float(search.best_score_), 4),
            "best_parameters": search.best_params_,
        }
        models[name] = search.best_estimator_.named_steps["classifier"]
        vectorizer = search.best_estimator_.named_steps["features"]
    # All best estimators refit the identical vectorizer configuration on identical rows.
    ensemble = np.mean(probabilities, axis=0)
    alignment = np.array(
        [
            [
                len(
                    set(CAREERS.get(label, []))
                    & {canonical(s) for s in records[i].get("technical_skills", [])}
                )
                / max(1, len(CAREERS.get(label, [])))
                for label in encoder.classes_
            ]
            for i in test
        ]
    )
    ranked_scores = 0.8 * ensemble + 0.2 * alignment
    ARTIFACTS.mkdir(exist_ok=True)
    version = ("career-survey-semantic-v3-" if semantic else "career-survey-v2-") + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    joblib.dump(
        {
            "models": models,
            "vectorizer": vectorizer,
            "labels": encoder.classes_.tolist(),
            "version": version,
            "data_scope": "Public first-job survey, broad technology career categories. Not a longitudinal career-transition benchmark.",
        },
        candidate_dir / "career_models.joblib",
    )
    result = {
        "status": "trained",
        "version": version,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset": "dyno7/career_recommender (anonymized subset)",
        "train_rows": len(train),
        "test_rows": len(test),
        "classes": encoder.classes_.tolist(),
        "split": "Stratified 75/25; seed 42; exact feature duplicates removed before split. Vectorizer fitted inside each CV fold.",
        "models": report,
        "ensemble": metrics(y[test], ensemble),
        "gates": {
            "baseline_top1_65": report["logistic_regression"]["accuracy"] >= 0.65,
            "ensemble_f1_80": metrics(y[test], ensemble)["f1_macro"] >= 0.8,
            "top5_recall_90": metrics(y[test], ensemble)["top5_recall"] >= 0.9,
            "parser_200_resumes": "not_verified_no_independently_annotated_corpus",
            "semeval_linkedin": "not_available",
        },
        "limitations": [
            "Metrics apply only to the small public survey split.",
            "Class confidence is uncalibrated model probability, not job success likelihood.",
            "Top-5 recall is less informative with few career classes.",
            "No independent 200-resume annotation set or identified SemEval/LinkedIn benchmark.",
            "No live market demand data is used.",
        ],
    }
    result["features"] = "TF-IDF + canonical multi-hot skills" + (
        " + fine-tuned Sentence-BERT embeddings" if semantic else ""
    )
    result["ranking"] = metrics(y[test], ranked_scores)
    result["gates"]["top5_recall_90"] = result["ranking"]["top5_recall"] >= 0.9
    embedding_report = ARTIFACTS / "embedding_evaluation.json"
    if semantic and embedding_report.exists():
        result["embedding"] = json.loads(embedding_report.read_text(encoding="utf-8"))
        result["gates"]["embedding_mean_cosine_85"] = result["embedding"][
            "mean_cosine_85_gate"
        ]
    (candidate_dir / "evaluation.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    (candidate_dir / "split.json").write_text(
        json.dumps({"train": train.tolist(), "test": test.tolist()}), encoding="utf-8"
    )
    print(json.dumps(result, indent=2))
    print(f"Candidate saved in {candidate_dir}; the live model has not been replaced.")
    if promote:
        failures = promotion_errors(result)
        if failures:
            raise SystemExit("Promotion blocked: " + "; ".join(failures))
        from .quality_gate import content_hash, required_f1
        contract = json.loads((ARTIFACTS / "quality_contract.json").read_text())
        if result["ensemble"]["f1_macro"] < required_f1(contract):
            raise SystemExit("Promotion blocked: configured CI threshold not met")
        if content_hash(ROOT / "data/career_profiles.json") != contract["dataset_sha256"]:
            raise SystemExit("Promotion blocked: frozen evaluation data changed")
        if (ARTIFACTS / "evaluation.json").exists():
            current = json.loads((ARTIFACTS / "evaluation.json").read_text())
            if result["ensemble"]["f1_macro"] < current["ensemble"]["f1_macro"]:
                raise SystemExit("Promotion blocked: macro F1 regression")
        # Keep the evaluation split fixed; changing it requires a reviewed contract.
        if json.loads((candidate_dir / "split.json").read_text()) != json.loads((ARTIFACTS / "split.json").read_text()):
            raise SystemExit("Promotion blocked: evaluation split changed")
        for name in ["career_models.joblib", "evaluation.json"]:
            shutil.copy2(candidate_dir / name, ARTIFACTS / name)
        print("Candidate promoted. Restart the API to load its weights.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--semantic", action="store_true")
    parser.add_argument("--output-dir", help="New directory for candidate artifacts; defaults to artifacts/candidates/<timestamp>")
    parser.add_argument("--promote", action="store_true", help="Replace live weights only after every model acceptance check passes")
    args = parser.parse_args()
    main(args.semantic, args.output_dir, args.promote)
