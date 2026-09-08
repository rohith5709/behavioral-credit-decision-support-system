import pandas as pd

from src.data import simulator_adapter


def test_build_behaviour_dataset_selects_documented_columns(monkeypatch):
    source = pd.DataFrame({
        "customer_id": ["C-001"],
        "as_of_month": ["2026-01"],
        "prediction_horizon_months": [3],
        "salary_credit_consistency": [0.95],
        "credit_utilization": [0.35],
        "emi_to_income_ratio": [0.22],
        "churned_3m": [0],
    })
    monkeypatch.setattr(simulator_adapter, "load_simulator_table", lambda *_: source)
    result = simulator_adapter.build_behaviour_dataset("unused")
    assert result.columns.tolist() == [
        "customer_id", "as_of_month", "salary_credit_consistency",
        "credit_utilization", "emi_to_income_ratio",
    ]
