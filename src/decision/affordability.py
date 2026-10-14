"""Transparent affordability score for compatible uploaded bank statements."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from src.documents.statement_csv import StatementQualityReport

POLICY_PATH = Path(__file__).resolve().parents[2] / "config" / "affordability_policy_v1.json"
POLICY = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
AFFORDABILITY_RULE_VERSION = POLICY["version"]


@dataclass(frozen=True)
class AffordabilityAssessment:
    """Rule-based statement assessment, intended for officer review rather than final lending."""

    score: int
    components: dict[str, float]
    reasons: list[str]
    mandatory_review_reasons: list[str]


def _savings_points(ratio: float) -> float:
    for threshold, points in POLICY["components"]["savings_ratio"]["bands"]:
        if ratio >= threshold:
            return float(points)
    return 0.0


def _emi_points(ratio: float) -> float:
    for threshold, points in POLICY["components"]["emi_burden"]["bands"]:
        if ratio <= threshold:
            return float(points)
    return 0.0


def _consistency_points(ratio: float, salary_months: float) -> float:
    if salary_months == 0:
        return 0.0
    for threshold, points in POLICY["components"]["salary_consistency"]["bands"]:
        if ratio <= threshold:
            return float(points)
    return 0.0


def _stability_points(expense_variation: float, balance_volatility: float, has_balance_history: bool) -> float:
    variation_points = 10.0 if expense_variation <= 0.15 else 7.0 if expense_variation <= 0.30 else 3.0 if expense_variation <= 0.60 else 0.0
    if not has_balance_history:
        return variation_points
    balance_points = 5.0 if balance_volatility <= 0.30 else 3.0 if balance_volatility <= 0.60 else 1.0
    return variation_points + balance_points


def assess_affordability(features: dict[str, float], quality_report: StatementQualityReport | None) -> AffordabilityAssessment:
    """Score uploaded-statement evidence using documented rule components and safeguards."""
    savings_ratio = float(features.get("savings_ratio", 0.0))
    emi_ratio = float(features.get("emi_to_income_ratio", 0.0))
    salary_months = float(features.get("salary_income_months", 0.0))
    recognised_income_months = float(features.get("recognised_income_months", salary_months))
    salary_consistency = float(features.get("salary_consistency_ratio", 1.0))
    expense_variation = float(features.get("expense_variation_ratio", 1.0))
    balance_volatility = float(features.get("balance_volatility_ratio", 0.0))
    has_balance_history = bool(features.get("has_balance_history", 0.0))
    utility_regularity = float(features.get("utility_payment_regularity", 0.0))

    components = {
        "Savings ratio (25)": _savings_points(savings_ratio),
        "EMI burden (25)": _emi_points(emi_ratio),
        "Salary consistency (20)": _consistency_points(salary_consistency, salary_months),
        "Expense stability (15)": _stability_points(expense_variation, balance_volatility, has_balance_history),
        "Utility regularity (10)": POLICY["components"]["utility_regularity"]["max_points"] * min(max(utility_regularity, 0.0), 1.0),
        "Data quality (5)": POLICY["components"]["data_quality"]["max_points"] * (quality_report.score if quality_report else 0.0),
    }
    score = int(round(sum(components.values())))
    reasons = [
        f"Savings ratio is {savings_ratio:.1%}, contributing {components['Savings ratio (25)']:.0f}/25 affordability points.",
        f"EMI burden is {emi_ratio:.1%}, contributing {components['EMI burden (25)']:.0f}/25 affordability points.",
    ]
    if recognised_income_months:
        reasons.append(f"Recognised recurring income credits were found in {recognised_income_months:.0f} observed month(s).")
    if utility_regularity:
        reasons.append(f"Utility payments appeared in {utility_regularity:.0%} of observed months.")

    mandatory_review_reasons: list[str] = []
    hard_stops = POLICY["hard_stops"]
    if not quality_report or quality_report.observed_months < hard_stops["minimum_months"]:
        mandatory_review_reasons.append("Fewer than three months of transactions are available.")
    if not quality_report or quality_report.score < hard_stops["minimum_quality_score"]:
        mandatory_review_reasons.append("Statement data quality is below the 80% review threshold.")
    if recognised_income_months == 0:
        mandatory_review_reasons.append("No recognised recurring income was found in the uploaded statement.")
    if quality_report and quality_report.balance_mismatch_rows:
        mandatory_review_reasons.append("Balance transitions contradict the stated debit/credit values.")
    if emi_ratio > hard_stops["maximum_existing_emi_ratio"]:
        mandatory_review_reasons.append("EMI burden exceeds the 50% critical review threshold.")
    if float(features.get("proposed_emi_to_income_ratio", 0.0)) > hard_stops["maximum_proposed_emi_ratio"]:
        mandatory_review_reasons.append("Existing plus proposed EMI burden exceeds the critical review threshold.")
    if (
        float(features.get("emi_difference_amount", 0.0)) >= hard_stops["emi_discrepancy_minimum_amount"]
        and float(features.get("emi_discrepancy_ratio", 0.0)) > hard_stops["emi_discrepancy_tolerance"]
    ):
        mandatory_review_reasons.append(
            "Declared EMI and detected EMI-payment occurrence differ materially; officer verification is required."
        )
    # Older or externally supplied feature dictionaries may not include this
    # Phase-6 measure. Missing evidence must be shown as unavailable, not
    # silently converted to a zero-month buffer and treated as a hard stop.
    if (
        bool(features.get("has_balance_history", 0.0))
        and "emergency_buffer_months" in features
        and float(features["emergency_buffer_months"]) < hard_stops["minimum_emergency_buffer_months"]
    ):
        mandatory_review_reasons.append("Emergency cash buffer is below the policy review threshold.")
    if float(features.get("uncertain_transaction_share", 0.0)) > hard_stops["maximum_uncertain_transaction_share"]:
        mandatory_review_reasons.append("Too many transaction categories require officer review.")
    return AffordabilityAssessment(score, components, reasons, mandatory_review_reasons)
