"""Transparent, policy-based recommendation engine."""
from __future__ import annotations

from dataclasses import dataclass

from src.config import HIGH_RISK_THRESHOLD, LOW_RISK_THRESHOLD, MAX_EMI_TO_INCOME, MIN_EXTRACTION_CONFIDENCE
from src.decision.affordability import AFFORDABILITY_RULE_VERSION, POLICY, assess_affordability
from src.documents.statement_csv import StatementQualityReport


@dataclass(frozen=True)
class Decision:
    recommendation: str
    reasons: list[str]
    model_probability: float | None
    affordability_score: int | None = None
    affordability_components: dict[str, float] | None = None
    rule_version: str | None = None


def recommend(
    model_probability: float | None,
    statement_features: dict[str, float] | None = None,
    extraction_confidence: float | None = None,
    quality_report: StatementQualityReport | None = None,
) -> Decision:
    """Produce a reviewable recommendation; never a final lending decision."""
    if statement_features is not None and model_probability is None:
        assessment = assess_affordability(statement_features, quality_report)
        reasons = assessment.reasons + assessment.mandatory_review_reasons
        if assessment.mandatory_review_reasons:
            evidence_gaps = (
                "Fewer than three months",
                "Statement data quality",
                "No salary/income",
                "Too many transaction categories",
            )
            if any(reason.startswith(evidence_gaps) for reason in assessment.mandatory_review_reasons):
                reasons.append("Additional reliable evidence is needed before an officer can complete review.")
                recommendation = "Refer for additional documents"
            else:
                reasons.append("Mandatory review safeguard applies regardless of the affordability score.")
                recommendation = "Manual review"
        elif assessment.score >= POLICY["decision_bands"]["approve_at"]:
            reasons.append(f"Affordability score meets the {POLICY['decision_bands']['approve_at']}-point recommendation threshold.")
            recommendation = "Approve recommendation"
        elif assessment.score < POLICY["decision_bands"]["manual_review_at"]:
            reasons.append(f"Affordability score is below the {POLICY['decision_bands']['manual_review_at']}-point threshold.")
            recommendation = "Decline recommendation"
        else:
            reasons.append(
                f"Affordability score is in the {POLICY['decision_bands']['manual_review_at']}–"
                f"{POLICY['decision_bands']['approve_at'] - 1} officer-review band."
            )
            recommendation = "Manual review"
        return Decision(recommendation, reasons, None, assessment.score, assessment.components, AFFORDABILITY_RULE_VERSION)

    reasons: list[str] = []
    features = statement_features or {}

    if extraction_confidence is not None and extraction_confidence < MIN_EXTRACTION_CONFIDENCE:
        reasons.append("Document extraction confidence is low; the data requires officer verification.")
    if features.get("emi_to_income_ratio", 0.0) > MAX_EMI_TO_INCOME:
        reasons.append("EMI burden exceeds 50% of observed monthly income.")
    if features.get("savings_ratio", 0.0) < 0:
        reasons.append("Observed monthly expenses are higher than observed monthly income.")
    if model_probability is None:
        reasons.append("No validated credit-risk score is available for this applicant profile.")
        return Decision("Manual review", reasons, None)
    if model_probability >= HIGH_RISK_THRESHOLD:
        reasons.append("Predicted default risk is in the high-risk band.")
        return Decision("Decline recommendation", reasons, model_probability)
    if model_probability >= LOW_RISK_THRESHOLD or reasons:
        reasons.append("Predicted default risk or affordability indicators require an officer review.")
        return Decision("Manual review", reasons, model_probability)

    reasons.append("Predicted risk is low and no affordability rule was triggered.")
    return Decision("Approve recommendation", reasons, model_probability)
