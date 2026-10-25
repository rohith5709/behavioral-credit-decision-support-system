from io import StringIO

from src.decision.engine import recommend
from src.documents.statement_csv import parse_statement_csv
from src.reporting.case_summary import (
    build_case_summary_rows,
    build_decision_record,
    case_status,
    extract_review_flags,
)


def _quality_report():
    _, report = parse_statement_csv(StringIO("""date,description,credit,debit,balance
2026-01-01,Salary,50000,0,50000
2026-02-01,Salary,50000,0,100000
2026-03-01,Salary,50000,0,150000
"""))
    return report


def _features():
    return {
        "savings_ratio": 0.35, "emi_to_income_ratio": 0.15,
        "salary_income_months": 3.0, "recognised_income_months": 3.0,
        "salary_consistency_ratio": 0.02, "expense_variation_ratio": 0.10,
        "balance_volatility_ratio": 0.20, "has_balance_history": 1.0,
        "utility_payment_regularity": 1.0, "emergency_buffer_months": 1.0,
        "uncertain_transaction_share": 0.0, "proposed_emi_to_income_ratio": 0.20,
        "average_monthly_income": 50_000.0, "other_statement_credits": 6_000.0,
        "months_observed": 3.0, "average_monthly_expense": 25_000.0,
        "post_loan_monthly_surplus": 20_000.0,
    }


def test_case_summary_rows_keep_evidence_scope_and_loan_impact():
    report = _quality_report()
    decision = recommend(None, _features(), quality_report=report)
    summary = build_case_summary_rows(_features(), report, decision, 100_000, 5_000, "APP-1")
    assert {"Request", "Assessment", "Evidence", "Cash flow", "Loan impact", "Liquidity", "Score breakdown"}.issubset(set(summary["Section"]))
    assert summary.loc[summary["Metric"].eq("Applicant ID"), "Value"].iloc[0] == "APP-1"
    assert summary.loc[summary["Metric"].eq("Policy version"), "Value"].iloc[0] == "statement-affordability-v1"
    assert "Recognised monthly income" in summary["Metric"].tolist()
    assert "₹2,000" in summary.loc[summary["Metric"].eq("Other monthly credits"), "Value"].iloc[0]


def test_case_summary_marks_missing_balance_evidence_as_unavailable():
    report = _quality_report()
    decision = recommend(None, _features() | {"has_balance_history": 0.0}, quality_report=report)
    summary = build_case_summary_rows(_features() | {"has_balance_history": 0.0}, report, decision, 100_000, 5_000)
    assert summary.loc[summary["Metric"].eq("Emergency buffer"), "Value"].iloc[0] == "Not available"


def test_decision_record_carries_scope_and_review_flags():
    report = _quality_report()
    features = _features() | {"emi_difference_amount": 5_000.0, "emi_discrepancy_ratio": 0.50}
    decision = recommend(None, features, quality_report=report)
    record = build_decision_record({"applicant_id": "APP-1"}, decision, report)
    assert record["record_type"] == "prototype_decision_log"
    assert record["mandatory_review_flags"]
    assert "one uploaded account" in record["evidence_boundary"]


def test_status_and_review_flag_helpers_are_explicit():
    assert case_status("Meets indicative affordability criteria")[0] == "Green"
    assert case_status("Manual review")[0] == "Amber"
    assert case_status("Does not meet indicative affordability criteria")[0] == "Red"
    assert extract_review_flags(["Savings ratio is 20.0%.", "Fewer than three months of transactions are available."])


def test_decision_record_integrates_unsupervised_ml_anomaly():
    report = _quality_report()
    decision = recommend(None, _features(), quality_report=report)
    behavioral_profile = {
        "status": "scored",
        "anomaly_detection": {
            "is_anomaly": True,
            "anomaly_score": 0.82,
            "verdict": "Elevated Cash Flow Outlier Detected",
        },
        "behavioral_persona": {
            "name": "Volatile Cash Flow / Gig Earner",
            "risk_profile": "Moderate to High Risk",
        },
    }
    record = build_decision_record({"applicant_id": "APP-ANOM-1"}, decision, report, behavioral_profile=behavioral_profile)
    assert record["record_type"] == "prototype_decision_log"
    assert "behavioral_unsupervised_ml" in record
    assert any("Isolation Forest detected atypical cash flow volatility" in flag for flag in record["mandatory_review_flags"])

