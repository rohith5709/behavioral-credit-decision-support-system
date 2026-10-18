"""Cross-document verification between declared salary slip and bank statement credits."""
from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class SalaryVerificationResult:
    """Outcomes of comparing declared salary slip with bank statement evidence."""

    is_verified: bool
    slip_net_salary: float
    detected_statement_salary: float
    discrepancy_amount: float
    discrepancy_ratio: float
    employer_name: str | None
    employer_matched_in_statement: bool
    status: str
    reasons: list[str]


def verify_salary_slip_cross_document(
    statement_transactions: pd.DataFrame,
    slip_net_salary: float,
    employer_name: str | None = None,
    tolerance_ratio: float = 0.15,
) -> SalaryVerificationResult:
    """Cross-verify salary slip net amount and employer against bank statement credits.

    A material difference (>15%) triggers a discrepancy alert for officer review.
    """
    if "category" not in statement_transactions or "credit" not in statement_transactions:
        raise ValueError("Transactions must be categorised before salary verification.")

    salary_tx = statement_transactions[
        statement_transactions["category"].eq("Salary/income") & (statement_transactions["credit"] > 0)
    ]

    reasons = []
    if salary_tx.empty:
        return SalaryVerificationResult(
            is_verified=False,
            slip_net_salary=float(slip_net_salary),
            detected_statement_salary=0.0,
            discrepancy_amount=float(slip_net_salary),
            discrepancy_ratio=1.0,
            employer_name=employer_name,
            employer_matched_in_statement=False,
            status="CRITICAL: No matching salary credits detected on bank statement",
            reasons=["No credits labelled as Salary/income were detected in the statement period."],
        )

    # Average monthly salary detected in statement
    detected_avg_salary = float(salary_tx["credit"].mean())
    discrepancy_amount = abs(detected_avg_salary - slip_net_salary)
    discrepancy_ratio = discrepancy_amount / max(slip_net_salary, 1.0)

    # Check employer name occurrence in descriptions
    employer_matched = False
    if employer_name and employer_name.strip():
        emp_clean = employer_name.strip().lower()
        descriptions = salary_tx["description"].fillna("").astype(str).str.lower()
        employer_matched = bool(descriptions.str.contains(emp_clean, regex=False).any())

    is_within_tolerance = discrepancy_ratio <= tolerance_ratio
    if is_within_tolerance:
        status = "VERIFIED: Salary slip aligns with bank statement credits"
        reasons.append(
            f"Detected statement salary (₹{detected_avg_salary:,.0f}) is within {discrepancy_ratio:.1%} "
            f"of declared salary slip net pay (₹{slip_net_salary:,.0f})."
        )
    else:
        status = "DISCREPANCY: Material variance between salary slip and statement credits"
        reasons.append(
            f"Variance of ₹{discrepancy_amount:,.0f} ({discrepancy_ratio:.1%}) exceeds "
            f"the {tolerance_ratio:.0%} policy review tolerance."
        )

    if employer_name:
        if employer_matched:
            reasons.append(f"Employer name '{employer_name}' was identified in statement transaction narrations.")
        else:
            reasons.append(f"Employer name '{employer_name}' was not found in statement transaction narrations.")

    return SalaryVerificationResult(
        is_verified=is_within_tolerance,
        slip_net_salary=float(slip_net_salary),
        detected_statement_salary=round(detected_avg_salary, 2),
        discrepancy_amount=round(discrepancy_amount, 2),
        discrepancy_ratio=round(discrepancy_ratio, 4),
        employer_name=employer_name,
        employer_matched_in_statement=employer_matched,
        status=status,
        reasons=reasons,
    )
