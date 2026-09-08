"""Import behavioural features produced by Bank Data Simulator.

The upstream simulator emits partitioned Parquet output. This adapter deliberately
keeps its output separate from the real-data default model: upstream labels are
churn-oriented, while this project validates default prediction on Home Credit.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

FEATURE_COLUMNS = (
    "salary_credit_consistency",
    "credit_utilization",
    "emi_to_income_ratio",
    "balance_change_3m",
    "txn_count_change_3m",
    "tenure_months",
    "products_count",
    "dormant_days",
)


def _find_parquet_files(root: Path, table_name: str) -> list[Path]:
    """Find a simulator table whether it is a file or monthly partitions."""
    matches = sorted(root.rglob(f"{table_name}*.parquet"))
    if not matches:
        matches = sorted(path for path in root.rglob("*.parquet") if table_name in path.as_posix())
    return matches


def load_simulator_table(root: str | Path, table_name: str) -> pd.DataFrame:
    """Load one partitioned simulator table into a pandas DataFrame."""
    source = Path(root)
    files = _find_parquet_files(source, table_name)
    if not files:
        raise FileNotFoundError(f"Could not find '{table_name}' Parquet files below {source}")
    return pd.concat((pd.read_parquet(file) for file in files), ignore_index=True)


def build_behaviour_dataset(root: str | Path, horizon_months: int = 3) -> pd.DataFrame:
    """Return a portable behavioural dataset from `churn_feature_snapshot`.

    It is for feature demonstrations and dashboard testing. Do not treat a churn
    label as a loan-default label.
    """
    frame = load_simulator_table(root, "churn_feature_snapshot")
    if "prediction_horizon_months" in frame.columns:
        frame = frame.loc[frame["prediction_horizon_months"] == horizon_months].copy()
    available = [column for column in FEATURE_COLUMNS if column in frame.columns]
    if not available:
        raise ValueError(
            "The feature snapshot did not contain recognised behavioural columns. "
            f"Available columns: {sorted(frame.columns.tolist())}"
        )
    identifier = next((name for name in ("customer_id", "customer_key", "id") if name in frame.columns), None)
    time_column = next((name for name in ("as_of_month", "snapshot_month", "month") if name in frame.columns), None)
    selected = [column for column in (identifier, time_column, *available) if column]
    return frame[selected].copy()


def export_behaviour_dataset(source: str | Path, output: str | Path, horizon_months: int = 3) -> Path:
    """Build and save the synthetic portfolio as CSV for dashboard exploration."""
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    build_behaviour_dataset(source, horizon_months=horizon_months).to_csv(destination, index=False)
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Bank Data Simulator behavioural features.")
    parser.add_argument("--input", required=True, help="Simulator Parquet output directory.")
    parser.add_argument("--output", default="data/synthetic/simulator_behaviour_features.csv")
    parser.add_argument("--horizon", type=int, default=3, help="Prediction horizon to retain; default: 3 months.")
    arguments = parser.parse_args()
    print(export_behaviour_dataset(arguments.input, arguments.output, horizon_months=arguments.horizon))
