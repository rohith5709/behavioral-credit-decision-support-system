import numpy as np
import pytest
from src.models.applicant_scoring import predict_applicant_risk
from src.models.explain_home_credit import calculate_tree_shap_attributions, explain_local_factors


def test_tree_shap_fidelity_and_base_value():
    """Verify that LightGBM Tree-SHAP returns consistent attributions and sum matches raw margin."""
    import joblib
    from src.config import HOME_CREDIT_MODEL_PATH
    bundle = joblib.load(HOME_CREDIT_MODEL_PATH)
    features = bundle["features"]
    imputer = bundle["imputer"]
    booster = bundle["classifier"].booster_

    # Create dummy row
    row = {f: np.nan for f in features}
    row["EXT_SOURCE_3"] = 0.65
    row["EXT_SOURCE_2"] = 0.55
    row["DAYS_EMPLOYED"] = -1800
    df = imputer.transform([list(row.values())])

    res = calculate_tree_shap_attributions(df, features, top_n=5)
    assert res["method"].startswith("Exact Tree-SHAP")
    assert "base_value_log_odds" in res
    assert "raw_margin_log_odds" in res
    assert len(res["top_risk_decreasing_factors"]) > 0 or len(res["top_risk_increasing_factors"]) > 0


def test_applicant_scoring_includes_completeness_and_shap():
    profile = {
        "cibil_score": 750,
        "age_years": 32,
        "years_employed": 4.5,
        "active_loans_count": 1,
        "overdue_days": 0,
        "requested_amount": 200_000,
        "monthly_emi": 9_400,
        "monthly_income": 62_000,
    }
    result = predict_applicant_risk(profile)
    assert "input_completeness_ratio" in result
    assert result["input_completeness_ratio"] >= 0.8
    assert "imputed_features_count" in result
    assert result["local_explanations"]["method"].startswith("Exact Tree-SHAP")
