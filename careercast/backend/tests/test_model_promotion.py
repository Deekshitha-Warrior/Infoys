"""Failed or incomplete training candidates must not qualify for promotion."""
from ml.train import promotion_errors
from ml.quality_gate import required_f1
import pytest
import json
from types import SimpleNamespace
import numpy as np


def candidate():
    return {"models": {"logistic_regression": {"accuracy": .65}}, "ensemble": {"f1_macro": .8},
        "ranking": {"top5_recall": .9}, "embedding": {"mean_synonym_cosine": .85}}


def test_current_quality_does_not_qualify():
    result = candidate()
    result["ensemble"]["f1_macro"] = .3697
    assert "ensemble macro F1 >=80%" in promotion_errors(result)


def test_ci_threshold_cannot_accidentally_drop_below_the_specification():
    assert required_f1({"minimum_macro_f1": .2}) == .78
    assert required_f1({"minimum_macro_f1": .8}) == .8
    for value in [float("nan"), -1, 2]:
        with pytest.raises(ValueError):
            required_f1({"minimum_macro_f1": value})


def test_all_acceptance_thresholds_are_required():
    result = candidate()
    assert promotion_errors(result) == []
    for group, key in [("ensemble", "f1_macro"), ("ranking", "top5_recall"), ("embedding", "mean_synonym_cosine")]:
        value = candidate()
        value[group][key] -= .0001
        assert promotion_errors(value)
    value = candidate()
    value["models"]["logistic_regression"]["accuracy"] = .6499
    assert promotion_errors(value)
    value = candidate()
    del value["embedding"]
    assert promotion_errors(value)


def test_failed_training_preserves_live_model_and_reports(tmp_path, monkeypatch):
    from ml import train
    live = tmp_path / "live"
    live.mkdir()
    original = {
        "career_models.joblib": b"existing-live-weights",
        "evaluation.json": b'{"ensemble":{"f1_macro":0.3697}}',
        "split.json": b'{"train":[0],"test":[1]}',
    }
    for name, content in original.items():
        (live / name).write_bytes(content)

    class WeakSearch:
        def __init__(self, pipeline, *args, **kwargs):
            self.best_estimator_ = SimpleNamespace(named_steps=pipeline.named_steps)
            self.best_params_ = {}
            self.best_score_ = .1
        def fit(self, x, y, **kwargs):
            return self
        def predict_proba(self, x):
            return np.full((len(x), 10), .1)

    monkeypatch.setattr(train, "ARTIFACTS", live)
    monkeypatch.setattr(train, "GridSearchCV", WeakSearch)
    candidate_dir = tmp_path / "candidate"
    with pytest.raises(SystemExit, match="Promotion blocked"):
        train.main(output_dir=candidate_dir, promote=True)
    assert (candidate_dir / "career_models.joblib").is_file()
    assert json.loads((candidate_dir / "evaluation.json").read_text())["ensemble"]["f1_macro"] < .8
    for name, content in original.items():
        assert (live / name).read_bytes() == content
