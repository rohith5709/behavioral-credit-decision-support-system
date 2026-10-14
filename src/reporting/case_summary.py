"""Build concise, exportable summaries for officer review."""
from __future__ import annotations

from typing import Any

import pandas as pd

from src.decision.engine import Decision
from src.documents.statement_csv import StatementQualityReport


REVIEW_MARKERS = (
    "Fewer than", "quality", "No recognised", "contradict", "critical review threshold",
    "Emergency cash buffer", "Too many transaction categories", "differ materially",
)


def case_status(recommendation: str) -> tuple[str, str]:
    """Return a human-readable traffic-light aid without changing the decision meaning."""
    if recommendation == "Meets indicative affordability criteria":
        return "Green", "Available statement evidence meets indicative affordability criteria."
    if recommendation in {"Manual review", "Refer for additional documents"}:
        return "Amber", "Officer review or additional evidence is required."
    return "Red", "Available statement evidence does not meet indicative affordability criteria."


def extract_review_flags(reasons: list[str]) -> list[str]:
    """Keep only safeguard/evidence-gap reasons for the case-review checklist."""
    return [reason for reason in reasons if any(marker.lower() in reason.lower() for marker in REVIEW_MARKERS)]


def build_case_summary_rows(
    features: dict[str, Any], quality_report: StatementQualityReport, decision: Decision,
    requested_amount: float, proposed_emi: float, applicant_id: str | None = None,
) -> pd.DataFrame:
    """Build an officer-readable summary table with explicit unavailable values."""
    status, _ = case_status(decision.recommendation)
    months = max(float(features.get("months_observed", 1.0)), 1.0)
    has_balance_history = bool(features.get("has_balance_history", False))
    min_balance = features.get("minimum_daily_balance")
    rows: list[dict[str, object]] = [
        {"Section": "Request", "Metric": "Applicant ID", "Value": applicant_id or "Not supplied", "Meaning": "Officer-entered prototype identifier."},
        {"Section": "Request", "Metric": "Requested amount", "Value": f"₹{requested_amount:,.0f}", "Meaning": "Officer-entered request."},
        {"Section": "Assessment", "Metric": "Visual status", "Value": status, "Meaning": "Visual aid only; read the written recommendation and flags."},
        {"Section": "Assessment", "Metric": "System recommendation", "Value": decision.recommendation, "Meaning": "Not a final lending decision."},
        {"Section": "Assessment", "Metric": "Affordability score", "Value": f"{decision.affordability_score}/100" if decision.affordability_score is not None else "Not available", "Meaning": "Transparent policy score."},
        {"Section": "Assessment", "Metric": "Policy version", "Value": decision.rule_version or "Not available", "Meaning": "Versioned transparent affordability policy."},
        {"Section": "Evidence", "Metric": "Statement quality", "Value": f"{quality_report.score:.0%}", "Meaning": "CSV completeness and consistency; not source-document authenticity."},
        {"Section": "Evidence", "Metric": "Observed months", "Value": quality_report.observed_months, "Meaning": "Months represented by valid transactions."},
        {"Section": "Evidence", "Metric": "Statement date range", "Value": f"{quality_report.date_range_start or 'Not available'} to {quality_report.date_range_end or 'Not available'}", "Meaning": "Valid transaction period represented in the upload."},
        {"Section": "Cash flow", "Metric": "Recognised monthly income", "Value": f"₹{float(features.get('average_monthly_income', 0.0)):,.0f}", "Meaning": "Salary/income evidence and conservative recurring candidates only."},
        {"Section": "Cash flow", "Metric": "Other monthly credits", "Value": f"₹{float(features.get('other_statement_credits', 0.0)) / months:,.0f}", "Meaning": "Excluded from affordability income until verified."},
        {"Section": "Cash flow", "Metric": "Uncertain statement credits", "Value": f"₹{float(features.get('uncertain_statement_credits', 0.0)):,.0f}", "Meaning": "Credits whose category requires officer review; not treated as income."},
        {"Section": "Cash flow", "Metric": "Monthly expense", "Value": f"₹{float(features.get('average_monthly_expense', 0.0)):,.0f}", "Meaning": "Observed debit spending in this account."},
        {"Section": "Cash flow", "Metric": "Before-loan monthly surplus", "Value": f"₹{float(features.get('monthly_surplus', 0.0)):,.0f}", "Meaning": "Recognised income minus observed expense."},
        {"Section": "Loan impact", "Metric": "Existing effective EMI", "Value": f"₹{float(features.get('effective_monthly_emi', 0.0)):,.0f}", "Meaning": "Higher of declared EMI and detected EMI-payment occurrence."},
        {"Section": "Loan impact", "Metric": "Estimated proposed EMI", "Value": f"₹{proposed_emi:,.0f}", "Meaning": "Illustrative amortisation calculation, not a loan offer."},
        {"Section": "Loan impact", "Metric": "Post-loan monthly surplus", "Value": f"₹{float(features.get('post_loan_monthly_surplus', 0.0)):,.0f}", "Meaning": "Recognised income minus observed expense and estimated new EMI."},
        {"Section": "Loan impact", "Metric": "Post-loan EMI burden", "Value": f"{float(features.get('proposed_emi_to_income_ratio', 0.0)):.1%}" if features.get("average_monthly_income", 0.0) else "Not available", "Meaning": "Existing effective EMI plus estimated new EMI divided by recognised income."},
        {"Section": "Liquidity", "Metric": "Emergency buffer", "Value": f"{float(features.get('emergency_buffer_months', 0.0)):.1f} months" if has_balance_history else "Not available", "Meaning": "Average closing balance divided by average monthly expense."},
        {"Section": "Liquidity", "Metric": "Minimum observed daily balance", "Value": f"₹{float(min_balance):,.0f}" if has_balance_history and min_balance is not None else "Not available", "Meaning": "Lowest reconstructed daily closing balance in the uploaded period."},
        {"Section": "Evidence", "Metric": "Uncertain category share", "Value": f"{float(features.get('uncertain_transaction_share', 0.0)):.1%}", "Meaning": "Transactions with no clear or multiple category-rule matches."},
    ]
    rows.extend(
        {
            "Section": "Score breakdown",
            "Metric": component,
            "Value": f"{points:.1f}",
            "Meaning": "Policy component points; safeguards can override the score.",
        }
        for component, points in (decision.affordability_components or {}).items()
    )
    return pd.DataFrame(rows)


def build_decision_record(
    base_record: dict[str, Any], decision: Decision, quality_report: StatementQualityReport | None,
) -> dict[str, Any]:
    """Enrich a prototype decision log with scope, status, flags, and policy evidence."""
    status, status_message = case_status(decision.recommendation)
    return base_record | {
        "record_type": "prototype_decision_log",
        "visual_status": status,
        "status_message": status_message,
        "mandatory_review_flags": extract_review_flags(decision.reasons),
        "statement_quality_warnings": list(quality_report.warnings) if quality_report else [],
        "evidence_boundary": (
            "CSV statement evidence from one uploaded account only. It does not authenticate documents, "
            "verify employment, or observe other accounts, household costs, cash income, or off-statement liabilities."
        ),
        "home_credit_model_scope": "Separate benchmark only; not applied to this uploaded statement.",
    }
