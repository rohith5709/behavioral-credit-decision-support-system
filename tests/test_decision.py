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


def test_strong_statement_receives_approve_recommendation():
    decision = recommend(None, _features(), quality_report=_quality_report())
    assert decision.recommendation == "Approve recommendation"
    assert decision.affordability_score >= 75


def test_low_score_statement_receives_decline_recommendation():
    decision = recommend(None, _features(savings_ratio=-0.20, emi_to_income_ratio=0.45, salary_consistency_ratio=0.8, expense_variation_ratio=0.8, utility_payment_regularity=0.0), quality_report=_quality_report())
    assert decision.recommendation == "Decline recommendation"
    assert decision.affordability_score < 45


def test_missing_salary_requests_additional_documents_even_with_good_other_signals():
    decision = recommend(None, _features(salary_income_months=0.0), quality_report=_quality_report())
    assert decision.recommendation == "Refer for additional documents"
    assert any("No salary/income" in reason for reason in decision.reasons)
