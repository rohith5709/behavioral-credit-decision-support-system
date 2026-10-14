from src.evaluation.evaluate_affordability_policy import build_policy_report, evaluate


def test_policy_truth_table_covers_every_decision_band_and_hard_stop():
    report = build_policy_report()
    rows = {row["scenario"]: row for row in report["truth_table"]}
    assert rows["Strong complete evidence"]["recommendation"] == "Meets indicative affordability criteria"
    assert rows["Score below manual-review band"]["recommendation"] == "Does not meet indicative affordability criteria"
    assert rows["Score in manual-review band"]["recommendation"] == "Manual review"
    assert rows["Insufficient statement months"]["recommendation"] == "Refer for additional documents"
    assert rows["No recurring income evidence"]["recommendation"] == "Refer for additional documents"
    assert rows["Uncertain categories"]["recommendation"] == "Refer for additional documents"
    for scenario in (
        "Balance contradiction", "Existing EMI hard stop", "Proposed EMI hard stop",
        "Low emergency buffer", "Declared/detected EMI mismatch",
    ):
        assert rows[scenario]["recommendation"] == "Manual review"


def test_policy_sensitivity_has_expected_boundary_progression():
    report = build_policy_report()
    savings = [row for row in report["sensitivity"] if row["component"] == "Savings ratio"]
    assert [row["score"] for row in savings] == sorted(
        [row["score"] for row in savings], reverse=True
    )
    emi = [row for row in report["sensitivity"] if row["component"] == "Existing EMI burden"]
    assert emi[-1]["recommendation"] == "Manual review"


def test_policy_report_is_written(tmp_path):
    output = tmp_path / "policy.json"
    report = evaluate(output)
    assert output.exists()
    assert report["policy_version"] == "statement-affordability-v1"
