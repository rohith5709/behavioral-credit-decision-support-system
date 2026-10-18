from functools import lru_cache
import json
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.config import HOME_CREDIT_MODEL_PATH, REPORT_DIR


@lru_cache(maxsize=1)
def _get_cached_bundle(model_path: str = str(HOME_CREDIT_MODEL_PATH)) -> dict[str, Any]:
    return joblib.load(model_path)


FEATURE_DESCRIPTIONS: dict[str, str] = {
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
    "bureau_record_count": "Active Bureau Trade Lines Count",
    "bureau_CREDIT_DAY_OVERDUE": "Bureau Days Overdue Delinquency",
    "app_credit_to_income": "Loan Credit-to-Income Multiple",
    "app_annuity_to_income": "Annualized Annuity-to-Income Ratio",
}


def export_global_importance(top_n: int = 15) -> pd.DataFrame:
    """Save LightGBM gain importance for the model-validation dashboard/report."""
    model_bundle = _get_cached_bundle(str(HOME_CREDIT_MODEL_PATH))
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


def calculate_tree_shap_attributions(
    imputed_feature_array: np.ndarray,
    feature_names: list[str],
    top_n: int = 5,
) -> dict[str, Any]:
    """Calculate exact Tree-SHAP feature contributions via LightGBM booster.

    Parameters
    ----------
    imputed_feature_array : np.ndarray
        Shape (1, n_features) numeric array after imputer pipeline.
    feature_names : list[str]
        List of feature column names matching model.
    top_n : int
        Number of top attributions to return for risk and protective factors.

    Returns
    -------
    dict[str, Any]
        Exact Shapley values, base value, and ranked drivers in log-odds space.
    """
    model_bundle = _get_cached_bundle(str(HOME_CREDIT_MODEL_PATH))
    booster = model_bundle["classifier"].booster_

    # predict with pred_contrib=True returns (1, n_features + 1) where last col is base value (expected value)
    shap_matrix = booster.predict(imputed_feature_array, pred_contrib=True)
    shap_values = shap_matrix[0, :-1]
    base_value = float(shap_matrix[0, -1])
    raw_margin = float(np.sum(shap_matrix[0]))

    shap_series = pd.Series(shap_values, index=feature_names)

    # Positive SHAP value increases log-odds of default -> Risk-increasing
    risk_increasing = []
    for feat, val in shap_series.sort_values(ascending=False).items():
        if val > 0.001:
            name = FEATURE_DESCRIPTIONS.get(feat, str(feat).replace("_", " ").title())
            risk_increasing.append({
                "feature": name,
                "raw_feature": str(feat),
                "shap_value": round(float(val), 4),
                "impact": f"+{val:.3f} default log-odds",
            })

    # Negative SHAP value reduces log-odds of default -> Protective factor
    risk_decreasing = []
    for feat, val in shap_series.sort_values(ascending=True).items():
        if val < -0.001:
            name = FEATURE_DESCRIPTIONS.get(feat, str(feat).replace("_", " ").title())
            risk_decreasing.append({
                "feature": name,
                "raw_feature": str(feat),
                "shap_value": round(float(val), 4),
                "impact": f"{val:.3f} default log-odds (protective)",
            })

    return {
        "method": "Exact Tree-SHAP (Path-dependent Shapley Values via LightGBM)",
        "base_value_log_odds": round(base_value, 4),
        "raw_margin_log_odds": round(raw_margin, 4),
        "top_risk_increasing_factors": risk_increasing[:top_n],
        "top_risk_decreasing_factors": risk_decreasing[:top_n],
        "all_shap_contributions": {k: round(float(v), 5) for k, v in shap_series.items() if abs(v) > 0.005},
    }


def explain_local_factors(
    applicant_features: dict[str, float],
    top_n: int = 3,
) -> dict[str, list[dict[str, str | float]]]:
    """Calculate local feature attribution using exact Tree-SHAP when full vector available,

    with descriptive fallback for partial inputs.
    """
    model_bundle = _get_cached_bundle(str(HOME_CREDIT_MODEL_PATH))
    features = model_bundle["features"]
    imputer = model_bundle["imputer"]

    # Construct single-row DataFrame
    row = {f: applicant_features.get(f, np.nan) for f in features}
    df = pd.DataFrame([row])[features]
    imputed = imputer.transform(df)

    shap_res = calculate_tree_shap_attributions(imputed, features, top_n=top_n)

    # Format for downstream UI and summary compatibility
    return {
        "method": shap_res["method"],
        "base_value": shap_res["base_value_log_odds"],
        "top_risk_increasing_factors": shap_res["top_risk_increasing_factors"],
        "top_risk_decreasing_factors": shap_res["top_risk_decreasing_factors"],
    }


if __name__ == "__main__":
    print(export_global_importance().to_string(index=False))
