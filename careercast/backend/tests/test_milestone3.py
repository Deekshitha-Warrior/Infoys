"""Milestone 3: account isolation, gap actions, exports, actual model gates."""
import json
import pytest
from app.intelligence import ARTIFACTS
from test_flow import client, account, profile_payload
from app.gaps import gap_report
from ml.quality_gate import evaluate


def test_gap_api_and_feedback_isolation(client):
    path = "/api/intelligence/gap-report"
    params = {"career": "Backend Developer"}
    assert client.get(path, params=params).status_code == 401
    alice = account(client)
    bob = account(client, "other@example.com")
    assert client.get("/api/intelligence/recommend", headers=alice).status_code == 422
    assert client.post("/api/profile/me", json=profile_payload(), headers=alice).status_code in (200, 201)
    response = client.get(path, params=params, headers=alice)
    assert response.status_code == 200, response.text
    gap = response.json()
    assert "docker" in gap["missing_skills"]
    assert all(a["practice"] and a["evidence"] and a["resource_url"].startswith("https://") for a in gap["actions"])
    assert client.get(path, params=params, headers=bob).status_code == 422
    csv = client.get(path, params={**params, "format": "csv"}, headers=alice)
    assert csv.status_code == 200 and "text/csv" in csv.headers["content-type"]
    assert "docker" in csv.text and "to develop" in csv.text
    assert client.get(path, params={"career": "Nonexistent"}, headers=alice).status_code == 422
    assert client.get(path, params={**params, "format": "exe"}, headers=alice).status_code == 422
    payload = {"career": "Backend Developer", "profile_hash": gap["profile_hash"], "ratings": {"docker": True}}
    assert client.post("/api/intelligence/gap-feedback", json=payload, headers=alice).status_code == 200
    assert client.post("/api/intelligence/gap-feedback", json=payload, headers=alice).json()["rated_skills"] == 1
    assert client.post("/api/intelligence/gap-feedback", json=payload, headers=bob).status_code == 422
    payload["profile_hash"] = "0" * 64
    assert client.post("/api/intelligence/gap-feedback", json=payload, headers=alice).status_code == 409
    payload["profile_hash"] = gap["profile_hash"]
    payload["ratings"] = {"not-a-missing-skill": True}
    assert client.post("/api/intelligence/gap-feedback", json=payload, headers=alice).status_code == 422
    before = client.get("/api/intelligence/history", headers=alice).json()
    recommendation = client.get("/api/intelligence/recommend", headers=alice)
    assert recommendation.status_code == 200
    assert len(recommendation.json()["recommendations"]) == 5
    assert client.get("/api/intelligence/history", headers=alice).json() == before


def test_gap_canonical_matching_and_complete_profile():
    gap = gap_report({"technical_skills": ["py", "java", "js", "git", "sql", "rest api"]}, "Software Developer")
    assert gap["alignment"] == 100
    assert not gap["missing_skills"] and not gap["actions"]
    with pytest.raises(ValueError):
        gap_report({"technical_skills": []}, "Software Developer")


def test_quality_gate_uses_actual_model_predictions():
    result = evaluate()
    assert result["test_rows"] == 90
    assert result["minimum_macro_f1"] == .78
    stored = json.loads((ARTIFACTS / "evaluation.json").read_text())
    assert result["ensemble"] == stored["ensemble"]
    assert result["threshold_pass"] == (result["ensemble"]["f1_macro"] >= .78)


def test_frozen_contract_ignores_line_endings_but_detects_data_changes(tmp_path):
    from ml.quality_gate import content_hash
    windows, linux = tmp_path / "windows.json", tmp_path / "linux.json"
    windows.write_bytes(b'{\r\n  "skills": ["python"], "career": "Developer"\r\n}')
    linux.write_bytes(b'{"career":"Developer","skills":["python"]}\n')
    assert content_hash(windows) == content_hash(linux)
    linux.write_bytes(b'{"career":"Other","skills":["python"]}\n')
    assert content_hash(windows) != content_hash(linux)
