"""Create transparent scenario and sensitivity artefacts for the affordability policy."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.decision.affordability import POLICY
from src.decision.engine import recommend
from src.documents.statement_csv import StatementQualityReport


def _quality(score: float = 0.95, months: int = 3, balance_mismatches: int = 0) -> StatementQualityReport:
    """Build deterministic, non-applicant evidence for policy scenario testing."""
    return StatementQualityReport(
        score=score,
        valid_transactions=12,
        rejected_rows=0,
        observed_months=months,
        date_range_start="2026-01-01",
        date_range_end="2026-03-31",
        duplicate_rows_removed=0,
        invalid_date_rows=0,
        ambiguous_date_rows=0,
        invalid_amount_cells=0,
        both_debit_credit_rows=0,
        zero_value_rows=0,
        balance_mismatch_rows=balance_mismatches,
        salary_income_detected=True,
        warnings=(),
    )


def _base_features(**overrides: float | bool) -> dict[str, float | bool]:
    """Return a stable, strong-evidence scenario that can be varied one field at a time."""
    base: dict[str, float | bool] = {
        "savings_ratio": 0.35,
        "emi_to_income_ratio": 0.15,
        "salary_income_months": 3.0,
        "recognised_income_months": 3.0,
        "salary_consistency_ratio": 0.03,
        "expense_variation_ratio": 0.10,
        "balance_volatility_ratio": 0.20,
        "has_balance_history": True,
        "utility_payment_regularity": 1.0,
        "emergency_buffer_months": 1.0,
        "uncertain_transaction_share": 0.0,
        "proposed_emi_to_income_ratio": 0.20,
        "emi_difference_amount": 0.0,
        "emi_discrepancy_ratio": 0.0,
    }
    return base | overrides


def build_policy_report() -> dict[str, object]:
    """Generate a policy truth table and one-variable sensitivity table.

    These scenarios test deterministic rule behaviour. They are not estimates of
    default probability and do not validate the policy against lender outcomes.
    """
    truth_cases = [
        ("Strong complete evidence", _base_features(), _quality()),
        ("Score below manual-review band", _base_features(savings_ratio=-0.25, emi_to_income_ratio=0.48, salary_consistency_ratio=0.80, expense_variation_ratio=0.80, utility_payment_regularity=0.0), _quality()),
        ("Score in manual-review band", _base_features(savings_ratio=0.12, emi_to_income_ratio=0.35, salary_consistency_ratio=0.25, expense_variation_ratio=0.45, utility_payment_regularity=0.4), _quality()),
        ("Insufficient statement months", _base_features(), _quality(months=2)),
        ("Poor data quality", _base_features(), _quality(score=0.70)),
        ("No recurring income evidence", _base_features(salary_income_months=0.0, recognised_income_months=0.0), _quality()),
        ("Balance contradiction", _base_features(), _quality(balance_mismatches=1)),
        ("Existing EMI hard stop", _base_features(emi_to_income_ratio=0.55), _quality()),
        ("Proposed EMI hard stop", _base_features(proposed_emi_to_income_ratio=0.55), _quality()),
        ("Low emergency buffer", _base_features(emergency_buffer_months=0.10), _quality()),
        ("Uncertain categories", _base_features(uncertain_transaction_share=0.30), _quality()),
        ("Declared/detected EMI mismatch", _base_features(emi_difference_amount=5_000, emi_discrepancy_ratio=0.50), _quality()),
    ]
    truth_table: list[dict[str, object]] = []
    for scenario, features, report in truth_cases:
        decision = recommend(None, features, quality_report=report)
        truth_table.append({
            "scenario": scenario,
            "score": decision.affordability_score,
            "recommendation": decision.recommendation,
            "mandatory_review": bool(decision.reasons and any(
                phrase in " ".join(decision.reasons)
                for phrase in ("Fewer than", "quality", "No recognised", "contradict", "critical", "buffer", "categories", "differ materially")
            )),
        })

    sensitivity_cases = [
        ("Savings ratio", "savings_ratio", [0.35, 0.20, 0.10, 0.00, -0.10]),
        ("Existing EMI burden", "emi_to_income_ratio", [0.15, 0.20, 0.30, 0.40, 0.50, 0.55]),
        ("Salary consistency", "salary_consistency_ratio", [0.03, 0.15, 0.30, 0.50, 0.70]),
        ("Expense variation", "expense_variation_ratio", [0.10, 0.30, 0.60, 0.80]),
    ]
    sensitivity: list[dict[str, object]] = []
    for component, field, values in sensitivity_cases:
        for value in values:
            decision = recommend(None, _base_features(**{field: value}), quality_report=_quality())
            sensitivity.append({
                "component": component,
                "value": value,
                "score": decision.affordability_score,
                "recommendation": decision.recommendation,
            })

    return {
        "policy_version": POLICY["version"],
        "policy_type": POLICY["policy_type"],
        "evidence_status": POLICY["evidence_status"],
        "note": "Scenario checks verify policy implementation only; they are not validation against lending outcomes.",
        "truth_table": truth_table,
        "sensitivity": sensitivity,
    }


def evaluate(output_path: str | Path) -> dict[str, object]:
    """Write the policy artefact as JSON for the dashboard, report, and review."""
    report = build_policy_report()
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate affordability policy scenarios.")
    parser.add_argument("--output", default="reports/affordability_policy_evaluation.json")
    arguments = parser.parse_args()
    print(json.dumps(evaluate(arguments.output), indent=2))
