import pandas as pd
import numpy as np

from src.features.behavioral import (
    add_uci_behavioral_features,
    build_category_summary,
    build_monthly_statement_summary,
    build_statement_features,
    categorise_statement_transactions,
)
from src.models.benchmark_home_credit import evaluate_probabilities, select_best_model, threshold_analysis


def test_uci_behavioral_features_are_created():
    row = {"LIMIT_BAL": 100_000}
    row.update({f"PAY_{month}": 1 for month in (0, 2, 3, 4, 5, 6)})
    row.update({f"BILL_AMT{month}": 10_000 for month in range(1, 7)})
    row.update({f"PAY_AMT{month}": 5_000 for month in range(1, 7)})
    result = add_uci_behavioral_features(pd.DataFrame([row]))
    assert result.loc[0, "behaviour_late_month_count"] == 6
    assert result.loc[0, "behaviour_payment_to_bill_ratio"] == 0.5


def test_statement_features_calculate_savings_ratio():
    transactions = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-10", "2026-01-12"],
        "description": ["Salary", "Rent", "EMI payment"],
        "credit": [50_000, 0, 0],
        "debit": [0, 20_000, 10_000],
    })
    features = build_statement_features(transactions)
    assert features["savings_ratio"] == 0.4
    assert features["emi_to_income_ratio"] == 0.2


def test_statement_categories_and_monthly_summary_are_transparent():
    transactions = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-02-01"],
        "description": ["Salary credit", "Electricity bill", "Zomato order", "Salary credit"],
        "credit": [50_000, 0, 0, 50_000],
        "debit": [0, 1_000, 500, 0],
        "balance": [50_000, 49_000, 48_500, 98_500],
    })
    categorised = categorise_statement_transactions(transactions)
    assert categorised["category"].tolist() == ["Salary/income", "Utilities", "Shopping/discretionary", "Salary/income"]
    summary = build_monthly_statement_summary(transactions)
    assert summary.loc[0, "surplus"] == 48_500
    categories = build_category_summary(transactions)
    assert categories["Expense"].sum() == 1_500
    features = build_statement_features(transactions)
    assert features["utility_payment_regularity"] == 0.5
    assert features["discretionary_expense_ratio"] == 1 / 3


def test_ambiguous_category_is_marked_for_review_and_loan_features_are_derived():
    transactions = pd.DataFrame({
        "date": ["2026-01-01", "2026-02-01", "2026-03-01", "2026-03-02"],
        "description": ["Salary", "Salary", "Salary", "Amazon fuel purchase"],
        "credit": [50_000, 50_000, 50_000, 0],
        "debit": [0, 0, 0, 5_000],
    })
    categorised = categorise_statement_transactions(transactions)
    assert categorised.loc[3, "category_review_status"] == "Uncertain / needs review"
    features = build_statement_features(transactions, requested_amount=100_000, proposed_emi=5_000)
    assert features["requested_loan_to_annual_income_ratio"] == 100_000 / (50_000 * 12)
    assert features["proposed_emi_to_income_ratio"] == 0.1


def test_model_benchmark_metrics_and_selection_are_deterministic():
    metrics = evaluate_probabilities(pd.Series([0, 0, 1, 1]), np.array([0.1, 0.2, 0.7, 0.9]))
    assert metrics["roc_auc"] == 1.0
    winner = select_best_model([
        {"model": "A", "roc_auc": 0.75, "pr_auc": 0.20, "brier_score": 0.15},
        {"model": "B", "roc_auc": 0.75, "pr_auc": 0.25, "brier_score": 0.18},
    ])
    assert winner["model"] == "B"
    thresholds = threshold_analysis(pd.Series([0, 0, 1, 1]), np.array([0.1, 0.2, 0.7, 0.9]))
    assert thresholds[-1]["recall"] == 1.0
