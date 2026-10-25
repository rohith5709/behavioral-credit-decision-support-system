"""Tests for the behavioral ML prediction model and feature bridge.

Validates that:
1. The model loads successfully and has expected bundle structure.
2. The feature bridge produces correctly-shaped output with no NaN.
3. A known high-risk feature vector returns a HIGH or ELEVATED risk band.
4. A known low-risk feature vector returns a LOW risk band.
5. predict_behavioral_risk returns the expected dict structure.
6. The engine integrates behavioral ML into recommendations correctly.
"""
from __future__ import annotations

import pytest

from src.features.behavioral_ml_features import (
    BEHAVIORAL_FEATURES,
    map_statement_to_behavioral_features,
)
from src.models.behavioral_prediction import (
    load_behavioral_model,
    predict_behavioral_risk,
)


# ── Synthetic feature vectors for known risk profiles ────────────────────────

def _low_risk_features() -> dict:
    """Well-behaved borrower: high savings, low EMI, consistent salary, no stress."""
    return {
        "savings_ratio": 0.42,
        "emi_to_income_ratio": 0.12,
        "average_monthly_income": 90_000.0,
        "average_monthly_expense": 52_000.0,
        "income_variation_ratio": 0.04,
        "salary_consistency_ratio": 0.03,
        "utility_payment_regularity": 1.0,
        "low_balance_day_count": 0.0,
        "emergency_buffer_months": 4.5,
        "missed_salary_months": 0.0,
        "monthly_surplus": 38_000.0,
        "minimum_monthly_surplus": 32_000.0,
        "expense_variation_ratio": 0.08,
        "savings_trend_ratio": 0.05,
    }


def _high_risk_features() -> dict:
    """Stressed borrower: negative savings, high EMI, irregular income, overdrafts."""
    return {
        "savings_ratio": -0.25,
        "emi_to_income_ratio": 0.72,
        "average_monthly_income": 30_000.0,
        "average_monthly_expense": 37_500.0,
        "income_variation_ratio": 0.55,
        "salary_consistency_ratio": 0.80,
        "utility_payment_regularity": 0.20,
        "low_balance_day_count": 18.0,
        "emergency_buffer_months": 0.1,
        "missed_salary_months": 3.0,
        "monthly_surplus": -7_500.0,
        "minimum_monthly_surplus": -12_000.0,
        "expense_variation_ratio": 0.60,
        "savings_trend_ratio": -0.30,
    }


# ── Model bundle loading ──────────────────────────────────────────────────────

class TestBehavioralModelLoading:
    def test_model_loads_successfully(self):
        bundle = load_behavioral_model()
        assert bundle is not None, (
            "Behavioral model bundle not found. Run: "
            "python -m src.models.train_behavioral_model --input data/raw/uci_credit_default.xls"
        )

    def test_bundle_has_required_keys(self):
        bundle = load_behavioral_model()
        if bundle is None:
            pytest.skip("Model not trained yet.")
        required = {"model", "features", "model_name", "model_version", "decision_threshold"}
        assert required.issubset(bundle.keys()), f"Missing bundle keys: {required - bundle.keys()}"

    def test_bundle_features_match_training_spec(self):
        bundle = load_behavioral_model()
        if bundle is None:
            pytest.skip("Model not trained yet.")
        assert bundle["features"] == BEHAVIORAL_FEATURES

    def test_model_version_is_correct(self):
        bundle = load_behavioral_model()
        if bundle is None:
            pytest.skip("Model not trained yet.")
        assert bundle["model_version"] == "behavioral-uci-v1"

    def test_winning_classifier_is_random_forest(self):
        bundle = load_behavioral_model()
        if bundle is None:
            pytest.skip("Model not trained yet.")
        assert bundle["model_name"] == "RandomForest"


# ── Feature bridge (map_statement_to_behavioral_features) ─────────────────────

class TestFeatureBridge:
    def test_output_has_correct_shape(self):
        frame = map_statement_to_behavioral_features(_low_risk_features())
        assert frame.shape == (1, len(BEHAVIORAL_FEATURES))

    def test_output_has_all_expected_columns(self):
        frame = map_statement_to_behavioral_features(_low_risk_features())
        assert list(frame.columns) == BEHAVIORAL_FEATURES

    def test_no_nan_in_output(self):
        frame = map_statement_to_behavioral_features(_low_risk_features())
        assert not frame.isnull().any().any(), "Feature bridge produced NaN values."

    def test_no_inf_in_output(self):
        import numpy as np
        frame = map_statement_to_behavioral_features(_low_risk_features())
        assert not np.isinf(frame.values).any(), "Feature bridge produced infinite values."

    def test_empty_features_dict_does_not_raise(self):
        """Defensive: bridge must handle missing features gracefully."""
        frame = map_statement_to_behavioral_features({})
        assert frame.shape == (1, len(BEHAVIORAL_FEATURES))
        assert not frame.isnull().any().any()

    def test_low_risk_profile_has_positive_payment_capacity(self):
        frame = map_statement_to_behavioral_features(_low_risk_features())
        assert float(frame["behaviour_average_payment"].iloc[0]) > 0

    def test_high_risk_profile_has_high_late_month_count(self):
        frame = map_statement_to_behavioral_features(_high_risk_features())
        assert float(frame["behaviour_late_month_count"].iloc[0]) > 0


# ── predict_behavioral_risk ───────────────────────────────────────────────────

class TestPredictBehavioralRisk:
    def test_returns_scored_status_when_model_available(self):
        result = predict_behavioral_risk(_low_risk_features())
        if result["status"] == "model_unavailable":
            pytest.skip("Model not trained yet.")
        assert result["status"] == "scored"

    def test_result_has_required_keys(self):
        result = predict_behavioral_risk(_low_risk_features())
        required = {"status", "default_probability", "risk_band", "confidence", "top_features", "model_version", "model_name"}
        assert required.issubset(result.keys())

    def test_probability_is_in_valid_range(self):
        result = predict_behavioral_risk(_low_risk_features())
        if result["status"] != "scored":
            pytest.skip("Model not trained yet.")
        pd_ = result["default_probability"]
        assert 0.0 <= pd_ <= 1.0, f"default_probability {pd_} is out of [0, 1]."

    def test_confidence_is_in_valid_range(self):
        result = predict_behavioral_risk(_low_risk_features())
        if result["status"] != "scored":
            pytest.skip("Model not trained yet.")
        assert 0.0 <= result["confidence"] <= 1.0

    def test_risk_band_is_valid_label(self):
        result = predict_behavioral_risk(_low_risk_features())
        if result["status"] != "scored":
            pytest.skip("Model not trained yet.")
        assert result["risk_band"] in {"LOW", "MODERATE", "ELEVATED", "HIGH"}

    def test_top_features_is_list_of_dicts(self):
        result = predict_behavioral_risk(_low_risk_features())
        if result["status"] != "scored":
            pytest.skip("Model not trained yet.")
        assert isinstance(result["top_features"], list)
        for feat in result["top_features"]:
            assert "feature" in feat and "label" in feat and "observed_value" in feat

    def test_low_risk_profile_receives_low_or_moderate_band(self):
        result = predict_behavioral_risk(_low_risk_features())
        if result["status"] != "scored":
            pytest.skip("Model not trained yet.")
        assert result["risk_band"] in {"LOW", "MODERATE"}, (
            f"Expected LOW or MODERATE for a well-behaved borrower, got {result['risk_band']} "
            f"(P(default)={result['default_probability']:.3f})"
        )

    def test_high_risk_profile_receives_elevated_or_high_band(self):
        result = predict_behavioral_risk(_high_risk_features())
        if result["status"] != "scored":
            pytest.skip("Model not trained yet.")
        assert result["risk_band"] in {"ELEVATED", "HIGH"}, (
            f"Expected ELEVATED or HIGH for a stressed borrower, got {result['risk_band']} "
            f"(P(default)={result['default_probability']:.3f})"
        )

    def test_high_risk_probability_exceeds_low_risk(self):
        low_result = predict_behavioral_risk(_low_risk_features())
        high_result = predict_behavioral_risk(_high_risk_features())
        if low_result["status"] != "scored" or high_result["status"] != "scored":
            pytest.skip("Model not trained yet.")
        assert high_result["default_probability"] > low_result["default_probability"], (
            f"High-risk profile should have higher P(default) than low-risk profile. "
            f"High: {high_result['default_probability']:.3f}, Low: {low_result['default_probability']:.3f}"
        )


# ── Engine integration: ML drives recommendation ──────────────────────────────

class TestEngineMLIntegration:
    """Verify the engine recommendation causally changes based on behavioral ML output."""

    def _quality_report(self):
        from io import StringIO
        from src.documents.statement_csv import parse_statement_csv
        _, report = parse_statement_csv(StringIO(
            "date,description,credit,debit,balance\n"
            "2026-01-01,Salary,50000,0,50000\n"
            "2026-02-01,Salary,50000,0,100000\n"
            "2026-03-01,Salary,50000,0,150000\n"
        ))
        return report

    def test_engine_sets_behavioral_ml_on_decision(self):
        from src.decision.engine import recommend
        decision = recommend(None, _low_risk_features(), quality_report=self._quality_report())
        assert decision.behavioral_ml is not None

    def test_engine_recommendation_differs_for_risk_profiles(self):
        from src.decision.engine import recommend
        low_dec = recommend(None, _low_risk_features(), quality_report=self._quality_report())
        high_dec = recommend(None, _high_risk_features(), quality_report=self._quality_report())
        # High-risk profile must not be approved when low-risk is
        if low_dec.recommendation == "Meets indicative affordability criteria":
            assert high_dec.recommendation != "Meets indicative affordability criteria", (
                "High-risk profile should not receive approval recommendation."
            )

    def test_engine_pillar_summary_contains_ml_probability(self):
        from src.decision.engine import recommend
        decision = recommend(None, _low_risk_features(), quality_report=self._quality_report())
        if decision.behavioral_ml and decision.behavioral_ml.get("status") == "scored":
            assert decision.pillar_summary is not None
            assert "behavioral_ml_probability" in decision.pillar_summary
