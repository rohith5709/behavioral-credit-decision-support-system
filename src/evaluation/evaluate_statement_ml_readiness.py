"""Validate a consented applicant-level dataset against the Phase 12 contract."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.models.statement_compatible import validate_statement_training_data


def evaluate(input_path: str | Path, output_path: str | Path) -> dict[str, object]:
    """Write a non-sensitive readiness report without copying applicant records."""
    report = validate_statement_training_data(pd.read_csv(input_path))
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check Phase 12 statement-compatible ML data readiness.")
    parser.add_argument("--input", required=True, help="Consented, anonymised labelled applicant CSV.")
    parser.add_argument("--output", default="reports/statement_ml_data_readiness.json")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.input, args.output), indent=2))
