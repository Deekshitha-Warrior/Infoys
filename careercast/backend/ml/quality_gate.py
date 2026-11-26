"""Recompute saved-model holdout metrics; fail closed below PDF F1 or on regression."""
import argparse
import hashlib
import json
import os
import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from app.intelligence import ROOT, ARTIFACTS, load_bundle
from .train import metrics


def content_hash(path):
    """Ignore JSON whitespace/key order, but detect any actual value change."""
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def required_f1(contract):
    value = float(contract["minimum_macro_f1"])
    if not np.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("Invalid macro F1 threshold")
    return max(.78, value)


def career_diagnostics(labels, actual, predicted, training_labels):
    """Aggregate counts only; never publish individual profile text in CI."""
    indices = list(range(len(labels)))
    precision, recall, f1, support = precision_recall_fscore_support(
        actual, predicted, labels=indices, zero_division=0
    )
    matrix = confusion_matrix(actual, predicted, labels=indices)
    per_career = [
        {"career": name, "training_profiles": training_labels.count(name),
         "test_profiles": int(support[i]), "predicted_profiles": int(matrix[:, i].sum()),
         "precision": round(float(precision[i]), 4), "recall": round(float(recall[i]), 4),
         "f1": round(float(f1[i]), 4)}
        for i, name in enumerate(labels)
    ]
    confusions = sorted(
        [{"actual": labels[i], "predicted": labels[j], "profiles": int(matrix[i, j])}
         for i in indices for j in indices if i != j and matrix[i, j]],
        key=lambda row: (-row["profiles"], row["actual"], row["predicted"]),
    )
    return {"per_career": per_career, "confusion_matrix": matrix.tolist(),
            "confusion_matrix_labels": list(labels), "confusions": confusions,
            "interpretation": "Macro F1 weights every career equally. Small test counts make per-career estimates uncertain; these results are diagnostics, not a fresh validation set."}


def evaluate():
    contract = json.loads((ARTIFACTS / "quality_contract.json").read_text())
    if contract.get("hash_format") != "canonical-json-v1":
        raise ValueError("Unsupported evaluation hash format")
    for path, key in [(ROOT / "data/career_profiles.json", "dataset_sha256"), (ARTIFACTS / "split.json", "split_sha256")]:
        if content_hash(path) != contract[key]:
            raise ValueError(f"Frozen evaluation contract changed: {path.name}. A reviewed new benchmark is required.")
    records = json.loads((ROOT / "data/career_profiles.json").read_text())
    split = json.loads((ARTIFACTS / "split.json").read_text())
    if set(split["train"]) & set(split["test"]):
        raise ValueError("Train/test leakage detected")
    bundle = load_bundle()
    labels = bundle["labels"]
    rows = [records[i] for i in split["test"]]
    x = bundle["vectorizer"].transform([r["text"] for r in rows])
    p = np.mean([m.predict_proba(x) for m in bundle["models"].values()], axis=0)
    actual = np.array([labels.index(r["career"]) for r in rows])
    measured = metrics(actual, p)
    diagnostics = career_diagnostics(labels, actual, p.argmax(1),
                                     [records[i]["career"] for i in split["train"]])
    minimum = required_f1(contract)
    return {"version": bundle["version"], "test_rows": len(rows), "ensemble": measured,
        "minimum_macro_f1": minimum, "baseline_macro_f1": contract["baseline_macro_f1"],
        "threshold_pass": measured["f1_macro"] >= minimum,
        "regression_pass": measured["f1_macro"] + 0.0001 >= contract["baseline_macro_f1"],
        "scope": contract["description"], "diagnostics": diagnostics}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ARTIFACTS / "quality_gate.json"))
    args = parser.parse_args()
    result = evaluate()
    from pathlib import Path
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    measured = result["ensemble"]["f1_macro"] * 100
    required = result["minimum_macro_f1"] * 100
    passed = result["threshold_pass"] and result["regression_pass"]
    summary = (
        "## CareerCast model quality\n\n"
        f"- Measured holdout macro F1: **{measured:.2f}%**\n"
        f"- Required macro F1: **{required:.2f}%**\n"
        f"- Regression check: **{'passed' if result['regression_pass'] else 'failed'}**\n"
        f"- Quality gate: **{'passed' if passed else 'failed'}**\n\n"
        "A failed quality threshold is distinct from a test/build failure. "
        "The model must improve on genuine validation data; the threshold is not bypassed.\n"
    )
    summary += "\n### Career category results\n\n| Career | Train | Test | Predicted | Precision | Recall | F1 |\n|---|---:|---:|---:|---:|---:|---:|\n"
    for row in result["diagnostics"]["per_career"]:
        name = row["career"].replace("|", "\\|").replace("\n", " ")
        summary += (f"| {name} | {row['training_profiles']} | {row['test_profiles']} | "
                    f"{row['predicted_profiles']} | {row['precision']:.2%} | {row['recall']:.2%} | {row['f1']:.2%} |\n")
    summary += "\n" + result["diagnostics"]["interpretation"] + "\n"
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.write(summary)
    if not passed:
        message = f"Model macro F1 {measured:.2f}% versus required {required:.2f}%; regression check {'passed' if result['regression_pass'] else 'failed'}."
        print(f"::error title=Model acceptance target not met::{message}" if os.getenv("GITHUB_ACTIONS") == "true" else message)
    raise SystemExit(0 if result["threshold_pass"] and result["regression_pass"] else 1)


if __name__ == "__main__":
    main()
