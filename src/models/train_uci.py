"""Train the initial interpretable UCI credit-default baseline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import METRICS_PATH, MODEL_PATH
from src.data.uci import TARGET_COLUMN, load_uci_credit_default
from src.features.behavioral import add_uci_behavioral_features


def train(input_path: str | Path, model_path: Path = MODEL_PATH, metrics_path: Path = METRICS_PATH) -> dict[str, float]:
    """Train, evaluate, and persist a reproducible logistic-regression pipeline."""
    frame = add_uci_behavioral_features(load_uci_credit_default(input_path))
    target = frame.pop(TARGET_COLUMN).astype(int)
    features = frame.select_dtypes(include="number").columns.tolist()
    x_train, x_test, y_train, y_test = train_test_split(
        frame[features], target, test_size=0.20, stratify=target, random_state=42
    )
    preprocessing = ColumnTransformer([
        ("numeric", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), features)
    ])
    pipeline = Pipeline([
        ("preprocessing", preprocessing),
        ("classifier", LogisticRegression(max_iter=2_000, class_weight="balanced", random_state=42)),
    ])
    pipeline.fit(x_train, y_train)
    probability = pipeline.predict_proba(x_test)[:, 1]
    prediction = (probability >= 0.50).astype(int)
    metrics = {
        "roc_auc": round(float(roc_auc_score(y_test, probability)), 4),
        "pr_auc": round(float(average_precision_score(y_test, probability)), 4),
        "recall_at_0_50": round(float(recall_score(y_test, prediction, zero_division=0)), 4),
        "precision_at_0_50": round(float(precision_score(y_test, prediction, zero_division=0)), 4),
        "test_rows": int(len(y_test)),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": pipeline, "features": features, "dataset": "UCI Default of Credit Card Clients"}, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the UCI baseline credit-risk model.")
    parser.add_argument("--input", required=True, help="Path to the downloaded UCI .xls file.")
    args = parser.parse_args()
    print(json.dumps(train(args.input), indent=2))

