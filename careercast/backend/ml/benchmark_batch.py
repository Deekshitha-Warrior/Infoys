"""Cold-process CLI benchmark: file ingestion, validation, features, ranking, gaps, JSON."""
import argparse
import json
import platform
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from app.intelligence import ARTIFACTS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ARTIFACTS / "batch_benchmark.json"))
    args = parser.parse_args()
    seeds = [["python", "sql", "git"], ["javascript", "html", "css", "react"], ["excel", "accounting"], ["python", "pandas", "statistics", "machine learning"]]
    with tempfile.TemporaryDirectory(prefix="careercast-batch-") as folder:
        source, target = Path(folder) / "profiles.json", Path(folder) / "results.json"
        source.write_text(json.dumps([{"technical_skills": seeds[i % len(seeds)], "degree": "Synthetic benchmark degree"} for i in range(1000)]), encoding="utf-8")
        start = time.perf_counter()
        subprocess.run([sys.executable, "-m", "careercast_tools", "batch", str(source), "--output", str(target)], check=True, capture_output=True, text=True)
        duration = time.perf_counter() - start
        reports = json.loads(target.read_text(encoding="utf-8"))
        assert len(reports) == 1000 and all(r["recommendations"] and "gap_report" in r for r in reports)
    result = {"profiles": 1000, "elapsed_seconds": round(duration, 3), "target_seconds": 240,
        "passed": duration < 240, "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.system(),
        "scope": "Cold-process local CLI: structured JSON read, schema validation, text/skill vectorization, three classifiers, career ranking, top-career gap plans and JSON write. Synthetic repeated profiles for throughput only; excludes document parsing, HTTP and public-host performance."}
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
