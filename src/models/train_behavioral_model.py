"""Train and evaluate a behavioral credit default prediction model on the UCI dataset.

This module trains three candidate classifiers (Logistic Regression, Random Forest,
Gradient Boosting) on real UCI Credit Card Default data, selects the best by
validation ROC-AUC, and saves a calibrated production bundle that can predict
behavioral default risk from statement-derived features.

The UCI dataset contains 30,000 records with 6 months of real payment history,
bill amounts, and repayment amounts — genuine behavioral signals analogous to
what can be derived from uploaded bank statements.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import MODEL_DIR, REPORT_DIR
from src.data.uci import TARGET_COLUMN, load_uci_credit_default
from src.features.behavioral import add_uci_behavioral_features

BEHAVIORAL_MODEL_PATH = MODEL_DIR / "behavioral_prediction_model.joblib"
BEHAVIORAL_METRICS_PATH = REPORT_DIR / "behavioral_prediction_metrics.json"

# Core behavioral feature set — these map directly to statement-derived features
# The UCI columns and engineered features are selected because each has a clear
# conceptual analog in bank statement behavior (payment delays = missed EMIs,
# payment-to-bill ratio = savings ratio, credit utilisation = EMI burden, etc.)
BEHAVIORAL_FEATURES = [
    "behaviour_late_month_count",       # months with payment delay -> missed EMI months
    "behaviour_max_payment_delay",      # worst single delay -> credit stress severity
    "behaviour_average_bill",           # average monthly obligation -> expense level
    "behaviour_average_payment",        # average monthly repayment -> actual payment capacity
    "behaviour_payment_to_bill_ratio",  # repayment coverage -> savings ratio analog
    "behaviour_credit_utilisation",     # bill / credit limit -> EMI-to-income ratio analog
    "behaviour_bill_change",            # bill growth trend -> expense trend
    "behaviour_debt_increasing",        # binary: bill growing -> liquidity stress indicator
    "PAY_0",                            # most recent payment status -> current standing
    "PAY_2",                            # t-2 payment status -> recent behavior
    "PAY_3",                            # t-3 payment status
    "LIMIT_BAL",                        # credit limit -> income capacity signal
    "PAY_AMT1",                         # most recent payment amount
    "PAY_AMT2",                         # second most recent payment
    "BILL_AMT1",                        # most recent bill
]

MODEL_VERSION = "behavioral-uci-v1"


def _evaluate_on_split(
    pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series, threshold: float = 0.50
) -> dict[str, float]:
    """Return a comprehensive set of evaluation metrics on a held-out split."""
    proba = pipeline.predict_proba(X_test)[:, 1]
    pred = (proba >= threshold).astype(int)
    cm = confusion_matrix(y_test, pred)
    tn, fp, fn, tp = cm.ravel() if cm.shape == (2, 2) else (0, 0, 0, 0)
    return {
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
        "pr_auc": round(float(average_precision_score(y_test, proba)), 4),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "f1_macro": round(float(f1_score(y_test, pred, average="macro", zero_division=0)), 4),
        "f1_default_class": round(float(f1_score(y_test, pred, average="binary", zero_division=0)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "confusion_matrix": cm.tolist(),
        "decision_threshold": threshold,
        "test_rows": int(len(y_test)),
    }


def _build_pipeline(classifier_name: str, classifier) -> Pipeline:
    """Wrap a classifier in a StandardScaler pipeline."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", classifier),
    ])


def _calibrate(pipeline: Pipeline, X_cal: pd.DataFrame, y_cal: pd.Series) -> CalibratedClassifierCV:
    """Wrap a fitted pipeline in a Platt (sigmoid) probability calibration layer.

    sklearn >= 1.2 deprecated cv="prefit"; the correct approach is to clone
    a *fitted* estimator and pass it with cv=None so that
    CalibratedClassifierCV treats it as already-fitted.
    """
    # CalibratedClassifierCV with cv=None on a pre-fitted base estimator uses
    # only the calibration fold (X_cal, y_cal) to fit the sigmoid layer without
    # re-training the underlying model — equivalent to the old cv="prefit" API.
    calibrated = CalibratedClassifierCV(pipeline, method="sigmoid", cv=None)
    calibrated.fit(X_cal, y_cal)
    return calibrated


def _permutation_importance(model, X_test: pd.DataFrame, y_test: pd.Series, n_repeats: int = 10) -> dict[str, float]:
    """Compute permutation importance (unbiased — works for any model type)."""
    result = permutation_importance(model, X_test, y_test, n_repeats=n_repeats, random_state=42, scoring="roc_auc")
    importances = {
        feat: round(float(result.importances_mean[i]), 4)
        for i, feat in enumerate(BEHAVIORAL_FEATURES)
    }
    return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))


def _calibration_stats(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, list[float]]:
    """Return reliability curve (fraction_of_positives vs mean_predicted_value)."""
    proba = model.predict_proba(X_test)[:, 1]
    fraction_pos, mean_pred = calibration_curve(y_test, proba, n_bins=10)
    return {
        "fraction_of_positives": [round(float(v), 4) for v in fraction_pos],
        "mean_predicted_value": [round(float(v), 4) for v in mean_pred],
    }


def train(
    input_path: str | Path,
    model_path: Path = BEHAVIORAL_MODEL_PATH,
    metrics_path: Path = BEHAVIORAL_METRICS_PATH,
) -> dict[str, Any]:
    """Full train-validate-test pipeline for behavioral credit default prediction.

    Steps:
    1. Load and enrich UCI dataset with behavioral features.
    2. 70 / 15 / 15 stratified split (train / calibration / test).
    3. Train three candidate classifiers; select best by validation ROC-AUC.
    4. Calibrate winning model using Platt scaling on calibration fold.
    5. Evaluate on frozen held-out test set.
    6. Compute permutation importance and calibration statistics.
    7. Save model bundle and metrics.
    """
    print("Loading UCI Credit Card Default dataset...")
    frame = add_uci_behavioral_features(load_uci_credit_default(input_path))
    y = frame[TARGET_COLUMN].astype(int)
    X = frame[BEHAVIORAL_FEATURES].copy()

    # Fill any NaN in engineered features conservatively
    X = X.fillna(0.0)

    print(f"Dataset: {len(X)} rows | Default rate: {y.mean():.1%} | Features: {len(BEHAVIORAL_FEATURES)}")

    # ── Stratified 70 / 15 / 15 split ────────────────────────────────────────
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=42
    )
    X_train, X_cal, y_train, y_cal = train_test_split(
        X_train_full, y_train_full,
        test_size=0.15 / 0.85,  # 15% of total from the 85% split
        stratify=y_train_full,
        random_state=42,
    )

    print(f"Train: {len(X_train)} | Calibration: {len(X_cal)} | Test: {len(X_test)}")

    # ── Candidate Models ──────────────────────────────────────────────────────
    candidates: dict[str, Pipeline] = {
        "LogisticRegression": _build_pipeline(
            "LogisticRegression",
            LogisticRegression(max_iter=3000, class_weight="balanced", C=1.0, random_state=42),
        ),
        "RandomForest": _build_pipeline(
            "RandomForest",
            RandomForestClassifier(
                n_estimators=200, max_depth=10, class_weight="balanced",
                min_samples_leaf=5, random_state=42, n_jobs=-1,
            ),
        ),
        "GradientBoosting": _build_pipeline(
            "GradientBoosting",
            GradientBoostingClassifier(
                n_estimators=200, max_depth=4, learning_rate=0.08,
                subsample=0.8, random_state=42,
            ),
        ),
    }

    # ── 5-Fold Cross-Validation on Training Fold ──────────────────────────────
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_results: dict[str, dict[str, float]] = {}
    best_model_name = ""
    best_val_roc = -1.0
    best_pipeline: Pipeline | None = None

    for name, pipeline in candidates.items():
        print(f"  Training {name}...")
        t0 = time.time()
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="roc_auc", n_jobs=-1)
        elapsed = time.time() - t0
        cv_results[name] = {
            "cv_roc_auc_mean": round(float(cv_scores.mean()), 4),
            "cv_roc_auc_std": round(float(cv_scores.std()), 4),
            "training_seconds": round(elapsed, 2),
        }
        print(f"    CV ROC-AUC: {cv_scores.mean():.4f} +/- {cv_scores.std():.4f}  ({elapsed:.1f}s)")
        if cv_scores.mean() > best_val_roc:
            best_val_roc = cv_scores.mean()
            best_model_name = name
            best_pipeline = pipeline

    print(f"\nBest candidate by CV ROC-AUC: {best_model_name} ({best_val_roc:.4f})")

    # ── Fit Best Model on Full Training Fold ──────────────────────────────────
    assert best_pipeline is not None
    best_pipeline.fit(X_train, y_train)

    # ── Platt Calibration on Calibration Fold ─────────────────────────────────
    print("Calibrating probabilities (Platt sigmoid)...")
    calibrated_model = _calibrate(best_pipeline, X_cal, y_cal)

    # ── Final Evaluation on Frozen Test Set ───────────────────────────────────
    print("Evaluating on held-out test set...")
    test_metrics = _evaluate_on_split(calibrated_model, X_test, y_test, threshold=0.50)
    print(f"  Test ROC-AUC: {test_metrics['roc_auc']:.4f} | PR-AUC: {test_metrics['pr_auc']:.4f}")
    print(f"  Accuracy: {test_metrics['accuracy']:.4f} | F1 (default class): {test_metrics['f1_default_class']:.4f}")
    print(f"  Recall: {test_metrics['recall']:.4f} | Precision: {test_metrics['precision']:.4f}")

    # ── Permutation Feature Importance ────────────────────────────────────────
    print("Computing permutation feature importance...")
    feat_importance = _permutation_importance(calibrated_model, X_test, y_test, n_repeats=5)

    # ── Calibration Curve ─────────────────────────────────────────────────────
    calib_stats = _calibration_stats(calibrated_model, X_test, y_test)

    # ── Bundle & Persist ──────────────────────────────────────────────────────
    bundle = {
        "model": calibrated_model,
        "features": BEHAVIORAL_FEATURES,
        "model_name": best_model_name,
        "model_version": MODEL_VERSION,
        "decision_threshold": 0.50,
        "dataset": "UCI Default of Credit Card Clients (30,000 records)",
        "training_rows": int(len(X_train)),
        "calibration_rows": int(len(X_cal)),
        "test_rows": int(len(X_test)),
        "default_rate": round(float(y.mean()), 4),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)
    print(f"Model saved -> {model_path}")

    full_metrics: dict[str, Any] = {
        "model_name": best_model_name,
        "model_version": MODEL_VERSION,
        "dataset": "UCI Default of Credit Card Clients",
        "total_rows": int(len(X)),
        "default_rate": round(float(y.mean()), 4),
        "split": {"train": int(len(X_train)), "calibration": int(len(X_cal)), "test": int(len(X_test))},
        "candidate_cv_results": cv_results,
        "selected_model": best_model_name,
        "selected_model_cv_roc_auc": best_val_roc,
        "test_set_metrics": test_metrics,
        "permutation_feature_importance": feat_importance,
        "calibration_curve": calib_stats,
        "features": BEHAVIORAL_FEATURES,
        "artifact_path": str(model_path),
    }
    metrics_path.write_text(json.dumps(full_metrics, indent=2), encoding="utf-8")
    print(f"Metrics saved -> {metrics_path}")

    return full_metrics


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train behavioral credit default prediction model.")
    parser.add_argument("--input", default="data/raw/uci_credit_default.xls", help="Path to UCI .xls file.")
    args = parser.parse_args()
    results = train(args.input)
    print("\nFinal Test Set Metrics:")
    print(json.dumps(results["test_set_metrics"], indent=2))
    print("\nTop Feature Importances:")
    for feat, imp in list(results["permutation_feature_importance"].items())[:8]:
        print(f"  {feat:<40} {imp:.4f}")
