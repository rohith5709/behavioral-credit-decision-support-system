"""Benchmark candidate default-risk models on one leakage-safe Home Credit split."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.config import (
    HOME_CREDIT_COMPARISON_PATH,
    HOME_CREDIT_CALIBRATION_PATH,
    HOME_CREDIT_DIR,
    HOME_CREDIT_METRICS_PATH,
    HOME_CREDIT_MODEL_PATH,
    HOME_CREDIT_THRESHOLD_PATH,
)
from src.data.home_credit import build_home_credit_features


def evaluate_probabilities(y_true: pd.Series, probability: np.ndarray) -> dict[str, float]:
    """Calculate comparable held-out classification metrics at a documented threshold."""
    prediction = (probability >= 0.50).astype(int)
    return {
        "roc_auc": round(float(roc_auc_score(y_true, probability)), 4),
        "pr_auc": round(float(average_precision_score(y_true, probability)), 4),
        "brier_score": round(float(brier_score_loss(y_true, probability)), 4),
        "recall_at_0_50": round(float(recall_score(y_true, prediction, zero_division=0)), 4),
        "precision_at_0_50": round(float(precision_score(y_true, prediction, zero_division=0)), 4),
    }


def select_best_model(results: list[dict[str, float | str]]) -> dict[str, float | str]:
    """Choose by ROC-AUC, then PR-AUC, then lower Brier score on the same hold-out set."""
    if not results:
        raise ValueError("At least one benchmark result is required.")
    return sorted(
        results,
        key=lambda row: (-float(row["roc_auc"]), -float(row["pr_auc"]), float(row["brier_score"]), str(row["model"])),
    )[0]


def threshold_analysis(y_true: pd.Series, probability: np.ndarray) -> list[dict[str, float]]:
    """Report the recall/precision trade-off at project-policy risk thresholds."""
    rows: list[dict[str, float]] = []
    for threshold in (0.20, 0.30, 0.40, 0.50):
        prediction = (probability >= threshold).astype(int)
        rows.append({
            "threshold": threshold,
            "recall": round(float(recall_score(y_true, prediction, zero_division=0)), 4),
            "precision": round(float(precision_score(y_true, prediction, zero_division=0)), 4),
            "flagged_applicant_rate": round(float(prediction.mean()), 4),
        })
    return rows


def reliability_rows(y_true: pd.Series, probability: np.ndarray, bins: int = 10) -> list[dict[str, float]]:
    """Summarise whether predicted default probability matches observed default rate."""
    observed, predicted = calibration_curve(y_true, probability, n_bins=bins, strategy="uniform")
    return [
        {"mean_predicted_risk": round(float(pred), 4), "observed_default_rate": round(float(obs), 4)}
        for pred, obs in zip(predicted, observed, strict=True)
    ]


def _stratified_sample(features: np.ndarray, target: pd.Series, maximum_rows: int = 50_000) -> tuple[np.ndarray, pd.Series]:
    """Cap expensive baseline training while retaining the class distribution."""
    if len(target) <= maximum_rows:
        return features, target
    sampled_features, _, sampled_target, _ = train_test_split(
        features, target, train_size=maximum_rows, stratify=target, random_state=42
    )
    return sampled_features, sampled_target


def train(data_dir: str | Path = HOME_CREDIT_DIR) -> dict[str, float | str | int]:
    """Train candidate models, save the selected artifact, and persist an audit-friendly comparison."""
    features, target = build_home_credit_features(data_dir)
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.20, stratify=target, random_state=42
    )
    imputer = SimpleImputer(strategy="median")
    x_train_ready = imputer.fit_transform(x_train)
    x_test_ready = imputer.transform(x_test)

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train_ready)
    x_test_scaled = scaler.transform(x_test_ready)
    tree_train, tree_target = _stratified_sample(x_train_ready, y_train)
    candidates: list[tuple[str, object, np.ndarray, pd.Series, np.ndarray, str]] = [
        (
            "Logistic regression (balanced)",
            LogisticRegression(max_iter=300, class_weight="balanced", C=0.5, random_state=42),
            x_train_scaled,
            y_train,
            x_test_scaled,
            "imputer_plus_scaler",
        ),
        (
            "LightGBM (unweighted)",
            LGBMClassifier(
                objective="binary", n_estimators=350, learning_rate=0.05, num_leaves=15,
                subsample=0.80, colsample_bytree=0.80, random_state=42, n_jobs=-1, verbosity=-1,
            ),
            x_train_ready,
            y_train,
            x_test_ready,
            "imputer",
        ),
        (
            "LightGBM (balanced)",
            LGBMClassifier(
                objective="binary", n_estimators=500, learning_rate=0.04, num_leaves=31,
                subsample=0.80, colsample_bytree=0.80, class_weight="balanced",
                random_state=42, n_jobs=-1, verbosity=-1,
            ),
            x_train_ready,
            y_train,
            x_test_ready,
            "imputer",
        ),
        (
            "Random forest (balanced, 50k cap)",
            RandomForestClassifier(
                n_estimators=80, max_depth=14, min_samples_leaf=20, max_features=0.70,
                class_weight="balanced_subsample", random_state=42, n_jobs=8,
            ),
            tree_train,
            tree_target,
            x_test_ready,
            "imputer",
        ),
        (
            "XGBoost (balanced, 50k cap)",
            XGBClassifier(
                objective="binary:logistic", n_estimators=250, learning_rate=0.05, max_depth=6,
                subsample=0.80, colsample_bytree=0.80, scale_pos_weight=float((y_train == 0).sum() / (y_train == 1).sum()),
                random_state=42, n_jobs=8, eval_metric="logloss",
            ),
            tree_train,
            tree_target,
            x_test_ready,
            "imputer",
        ),
    ]

    results: list[dict[str, float | str]] = []
    fitted: dict[str, tuple[object, str]] = {}
    winner_probability: np.ndarray | None = None
    winner_train: np.ndarray | None = None
    winner_target: pd.Series | None = None
    winner_test: np.ndarray | None = None
    for name, classifier, candidate_train, candidate_target, candidate_test, preprocessing in candidates:
        started_at = perf_counter()
        classifier.fit(candidate_train, candidate_target)
        probability = classifier.predict_proba(candidate_test)[:, 1]
        result: dict[str, float | str] = {
            "model": name,
            "training_rows": int(len(candidate_target)),
            "training_seconds": round(perf_counter() - started_at, 2),
            **evaluate_probabilities(y_test, probability),
        }
        results.append(result)
        fitted[name] = (classifier, preprocessing)

    winner = select_best_model(results)
    winner_name = str(winner["model"])
    classifier, preprocessing = fitted[winner_name]
    for name, candidate, candidate_train, candidate_target, candidate_test, _ in candidates:
        if name == winner_name:
            winner_probability = candidate.predict_proba(candidate_test)[:, 1]
            winner_train, winner_target, winner_test = candidate_train, candidate_target, candidate_test
            break
    if winner_probability is None or winner_train is None or winner_target is None or winner_test is None:
        raise RuntimeError("Selected model probabilities were not found.")
    calibrator = CalibratedClassifierCV(estimator=clone(classifier), method="sigmoid", cv=3, n_jobs=8)
    calibrator.fit(winner_train, winner_target)
    calibrated_probability = calibrator.predict_proba(winner_test)[:, 1]
    metrics: dict[str, float | str | int] = {
        **winner,
        "model_name": winner_name,
        "selection_metric": "ROC-AUC, then PR-AUC, then lower Brier score",
        "train_rows": int(len(y_train)),
        "test_rows": int(len(y_test)),
        "feature_count": int(features.shape[1]),
    }
    comparison = {
        "dataset": "Home Credit Default Risk",
        "split": "Stratified 80/20 hold-out split, random_state=42",
        "threshold": 0.50,
        "selection_metric": metrics["selection_metric"],
        "selected_model": winner_name,
        "models": results,
    }
    thresholds = {
        "selected_model": winner_name,
        "dataset_split": comparison["split"],
        "rows": threshold_analysis(y_test, calibrated_probability),
    }
    calibration = {
        "selected_model": winner_name,
        "method": "Platt scaling (3-fold sigmoid calibration)",
        "uncalibrated_brier_score": round(float(brier_score_loss(y_test, winner_probability)), 4),
        "calibrated_brier_score": round(float(brier_score_loss(y_test, calibrated_probability)), 4),
        "reliability": reliability_rows(y_test, calibrated_probability),
    }

    HOME_CREDIT_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    HOME_CREDIT_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "imputer": imputer,
            "scaler": scaler if preprocessing == "imputer_plus_scaler" else None,
            "classifier": classifier,
            "calibrator": calibrator,
            "features": features.columns.tolist(),
            "dataset": "Home Credit Default Risk",
            "model_name": winner_name,
        },
        HOME_CREDIT_MODEL_PATH,
    )
    HOME_CREDIT_METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    HOME_CREDIT_COMPARISON_PATH.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    HOME_CREDIT_THRESHOLD_PATH.write_text(json.dumps(thresholds, indent=2), encoding="utf-8")
    HOME_CREDIT_CALIBRATION_PATH.write_text(json.dumps(calibration, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Home Credit default-risk models.")
    parser.add_argument("--input", default=str(HOME_CREDIT_DIR), help="Directory containing Home Credit CSV files.")
    arguments = parser.parse_args()
    print(json.dumps(train(arguments.input), indent=2))
