"""Tests for affordability policy hard stops and data quality gates.

The rule-based 0-100 score is no longer part of the primary credit decision path.
assess_affordability() now functions as a data quality and hard-stop gate only.
These tests verify the hard stop triggers, mandatory review reasons, and sensitivity
of the score components (for backward compatibility and officer reference).

The engine now uses behavioral ML for recommendations — the recommendation from
build_policy_report() reflects ML-driven decisions, not pure rule bands.
"""
from __future__ import annotations

from src.evaluation.evaluate_affordability_policy import build_policy_report, evaluate
from src.decision.affordability import assess_affordability
from src.documents.statement_csv import StatementQualityReport


def _quality(score: float = 0.95, months: int = 3, balance_mismatches: int = 0) -> StatementQualityReport:
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


def _base_features(**overrides):
    base = {
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


# ── Hard stop gate tests (via assess_affordability directly) ──────────────────

def test_insufficient_months_triggers_mandatory_review_reason():
    assessment = assess_affordability(_base_features(), _quality(months=2))
    assert any("Fewer than three months" in r for r in assessment.mandatory_review_reasons)


def test_low_quality_score_triggers_mandatory_review_reason():
    assessment = assess_affordability(_base_features(), _quality(score=0.70))
    assert any("Statement data quality" in r for r in assessment.mandatory_review_reasons)


def test_no_recurring_income_triggers_mandatory_review_reason():
    assessment = assess_affordability(
        _base_features(salary_income_months=0.0, recognised_income_months=0.0), _quality()
    )
    assert any("No recognised recurring income" in r for r in assessment.mandatory_review_reasons)


def test_balance_contradiction_triggers_mandatory_review_reason():
    assessment = assess_affordability(_base_features(), _quality(balance_mismatches=1))
    assert any("Balance transitions contradict" in r for r in assessment.mandatory_review_reasons)


def test_existing_emi_hard_stop_triggers_mandatory_review_reason():
    assessment = assess_affordability(_base_features(emi_to_income_ratio=0.55), _quality())
    assert any("EMI burden exceeds" in r for r in assessment.mandatory_review_reasons)


def test_proposed_emi_hard_stop_triggers_mandatory_review_reason():
    assessment = assess_affordability(_base_features(proposed_emi_to_income_ratio=0.55), _quality())
    assert any("Existing plus proposed EMI" in r for r in assessment.mandatory_review_reasons)


def test_low_emergency_buffer_triggers_mandatory_review_reason():
    assessment = assess_affordability(_base_features(emergency_buffer_months=0.10), _quality())
    assert any("Emergency cash buffer" in r for r in assessment.mandatory_review_reasons)


def test_uncertain_categories_triggers_mandatory_review_reason():
    assessment = assess_affordability(_base_features(uncertain_transaction_share=0.30), _quality())
    assert any("Too many transaction categories" in r for r in assessment.mandatory_review_reasons)


def test_emi_mismatch_triggers_mandatory_review_reason():
    assessment = assess_affordability(
        _base_features(emi_difference_amount=5_000, emi_discrepancy_ratio=0.50), _quality()
    )
    assert any("Declared EMI" in r for r in assessment.mandatory_review_reasons)


def test_strong_evidence_has_no_mandatory_review_reasons():
    """A clean, complete profile must not trigger any hard stops."""
    assessment = assess_affordability(_base_features(), _quality())
    assert assessment.mandatory_review_reasons == [], (
        f"Unexpected mandatory review reasons for clean profile: {assessment.mandatory_review_reasons}"
    )


# ── Score component monotonicity (backward compat, officer reference) ─────────

def test_policy_sensitivity_has_expected_boundary_progression():
    report = build_policy_report()
    savings = [row for row in report["sensitivity"] if row["component"] == "Savings ratio"]
    assert [row["score"] for row in savings] == sorted(
        [row["score"] for row in savings], reverse=True
    )
    emi = [row for row in report["sensitivity"] if row["component"] == "Existing EMI burden"]
    # At maximum EMI (0.55), hard stop triggers → Manual review from engine
    assert emi[-1]["recommendation"] == "Manual review"


def test_policy_report_is_written(tmp_path):
    output = tmp_path / "policy.json"
    report = evaluate(output)
    assert output.exists()
    assert report["policy_version"] == "statement-affordability-v1"
