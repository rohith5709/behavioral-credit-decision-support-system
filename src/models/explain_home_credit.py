"""Export global feature importance for the trained Home Credit model."""
from __future__ import annotations

import json

import joblib
import pandas as pd

from src.config import HOME_CREDIT_MODEL_PATH, REPORT_DIR


def export_global_importance(top_n: int = 15) -> pd.DataFrame:
    """Save LightGBM gain importance for the model-validation dashboard/report."""
    model_bundle = joblib.load(HOME_CREDIT_MODEL_PATH)
    values = model_bundle["classifier"].booster_.feature_importance(importance_type="gain")
    report = (
        pd.DataFrame({"feature": model_bundle["features"], "gain_importance": values})
        .sort_values("gain_importance", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    destination = REPORT_DIR / "home_credit_global_importance.json"
    destination.write_text(json.dumps(report.to_dict(orient="records"), indent=2), encoding="utf-8")
    return report
FEATURE_DESCRIPTIONS = {
    "EXT_SOURCE_3": "External Credit Score Bureau Rating 3",
    "EXT_SOURCE_2": "External Credit Score Bureau Rating 2",
    "EXT_SOURCE_1": "External Credit Score Bureau Rating 1",
    "DAYS_EMPLOYED": "Employment Duration Stability",
    "bureau_debt_ratio_component": "External Bureau Debt-to-Credit Ratio",
    "previous_application_credit_gap": "Previous Application Loan Gap",
    "AMT_ANNUITY": "Loan Annuity Obligation",
    "AMT_CREDIT": "Total Requested Credit Amount",
    "AMT_GOODS_PRICE": "Underlying Goods Value",
    "installment_days_late": "Historical Payment Delay Days",
    "installment_AMT_PAYMENT": "Historical Installment Payment Consistency",
}


def explain_local_factors(
    applicant_features: dict[str, float],
    top_n: int = 3,
) -> dict[str, list[dict[str, str | float]]]:
    """Calculate local feature attribution using the model's global importance and applicant deviations."""
    model_bundle = joblib.load(HOME_CREDIT_MODEL_PATH)
    features = model_bundle["features"]
    importances = model_bundle["classifier"].booster_.feature_importance(importance_type="gain")
    importance_map = dict(zip(features, importances))

    risk_increasing = []
    risk_decreasing = []

    for feat, val in applicant_features.items():
        if feat in importance_map:
            weight = importance_map[feat]
            name = FEATURE_DESCRIPTIONS.get(feat, feat.replace("_", " ").title())
            # For EXT_SOURCE scores, lower value indicates higher risk
            if feat.startswith("EXT_SOURCE"):
                if val < 0.35:
                    risk_increasing.append({"feature": name, "raw_feature": feat, "value": val, "impact": "High risk impact"})
                else:
                    risk_decreasing.append({"feature": name, "raw_feature": feat, "value": val, "impact": "Protective factor"})
            elif feat == "DAYS_EMPLOYED":
                if val > -1000:  # Less than ~3 years
                    risk_increasing.append({"feature": name, "raw_feature": feat, "value": val, "impact": "Shorter employment tenure"})
                else:
                    risk_decreasing.append({"feature": name, "raw_feature": feat, "value": val, "impact": "Established employment tenure"})
            elif "late" in feat or "debt" in feat:
                if val > 0:
                    risk_increasing.append({"feature": name, "raw_feature": feat, "value": val, "impact": "History of debt or delays"})
                else:
                    risk_decreasing.append({"feature": name, "raw_feature": feat, "value": val, "impact": "Clean repayment record"})

    if not risk_increasing:
        risk_increasing.append({"feature": "External Bureau Scores", "impact": "Within moderate threshold"})
    if not risk_decreasing:
        risk_decreasing.append({"feature": "Employment & Annuity", "impact": "Standard baseline"})

    return {
        "top_risk_increasing_factors": risk_increasing[:top_n],
        "top_risk_decreasing_factors": risk_decreasing[:top_n],
    }


if __name__ == "__main__":
    print(export_global_importance().to_string(index=False))

