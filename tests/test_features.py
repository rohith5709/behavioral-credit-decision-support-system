import pandas as pd
import numpy as np

from src.features.behavioral import (
    apply_bulk_category_override,
    build_repeated_merchant_groups,
    add_uci_behavioral_features,
    build_category_summary,
    build_monthly_statement_summary,
    build_statement_features,
    categorise_statement_transactions,
)


def test_bulk_category_override_updates_only_selected_repeated_merchant():
    transactions = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-02-01", "2026-02-02"]),
        "description": ["UPI-AMZN-123", "UPI-AMZN-456", "Rent payment"],
        "debit": [100.0, 120.0, 10_000.0],
        "credit": [0.0, 0.0, 0.0],
    })
    categorised = categorise_statement_transactions(transactions)
    groups = build_repeated_merchant_groups(categorised)
    assert groups["merchant_key"].tolist() == ["upi amzn"]

    updated, changed = apply_bulk_category_override(
        categorised, "upi amzn", "Groceries", "Officer A", "Merchant confirmed as grocery", "2026-01-01T00:00:00+00:00"
    )

    assert changed == 2
    assert updated.loc[:1, "category"].tolist() == ["Groceries", "Groceries"]
    assert updated.loc[2, "category"] == "Rent"
    assert updated.loc[:1, "category_review_status"].eq("Officer bulk override").all()


def test_bulk_category_override_requires_a_rationale():
    transactions = pd.DataFrame({
        "description": ["AMZN 1", "AMZN 2"], "debit": [1.0, 1.0], "credit": [0.0, 0.0]
    })
    try:
        apply_bulk_category_override(transactions, "amzn", "Groceries", "Officer A", "", "2026-01-01T00:00:00+00:00")
    except ValueError as error:
        assert "rationale" in str(error).lower()
    else:
        raise AssertionError("Expected a rationale validation error")
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


def test_other_credits_are_not_treated_as_affordability_income():
    transactions = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-03", "2026-02-01", "2026-02-03"],
        "description": ["Salary", "Loan disbursement", "Salary", "Refund from merchant"],
        "credit": [50_000, 100_000, 50_000, 20_000],
        "debit": [0, 0, 0, 0],
    })
    features = build_statement_features(transactions)
    assert features["average_monthly_income"] == 50_000
    assert features["gross_statement_credits"] == 220_000
    assert features["other_statement_credits"] == 120_000


def test_recurring_unlabelled_credits_can_be_income_candidates():
    transactions = pd.DataFrame({
        "date": ["2026-01-01", "2026-02-01", "2026-03-01"],
        "description": ["ACME SERVICES CREDIT", "ACME SERVICES CREDIT", "ACME SERVICES CREDIT"],
        "credit": [40_000, 40_000, 40_000],
        "debit": [0, 0, 0],
    })
    features = build_statement_features(transactions)
    assert features["average_monthly_income"] == 40_000
    assert features["recognised_income_months"] == 3


def test_merchant_aliases_and_extended_categories_are_classified():
    transactions = pd.DataFrame({
        "date": ["2026-01-01"] * 7,
        "description": [
            "AMZN Marketplace", "JIOMART ONLINE", "FASTAG recharge", "LIC PREMIUM",
            "TUITION FEE", "HDFC CREDIT CARD BILL", "LOAN DISB TO ACCOUNT",
        ],
        "credit": [0, 0, 0, 0, 0, 0, 100_000],
        "debit": [500, 600, 300, 900, 2_000, 3_000, 0],
    })
    result = categorise_statement_transactions(transactions)
    assert result["category"].tolist() == [
        "Shopping/discretionary", "Groceries", "Transport/fuel", "Insurance",
        "Education", "Card-bill payment", "Loan disbursement",
    ]


def test_multilingual_and_self_transfer_categorisation():
    transactions = pd.DataFrame({
        "date": ["2026-01-01"] * 5,
        "description": [
            "SELF TRANSFER TO SAVINGS", "PAYTM WALLET TOPUP", "MONTHLY TANKHAH", "BIJLI BILL PAYMENT", "KIRANA STORE",
        ],
        "credit": [0, 0, 45_000, 0, 0],
        "debit": [10_000, 2_000, 0, 1_400, 1_100],
    })
    result = categorise_statement_transactions(transactions)
    assert result["category"].tolist() == [
        "Transfer/other inflow", "Transfer/other inflow", "Salary/income", "Utilities", "Groceries",
    ]


def test_balance_features_use_daily_forward_filled_balance_and_withhold_partial_trends():
    transactions = pd.DataFrame({
        "date": ["2026-01-10", "2026-01-11", "2026-02-01", "2026-03-31"],
        "description": ["Salary", "Rent", "Salary", "Salary"],
        "credit": [10_000, 0, 10_000, 10_000],
        "debit": [0, 9_500, 0, 0],
        "balance": [10_000, 500, 10_500, 20_500],
    })
    features = build_statement_features(transactions)
    assert features["balance_observed_days"] == 81
    assert features["low_balance_day_count"] == 21
    assert features["partial_boundary_month"] is True
    assert features["income_trend_ratio"] is None


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
