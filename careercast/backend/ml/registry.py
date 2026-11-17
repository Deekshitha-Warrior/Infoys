"""Register fitted classifiers in local/remote MLflow; no automatic promotion."""
import argparse
import json
import os
import hashlib
from pathlib import Path
from contextlib import contextmanager
import tempfile
import shutil
from app.intelligence import ROOT, ARTIFACTS, load_bundle
from .quality_gate import evaluate


@contextmanager
def staged_code():
    # Fresh plain directories avoid carrying Windows OneDrive read-only flags.
    with tempfile.TemporaryDirectory(prefix="careercast-registry-") as directory:
        paths = []
        for package in ["app", "ml"]:
            target = Path(directory) / package
            target.mkdir()
            for source in (ROOT / "backend" / package).rglob("*.py"):
                if "__pycache__" in source.parts:
                    continue
                destination = target / source.relative_to(ROOT / "backend" / package)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
            paths.append(str(target))
        yield paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracking-uri", default=os.getenv("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"))
    args = parser.parse_args()
    import mlflow
    import mlflow.sklearn
    from sklearn.pipeline import Pipeline
    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment("CareerCast")
    evaluation = evaluate()
    bundle = load_bundle()
    # Only public feature rows and source code are logged; no user DB/uploads.
    with staged_code() as code, mlflow.start_run(run_name=bundle["version"]) as run:
        mlflow.set_tags({"bundle_version": bundle["version"], "quality_gate": "passed" if evaluation["threshold_pass"] and evaluation["regression_pass"] else "blocked",
            "data_scope": bundle["data_scope"], "bundle_sha256": hashlib.sha256((ARTIFACTS / "career_models.joblib").read_bytes()).hexdigest()})
        mlflow.log_metrics({"ensemble_" + k: v for k, v in evaluation["ensemble"].items()})
        for path in ["evaluation.json", "quality_contract.json", "split.json"]:
            mlflow.log_artifact(str(ARTIFACTS / path), "evaluation")
        registered = []
        for name, classifier in bundle["models"].items():
            pipeline = Pipeline([("features", bundle["vectorizer"]), ("classifier", classifier)])
            info = mlflow.sklearn.log_model(pipeline, name=name, code_paths=code,
                serialization_format="cloudpickle", pyfunc_predict_fn="predict_proba",
                metadata={"career_labels": bundle["labels"]},
                pip_requirements=["scikit-learn==1.9.1", "xgboost==3.4.1", "joblib==1.6.0"])
            version = mlflow.register_model(info.model_uri, "CareerCast-" + name)
            registered.append({"name": version.name, "version": version.version})
        result = {"run_id": run.info.run_id, "registered": registered, "promoted": False, "quality_gate": evaluation}
        mlflow.log_dict(result, "registry_result.json")
    (ARTIFACTS / "registry_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
