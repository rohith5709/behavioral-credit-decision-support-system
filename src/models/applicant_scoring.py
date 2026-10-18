"""Single-applicant bureau risk scoring using the trained Home Credit LightGBM benchmark model."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd

from src.config import HOME_CREDIT_MODEL_PATH, LOW_RISK_THRESHOLD, HIGH_RISK_THRESHOLD
from src.models.explain_home_credit import explain_local_factors


def load_bureau_model(model_path: Path | str = HOME_CREDIT_MODEL_PATH) -> dict[str, Any]:
    """Load the trained Home Credit model bundle."""
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Home Credit model not found at {path}")
    return joblib.load(path)


def predict_applicant_risk(
    bureau_profile: dict[str, Any],
    model_path: Path | str = HOME_CREDIT_MODEL_PATH,
) -> dict[str, Any]:
    """Calculate the calibrated default probability and local factor attributions for an applicant.

    Parameters
    ----------
    bureau_profile : dict
        Applicant attributes. Supported keys include:
        - cibil_score: int | float in [300, 900] (normalized to external sources)
        - ext_source_1, ext_source_2, ext_source_3: float in [0.0, 1.0]
        - age_years: float | int (converted to DAYS_BIRTH = -age_years * 365)
        - years_employed: float | int (converted to DAYS_EMPLOYED = -years_employed * 365)
        - active_loans_count: int (mapped to bureau_record_count)
        - overdue_days: float | int (mapped to bureau_CREDIT_DAY_OVERDUE and installment_days_late)
        - requested_amount: float (mapped to AMT_CREDIT)
        - monthly_emi: float (mapped to AMT_ANNUITY)
        - annual_income: float (mapped to AMT_INCOME_TOTAL)
    """
    bundle = load_bureau_model(model_path)
    features_list = bundle["features"]
    imputer = bundle["imputer"]
    scaler = bundle.get("scaler")
    classifier = bundle["classifier"]
    calibrator = bundle.get("calibrator")
    threshold = float(bundle.get("selected_threshold", LOW_RISK_THRESHOLD))

    # Construct a single-row feature template
    row: dict[str, Any] = {feat: np.nan for feat in features_list}

    # Normalize CIBIL (300-900) to [0.0, 1.0] if provided
    cibil = bureau_profile.get("cibil_score")
    if cibil is not None:
        normalized_cibil = max(0.0, min(1.0, (float(cibil) - 300.0) / 600.0))
        row["EXT_SOURCE_3"] = normalized_cibil
        row["EXT_SOURCE_2"] = normalized_cibil
        row["EXT_SOURCE_1"] = normalized_cibil

    # Direct external scores override if provided
    for key in ("ext_source_1", "ext_source_2", "ext_source_3"):
        if key in bureau_profile and bureau_profile[key] is not None:
            row[key.upper()] = float(bureau_profile[key])

    if "age_years" in bureau_profile and bureau_profile["age_years"] is not None:
        row["DAYS_BIRTH"] = -float(bureau_profile["age_years"]) * 365.25

    if "years_employed" in bureau_profile and bureau_profile["years_employed"] is not None:
        row["DAYS_EMPLOYED"] = -float(bureau_profile["years_employed"]) * 365.25

    if "active_loans_count" in bureau_profile and bureau_profile["active_loans_count"] is not None:
        row["bureau_record_count"] = float(bureau_profile["active_loans_count"])

    if "overdue_days" in bureau_profile and bureau_profile["overdue_days"] is not None:
        days = float(bureau_profile["overdue_days"])
        row["bureau_CREDIT_DAY_OVERDUE"] = days
        row["installment_days_late"] = days
        if days > 0:
            row["bureau_balance_late_status_count"] = 1.0

    if "requested_amount" in bureau_profile and bureau_profile["requested_amount"] is not None:
        row["AMT_CREDIT"] = float(bureau_profile["requested_amount"])
        row["AMT_GOODS_PRICE"] = float(bureau_profile["requested_amount"])

    if "monthly_emi" in bureau_profile and bureau_profile["monthly_emi"] is not None:
        row["AMT_ANNUITY"] = float(bureau_profile["monthly_emi"])

    if "annual_income" in bureau_profile and bureau_profile["annual_income"] is not None:
        row["AMT_INCOME_TOTAL"] = float(bureau_profile["annual_income"])
    elif "monthly_income" in bureau_profile and bureau_profile["monthly_income"] is not None:
        row["AMT_INCOME_TOTAL"] = float(bureau_profile["monthly_income"]) * 12.0

    # Calculate derivative ratios if components available
    if row.get("AMT_CREDIT") and row.get("AMT_INCOME_TOTAL"):
        row["app_credit_to_income"] = row["AMT_CREDIT"] / row["AMT_INCOME_TOTAL"]
    if row.get("AMT_ANNUITY") and row.get("AMT_INCOME_TOTAL"):
        row["app_annuity_to_income"] = (row["AMT_ANNUITY"] * 12.0) / row["AMT_INCOME_TOTAL"]

    # Transform through median imputer & predictor
    df_raw = pd.DataFrame([row])[features_list]
    imputed = imputer.transform(df_raw)
    features_ready = scaler.transform(imputed) if scaler is not None else imputed

    if calibrator is not None:
        pred_prob = float(calibrator.predict_proba(features_ready)[:, 1][0])
    else:
        pred_prob = float(classifier.predict_proba(features_ready)[:, 1][0])

    pred_prob = round(pred_prob, 4)

    # Determine risk band
    if pred_prob < LOW_RISK_THRESHOLD:
        risk_band = "Low Default Risk"
    elif pred_prob < HIGH_RISK_THRESHOLD:
        risk_band = "Moderate Default Risk"
    else:
        risk_band = "High Default Risk"

    threshold_verdict = (
        "Above review alert threshold (elevated risk)"
        if pred_prob >= threshold
        else "Below review alert threshold (acceptable risk)"
    )

    # Calculate feature completeness: how many core underwriting drivers were directly supplied by officer vs median-imputed
    core_underwriting_fields = [
        "cibil_score", "age_years", "years_employed", "active_loans_count",
        "overdue_days", "requested_amount", "monthly_emi", "annual_income", "monthly_income"
    ]
    supplied_count = sum(1 for k in core_underwriting_fields if bureau_profile.get(k) is not None)
    total_core = len(core_underwriting_fields) - 1 # monthly/annual income is alternative
    completeness_ratio = round(min(1.0, supplied_count / total_core), 2)

    # Calculate local Tree-SHAP explanations
    features_for_explanation = {
        k: v for k, v in row.items() if v is not None and not (isinstance(v, float) and np.isnan(v))
    }
    explanations = explain_local_factors(features_for_explanation)

    return {
        "model_probability": pred_prob,
        "risk_band": risk_band,
        "threshold": threshold,
        "is_above_threshold": pred_prob >= threshold,
        "threshold_verdict": threshold_verdict,
        "input_completeness_ratio": completeness_ratio,
        "input_completeness_percent": f"{completeness_ratio:.0%}",
        "supplied_fields_count": supplied_count,
        "imputed_features_count": len(features_list) - len(features_for_explanation),
        "local_explanations": explanations,
        "bureau_profile_features": features_for_explanation,
    }

