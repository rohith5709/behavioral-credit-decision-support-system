"""Evaluate the transparent statement category rules on a small labelled sample."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.features.behavioral import categorise_statement_transactions


def evaluate(input_path: str | Path, output_path: str | Path) -> dict[str, object]:
    """Write simple macro precision/recall/F1 and a confusion matrix as JSON."""
    labelled = pd.read_csv(input_path)
    required = {"description", "debit", "credit", "expected_category"}
    missing = required.difference(labelled.columns)
    if missing:
        raise ValueError(f"Labelled evaluation data is missing: {sorted(missing)}")
    predicted = categorise_statement_transactions(labelled)
    labels = sorted(set(labelled["expected_category"]).union(predicted["category"]))
    rows: list[dict[str, object]] = []
    for label in labels:
        actual = labelled["expected_category"].eq(label)
        guess = predicted["category"].eq(label)
        true_positive = int((actual & guess).sum())
        precision = true_positive / int(guess.sum()) if guess.any() else 0.0
        recall = true_positive / int(actual.sum()) if actual.any() else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        rows.append({"category": label, "precision": precision, "recall": recall, "f1": f1, "support": int(actual.sum())})
    confusion = pd.crosstab(labelled["expected_category"], predicted["category"], dropna=False)
    report = {
        "dataset": str(input_path),
        "rows": len(labelled),
        "note": "Small manually labelled regression sample; it is not a production-performance claim.",
        "macro_precision": sum(float(row["precision"]) for row in rows) / len(rows),
        "macro_recall": sum(float(row["recall"]) for row in rows) / len(rows),
        "macro_f1": sum(float(row["f1"]) for row in rows) / len(rows),
        "per_category": rows,
        "confusion_matrix": {
            actual: {predicted_label: int(value) for predicted_label, value in values.items()}
            for actual, values in confusion.to_dict(orient="index").items()
        },
    }
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/evaluation/labelled_transactions.csv")
    parser.add_argument("--output", default="reports/category_rule_evaluation.json")
    arguments = parser.parse_args()
    print(json.dumps(evaluate(arguments.input, arguments.output), indent=2))
