"""Evaluate independently annotated resumes; never manufactures ground truth.

Input JSON: [{"text": "...", "expected": {"technical_skills": [...],
"job_roles": [...], "education": [...]}}]. Exact normalized entity matching.
"""

import argparse
import json
from pathlib import Path
from app.parser import parse_resume
from app.intelligence import canonical


def evaluate(records):
    counts = {
        field: {"tp": 0, "fp": 0, "fn": 0}
        for field in ("technical_skills", "job_roles", "education")
    }
    for row in records:
        parsed = parse_resume(row["text"])
        for field, c in counts.items():
            normalize = (
                canonical
                if field == "technical_skills"
                else lambda s: " ".join(s.lower().split())
            )
            predicted = set(map(normalize, parsed.get(field, [])))
            expected = set(map(normalize, row["expected"].get(field, [])))
            c["tp"] += len(predicted & expected)
            c["fp"] += len(predicted - expected)
            c["fn"] += len(expected - predicted)
    result = {}
    for field, c in counts.items():
        result[field] = {
            **c,
            "precision": c["tp"] / max(1, c["tp"] + c["fp"]),
            "recall": c["tp"] / max(1, c["tp"] + c["fn"]),
        }
    tp = sum(c["tp"] for c in counts.values())
    fp = sum(c["fp"] for c in counts.values())
    return {
        "resume_count": len(records),
        "entities": result,
        "micro_precision": tp / max(1, tp + fp),
        "milestone_gate": len(records) >= 200 and tp / max(1, tp + fp) >= 0.9,
        "matching": "Exact case/whitespace-normalized entity match; canonical aliases for skills.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_json")
    parser.add_argument("--output", default="parser_evaluation.json")
    args = parser.parse_args()
    result = evaluate(json.loads(Path(args.gold_json).read_text(encoding="utf-8")))
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
