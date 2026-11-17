"""Install a wheel in an isolated target, then smoke-test outside the source tree."""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("wheel")
args = parser.parse_args()
wheel = Path(args.wheel).resolve()
with tempfile.TemporaryDirectory(prefix="careercast-wheel-") as folder:
    target = Path(folder) / "installed"
    subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(target), str(wheel)], check=True)
    code = r'''
import sys, json
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from careercast_tools import predict_profile, skill_gap, __version__
from careercast_tools.cli import main
from app.intelligence import ROOT
from importlib.metadata import distributions
assert "careercast_assets" in ROOT.parts, ROOT
assert any(e.name == "careercast" for d in distributions(path=[sys.argv[1]]) for e in d.entry_points)
source = Path("profile.json")
source.write_text(json.dumps({"technical_skills": ["python", "sql", "git"]}))
main(["predict", str(source), "--output", "prediction.json"])
report = json.loads(Path("prediction.json").read_text())
assert len(report["recommendations"]) == 5
assert skill_gap({"technical_skills": ["python"]}, "Software Developer")["missing_skills"]
assert (ROOT / "data/career_profiles.json").is_file()
assert (ROOT / "docs/API.md").is_file()
assert (Path(sys.argv[1]) / "careercast_tools/review.py").is_file()
assert not list(Path(sys.argv[1]).rglob("*.db"))
print("Installed wheel API, CLI, model assets, public data and docs passed:", __version__)
'''
    subprocess.run([sys.executable, "-I", "-c", code, str(target)], cwd=folder, check=True)
