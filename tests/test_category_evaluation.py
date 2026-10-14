from pathlib import Path

from src.evaluation.evaluate_categories import evaluate


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_curated_category_coverage_fixture_is_evaluated_separately(tmp_path):
    output = tmp_path / "coverage.json"
    report = evaluate(
        PROJECT_ROOT / "data" / "evaluation" / "heldout_transaction_categories.csv",
        output,
        "Curated category-coverage fixture; it is not production validation.",
    )
    assert output.exists()
    assert report["rows"] == 19
    assert report["macro_f1"] == 1.0
    assert "not production validation" in report["note"]
