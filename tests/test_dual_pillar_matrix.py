"""Tests for the ML-driven dual-pillar decision matrix.

The dual-pillar matrix now combines:
  Pillar 1 — Behavioral ML (statement-derived, trained Random Forest)
  Pillar 2 — Bureau ML (LightGBM, applicant profile-derived)

The 2x2 matrix logic is: behavioral_pd (ML) x bureau_pd (LightGBM).
These tests verify the correct quadrant assignment and recommendation
for each combination of high/low behavioral and bureau risk.
"""
from __future__ import annotations

from io import StringIO

import pytest

from src.decision.engine import recommend
from src.documents.statement_csv import parse_statement_csv
from src.documents.salary_verification import SalaryVerificationResult


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


def _high_stress_features(**overrides: float) -> dict[str, float]:
    """Feature set that produces elevated behavioral ML risk."""
    base = {
        "savings_ratio": -0.20,
        "emi_to_income_ratio": 0.65,
        "salary_income_months": 3.0,
        "salary_consistency_ratio": 0.80,
        "expense_variation_ratio": 0.70,
        "balance_volatility_ratio": 0.80,
        "has_balance_history": 1.0,
        "utility_payment_regularity": 0.10,
        "missed_salary_months": 2.0,
        "low_balance_day_count": 15.0,
        "emergency_buffer_months": 0.1,
        "monthly_surplus": -5000.0,
        "minimum_monthly_surplus": -8000.0,
        "average_monthly_income": 25000.0,
        "average_monthly_expense": 30000.0,
        "income_variation_ratio": 0.60,
    }
    return base | overrides


def _quality_report():
    _, report = parse_statement_csv(StringIO("""date,description,credit,debit,balance
2026-01-01,Salary,50000,0,50000
2026-02-01,Salary,50000,0,100000
2026-03-01,Salary,50000,0,150000
"""))
    return report


class TestDualPillarMLMatrix:
    """Dual-pillar 2x2 matrix: behavioral ML x bureau ML."""

    def test_dual_pillar_low_behavioral_and_low_bureau_approves(self):
        """Pillar alignment: both ML signals low → Recommend Approval."""
        decision = recommend(
            model_probability=0.08,
            statement_features=_features(),
            quality_report=_quality_report(),
        )
        assert decision.recommendation == "Meets indicative affordability criteria"
        assert decision.pillar_summary is not None
        assert "Recommend Approval" in decision.pillar_summary["quadrant"]
        assert any("Dual-Pillar Alignment" in r for r in decision.reasons)

    def test_dual_pillar_low_behavioral_and_elevated_bureau_triggers_review(self):
        """Divergence: bureau risk elevated but behavioral ML low → Manual review."""
        decision = recommend(
            model_probability=0.35,
            statement_features=_features(),
            quality_report=_quality_report(),
        )
        assert decision.recommendation == "Manual review"
        assert decision.pillar_summary is not None
        assert "Divergent Evidence" in decision.pillar_summary["quadrant"]

    def test_dual_pillar_high_behavioral_and_low_bureau_triggers_review(self):
        """Divergence: behavioral ML elevated but bureau clean → Manual review."""
        decision = recommend(
            model_probability=0.08,
            statement_features=_high_stress_features(),
            quality_report=_quality_report(),
        )
        assert decision.recommendation == "Manual review"
        assert decision.pillar_summary is not None
        # Should be divergent or decline depending on behavioral_pd level
        assert decision.recommendation in {"Manual review", "Does not meet indicative affordability criteria"}

    def test_dual_pillar_result_has_behavioral_ml_in_summary(self):
        """Pillar summary must expose both ML signals."""
        decision = recommend(
            model_probability=0.08,
            statement_features=_features(),
            quality_report=_quality_report(),
        )
        assert decision.pillar_summary is not None
        assert "behavioral_ml_probability" in decision.pillar_summary
        assert "model_probability" in decision.pillar_summary

    def test_dual_pillar_mode_label_reflects_ml(self):
        """Pillar summary mode must reference Behavioral ML."""
        decision = recommend(
            model_probability=0.08,
            statement_features=_features(),
            quality_report=_quality_report(),
        )
        assert decision.pillar_summary is not None
        assert "Behavioral ML" in decision.pillar_summary["mode"]

    def test_salary_slip_discrepancy_safeguard_forces_referral(self):
        """Salary verification failure overrides ML recommendation."""
        failed_verification = SalaryVerificationResult(
            is_verified=False,
            slip_net_salary=80_000.0,
            detected_statement_salary=50_000.0,
            discrepancy_amount=30_000.0,
            discrepancy_ratio=0.375,
            employer_name="Acme Corp",
            employer_matched_in_statement=True,
            status="DISCREPANCY: Declared net salary differs significantly",
            reasons=["Discrepancy ratio 37.5% exceeds tolerance 15.0%"],
        )
        decision = recommend(
            model_probability=0.05,
            statement_features=_features(),
            quality_report=_quality_report(),
            salary_verification=failed_verification,
        )
        assert decision.recommendation == "Refer for additional documents"
        assert any("Salary slip cross-verification failed" in r for r in decision.reasons)

    def test_hard_stop_no_salary_forces_referral_in_dual_pillar(self):
        """Hard stop: missing income evidence overrides ML in dual-pillar mode."""
        decision = recommend(
            model_probability=0.05,
            statement_features=_features(salary_income_months=0.0),
            quality_report=_quality_report(),
        )
        assert decision.recommendation == "Refer for additional documents"
        assert any("No recognised recurring income" in r for r in decision.reasons)

    def test_decision_has_behavioral_ml_field(self):
        """Decision dataclass must carry the behavioral_ml result."""
        decision = recommend(
            model_probability=0.08,
            statement_features=_features(),
            quality_report=_quality_report(),
        )
        assert decision.behavioral_ml is not None
        assert "status" in decision.behavioral_ml

    def test_decision_has_unsupervised_ml_field(self):
        """Decision dataclass must carry the unsupervised_ml result."""
        decision = recommend(
            model_probability=0.08,
            statement_features=_features(),
            quality_report=_quality_report(),
        )
        assert decision.unsupervised_ml is not None
        assert "status" in decision.unsupervised_ml

    def test_isolation_forest_anomaly_overrides_clean_ml_profile_to_manual_review(self):
        """Tier 3 Anomaly Safeguard: Outlier volatility forces officer review despite low PD."""
        outlier_features = {
            "savings_ratio": 0.10,
            "emi_to_income_ratio": 0.10,
            "salary_income_months": 3.0,
            "salary_consistency_ratio": 0.02,
            "expense_variation_ratio": 2.5,
            "balance_volatility_ratio": 4.0,
            "has_balance_history": 1.0,
            "utility_payment_regularity": 1.0,
            "cash_withdrawal_share": 0.95,
            "low_balance_day_count": 25.0,
        }
        decision = recommend(
            model_probability=0.08,  # Bureau low
            statement_features=outlier_features,
            quality_report=_quality_report(),
        )
        assert decision.recommendation == "Manual review"
        assert any("Unsupervised ML Anomaly Safeguard" in r for r in decision.reasons)

    def test_evaluate_data_quality_gates_directly(self):
        """evaluate_data_quality_gates function correctly identifies hard stops."""
        from src.decision.affordability import evaluate_data_quality_gates
        clean_reasons = evaluate_data_quality_gates(_features(), _quality_report())
        assert clean_reasons == []

        failing_reasons = evaluate_data_quality_gates(_features(emi_to_income_ratio=0.60), _quality_report())
        assert any("EMI burden exceeds" in r for r in failing_reasons)
