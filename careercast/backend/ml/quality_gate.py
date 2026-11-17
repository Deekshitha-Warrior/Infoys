"""Recompute saved-model holdout metrics; fail closed below PDF F1 or on regression."""
import argparse
import hashlib
import json
import numpy as np
from app.intelligence import ROOT, ARTIFACTS, load_bundle
from .train import metrics


def evaluate():
    contract = json.loads((ARTIFACTS / "quality_contract.json").read_text())
    for path, key in [(ROOT / "data/career_profiles.json", "dataset_sha256"), (ARTIFACTS / "split.json", "split_sha256")]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != contract[key]:
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
    measured = metrics(np.array([labels.index(r["career"]) for r in rows]), p)
    return {"version": bundle["version"], "test_rows": len(rows), "ensemble": measured,
        "minimum_macro_f1": contract["minimum_macro_f1"], "baseline_macro_f1": contract["baseline_macro_f1"],
        "threshold_pass": measured["f1_macro"] >= contract["minimum_macro_f1"],
        "regression_pass": measured["f1_macro"] + 0.0001 >= contract["baseline_macro_f1"],
        "scope": contract["description"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ARTIFACTS / "quality_gate.json"))
    args = parser.parse_args()
    result = evaluate()
    from pathlib import Path
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["threshold_pass"] and result["regression_pass"] else 1)


if __name__ == "__main__":
    main()
