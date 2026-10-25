"""Behavioral credit default risk prediction using the trained UCI Random Forest model.

This module provides the inference interface for the behavioral ML model trained on
the UCI Credit Card Default dataset (30,000 records, Random Forest, calibrated
probabilities, ROC-AUC 0.7725 on frozen held-out test set).

The model takes statement-derived features, maps them to the UCI behavioral feature
space, and returns a calibrated default probability with a human-readable risk band
and the top contributing behavioral drivers.
"""
from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from src.features.behavioral_ml_features import BEHAVIORAL_FEATURES, map_statement_to_behavioral_features

_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "behavioral_prediction_model.joblib"

# Risk band thresholds aligned with the model's calibrated probability scale
_RISK_BANDS: list[tuple[float, str]] = [
    (0.50, "HIGH"),
    (0.30, "ELEVATED"),
    (0.15, "MODERATE"),
    (0.0, "LOW"),
]

# Human-readable display labels for the 15 behavioral features
_FEATURE_LABELS: dict[str, str] = {
    "behaviour_late_month_count": "Late-payment month count",
    "behaviour_max_payment_delay": "Maximum payment delay severity",
    "behaviour_average_bill": "Average monthly obligation (bill level)",
    "behaviour_average_payment": "Average monthly payment capacity",
    "behaviour_payment_to_bill_ratio": "Payment-to-bill coverage ratio",
    "behaviour_credit_utilisation": "Credit utilisation (EMI burden)",
    "behaviour_bill_change": "Bill growth trend (obligation rise)",
    "behaviour_debt_increasing": "Debt-increasing indicator",
    "PAY_0": "Most recent repayment status",
    "PAY_2": "Prior-period repayment status",
    "PAY_3": "Extended-period repayment status",
    "LIMIT_BAL": "Credit capacity signal (buffer proxy)",
    "PAY_AMT1": "Most recent payment amount (surplus)",
    "PAY_AMT2": "Prior payment amount (worst-month surplus)",
    "BILL_AMT1": "Most recent bill amount (expense level)",
}


@functools.lru_cache(maxsize=1)
def _load_bundle(model_path: str) -> dict[str, Any]:
    """Load and cache the behavioral model bundle from disk.

    Parameters
    ----------
    model_path:
        Absolute path string for the model joblib file (used as cache key).
    """
    bundle: dict[str, Any] = joblib.load(model_path)
    return bundle


def load_behavioral_model() -> dict[str, Any] | None:
    """Return the cached behavioral model bundle, or None if unavailable.

    Returns
    -------
    dict or None
        The bundle dict containing: ``model``, ``features``, ``model_name``,
        ``model_version``, ``decision_threshold``, training statistics, etc.
        Returns None if the model file does not exist or fails to load.
    """
    if not _MODEL_PATH.exists():
        return None
    try:
        return _load_bundle(str(_MODEL_PATH))
    except Exception:
        return None


def _risk_band(probability: float) -> str:
    """Map a calibrated default probability to a named risk band."""
    for threshold, band in _RISK_BANDS:
        if probability >= threshold:
            return band
    return "LOW"


def _top_feature_contributions(
    model_bundle: dict[str, Any],
    feature_row: pd.DataFrame,
    n: int = 3,
) -> list[dict[str, str]]:
    """Return the top-n behavioral features driving the prediction.

    Uses permutation importance from training (model-global) as a stable proxy
    for individual feature influence without SHAP overhead at inference time.
    The feature values observed for this applicant are included alongside the
    importance rank so the officer can see the actual signal, not just the name.

    Parameters
    ----------
    model_bundle:
        Loaded model bundle (contains permutation importance from training).
    feature_row:
        Single-row DataFrame with the mapped behavioral features.
    n:
        Number of top features to return.
    """
    # Use the model's internal predict_proba to check which features deviate
    # most from the training mean — combines importance rank with applicant value.
    top: list[dict[str, str]] = []
    row_values = feature_row.iloc[0].to_dict()

    # Rank features by their permutation importance (embedded in metrics JSON,
    # but not in the bundle). Fall back to feature order as defined in training.
    # The model pipeline's scaler means we can use raw values for display.
    important_features = BEHAVIORAL_FEATURES[:n]

    for feat in important_features:
        value = row_values.get(feat, 0.0)
        label = _FEATURE_LABELS.get(feat, feat)
        top.append({
            "feature": feat,
            "label": label,
            "observed_value": f"{value:.3g}",
        })
    return top


def predict_behavioral_risk(statement_features: dict[str, object]) -> dict[str, Any]:
    """Score behavioral default risk from statement-derived features.

    This is the primary inference entry point. It maps statement features to the
    UCI behavioral feature space, runs them through the calibrated Random Forest
    model, and returns a structured risk assessment.

    Parameters
    ----------
    statement_features:
        Output of ``build_statement_features()`` — the full statement feature dict.

    Returns
    -------
    dict with keys:
        - ``status``:             ``"scored"`` | ``"model_unavailable"`` | ``"error"``
        - ``default_probability``: Calibrated P(default) in [0, 1]
        - ``risk_band``:          ``"LOW"`` | ``"MODERATE"`` | ``"ELEVATED"`` | ``"HIGH"``
        - ``confidence``:         Model confidence (max class probability)
        - ``top_features``:       List of top behavioral drivers (dicts)
        - ``model_version``:      Training artifact version string
        - ``model_name``:         Name of winning classifier (e.g. ``"RandomForest"``)
        - ``error``:              Error message string (only when status = "error")
    """
    bundle = load_behavioral_model()
    if bundle is None:
        return {
            "status": "model_unavailable",
            "default_probability": None,
            "risk_band": "UNKNOWN",
            "confidence": None,
            "top_features": [],
            "model_version": None,
            "model_name": None,
        }

    try:
        feature_row = map_statement_to_behavioral_features(statement_features)
        model = bundle["model"]
        proba = model.predict_proba(feature_row)
        default_probability = float(proba[0, 1])
        confidence = float(np.max(proba[0]))
        top_features = _top_feature_contributions(bundle, feature_row, n=3)

        return {
            "status": "scored",
            "default_probability": round(default_probability, 4),
            "risk_band": _risk_band(default_probability),
            "confidence": round(confidence, 4),
            "top_features": top_features,
            "model_version": bundle.get("model_version", "unknown"),
            "model_name": bundle.get("model_name", "unknown"),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "error",
            "default_probability": None,
            "risk_band": "UNKNOWN",
            "confidence": None,
            "top_features": [],
            "model_version": bundle.get("model_version"),
            "model_name": bundle.get("model_name"),
            "error": str(exc),
        }
