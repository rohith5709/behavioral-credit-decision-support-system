from io import StringIO
from dataclasses import dataclass
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


def _quality_report():
    _, report = parse_statement_csv(StringIO("""date,description,credit,debit,balance
2026-01-01,Salary,50000,0,50000
2026-02-01,Salary,50000,0,100000
2026-03-01,Salary,50000,0,150000
"""))
    return report


def test_dual_pillar_high_affordability_and_low_risk_approves():
    decision = recommend(
        model_probability=0.08,
        statement_features=_features(),
        quality_report=_quality_report(),
    )
    assert decision.recommendation == "Meets indicative affordability criteria"
    assert decision.pillar_summary is not None
    assert "Recommend Approval" in decision.pillar_summary["quadrant"]
    assert any("Dual-Pillar Alignment" in r for r in decision.reasons)


def test_dual_pillar_high_affordability_and_high_risk_triggers_manual_review():
    decision = recommend(
        model_probability=0.35,
        statement_features=_features(),
        quality_report=_quality_report(),
    )
    assert decision.recommendation == "Manual review"
    assert decision.pillar_summary is not None
    assert "Divergent Evidence" in decision.pillar_summary["quadrant"]
    assert any("Dual-Pillar Divergence" in r for r in decision.reasons)


def test_dual_pillar_low_affordability_and_low_risk_refers_restructure():
    decision = recommend(
        model_probability=0.08,
        statement_features=_features(savings_ratio=-0.20, emi_to_income_ratio=0.45, salary_consistency_ratio=0.8, expense_variation_ratio=0.8, utility_payment_regularity=0.0),
        quality_report=_quality_report(),
    )
    assert decision.recommendation == "Refer for additional documents"
    assert decision.pillar_summary is not None
    assert "Refer / Restructure" in decision.pillar_summary["quadrant"]
    assert any("Dual-Pillar Divergence" in r for r in decision.reasons)


def test_dual_pillar_low_affordability_and_high_risk_declines():
    decision = recommend(
        model_probability=0.35,
        statement_features=_features(savings_ratio=-0.20, emi_to_income_ratio=0.45, salary_consistency_ratio=0.8, expense_variation_ratio=0.8, utility_payment_regularity=0.0),
        quality_report=_quality_report(),
    )
    assert decision.recommendation == "Does not meet indicative affordability criteria"
    assert decision.pillar_summary is not None
    assert "Recommend Decline" in decision.pillar_summary["quadrant"]
    assert any("Dual-Pillar Alignment" in r for r in decision.reasons)


def test_salary_slip_discrepancy_safeguard_forces_referral():
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
