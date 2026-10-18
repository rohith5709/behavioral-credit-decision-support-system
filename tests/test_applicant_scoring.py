import pytest
from src.models.applicant_scoring import predict_applicant_risk


def test_predict_applicant_risk_low_risk_profile():
    profile = {
        "cibil_score": 780,
        "age_years": 35,
        "years_employed": 6,
        "active_loans_count": 1,
        "overdue_days": 0,
        "requested_amount": 200_000,
        "monthly_emi": 12_000,
        "monthly_income": 60_000,
    }
    result = predict_applicant_risk(profile)
    assert 0.0 <= result["model_probability"] <= 1.0
    assert result["model_probability"] < 0.20
    assert result["risk_band"] == "Low Default Risk"
    assert "top_risk_decreasing_factors" in result["local_explanations"]
    assert len(result["local_explanations"]["top_risk_decreasing_factors"]) > 0


def test_predict_applicant_risk_high_risk_profile():
    profile = {
        "cibil_score": 350,
        "age_years": 23,
        "years_employed": 0.5,
        "active_loans_count": 5,
        "overdue_days": 60,
        "requested_amount": 800_000,
        "monthly_emi": 40_000,
        "monthly_income": 45_000,
    }
    result = predict_applicant_risk(profile)
    assert result["model_probability"] >= 0.20
    assert result["is_above_threshold"] is True
    assert "Above review alert threshold" in result["threshold_verdict"]
    assert len(result["local_explanations"]["top_risk_increasing_factors"]) > 0
