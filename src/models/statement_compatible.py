"""Prepare and validate evidence for a future statement-compatible ML model.

No model is trained here unless a consented, anonymised applicant-level dataset
with outcome labels is supplied. The Home Credit benchmark is intentionally not
used as a substitute because its features are incompatible with raw statements.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = PROJECT_ROOT / "config" / "statement_ml_feature_contract_v1.json"
CONTRACT: dict[str, Any] = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
TARGET_COLUMN = str(CONTRACT["target"])
IDENTIFIER_COLUMNS = tuple(CONTRACT["identifiers"])
REQUEST_COLUMNS = tuple(CONTRACT["required_request_fields"])
EVIDENCE_COLUMNS = tuple(CONTRACT["required_evidence_fields"])
STATEMENT_FEATURES = tuple(CONTRACT["statement_features"])
MODEL_FEATURES = REQUEST_COLUMNS + STATEMENT_FEATURES


def statement_model_feature_row(
    statement_features: dict[str, Any],
    requested_amount: float,
    loan_tenure_months: int,
    annual_interest_rate: float,
) -> dict[str, float | None]:
    """Map dashboard evidence into the future statement-model feature contract.

    Missing balance evidence remains ``None`` rather than being fabricated as
    zero. A future pipeline must impute it using training data only.
    """
    income = float(statement_features.get("average_monthly_income", 0.0) or 0.0)
    request = float(requested_amount)
    row: dict[str, float | None] = {
        "requested_amount": request,
        "loan_tenure_months": float(loan_tenure_months),
        "annual_interest_rate": float(annual_interest_rate),
        "average_monthly_income": income,
        "average_monthly_expense": float(statement_features.get("average_monthly_expense", 0.0) or 0.0),
        "savings_ratio": _number(statement_features.get("savings_ratio")),
        "income_variation_ratio": _number(statement_features.get("income_variation_ratio")),
        "expense_variation_ratio": _number(statement_features.get("expense_variation_ratio")),
        "balance_volatility_ratio": _number(statement_features.get("balance_volatility_ratio")) if statement_features.get("has_balance_history") else None,
        "low_balance_day_count": _number(statement_features.get("low_balance_day_count")) if statement_features.get("has_balance_history") else None,
        "cash_withdrawal_share": _number(statement_features.get("cash_withdrawal_share")),
        "effective_monthly_emi": _number(statement_features.get("effective_monthly_emi")),
        "proposed_emi_to_income_ratio": _number(statement_features.get("proposed_emi_to_income_ratio")) if income else None,
        "emergency_buffer_months": _number(statement_features.get("emergency_buffer_months")) if statement_features.get("has_balance_history") else None,
        "uncertain_transaction_share": _number(statement_features.get("uncertain_transaction_share")),
        "income_to_requested_amount_ratio": income / request if request > 0 else None,
        "requested_to_annual_income_ratio": request / (income * 12) if income > 0 else None,
        "post_loan_monthly_surplus": _number(statement_features.get("post_loan_monthly_surplus")),
    }
    return row


def _number(value: Any) -> float | None:
    """Return a finite numeric value, preserving absent evidence as None."""
    if value is None or pd.isna(value):
        return None
    return float(value)


def validate_statement_training_data(frame: pd.DataFrame) -> dict[str, Any]:
    """Assess whether a supplied labelled dataset meets the Phase 12 gate.

    This validates schema and readiness only; it never fits a model or exposes
    applicant identifiers in reports.
    """
    required = set(IDENTIFIER_COLUMNS) | {TARGET_COLUMN} | set(EVIDENCE_COLUMNS) | set(MODEL_FEATURES)
    missing = sorted(required.difference(frame.columns))
    result: dict[str, Any] = {
        "contract_version": CONTRACT["version"],
        "rows": int(len(frame)),
        "missing_columns": missing,
        "duplicate_case_ids": int(frame["applicant_case_id"].duplicated().sum()) if "applicant_case_id" in frame else None,
        "invalid_target_rows": None,
        "positive_outcomes": None,
        "invalid_application_dates": None,
        "data_ready": False,
        "reasons": [],
    }
    if missing:
        result["reasons"].append("Dataset is missing required contract columns.")
        return result
    target = pd.to_numeric(frame[TARGET_COLUMN], errors="coerce")
    valid_target = target.isin([0, 1])
    result["invalid_target_rows"] = int((~valid_target).sum())
    result["positive_outcomes"] = int((target == 1).sum())
    dates = pd.to_datetime(frame["application_date"], errors="coerce")
    result["invalid_application_dates"] = int(dates.isna().sum())
    minimum = CONTRACT["minimum_data_requirements"]
    if len(frame) < minimum["minimum_labelled_cases"]:
        result["reasons"].append(f"At least {minimum['minimum_labelled_cases']} labelled applicant cases are required.")
    if result["positive_outcomes"] < minimum["minimum_positive_outcomes"]:
        result["reasons"].append(f"At least {minimum['minimum_positive_outcomes']} positive default outcomes are required.")
    if result["duplicate_case_ids"]:
        result["reasons"].append("Applicant case IDs must be unique.")
    if result["invalid_target_rows"]:
        result["reasons"].append("Outcome labels must be 0 or 1.")
    if result["invalid_application_dates"]:
        result["reasons"].append("Application dates are required for temporal validation.")
    observed_months = pd.to_numeric(frame["observed_statement_months"], errors="coerce")
    insufficient_months = int((observed_months < minimum["minimum_observed_statement_months"]).sum())
    result["insufficient_statement_month_rows"] = insufficient_months
    if insufficient_months:
        result["reasons"].append(
            f"Every case requires at least {minimum['minimum_observed_statement_months']} observed statement months."
        )
    result["data_ready"] = not result["reasons"]
    if result["data_ready"]:
        result["reasons"].append("Dataset meets the minimum schema/readiness gate; temporal validation is still mandatory during training.")
    return result


def build_ablation_sets(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create planned feature groups for later applicant-level ablation studies.

    The current contract deliberately excludes Home Credit-only credit-history
    columns. A future approved source may add a separately governed compatible
    credit-history group.
    """
    missing = set(MODEL_FEATURES).difference(frame.columns)
    if missing:
        raise ValueError(f"Dataset is missing model features: {sorted(missing)}")
    return {
        "application_request_only": frame.loc[:, list(REQUEST_COLUMNS)].copy(),
        "application_plus_behavioural": frame.loc[:, list(MODEL_FEATURES)].copy(),
    }
