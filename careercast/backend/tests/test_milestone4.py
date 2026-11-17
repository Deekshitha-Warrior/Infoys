"""Regression coverage for the package API, CLI, cohort privacy and user feedback."""
import json
import pytest
from test_flow import client, account, profile_payload
from careercast_tools import predict_profile, skill_gap
from careercast_tools.batch import predict_batch, cohort_summary
from careercast_tools.cli import main
from ml.uat_report import summarize


def test_batch_parity_validation_and_aggregate_privacy():
    profile = profile_payload()
    single = predict_profile(profile)
    batch = predict_batch([profile, {"technical_skills": ["html", "css", "react"]}])
    assert batch[0]["recommendations"] == single["recommendations"]
    assert batch[0]["gap_report"] == skill_gap(profile, single["recommendations"][0]["career"])
    summary = cohort_summary(batch)
    assert sum(r["count"] for r in summary["career_distribution"]) == 2
    assert summary["profile_count"] == 2
    assert "technical_skills" not in json.dumps(summary)
    with pytest.raises(ValueError):
        cohort_summary([])
    for invalid in [[], [{}], [profile] * 1001]:
        with pytest.raises(ValueError):
            predict_batch(invalid)


def test_cli_json_csv_and_invalid_profile(tmp_path):
    source = tmp_path / "profile.json"
    source.write_text(json.dumps(profile_payload()), encoding="utf-8")
    result = tmp_path / "result.json"
    main(["recommend", str(source), "--output", str(result)])
    assert len(json.loads(result.read_text())["recommendations"]) == 5
    csv = tmp_path / "gaps.csv"
    main(["gap-report", str(source), "--career", "Backend Developer", "--format", "csv", "--output", str(csv)])
    assert "docker" in csv.read_text()
    source.write_text('{"technical_skills": []}')
    with pytest.raises(SystemExit) as exc:
        main(["predict", str(source)])
    assert exc.value.code == 2


def test_cohort_and_satisfaction_are_account_scoped(client):
    path = "/api/intelligence/cohort"
    assert client.post(path, json={"profiles": [profile_payload()]}).status_code == 401
    alice, bob = account(client), account(client, "cohort-other@example.com")
    before = client.get("/api/intelligence/history", headers=alice).json()
    response = client.post(path, headers=alice, json={"profiles": [profile_payload(), {"technical_skills": ["autocad"]}]})
    assert response.status_code == 200
    assert response.json()["profile_count"] == 2
    assert client.get("/api/intelligence/history", headers=alice).json() == before
    assert client.post(path, headers=alice, json={"profiles": []}).status_code == 422
    assert client.post(path, headers=alice, json={"profiles": [profile_payload()] * 1001}).status_code == 422
    client.post("/api/profile/me", headers=alice, json=profile_payload())
    report = client.get("/api/intelligence/recommend", headers=alice).json()
    payload = {"profile_hash": report["profile_hash"], "rating": 5}
    endpoint = "/api/intelligence/recommendation-feedback"
    assert client.post(endpoint, headers=alice, json=payload).status_code == 200
    payload["rating"] = 4
    assert client.post(endpoint, headers=alice, json=payload).json()["rating"] == 4
    assert client.post(endpoint, headers=bob, json=payload).status_code == 422
    for rating in [0, 6, True]:
        assert client.post(endpoint, headers=alice, json={**payload, "rating": rating}).status_code == 422
    assert client.post(endpoint, headers=alice, json={**payload, "profile_hash": "0" * 64}).status_code == 409


def test_empty_uat_is_unverified_not_a_pass():
    assert summarize([])["target_met"] is None
    assert summarize([])["satisfaction"] is None
    assert summarize([4, 5, 4, 5, 4, 5, 4, 5, 4, 1])["satisfaction"] == .9
    assert summarize([1, 2, 3, 4, 5])["target_met"] is False
