"""Tests for the ML-driven recommendation engine.

The engine now uses the behavioral ML model (Pillar 1) as the primary decision
driver. Rule-based scoring is removed from the decision path; assess_affordability()
is used only for data quality hard stops. These tests verify the ML-based
recommendation logic and hard-stop safeguards.
"""
from __future__ import annotations

from io import StringIO

from src.decision.engine import recommend
from src.documents.statement_csv import parse_statement_csv


def _features(**overrides: float) -> dict[str, float]:
    base = {
        "savings_ratio": 0.35,
        "emi_to_income_ratio": 0.15,
        "salary_income_months": 3.0,
        "salary_consistency_ratio": 0.02,
        "expense_variation_ratio": 0.10,
        "balance_volatility_ratio": 0.20,
        "has_balance_history": 1.0,
        "utility_payment_regularity": 1.0,
    }
    return base | overrides


def _quality_report():
    _, report = parse_statement_csv(StringIO("""date,description,credit,debit,balance
2026-01-01,Salary,50000,0,50000
2026-02-01,Salary,50000,0,100000
2026-03-01,Salary,50000,0,150000
"""))
    return report


def test_engine_produces_behavioral_ml_output_when_statement_provided():
    """Decision must include a behavioral_ml result when statement features are given."""
    decision = recommend(None, _features(), quality_report=_quality_report())
    assert decision.behavioral_ml is not None
    assert "status" in decision.behavioral_ml
    assert "default_probability" in decision.behavioral_ml


def test_engine_recommendation_is_valid_string():
    decision = recommend(None, _features(), quality_report=_quality_report())
    valid = {
        "Meets indicative affordability criteria",
        "Does not meet indicative affordability criteria",
        "Manual review",
        "Refer for additional documents",
    }
    assert decision.recommendation in valid


def test_missing_salary_requests_additional_documents_even_with_good_other_signals():
    """Hard stop: no salary evidence triggers 'Refer for additional documents'."""
    decision = recommend(None, _features(salary_income_months=0.0), quality_report=_quality_report())
    assert decision.recommendation == "Refer for additional documents"
    assert any("No recognised recurring income" in reason for reason in decision.reasons)


def test_material_declared_and_detected_emi_difference_requires_manual_review():
    """Hard stop: EMI discrepancy triggers mandatory 'Manual review'."""
    decision = recommend(
        None,
        _features(emi_difference_amount=5_000, emi_discrepancy_ratio=0.50),
        quality_report=_quality_report(),
    )
    assert decision.recommendation == "Manual review"
    assert any("Declared EMI" in reason for reason in decision.reasons)


def test_affordability_score_is_still_returned_for_backward_compatibility():
    """affordability_score remains populated (used by existing UI visualisations)."""
    decision = recommend(None, _features(), quality_report=_quality_report())
    assert decision.affordability_score is not None
    assert isinstance(decision.affordability_score, int)


def test_pillar_summary_contains_behavioral_ml_probability():
    """pillar_summary must expose the behavioral ML probability for the UI."""
    decision = recommend(None, _features(), quality_report=_quality_report())
    assert decision.pillar_summary is not None
    if decision.behavioral_ml and decision.behavioral_ml.get("status") == "scored":
        assert "behavioral_ml_probability" in decision.pillar_summary


def test_actionable_affordability_metrics_and_counterfactuals():
    """calculate_actionable_affordability_metrics remains available and correct."""
    from src.decision.affordability import calculate_actionable_affordability_metrics
    features = {
        "average_monthly_income": 60_000.0,
        "effective_monthly_emi": 10_000.0,
        "average_monthly_expense": 35_000.0,
        "savings_ratio": 0.416,
    }
    metrics = calculate_actionable_affordability_metrics(features, loan_tenure_months=24, annual_interest_rate=12.0)
    assert metrics["max_sustainable_monthly_emi"] > 0
    assert metrics["max_indicative_loan_amount"] > 0
    assert metrics["stressed_income_minus_20"] == 48_000.0
    assert metrics["stressed_expense_plus_10"] == 38_500.0
    assert len(metrics["counterfactual_guidance"]) >= 1
