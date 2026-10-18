"""Transparent, policy-based recommendation engine incorporating dual-pillar decisioning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

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
    pillar_summary: dict[str, Any] | None = None


def recommend(
    model_probability: float | None,
    statement_features: dict[str, float] | None = None,
    extraction_confidence: float | None = None,
    quality_report: StatementQualityReport | None = None,
    salary_verification: Any | None = None,
) -> Decision:
    """Produce a reviewable recommendation; never a final lending decision.

    When both statement_features and model_probability are provided, evaluates
    a unified Dual-Pillar 2x2 decision matrix:
      Pillar 1: Bank Statement Affordability Score (0-100) & cash-flow safeguards
      Pillar 2: Bureau ML Default Risk Probability (0.0-1.0) with review alert threshold (0.20)
    """
    # -------------------------------------------------------------
    # Helper: Check salary slip cross-document verification
    # -------------------------------------------------------------
    salary_slip_reasons = []
    salary_slip_flagged = False
    if salary_verification is not None:
        is_verified = getattr(salary_verification, "is_verified", None)
        if is_verified is False:
            salary_slip_flagged = True
            slip_amt = getattr(salary_verification, "slip_net_salary", 0.0)
            stmt_amt = getattr(salary_verification, "detected_statement_salary", 0.0)
            ratio = getattr(salary_verification, "discrepancy_ratio", 0.0)
            salary_slip_reasons.append(
                f"Salary slip cross-verification failed: Declared ₹{slip_amt:,.0f} vs statement ₹{stmt_amt:,.0f} "
                f"({ratio:.1%} discrepancy exceeds 15% tolerance threshold)."
            )
            salary_slip_reasons.append("Mandatory cross-document safeguard: Inconsistent declared income requires officer review.")

    # -------------------------------------------------------------
    # Scenario 1: Statement Affordability Only (No Bureau Model)
    # -------------------------------------------------------------
    if statement_features is not None and model_probability is None:
        assessment = assess_affordability(statement_features, quality_report)
        reasons = assessment.reasons + assessment.mandatory_review_reasons + salary_slip_reasons

        if salary_slip_flagged:
            recommendation = "Refer for additional documents"
        elif assessment.mandatory_review_reasons:
            evidence_gaps = (
                "Fewer than three months",
                "Statement data quality",
                "No recognised recurring income",
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
            recommendation = "Meets indicative affordability criteria"
        elif assessment.score < POLICY["decision_bands"]["manual_review_at"]:
            reasons.append(f"Affordability score is below the {POLICY['decision_bands']['manual_review_at']}-point threshold.")
            recommendation = "Does not meet indicative affordability criteria"
        else:
            reasons.append(
                f"Affordability score is in the {POLICY['decision_bands']['manual_review_at']}–"
                f"{POLICY['decision_bands']['approve_at'] - 1} officer-review band."
            )
            recommendation = "Manual review"

        return Decision(
            recommendation=recommendation,
            reasons=reasons,
            model_probability=None,
            affordability_score=assessment.score,
            affordability_components=assessment.components,
            rule_version=AFFORDABILITY_RULE_VERSION,
            pillar_summary={
                "mode": "Single-Pillar (Statement Affordability)",
                "affordability_score": assessment.score,
                "affordability_band": "High" if assessment.score >= POLICY["decision_bands"]["approve_at"] else ("Low" if assessment.score < POLICY["decision_bands"]["manual_review_at"] else "Moderate"),
                "bureau_risk": "Not evaluated",
            },
        )

    # -------------------------------------------------------------
    # Scenario 2: Dual-Pillar 2x2 Matrix (Statement + Bureau ML Model)
    # -------------------------------------------------------------
    if statement_features is not None and model_probability is not None:
        assessment = assess_affordability(statement_features, quality_report)
        reasons = assessment.reasons + assessment.mandatory_review_reasons + salary_slip_reasons

        high_affordability = assessment.score >= POLICY["decision_bands"]["approve_at"]
        low_bureau_risk = model_probability < LOW_RISK_THRESHOLD

        if high_affordability:
            affordability_band = "High Affordability (Score >= 70)"
        elif assessment.score < POLICY["decision_bands"]["manual_review_at"]:
            affordability_band = "Low Affordability (Score < 45)"
        else:
            affordability_band = "Moderate Affordability (45-69)"

        bureau_risk_band = "Low Default Risk (< 20%)" if low_bureau_risk else "Elevated Default Risk (>= 20%)"

        if salary_slip_flagged:
            recommendation = "Refer for additional documents"
            quadrant = "Document Safeguard Override (Refer)"
        elif assessment.mandatory_review_reasons:
            evidence_gaps = (
                "Fewer than three months",
                "Statement data quality",
                "No recognised recurring income",
                "Too many transaction categories",
            )
            if any(reason.startswith(evidence_gaps) for reason in assessment.mandatory_review_reasons):
                reasons.append("Additional reliable evidence is needed before an officer can complete review.")
                recommendation = "Refer for additional documents"
                quadrant = "Evidence Gap Safeguard (Refer)"
            else:
                reasons.append("Mandatory review safeguard applies regardless of scores.")
                recommendation = "Manual review"
                quadrant = "Safeguard Override (Manual Review)"
        else:
            # 2x2 Matrix Logic
            if high_affordability and low_bureau_risk:
                recommendation = "Meets indicative affordability criteria"
                reasons.append("Dual-Pillar Alignment: High affordability score (>=70) and low bureau credit risk (<20%).")
                quadrant = "High Affordability / Low Risk (Recommend Approval)"
            elif high_affordability and not low_bureau_risk:
                recommendation = "Manual review"
                reasons.append(
                    f"Dual-Pillar Divergence: High statement affordability ({assessment.score}/100) conflicts with elevated bureau credit risk ({model_probability:.1%}). Officer review required."
                )
                quadrant = "High Affordability / Elevated Risk (Manual Review - Divergent Evidence)"
            elif not high_affordability and low_bureau_risk:
                if assessment.score < POLICY["decision_bands"]["manual_review_at"]:
                    recommendation = "Refer for additional documents"
                    reasons.append(
                        f"Dual-Pillar Divergence: Clean bureau history ({model_probability:.1%}), but statement cash flows are severely constrained ({assessment.score}/100). Consider loan restructuring, lower loan amount, or co-applicant."
                    )
                    quadrant = "Low Affordability / Low Risk (Refer / Restructure)"
                else:
                    recommendation = "Manual review"
                    reasons.append(
                        f"Dual-Pillar Divergence: Clean bureau history ({model_probability:.1%}), but borderline statement affordability ({assessment.score}/100). Officer review required."
                    )
                    quadrant = "Moderate Affordability / Low Risk (Manual Review)"
            else:
                # not high_affordability and not low_bureau_risk
                recommendation = "Does not meet indicative affordability criteria"
                reasons.append(
                    f"Dual-Pillar Alignment: Constrained statement affordability ({assessment.score}/100) and elevated bureau credit risk ({model_probability:.1%})."
                )
                quadrant = "Low Affordability / Elevated Risk (Recommend Decline)"

        pillar_summary = {
            "mode": "Dual-Pillar (Statement Affordability x Bureau Default Risk)",
            "affordability_score": assessment.score,
            "affordability_band": affordability_band,
            "model_probability": model_probability,
            "bureau_risk_band": bureau_risk_band,
            "quadrant": quadrant,
        }

        return Decision(
            recommendation=recommendation,
            reasons=reasons,
            model_probability=model_probability,
            affordability_score=assessment.score,
            affordability_components=assessment.components,
            rule_version=AFFORDABILITY_RULE_VERSION,
            pillar_summary=pillar_summary,
        )

    # -------------------------------------------------------------
    # Scenario 3: Bureau ML Model Only (No Statement Features)
    # -------------------------------------------------------------
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
        return Decision("Does not meet indicative affordability criteria", reasons, model_probability)
    if model_probability >= LOW_RISK_THRESHOLD or reasons:
        reasons.append("Predicted default risk or affordability indicators require an officer review.")
        return Decision("Manual review", reasons, model_probability)

    reasons.append("Predicted risk is low and no affordability rule was triggered.")
    return Decision("Meets indicative affordability criteria", reasons, model_probability)
