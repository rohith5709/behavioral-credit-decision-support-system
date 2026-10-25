"""Unit tests for account-level unsupervised behavioral ML (Isolation Forest & K-Means)."""
from pathlib import Path
import joblib
import pytest

from src.models.behavioral_unsupervised import (
    load_behavioral_bundle,
    score_behavioral_profile,
    BEHAVIORAL_MODEL_OUTPUT_PATH,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_behavioral_bundle_artifact_loads():
    """Verify behavioral bundle exists and contains both models and scaler."""
    assert BEHAVIORAL_MODEL_OUTPUT_PATH.exists()
    bundle = load_behavioral_bundle()
    assert bundle is not None
    assert "kmeans" in bundle
    assert "isolation_forest" in bundle
    assert "scaler" in bundle
    assert len(bundle["features"]) == 8


def test_score_disciplined_accumulator_profile():
    """Verify that a disciplined profile receives Cluster 0/1 and no anomaly flag."""
    disciplined_features = {
        "savings_ratio": 0.45,
        "income_variation_ratio": 0.05,
        "expense_variation_ratio": 0.08,
        "effective_monthly_emi": 4000.0,
        "cash_withdrawal_share": 0.03,
        "low_balance_day_count": 0,
        "emergency_buffer_months": 6.0,
        "uncertain_transaction_share": 0.01,
    }
    res = score_behavioral_profile(disciplined_features)
    assert res["status"] == "scored"
    assert res["anomaly_detection"]["is_anomaly"] is False
    assert res["anomaly_detection"]["anomaly_score"] < 0.60
    assert "behavioral_persona" in res
    assert res["behavioral_persona"]["fit_confidence"] > 0.50


def test_score_erratic_cashflow_triggers_anomaly_or_cautious_persona():
    """Verify that an extreme, erratic profile is flagged by Isolation Forest or placed in high risk cluster."""
    erratic_features = {
        "savings_ratio": -0.40,
        "income_variation_ratio": 0.85,
        "expense_variation_ratio": 0.95,
        "effective_monthly_emi": 55000.0,
        "cash_withdrawal_share": 0.70,
        "low_balance_day_count": 28,
        "emergency_buffer_months": 0.1,
        "uncertain_transaction_share": 0.35,
    }
    res = score_behavioral_profile(erratic_features)
    assert res["status"] == "scored"
    # Isolation Forest marks it as an anomaly, with elevated anomaly score (>0.70)
    assert res["anomaly_detection"]["is_anomaly"] is True
    assert res["anomaly_detection"]["anomaly_score"] >= 0.70
    # The persona should reflect strain or volatility
    assert res["behavioral_persona"]["name"] in [
        "Liquidity Strained / High Buffer Drag",
        "Volatile Cash Flow / Gig Earner",
    ]
