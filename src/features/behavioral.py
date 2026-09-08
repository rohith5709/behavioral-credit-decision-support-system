"""Feature engineering for repayment behaviour and bank-statement affordability."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd

UCI_PAY_COLUMNS = [f"PAY_{month}" for month in (0, 2, 3, 4, 5, 6)]
UCI_BILL_COLUMNS = [f"BILL_AMT{month}" for month in range(1, 7)]
UCI_PAYMENT_COLUMNS = [f"PAY_AMT{month}" for month in range(1, 7)]


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATEGORY_CONFIG_PATH = PROJECT_ROOT / "config" / "category_rules.json"
_category_config = json.loads(CATEGORY_CONFIG_PATH.read_text(encoding="utf-8"))
CATEGORY_RULES: tuple[tuple[str, str], ...] = tuple(
    (label, "|".join(patterns)) for label, patterns in _category_config["categories"].items()
)
ESSENTIAL_CATEGORIES = {"Rent", "EMI/loan repayment", "Utilities", "Groceries", "Transport/fuel", "Healthcare"}


def categorise_statement_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    """Assign transparent, description-based categories to statement transactions.

    The rules are intentionally local and inspectable. They are behavioural labels,
    not a machine-learning prediction or a claim about the purpose of a transaction.
    """
    required = {"description", "debit", "credit"}
    missing = required.difference(transactions.columns)
    if missing:
        raise ValueError(f"Transactions are missing required columns: {sorted(missing)}")

    result = transactions.copy()
    result["debit"] = pd.to_numeric(result["debit"], errors="coerce").fillna(0.0)
    result["credit"] = pd.to_numeric(result["credit"], errors="coerce").fillna(0.0)
    if "category" in result.columns:
        result["original_category"] = result.get("original_category", result["category"])
        result["category_confidence"] = result.get("category_confidence", 1.0)
        result["category_review_status"] = result.get("category_review_status", "Officer override")
        result["is_essential"] = result["category"].isin(ESSENTIAL_CATEGORIES)
        result["is_discretionary"] = result["category"].eq("Shopping/discretionary")
        return result
    description = result["description"].fillna("").astype(str).str.lower()
    category = pd.Series("Other", index=result.index, dtype="object")
    match_count = pd.Series(0, index=result.index, dtype="int64")
    for label, pattern in CATEGORY_RULES:
        matches = description.str.contains(pattern, case=False, regex=True, na=False)
        match_count += matches.astype(int)
        category.loc[matches & category.eq("Other")] = label

    # Unlabelled credits should not be presented as discretionary spending.
    category.loc[(result["credit"] > 0) & (category == "Other")] = "Income/other"
    result["category"] = category
    result["original_category"] = category
    result["category_confidence"] = np.where(match_count.eq(1), 1.0, np.where(match_count.gt(1), 0.5, 0.0))
    result["category_review_status"] = np.where(match_count.eq(1), "Rule match", "Uncertain / needs review")
    result["is_essential"] = result["category"].isin(ESSENTIAL_CATEGORIES)
    result["is_discretionary"] = result["category"].eq("Shopping/discretionary")
    return result


def build_monthly_statement_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """Build a month-level cash-flow view from categorised statement transactions."""
    result = categorise_statement_transactions(transactions)
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result = result.dropna(subset=["date"])
    if result.empty:
        raise ValueError("No valid transaction dates were found.")

    result["month"] = result["date"].dt.to_period("M")
    grouped = result.groupby("month", observed=True)
    summary = pd.DataFrame({
        "income": grouped["credit"].sum(),
        "expense": grouped["debit"].sum(),
        "salary_income": result.loc[result["category"].eq("Salary/income")].groupby("month", observed=True)["credit"].sum(),
        "essential_expense": result.loc[result["is_essential"]].groupby("month", observed=True)["debit"].sum(),
        "discretionary_expense": result.loc[result["is_discretionary"]].groupby("month", observed=True)["debit"].sum(),
        "utility_payment_count": result.loc[result["category"].eq("Utilities") & (result["debit"] > 0)].groupby("month", observed=True).size(),
        "cash_withdrawal_count": result.loc[result["category"].eq("Cash withdrawal") & (result["debit"] > 0)].groupby("month", observed=True).size(),
    }).fillna(0.0)
    summary["surplus"] = summary["income"] - summary["expense"]
    if "balance" in result.columns and result["balance"].abs().sum() > 0:
        closing_balance = result.sort_values("date").groupby("month", observed=True)["balance"].last()
        summary["closing_balance"] = closing_balance.reindex(summary.index).fillna(0.0)
    else:
        summary["closing_balance"] = np.nan
    return summary.reset_index().assign(month=lambda frame: frame["month"].astype(str))


def build_category_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return debit spending totals by transparent transaction category."""
    result = categorise_statement_transactions(transactions)
    expenses = result.loc[result["debit"] > 0].groupby("category", as_index=False, observed=True)["debit"].sum()
    return expenses.rename(columns={"category": "Category", "debit": "Expense"}).sort_values("Expense", ascending=False)


def add_uci_behavioral_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Add transparent behavioural features without modifying the source frame."""
    result = frame.copy()
    repayment_status = result[UCI_PAY_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0)
    bills = result[UCI_BILL_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0)
    payments = result[UCI_PAYMENT_COLUMNS].apply(pd.to_numeric, errors="coerce").fillna(0)

    result["behaviour_late_month_count"] = (repayment_status > 0).sum(axis=1)
    result["behaviour_max_payment_delay"] = repayment_status.clip(lower=0).max(axis=1)
    result["behaviour_average_bill"] = bills.mean(axis=1)
    result["behaviour_average_payment"] = payments.mean(axis=1)
    result["behaviour_payment_to_bill_ratio"] = np.where(
        result["behaviour_average_bill"] > 0,
        result["behaviour_average_payment"] / result["behaviour_average_bill"],
        0.0,
    )
    result["behaviour_credit_utilisation"] = np.where(
        result["LIMIT_BAL"] > 0,
        bills.mean(axis=1) / result["LIMIT_BAL"],
        0.0,
    )
    # Column 1 is the most recent month in the UCI data definition.
    result["behaviour_bill_change"] = bills["BILL_AMT1"] - bills["BILL_AMT6"]
    result["behaviour_debt_increasing"] = (result["behaviour_bill_change"] > 0).astype(int)
    return result.replace([np.inf, -np.inf], np.nan)


def build_statement_features(transactions: pd.DataFrame, monthly_emi: float = 0.0, requested_amount: float = 0.0, proposed_emi: float = 0.0) -> dict[str, float]:
    """Derive affordability features from normalised bank-statement transactions.

    `transactions` must contain `date`, `description`, `debit`, and `credit`.
    Credit transactions are treated as inflows; debit transactions as outflows.
    """
    if transactions.empty:
        raise ValueError("At least one transaction is required for behavioural analysis.")

    result = categorise_statement_transactions(transactions)
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result = result.dropna(subset=["date"])
    if result.empty:
        raise ValueError("No valid transaction dates were found.")

    result["credit"] = pd.to_numeric(result["credit"], errors="coerce").fillna(0.0)
    result["debit"] = pd.to_numeric(result["debit"], errors="coerce").fillna(0.0)
    result["month"] = result["date"].dt.to_period("M")
    monthly_summary = build_monthly_statement_summary(result)
    month_count = len(monthly_summary)
    total_income = float(result["credit"].sum())
    total_expense = float(result["debit"].sum())
    average_income = total_income / month_count
    average_expense = total_expense / month_count
    monthly_income = monthly_summary["income"]
    income_consistency = float(monthly_income.std(ddof=0) / average_income) if average_income else 0.0
    utility_payments = int((result["category"].eq("Utilities") & (result["debit"] > 0)).sum())
    detected_emi = float(result.loc[result["category"].eq("EMI/loan repayment"), "debit"].sum() / month_count)
    effective_emi = max(float(monthly_emi), detected_emi)
    essential_expense = float(monthly_summary["essential_expense"].sum())
    discretionary_expense = float(monthly_summary["discretionary_expense"].sum())
    utility_regularity = float((monthly_summary["utility_payment_count"] > 0).mean())
    cash_withdrawal_frequency = float(monthly_summary["cash_withdrawal_count"].sum() / month_count)
    salary_income = float(monthly_summary["salary_income"].sum())
    salary_months = int((monthly_summary["salary_income"] > 0).sum())
    salary_consistency = (
        float(monthly_summary["salary_income"].std(ddof=0) / monthly_summary["salary_income"].mean())
        if salary_months and monthly_summary["salary_income"].mean() > 0
        else 1.0
    )
    income_trend = (
        float((monthly_summary["income"].iloc[-1] - monthly_summary["income"].iloc[0]) / monthly_summary["income"].iloc[0])
        if month_count > 1 and monthly_summary["income"].iloc[0] > 0
        else 0.0
    )
    savings_trend = (
        float((monthly_summary["surplus"].iloc[-1] - monthly_summary["surplus"].iloc[0]) / average_income)
        if month_count > 1 and average_income > 0
        else 0.0
    )
    expense_variation = float(monthly_summary["expense"].std(ddof=0) / average_expense) if average_expense else 0.0
    nonzero_balances = monthly_summary["closing_balance"].dropna()
    balance_volatility = (
        float(nonzero_balances.std(ddof=0) / abs(nonzero_balances.mean()))
        if len(nonzero_balances) > 1 and nonzero_balances.mean() != 0
        else 0.0
    )
    low_balance_threshold = 0.10 * average_income
    low_balance_days = (
        int((result["balance"] < low_balance_threshold).sum())
        if "balance" in result and result["balance"].abs().sum() > 0
        else 0
    )
    has_balance_history = bool("balance" in result and result["balance"].abs().sum() > 0)
    monthly_surplus = monthly_summary["surplus"]
    transaction_frequency = float(len(result) / month_count)
    cash_withdrawal_share = float(result.loc[result["category"].eq("Cash withdrawal"), "debit"].sum() / total_expense) if total_expense else 0.0
    recurring_rent = float((result.loc[result["category"].eq("Rent")].groupby("month")["debit"].sum() > 0).mean()) if (result["category"] == "Rent").any() else 0.0
    grocery_transport = result["category"].isin(["Groceries", "Transport/fuel"])
    grocery_transport_trend = float((result.loc[grocery_transport].groupby("month")["debit"].sum().reindex(result["month"].drop_duplicates(), fill_value=0).iloc[-1] - result.loc[grocery_transport].groupby("month")["debit"].sum().reindex(result["month"].drop_duplicates(), fill_value=0).iloc[0]) / average_income) if month_count > 1 and average_income else 0.0
    average_closing_balance = float(nonzero_balances.mean()) if len(nonzero_balances) else 0.0
    emergency_buffer_months = average_closing_balance / average_expense if average_expense else 0.0
    negative_balance_count = int((result["balance"] < 0).sum()) if has_balance_history else 0
    low_balance_sequence = 0
    max_low_balance_sequence = 0
    if has_balance_history:
        for low in (result["balance"] < low_balance_threshold):
            low_balance_sequence = low_balance_sequence + 1 if low else 0
            max_low_balance_sequence = max(max_low_balance_sequence, low_balance_sequence)
    salary_series = monthly_summary["salary_income"]
    missed_salary_months = int((salary_series == 0).sum())
    salary_frequency = "monthly" if salary_months >= max(month_count - 1, 1) else "irregular" if salary_months else "unknown"
    income_sources = int(result.loc[result["credit"] > 0, "description"].str.lower().str.replace(r"\d+", "", regex=True).nunique())
    uncertain_share = float(result["category_review_status"].eq("Uncertain / needs review").mean())
    proposed_emi_ratio = (effective_emi + proposed_emi) / average_income if average_income else 0.0
    typical_debit = float(result.loc[result["debit"] > 0, "debit"].median())
    large_spending_count = int((result["debit"] > max(2 * typical_debit, 0.15 * average_income)).sum()) if typical_debit else 0

    return {
        "months_observed": float(month_count),
        "average_monthly_income": average_income,
        "average_monthly_expense": average_expense,
        "monthly_surplus": average_income - average_expense,
        "minimum_monthly_surplus": float(monthly_surplus.min()),
        "savings_ratio": max((average_income - average_expense) / average_income, -1.0) if average_income else 0.0,
        "income_variation_ratio": income_consistency,
        "salary_consistency_ratio": salary_consistency,
        "income_trend_ratio": income_trend,
        "savings_trend_ratio": savings_trend,
        "expense_variation_ratio": expense_variation,
        "emi_to_income_ratio": effective_emi / average_income if average_income else 0.0,
        "utility_payment_count": float(utility_payments),
        "detected_monthly_emi": detected_emi,
        "salary_income_share": salary_income / total_income if total_income else 0.0,
        "salary_income_months": float(salary_months),
        "essential_expense_ratio": essential_expense / total_expense if total_expense else 0.0,
        "discretionary_expense_ratio": discretionary_expense / total_expense if total_expense else 0.0,
        "utility_payment_regularity": utility_regularity,
        "emi_payment_occurrence_consistency": float((result.loc[result["category"].eq("EMI/loan repayment")].groupby("month")["debit"].sum() > 0).mean()) if (result["category"] == "EMI/loan repayment").any() else 0.0,
        "rent_payment_consistency": recurring_rent,
        "cash_withdrawals_per_month": cash_withdrawal_frequency,
        "cash_withdrawal_spend_share": cash_withdrawal_share,
        "transaction_frequency_per_month": transaction_frequency,
        "grocery_transport_trend_ratio": grocery_transport_trend,
        "low_balance_day_count": float(low_balance_days),
        "balance_volatility_ratio": balance_volatility,
        "has_balance_history": float(has_balance_history),
        "large_spending_count": float(large_spending_count),
        "sudden_expense_spike_count": float((monthly_summary["expense"] > monthly_summary["expense"].median() * 1.5).sum()),
        "emergency_buffer_months": emergency_buffer_months,
        "negative_balance_count": float(negative_balance_count),
        "max_consecutive_low_balance_days": float(max_low_balance_sequence),
        "salary_frequency": salary_frequency,
        "missed_salary_months": float(missed_salary_months),
        "income_source_count": float(income_sources),
        "uncertain_transaction_share": uncertain_share,
        "income_to_loan_request_ratio": average_income / requested_amount if requested_amount else 0.0,
        "requested_loan_to_annual_income_ratio": requested_amount / (average_income * 12) if average_income else 0.0,
        "proposed_emi_to_income_ratio": proposed_emi_ratio,
        "post_loan_monthly_surplus": average_income - average_expense - proposed_emi,
    }
