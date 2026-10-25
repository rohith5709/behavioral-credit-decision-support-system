"""Transparent, policy-based recommendation engine incorporating dual-pillar decisioning.

Decision architecture
----------------------
Pillar 1 — Behavioral ML Risk (this module, statement-derived):
    Trained Random Forest on UCI Credit Card Default data (30,000 records).
    Produces a calibrated P(default) from behavioral spending patterns.
    Risk bands: LOW (<0.15) | MODERATE (0.15-0.30) | ELEVATED (0.30-0.50) | HIGH (>=0.50)

Pillar 2 — Bureau ML Risk (LightGBM, applicant profile-derived):
    Home Credit default-risk benchmark model.
    Produces a calibrated P(default) from bureau/demographic signals.
    Review threshold at 0.20.

Hard stops (data quality gates, not scoring):
    Enforced via assess_affordability() which now extracts mandatory_review_reasons
    only — the 0-100 rule score is no longer part of the primary decision path.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.config import HIGH_RISK_THRESHOLD, LOW_RISK_THRESHOLD, MAX_EMI_TO_INCOME, MIN_EXTRACTION_CONFIDENCE
from src.decision.affordability import AFFORDABILITY_RULE_VERSION, POLICY, assess_affordability
from src.documents.statement_csv import StatementQualityReport

# Behavioral ML thresholds
_BEHAVIORAL_LOW = 0.15    # Below this: behavioral LOW risk
_BEHAVIORAL_HIGH = 0.50   # Above this: behavioral HIGH risk (decline / manual)
_BEHAVIORAL_ELEVATED = 0.30  # Above this: behavioral ELEVATED risk (manual)


@dataclass(frozen=True)
class Decision:
    recommendation: str
    reasons: list[str]
    model_probability: float | None
    affordability_score: int | None = None
    affordability_components: dict[str, float] | None = None
    rule_version: str | None = None
    pillar_summary: dict[str, Any] | None = None
    behavioral_ml: dict[str, Any] | None = None


def _behavioral_risk_band_label(pd_: float) -> str:
    if pd_ >= _BEHAVIORAL_HIGH:
        return f"HIGH Behavioral Risk ({pd_:.1%})"
    if pd_ >= _BEHAVIORAL_ELEVATED:
        return f"ELEVATED Behavioral Risk ({pd_:.1%})"
    if pd_ >= _BEHAVIORAL_LOW:
        return f"MODERATE Behavioral Risk ({pd_:.1%})"
    return f"LOW Behavioral Risk ({pd_:.1%})"


def recommend(
    model_probability: float | None,
    statement_features: dict[str, float] | None = None,
    extraction_confidence: float | None = None,
    quality_report: StatementQualityReport | None = None,
    salary_verification: Any | None = None,
) -> Decision:
    """Produce a reviewable recommendation; never a final lending decision.

    When statement_features are provided, the behavioral ML model (Pillar 1)
    predicts default risk from spending pattern signals. The affordability
    module is used only to enforce data quality hard stops, not for scoring.

    When model_probability (Pillar 2 bureau) is also available, both pillars
    are combined in a 2x2 risk matrix for the final recommendation.
    """
    # ── Lazy import to avoid circular imports and slow cold-start ────────────
    from src.models.behavioral_prediction import predict_behavioral_risk

    # ------------------------------------------------------------------
    # Salary slip cross-document verification safeguard
    # ------------------------------------------------------------------
    salary_slip_reasons: list[str] = []
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
            salary_slip_reasons.append(
                "Mandatory cross-document safeguard: Inconsistent declared income requires officer review."
            )

    # ------------------------------------------------------------------
    # Scenario 1: Statement features available — behavioral ML scoring
    # ------------------------------------------------------------------
    if statement_features is not None:
        # Data quality hard-stop gate (no scoring, only mandatory_review_reasons)
        assessment = assess_affordability(statement_features, quality_report)
        hard_stop_reasons = assessment.mandatory_review_reasons

        # Run behavioral ML prediction
        behavioral_result = predict_behavioral_risk(statement_features)
        behavioral_scored = behavioral_result.get("status") == "scored"
        behavioral_pd = behavioral_result.get("default_probability") if behavioral_scored else None

        # Build reason list from hard stops and salary safeguard
        reasons: list[str] = list(hard_stop_reasons) + salary_slip_reasons

        # ------------------------------------------------------------------
        # Scenario 1a: Dual-Pillar — Statement ML + Bureau ML
        # ------------------------------------------------------------------
        if model_probability is not None and behavioral_pd is not None:
            bureau_pd = model_probability
            low_bureau_risk = bureau_pd < LOW_RISK_THRESHOLD
            low_behavioral_risk = behavioral_pd < _BEHAVIORAL_ELEVATED
            high_behavioral_risk = behavioral_pd >= _BEHAVIORAL_HIGH

            bureau_band = "Low Default Risk (<20%)" if low_bureau_risk else f"Elevated Default Risk ({bureau_pd:.1%})"
            behavioral_band = _behavioral_risk_band_label(behavioral_pd)

            if salary_slip_flagged:
                recommendation = "Refer for additional documents"
                quadrant = "Document Safeguard Override (Refer)"
            elif hard_stop_reasons:
                evidence_gaps = (
                    "Fewer than three months",
                    "Statement data quality",
                    "No recognised recurring income",
                    "Too many transaction categories",
                )
                if any(r.startswith(evidence_gaps) for r in hard_stop_reasons):
                    reasons.append("Additional reliable evidence is needed before an officer can complete review.")
                    recommendation = "Refer for additional documents"
                    quadrant = "Evidence Gap Safeguard (Refer)"
                else:
                    reasons.append("Mandatory review safeguard applies regardless of ML risk scores.")
                    recommendation = "Manual review"
                    quadrant = "Safeguard Override (Manual Review)"
            elif high_behavioral_risk:
                # Behavioral ML flags HIGH risk — escalate regardless of bureau
                reasons.append(
                    f"Behavioral ML (Pillar 1): Predicted default probability {behavioral_pd:.1%} is in the HIGH-risk band. "
                    f"Payment history pattern analysis indicates elevated credit stress."
                )
                recommendation = "Does not meet indicative affordability criteria"
                quadrant = "HIGH Behavioral Risk / Bureau Convergence (Recommend Decline)"
            elif not low_behavioral_risk and not low_bureau_risk:
                # Both pillars show elevated risk
                reasons.append(
                    f"Dual-Pillar Convergence: Behavioral ML default risk {behavioral_pd:.1%} (ELEVATED) "
                    f"and bureau default risk {bureau_pd:.1%} both exceed review thresholds."
                )
                recommendation = "Manual review"
                quadrant = "Elevated Behavioral Risk / Elevated Bureau Risk (Manual Review - Dual Alert)"
            elif not low_behavioral_risk and low_bureau_risk:
                # Behavioral elevated but bureau clean — divergence
                reasons.append(
                    f"Dual-Pillar Divergence: Clean bureau history ({bureau_pd:.1%}) but behavioral ML "
                    f"pattern analysis indicates ELEVATED default risk ({behavioral_pd:.1%}). "
                    f"Cash flow patterns require officer assessment."
                )
                recommendation = "Manual review"
                quadrant = "Elevated Behavioral Risk / Low Bureau Risk (Manual Review - Divergent Evidence)"
            elif low_behavioral_risk and not low_bureau_risk:
                # Behavioral favorable but bureau shows risk — divergence
                reasons.append(
                    f"Dual-Pillar Divergence: Behavioral ML risk is LOW ({behavioral_pd:.1%}) but bureau "
                    f"profile shows elevated credit risk ({bureau_pd:.1%}). Officer review required."
                )
                recommendation = "Manual review"
                quadrant = "Low Behavioral Risk / Elevated Bureau Risk (Manual Review - Divergent Evidence)"
            else:
                # Both pillars LOW — recommend approval
                reasons.append(
                    f"Dual-Pillar Alignment: Behavioral ML default risk is LOW ({behavioral_pd:.1%}) "
                    f"and bureau credit risk is low ({bureau_pd:.1%})."
                )
                recommendation = "Meets indicative affordability criteria"
                quadrant = "Low Behavioral Risk / Low Bureau Risk (Recommend Approval)"

            pillar_summary = {
                "mode": "Dual-Pillar (Behavioral ML x Bureau Default Risk)",
                "behavioral_ml_probability": behavioral_pd,
                "behavioral_ml_band": behavioral_band,
                "model_probability": bureau_pd,
                "bureau_risk_band": bureau_band,
                "quadrant": quadrant,
                # Backward-compatible keys for existing visualisation code
                "affordability_score": assessment.score,
                "affordability_band": (
                    "High" if assessment.score >= POLICY["decision_bands"]["approve_at"]
                    else ("Low" if assessment.score < POLICY["decision_bands"]["manual_review_at"] else "Moderate")
                ),
            }

            return Decision(
                recommendation=recommendation,
                reasons=reasons,
                model_probability=bureau_pd,
                affordability_score=assessment.score,
                affordability_components=assessment.components,
                rule_version=AFFORDABILITY_RULE_VERSION,
                pillar_summary=pillar_summary,
                behavioral_ml=behavioral_result,
            )

        # ------------------------------------------------------------------
        # Scenario 1b: Statement ML only (no bureau model available)
        # ------------------------------------------------------------------
        if behavioral_pd is not None:
            if salary_slip_flagged:
                recommendation = "Refer for additional documents"
            elif hard_stop_reasons:
                evidence_gaps = (
                    "Fewer than three months",
                    "Statement data quality",
                    "No recognised recurring income",
                    "Too many transaction categories",
                )
                if any(r.startswith(evidence_gaps) for r in hard_stop_reasons):
                    reasons.append("Additional reliable evidence is needed before an officer can complete review.")
                    recommendation = "Refer for additional documents"
                else:
                    reasons.append("Mandatory review safeguard applies regardless of ML risk scores.")
                    recommendation = "Manual review"
            elif behavioral_pd >= _BEHAVIORAL_HIGH:
                reasons.append(
                    f"Behavioral ML: Predicted default probability {behavioral_pd:.1%} is in the HIGH-risk band."
                )
                recommendation = "Does not meet indicative affordability criteria"
            elif behavioral_pd >= _BEHAVIORAL_ELEVATED:
                reasons.append(
                    f"Behavioral ML: Predicted default probability {behavioral_pd:.1%} is in the ELEVATED-risk band. "
                    f"Officer assessment is required."
                )
                recommendation = "Manual review"
            elif behavioral_pd >= _BEHAVIORAL_LOW:
                reasons.append(
                    f"Behavioral ML: Predicted default probability {behavioral_pd:.1%} is MODERATE. "
                    f"Borderline profile requires officer review."
                )
                recommendation = "Manual review"
            else:
                reasons.append(
                    f"Behavioral ML: Predicted default probability {behavioral_pd:.1%} is in the LOW-risk band."
                )
                recommendation = "Meets indicative affordability criteria"

            pillar_summary = {
                "mode": "Single-Pillar (Behavioral ML)",
                "behavioral_ml_probability": behavioral_pd,
                "behavioral_ml_band": _behavioral_risk_band_label(behavioral_pd),
                "bureau_risk": "Not evaluated",
                # Backward-compatible keys
                "affordability_score": assessment.score,
                "affordability_band": (
                    "High" if assessment.score >= POLICY["decision_bands"]["approve_at"]
                    else ("Low" if assessment.score < POLICY["decision_bands"]["manual_review_at"] else "Moderate")
                ),
            }

            return Decision(
                recommendation=recommendation,
                reasons=reasons,
                model_probability=None,
                affordability_score=assessment.score,
                affordability_components=assessment.components,
                rule_version=AFFORDABILITY_RULE_VERSION,
                pillar_summary=pillar_summary,
                behavioral_ml=behavioral_result,
            )

        # ------------------------------------------------------------------
        # Scenario 1c: ML model unavailable — fall back to hard stops only
        # ------------------------------------------------------------------
        if salary_slip_flagged:
            recommendation = "Refer for additional documents"
        elif hard_stop_reasons:
            evidence_gaps = (
                "Fewer than three months",
                "Statement data quality",
                "No recognised recurring income",
                "Too many transaction categories",
            )
            if any(r.startswith(evidence_gaps) for r in hard_stop_reasons):
                reasons.append("Additional reliable evidence is needed before an officer can complete review.")
                recommendation = "Refer for additional documents"
            else:
                reasons.append("Mandatory review safeguard applies. Behavioral ML model is not available.")
                recommendation = "Manual review"
        else:
            reasons.append(
                "Behavioral ML model is not available. Officer manual review is required before a recommendation "
                "can be issued."
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
                "mode": "Data Quality Gate Only (Behavioral ML Unavailable)",
                "affordability_score": assessment.score,
                "affordability_band": "Unknown",
                "bureau_risk": "Not evaluated",
            },
            behavioral_ml=behavioral_result,
        )

    # ------------------------------------------------------------------
    # Scenario 2: Bureau ML model only (no statement features)
    # ------------------------------------------------------------------
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
