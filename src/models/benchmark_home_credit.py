"""Reproducible train/validation/test benchmarking for Home Credit models.

This benchmark is separate from the uploaded bank-statement workflow. It must
not score incompatible raw statement data.
"""
from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from time import perf_counter
from typing import Any

import joblib
import lightgbm
import numpy as np
import pandas as pd
import sklearn
import xgboost
from lightgbm import LGBMClassifier
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from src.config import (
    HOME_CREDIT_CALIBRATION_PATH, HOME_CREDIT_COMPARISON_PATH, HOME_CREDIT_DIR,
    HOME_CREDIT_METRICS_PATH, HOME_CREDIT_MODEL_PATH, HOME_CREDIT_THRESHOLD_PATH, REPORT_DIR,
)
from src.data.home_credit import build_home_credit_features

RANDOM_SEED = 42
TEST_FRACTION = 0.20
VALIDATION_FRACTION_OF_DEVELOPMENT = 0.20
DEFAULT_THRESHOLDS = (0.20, 0.30, 0.40, 0.50)
BOOTSTRAP_SAMPLES = 200
EXPENSIVE_MODEL_TRAINING_CAP = 50_000


def evaluate_probabilities(y_true: pd.Series, probability: np.ndarray, threshold: float = 0.50) -> dict[str, float]:
    """Calculate comparable probability and classification metrics."""
    prediction = (probability >= threshold).astype(int)
    return {
        "roc_auc": round(float(roc_auc_score(y_true, probability)), 4),
        "pr_auc": round(float(average_precision_score(y_true, probability)), 4),
        "brier_score": round(float(brier_score_loss(y_true, probability)), 4),
        "recall": round(float(recall_score(y_true, prediction, zero_division=0)), 4),
        "precision": round(float(precision_score(y_true, prediction, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, prediction, zero_division=0)), 4),
    }


def select_best_model(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Select only from validation results: PR-AUC, ROC-AUC, then Brier score."""
    if not results:
        raise ValueError("At least one validation result is required.")
    return sorted(results, key=lambda row: (-float(row["pr_auc"]), -float(row["roc_auc"]), float(row["brier_score"]), str(row["model"])))[0]


def threshold_analysis(y_true: pd.Series, probability: np.ndarray, thresholds: tuple[float, ...] = DEFAULT_THRESHOLDS) -> list[dict[str, float]]:
    """Show alert-threshold trade-offs without treating them as lending decisions."""
    rows: list[dict[str, float]] = []
    for threshold in thresholds:
        prediction = (probability >= threshold).astype(int)
        rows.append({"threshold": threshold, "recall": round(float(recall_score(y_true, prediction, zero_division=0)), 4), "precision": round(float(precision_score(y_true, prediction, zero_division=0)), 4), "f1": round(float(f1_score(y_true, prediction, zero_division=0)), 4), "flagged_applicant_rate": round(float(prediction.mean()), 4)})
    return rows


def select_threshold(rows: list[dict[str, float]]) -> dict[str, float]:
    """Select a validation-only officer-review alert threshold.

    Prefer the most precise evaluated threshold that reaches 50% validation
    recall. If none reaches that target, fall back to the evaluated threshold
    with highest recall and report that the target was not reached.
    """
    candidates = [row for row in rows if row["recall"] >= 0.50]
    if candidates:
        return sorted(candidates, key=lambda row: (-row["precision"], -row["recall"], row["threshold"]))[0]
    return sorted(rows, key=lambda row: (-row["recall"], -row["precision"], row["threshold"]))[0]


def reliability_rows(y_true: pd.Series, probability: np.ndarray, bins: int = 10) -> list[dict[str, float]]:
    """Create reliability-plot rows for calibrated/uncalibrated probabilities."""
    observed, predicted = calibration_curve(y_true, probability, n_bins=bins, strategy="uniform")
    return [{"mean_predicted_risk": round(float(pred), 4), "observed_default_rate": round(float(obs), 4)} for pred, obs in zip(predicted, observed, strict=True)]


def bootstrap_confidence_intervals(y_true: pd.Series, probability: np.ndarray, samples: int = BOOTSTRAP_SAMPLES, seed: int = RANDOM_SEED) -> dict[str, list[float]]:
    """Return deterministic nonparametric 95% CIs for sealed final-test AUC metrics."""
    target, probability = np.asarray(y_true), np.asarray(probability)
    rng = np.random.default_rng(seed)
    values: dict[str, list[float]] = {"roc_auc": [], "pr_auc": []}
    for _ in range(samples):
        indices = rng.integers(0, len(target), len(target))
        if len(np.unique(target[indices])) > 1:
            values["roc_auc"].append(float(roc_auc_score(target[indices], probability[indices])))
            values["pr_auc"].append(float(average_precision_score(target[indices], probability[indices])))
    return {name: [round(float(np.quantile(item, 0.025)), 4), round(float(np.quantile(item, 0.975)), 4)] for name, item in values.items() if item}


def _stratified_sample(features: np.ndarray, target: pd.Series, maximum_rows: int = EXPENSIVE_MODEL_TRAINING_CAP) -> tuple[np.ndarray, pd.Series]:
    if len(target) <= maximum_rows:
        return features, target
    sampled_features, _, sampled_target, _ = train_test_split(features, target, train_size=maximum_rows, stratify=target, random_state=RANDOM_SEED)
    return sampled_features, sampled_target


def _candidate_definitions(positive_weight: float) -> list[tuple[str, object, bool]]:
    return [
        ("Logistic regression (balanced)", LogisticRegression(max_iter=300, class_weight="balanced", C=0.5, random_state=RANDOM_SEED), True),
        ("LightGBM (unweighted)", LGBMClassifier(objective="binary", n_estimators=350, learning_rate=0.05, num_leaves=15, subsample=0.80, colsample_bytree=0.80, random_state=RANDOM_SEED, n_jobs=-1, verbosity=-1), False),
        ("LightGBM (balanced)", LGBMClassifier(objective="binary", n_estimators=500, learning_rate=0.04, num_leaves=31, subsample=0.80, colsample_bytree=0.80, class_weight="balanced", random_state=RANDOM_SEED, n_jobs=-1, verbosity=-1), False),
        ("Random forest (balanced, 50k cap)", RandomForestClassifier(n_estimators=80, max_depth=14, min_samples_leaf=20, max_features=0.70, class_weight="balanced_subsample", random_state=RANDOM_SEED, n_jobs=8), False),
        ("XGBoost (balanced, 50k cap)", XGBClassifier(objective="binary:logistic", n_estimators=250, learning_rate=0.05, max_depth=6, subsample=0.80, colsample_bytree=0.80, scale_pos_weight=positive_weight, random_state=RANDOM_SEED, n_jobs=8, eval_metric="logloss"), False),
    ]


def _split_data(features: pd.DataFrame, target: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    development, test, y_development, y_test = train_test_split(features, target, test_size=TEST_FRACTION, stratify=target, random_state=RANDOM_SEED)
    train, validation, y_train, y_validation = train_test_split(development, y_development, test_size=VALIDATION_FRACTION_OF_DEVELOPMENT, stratify=y_development, random_state=RANDOM_SEED)
    return train, validation, test, y_train, y_validation, y_test


def _prepare_train_validation_test(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame) -> tuple[SimpleImputer, StandardScaler, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Fit preprocessing only on training partition to avoid validation/test leakage."""
    imputer = SimpleImputer(strategy="median")
    train_ready = imputer.fit_transform(train)
    validation_ready, test_ready = imputer.transform(validation), imputer.transform(test)
    scaler = StandardScaler()
    train_scaled = scaler.fit_transform(train_ready)
    validation_scaled, test_scaled = scaler.transform(validation_ready), scaler.transform(test_ready)
    return imputer, scaler, train_ready, validation_ready, test_ready, train_scaled, validation_scaled, test_scaled


def _calibrate_on_training(classifier: object, train_data: np.ndarray, train_target: pd.Series, validation_data: np.ndarray, validation_target: pd.Series) -> tuple[str, list[dict[str, Any]]]:
    """Compare calibration methods on validation data while fitting them only on training data."""
    raw_probability = classifier.predict_proba(validation_data)[:, 1]  # type: ignore[attr-defined]
    attempts: list[tuple[str, np.ndarray]] = [("Uncalibrated", raw_probability)]
    for method, label in (("sigmoid", "Platt scaling"), ("isotonic", "Isotonic calibration")):
        calibrator = CalibratedClassifierCV(estimator=clone(classifier), method=method, cv=3, n_jobs=8)
        calibrator.fit(train_data, train_target)
        attempts.append((label, calibrator.predict_proba(validation_data)[:, 1]))
    results = [{"method": name, **evaluate_probabilities(validation_target, probability)} for name, probability in attempts]
    selected = min(results, key=lambda row: (float(row["brier_score"]), -float(row["pr_auc"])))
    return str(selected["method"]), results


def _environment_metadata() -> dict[str, str]:
    return {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scikit_learn": sklearn.__version__, "lightgbm": lightgbm.__version__, "xgboost": xgboost.__version__}


def train(data_dir: str | Path = HOME_CREDIT_DIR) -> dict[str, Any]:
    """Select on validation data and reveal final test metrics exactly once."""
    features, target = build_home_credit_features(data_dir)
    train_frame, validation_frame, test_frame, y_train, y_validation, y_test = _split_data(features, target)
    _, _, train_ready, validation_ready, _, train_scaled, validation_scaled, _ = _prepare_train_validation_test(train_frame, validation_frame, test_frame)
    positive_weight = float((y_train == 0).sum() / (y_train == 1).sum())
    results: list[dict[str, Any]] = []
    fitted: dict[str, tuple[object, bool]] = {}
    for name, classifier, needs_scaling in _candidate_definitions(positive_weight):
        candidate_train, candidate_validation, candidate_target = (train_scaled if needs_scaling else train_ready), (validation_scaled if needs_scaling else validation_ready), y_train
        if "50k cap" in name:
            candidate_train, candidate_target = _stratified_sample(candidate_train, y_train)
        started = perf_counter()
        classifier.fit(candidate_train, candidate_target)
        probability = classifier.predict_proba(candidate_validation)[:, 1]  # type: ignore[attr-defined]
        results.append({"model": name, "training_rows": int(len(candidate_target)), "training_seconds": round(perf_counter() - started, 2), **evaluate_probabilities(y_validation, probability)})
        fitted[name] = (classifier, needs_scaling)
    winner = select_best_model(results)
    winner_name = str(winner["model"])
    selected_classifier, needs_scaling = fitted[winner_name]
    selected_train, selected_validation = (train_scaled, validation_scaled) if needs_scaling else (train_ready, validation_ready)
    calibration_method, calibration_validation = _calibrate_on_training(selected_classifier, selected_train, y_train, selected_validation, y_validation)
    validation_probability = selected_classifier.predict_proba(selected_validation)[:, 1]  # type: ignore[attr-defined]
    if calibration_method != "Uncalibrated":
        calibration_kind = "sigmoid" if calibration_method == "Platt scaling" else "isotonic"
        selected_calibrator = CalibratedClassifierCV(estimator=clone(selected_classifier), method=calibration_kind, cv=3, n_jobs=8)
        selected_calibrator.fit(selected_train, y_train)
        validation_probability = selected_calibrator.predict_proba(selected_validation)[:, 1]
    validation_threshold_rows = threshold_analysis(y_validation, validation_probability)
    selected_threshold = select_threshold(validation_threshold_rows)

    development_frame, y_development = pd.concat([train_frame, validation_frame]), pd.concat([y_train, y_validation])
    final_imputer = SimpleImputer(strategy="median")
    development_ready, test_ready = final_imputer.fit_transform(development_frame), final_imputer.transform(test_frame)
    final_scaler = StandardScaler()
    development_scaled, test_scaled = final_scaler.fit_transform(development_ready), final_scaler.transform(test_ready)
    final_weight = float((y_development == 0).sum() / (y_development == 1).sum())
    _, final_classifier, final_needs_scaling = next(item for item in _candidate_definitions(final_weight) if item[0] == winner_name)
    final_train, final_test, final_target = (development_scaled if final_needs_scaling else development_ready), (test_scaled if final_needs_scaling else test_ready), y_development
    if "50k cap" in winner_name:
        final_train, final_target = _stratified_sample(final_train, y_development)
    final_classifier.fit(final_train, final_target)
    final_predictor: object = final_classifier
    if calibration_method != "Uncalibrated":
        calibration_kind = "sigmoid" if calibration_method == "Platt scaling" else "isotonic"
        final_predictor = CalibratedClassifierCV(estimator=clone(final_classifier), method=calibration_kind, cv=3, n_jobs=8)
        final_predictor.fit(final_train, final_target)  # type: ignore[attr-defined]
    final_probability = final_predictor.predict_proba(final_test)[:, 1]  # type: ignore[attr-defined]
    final_metrics = evaluate_probabilities(y_test, final_probability, float(selected_threshold["threshold"]))
    final_metrics |= {"threshold": float(selected_threshold["threshold"]), "confidence_intervals": bootstrap_confidence_intervals(y_test, final_probability)}
    split = {"strategy": "Stratified train/validation/untouched-test split", "random_seed": RANDOM_SEED, "train_rows": int(len(y_train)), "validation_rows": int(len(y_validation)), "test_rows": int(len(y_test)), "train_fraction": 0.64, "validation_fraction": 0.16, "test_fraction": TEST_FRACTION, "note": "Model, calibration, and threshold choices were made without accessing final test labels."}
    selection_metric = "Validation PR-AUC, then validation ROC-AUC, then lower validation Brier score"
    comparison = {"dataset": "Home Credit Default Risk", "evaluation_protocol": split, "selection_metric": selection_metric, "selected_model": winner_name, "models": results}
    calibration = {"selected_model": winner_name, "selection_partition": "validation", "selected_method": calibration_method, "validation_comparison": calibration_validation, "final_test": {"brier_score": round(float(brier_score_loss(y_test, final_probability)), 4), "reliability": reliability_rows(y_test, final_probability)}}
    thresholds = {"selected_model": winner_name, "selection_partition": "validation", "risk_policy": "Officer-review alert: prefer the most precise evaluated threshold reaching 50% validation recall; otherwise select the evaluated threshold with highest recall and report that the target was not reached.", "selected_threshold": selected_threshold, "validation_rows": validation_threshold_rows, "final_test_rows": threshold_analysis(y_test, final_probability)}
    metrics: dict[str, Any] = {"model_name": winner_name, "dataset": "Home Credit Default Risk", "evaluation_protocol": split, "selection_metric": selection_metric, "calibration_method": calibration_method, "final_test_metrics": final_metrics, "feature_count": int(features.shape[1])}
    model_card = {"model_name": winner_name, "purpose": "Separate Home Credit default-risk benchmark; not for raw uploaded bank statements.", "data": "Home Credit Default Risk historical applicant and credit-history data.", "features": features.columns.tolist(), "training_configuration": {"random_seed": RANDOM_SEED, "candidate_training_cap": EXPENSIVE_MODEL_TRAINING_CAP, "package_versions": _environment_metadata()}, "evaluation": metrics, "limitations": ["Dataset/application context may not match intended deployment context.", "No individual applicant scoring is shown in the statement dashboard.", "Threshold is an officer-review alert policy, not an automated decision rule."]}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"imputer": final_imputer, "scaler": final_scaler if final_needs_scaling else None, "classifier": final_classifier, "calibrator": final_predictor if calibration_method != "Uncalibrated" else None, "features": features.columns.tolist(), "dataset": "Home Credit Default Risk", "model_name": winner_name, "evaluation_protocol": split, "calibration_method": calibration_method, "selected_threshold": selected_threshold["threshold"]}, HOME_CREDIT_MODEL_PATH)
    HOME_CREDIT_METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    HOME_CREDIT_COMPARISON_PATH.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    HOME_CREDIT_THRESHOLD_PATH.write_text(json.dumps(thresholds, indent=2), encoding="utf-8")
    HOME_CREDIT_CALIBRATION_PATH.write_text(json.dumps(calibration, indent=2), encoding="utf-8")
    (REPORT_DIR / "home_credit_model_card.json").write_text(json.dumps(model_card, indent=2), encoding="utf-8")
    (REPORT_DIR / "home_credit_training_config.json").write_text(json.dumps({"split": split, "package_versions": _environment_metadata(), "feature_count": int(features.shape[1])}, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Home Credit models using a sealed test protocol.")
    parser.add_argument("--input", default=str(HOME_CREDIT_DIR), help="Directory containing Home Credit CSV files.")
    arguments = parser.parse_args()
    print(json.dumps(train(arguments.input), indent=2))
