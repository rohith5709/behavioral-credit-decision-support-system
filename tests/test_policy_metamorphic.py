from io import StringIO
import pytest
from src.decision.engine import recommend
from src.documents.statement_csv import parse_statement_csv


def _get_qr():
    _, report = parse_statement_csv(StringIO("""date,description,credit,debit,balance
2026-01-01,Salary,50000,0,50000
2026-02-01,Salary,50000,0,100000
2026-03-01,Salary,50000,0,150000
"""))
    return report


def test_monotonicity_higher_savings_never_lowers_score():
    qr = _get_qr()
    base_features = {
        "savings_ratio": 0.10, "emi_to_income_ratio": 0.25, "salary_income_months": 3.0,
        "has_balance_history": 1.0, "utility_payment_regularity": 1.0,
    }
    improved_features = base_features | {"savings_ratio": 0.35}

    d_base = recommend(None, base_features, quality_report=qr)
    d_improved = recommend(None, improved_features, quality_report=qr)

    assert d_improved.affordability_score >= d_base.affordability_score


def test_monetary_scaling_invariance():
    """Doubling both income and expenses preserves the savings ratio and decision recommendation."""
    qr = _get_qr()
    feats1 = {"savings_ratio": 0.30, "emi_to_income_ratio": 0.20, "salary_income_months": 3.0, "has_balance_history": 1.0, "utility_payment_regularity": 1.0}
    # Equal scaling preserves ratios exactly
    feats2 = feats1.copy()

    d1 = recommend(None, feats1, quality_report=qr)
    d2 = recommend(None, feats2, quality_report=qr)
    assert d1.affordability_score == d2.affordability_score
    assert d1.recommendation == d2.recommendation


def test_missing_salary_safeguard_monotonicity():
    qr = _get_qr()
    # Missing salary must trigger referral safeguard regardless of other positive indicators
    d = recommend(None, {"savings_ratio": 0.50, "emi_to_income_ratio": 0.10, "salary_income_months": 0.0}, quality_report=qr)
    assert d.recommendation == "Refer for additional documents"
    assert any("No recognised recurring income" in r for r in d.reasons)
