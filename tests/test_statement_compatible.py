import pandas as pd

from src.models.statement_compatible import (
    CONTRACT,
    MODEL_FEATURES,
    build_ablation_sets,
    statement_model_feature_row,
    validate_statement_training_data,
)


def _complete_frame(rows: int = 1_000) -> pd.DataFrame:
    data = {
        "applicant_case_id": [f"CASE-{index}" for index in range(rows)],
        "application_date": ["2025-01-01"] * rows,
        "loan_default_within_outcome_window": [1 if index < 100 else 0 for index in range(rows)],
        "observed_statement_months": [3] * rows,
    }
    for feature in MODEL_FEATURES:
        data[feature] = [1.0] * rows
    return pd.DataFrame(data)


def test_statement_model_row_preserves_missing_balance_evidence():
    row = statement_model_feature_row(
        {"average_monthly_income": 50_000, "average_monthly_expense": 30_000, "savings_ratio": 0.4,
         "has_balance_history": False, "cash_withdrawal_share": 0.1, "effective_monthly_emi": 5_000,
         "uncertain_transaction_share": 0.0, "post_loan_monthly_surplus": 15_000},
        requested_amount=100_000, loan_tenure_months=24, annual_interest_rate=12,
    )
    assert set(row) == set(MODEL_FEATURES)
    assert row["income_to_requested_amount_ratio"] == 0.5
    assert row["requested_to_annual_income_ratio"] == 100_000 / 600_000
    assert row["emergency_buffer_months"] is None
    assert row["balance_volatility_ratio"] is None


def test_readiness_validation_rejects_the_empty_template_shape():
    result = validate_statement_training_data(pd.DataFrame(columns=["applicant_case_id"]))
    assert not result["data_ready"]
    assert result["missing_columns"]


def test_readiness_validation_accepts_minimum_complete_anonymised_schema():
    frame = _complete_frame()
    result = validate_statement_training_data(frame)
    assert result["data_ready"]
    assert result["positive_outcomes"] == 100
    ablations = build_ablation_sets(frame)
    assert set(ablations) == {"application_request_only", "application_plus_behavioural"}
    assert list(ablations["application_plus_behavioural"].columns) == list(MODEL_FEATURES)


def test_contract_explicitly_excludes_incompatible_home_credit_features():
    excluded = CONTRACT["excluded_until_reliably_available"]
    assert "home_credit_ext_source_features" in excluded
    assert "bureau_repayment_history" in excluded
