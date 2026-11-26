from ml.quality_gate import career_diagnostics


def test_diagnostics_reveal_unpredicted_career_and_count_errors():
    result = career_diagnostics(["A", "B", "C"], [0, 0, 1, 2], [0, 1, 1, 1], ["A", "A", "B", "C"])
    rows = result["per_career"]
    assert rows[0]["training_profiles"] == 2
    assert rows[0]["recall"] == .5
    assert rows[1]["precision"] == .3333
    assert rows[2]["test_profiles"] == 1
    assert rows[2]["predicted_profiles"] == 0
    assert rows[2]["f1"] == 0
    assert sum(sum(row) for row in result["confusion_matrix"]) == 4
    assert sum(row["profiles"] for row in result["confusions"]) == 2
    assert result["confusion_matrix_labels"] == ["A", "B", "C"]
