"""Feature engineering for repayment behaviour and bank-statement affordability."""
from __future__ import annotations

import json
from pathlib import Path
import re
import numpy as np
import pandas as pd
import joblib

UCI_PAY_COLUMNS = [f"PAY_{month}" for month in (0, 2, 3, 4, 5, 6)]
UCI_BILL_COLUMNS = [f"BILL_AMT{month}" for month in range(1, 7)]
UCI_PAYMENT_COLUMNS = [f"PAY_AMT{month}" for month in range(1, 7)]


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATEGORY_CONFIG_PATH = PROJECT_ROOT / "config" / "category_rules.json"
NLP_MODEL_PATH = PROJECT_ROOT / "models" / "transaction_nlp_pipeline.joblib"
_category_config = json.loads(CATEGORY_CONFIG_PATH.read_text(encoding="utf-8"))
CATEGORY_RULES: tuple[tuple[str, str], ...] = tuple(
    (label, "|".join(patterns)) for label, patterns in _category_config["categories"].items()
)
CATEGORY_OPTIONS: tuple[str, ...] = tuple(_category_config["categories"]) + ("Other", "Income/other")
ESSENTIAL_CATEGORIES = {"Rent", "EMI/loan repayment", "Utilities", "Groceries", "Transport/fuel", "Healthcare"}
NON_INCOME_CREDIT_CATEGORIES = {
    "Refund/reversal",
    "Transfer/other inflow",
    "Cash deposit",
    "Loan disbursement",
    "Investment redemption",
}


def normalise_merchant_key(description: object) -> str:
    """Create a conservative grouping key for repeated statement narrations.

    The key is for an officer's bulk-review convenience only. It does not infer
    that descriptions with a similar key belong to the same real-world merchant.
    """
    value = str(description or "").lower()
    value = re.sub(r"\d+", " ", value)
    value = re.sub(r"[^a-z]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def build_repeated_merchant_groups(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return repeat-description groups that an officer may review in bulk."""
    if "description" not in transactions:
        raise ValueError("Transactions are missing required column: description")
    grouped = transactions.copy()
    grouped["merchant_key"] = grouped["description"].map(normalise_merchant_key)
    grouped = grouped[grouped["merchant_key"].ne("")]
    if grouped.empty:
        return pd.DataFrame(columns=["merchant_key", "example_description", "transactions", "current_categories"])
    groups = (
        grouped.groupby("merchant_key", sort=True, observed=True)
        .agg(
            example_description=("description", "first"),
            transactions=("description", "size"),
            current_categories=("category", lambda values: ", ".join(sorted(set(map(str, values))))),
        )
        .reset_index()
    )
    return groups[groups["transactions"].ge(2)].reset_index(drop=True)


def apply_bulk_category_override(
    transactions: pd.DataFrame,
    merchant_key: str,
    category: str,
    reviewer: str,
    rationale: str,
    timestamp_utc: str,
) -> tuple[pd.DataFrame, int]:
    """Apply one reviewed category to all rows sharing a displayed merchant key.

    A non-empty rationale and an allowed category are required so that the bulk
    operation remains reviewable. The original rule category is retained.
    """
    if category not in CATEGORY_OPTIONS:
        raise ValueError(f"Unknown transaction category: {category}")
    if not rationale.strip():
        raise ValueError("A rationale is required for a bulk category override.")
    result = categorise_statement_transactions(transactions)
    keys = result["description"].map(normalise_merchant_key)
    matches = keys.eq(merchant_key)
    if not matches.any():
        raise ValueError("No transactions match the selected merchant group.")
    if "original_category" not in result:
        result["original_category"] = result["category"]
    result["original_category"] = result["original_category"].fillna(result["category"])
    changed = matches & result["category"].ne(category)
    result.loc[changed, "category"] = category
    result.loc[changed, "category_review_status"] = "Officer bulk override"
    result.loc[changed, "category_confidence"] = 1.0
    result.loc[changed, "category_reviewer"] = reviewer or "Not supplied"
    result.loc[changed, "category_override_rationale"] = rationale.strip()
    result.loc[changed, "category_override_timestamp_utc"] = timestamp_utc
    result["is_essential"] = result["category"].isin(ESSENTIAL_CATEGORIES)
    result["is_discretionary"] = result["category"].eq("Shopping/discretionary")
    return result, int(changed.sum())


_nlp_pipeline_cache = None


def load_nlp_pipeline():
    """Load and memory-cache the transaction NLP classification pipeline."""
    global _nlp_pipeline_cache
    if _nlp_pipeline_cache is not None:
        return _nlp_pipeline_cache
    if NLP_MODEL_PATH.exists():
        try:
            bundle = joblib.load(NLP_MODEL_PATH)
            _nlp_pipeline_cache = bundle.get("pipeline")
        except Exception:
            _nlp_pipeline_cache = None
    return _nlp_pipeline_cache


def categorise_statement_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    """Assign hybrid rule-based and NLP machine-learning categories to transactions.

    Exact regex rules identify deterministic channels (e.g. salary, loan disbursal),
    while the trained TF-IDF + Calibrated Linear model categorises messy merchant descriptions
    and provides genuine probabilistic confidence scores.
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
        result["category_match_count"] = result.get("category_match_count", 1)
        result["is_essential"] = result["category"].isin(ESSENTIAL_CATEGORIES)
        result["is_discretionary"] = result["category"].eq("Shopping/discretionary")
        return result

    description = result["description"].fillna("").astype(str).str.lower()
    category = pd.Series("Other", index=result.index, dtype="object")
    match_count = pd.Series(0, index=result.index, dtype="int64")

    # Step 1: Rule-based matching for deterministic accounting categories
    for label, pattern in CATEGORY_RULES:
        matches = description.str.contains(pattern, case=False, regex=True, na=False)
        match_count += matches.astype(int)
        category.loc[matches & category.eq("Other")] = label

    # Unlabelled credits are treated conservatively as Income/other
    category.loc[(result["credit"] > 0) & (category == "Other")] = "Income/other"

    # Step 2: Apply Machine Learning (NLP Model) to augment/generalise unlabelled transactions
    nlp_model = load_nlp_pipeline()
    confidences = np.where(match_count.eq(1), 1.0, np.where(match_count.gt(1), 0.5, 0.0))
    review_status = np.where(match_count.eq(1), "Rule match", "Uncertain / needs review")

    if nlp_model is not None:
        try:
            # Predict for rows where rules were uncertain or unlabelled
            uncertain_mask = category.isin(["Other", "Income/other"]) | match_count.eq(0)
            if uncertain_mask.any():
                texts_to_predict = result.loc[uncertain_mask, "description"].fillna("").astype(str).tolist()
                preds = nlp_model.predict(texts_to_predict)
                probs = nlp_model.predict_proba(texts_to_predict)
                max_probs = np.max(probs, axis=1)

                for idx, (row_idx, _) in enumerate(result.loc[uncertain_mask].iterrows()):
                    prob = max_probs[idx]
                    pred_cat = preds[idx]
                    # Require a strong, decisive confidence (>= 65%) to override "Other"
                    if prob >= 0.65:
                        # Prevent misclassifying credit transactions as discretionary expense
                        if result.loc[row_idx, "credit"] > 0 and pred_cat in ESSENTIAL_CATEGORIES | {"Shopping/discretionary"}:
                            continue
                        category.loc[row_idx] = pred_cat
                        confidences[result.index.get_loc(row_idx)] = round(float(prob), 3)
                        review_status[result.index.get_loc(row_idx)] = f"NLP ML match ({prob:.0%})"
                        match_count.loc[row_idx] = 1
        except Exception:
            pass

    result["category"] = category
    result["original_category"] = category
    result["category_confidence"] = confidences
    result["category_review_status"] = review_status
    result["category_match_count"] = match_count
    result["is_essential"] = result["category"].isin(ESSENTIAL_CATEGORIES)
    result["is_discretionary"] = result["category"].eq("Shopping/discretionary")
    return result


def annotate_income_evidence(transactions: pd.DataFrame) -> pd.DataFrame:
    """Separate recognised recurring income from other statement credits.

    A credit is not automatically income. Salary-labelled credits are recognised
    as income evidence; otherwise an unlabelled credit must recur in at least two
    calendar months with a reasonably stable amount before it is treated as a
    recurring-income candidate. This is still statement evidence, not employer
    verification.
    """
    result = categorise_statement_transactions(transactions)
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result["income_evidence"] = "Not an inflow"
    result["income_evidence_confidence"] = 0.0
    credit_mask = result["credit"] > 0
    result.loc[credit_mask, "income_evidence"] = "Unverified other credit"

    salary_mask = credit_mask & result["category"].eq("Salary/income")
    result.loc[salary_mask, "income_evidence"] = "Salary/income rule match"
    result.loc[salary_mask, "income_evidence_confidence"] = 0.75

    for category in NON_INCOME_CREDIT_CATEGORIES:
        category_mask = credit_mask & result["category"].eq(category)
        result.loc[category_mask, "income_evidence"] = category

    candidate_mask = credit_mask & result["category"].eq("Income/other") & result["date"].notna()
    if candidate_mask.any():
        candidate = result.loc[candidate_mask, ["description", "credit", "date"]].copy()
        candidate["month"] = candidate["date"].dt.to_period("M")
        candidate["source_key"] = (
            candidate["description"].fillna("").astype(str).str.lower()
            .str.replace(r"\\d+", "", regex=True).str.replace(r"[^a-z]+", " ", regex=True)
            .str.replace(r"\\s+", " ", regex=True).str.strip()
        )
        for source_key, group in candidate.groupby("source_key", sort=False):
            if not source_key or group["month"].nunique() < 2:
                continue
            mean_credit = float(group["credit"].mean())
            variation = float(group["credit"].std(ddof=0) / mean_credit) if mean_credit else 1.0
            if variation <= 0.20:
                matches = candidate_mask & (
                    result["description"].fillna("").astype(str).str.lower()
                    .str.replace(r"\\d+", "", regex=True).str.replace(r"[^a-z]+", " ", regex=True)
                    .str.replace(r"\\s+", " ", regex=True).str.strip().eq(source_key)
                )
                result.loc[matches, "income_evidence"] = "Recurring income candidate"
                result.loc[matches, "income_evidence_confidence"] = 0.60
    result["is_recognised_income"] = result["income_evidence"].isin(
        {"Salary/income rule match", "Recurring income candidate"}
    )
    return result


def _daily_balance_series(transactions: pd.DataFrame) -> pd.Series:
    """Reconstruct observed daily closing balances by forward-filling transaction-day balances."""
    if "balance" not in transactions or transactions["balance"].abs().sum() == 0:
        return pd.Series(dtype="float64")
    dated = transactions.dropna(subset=["date"]).sort_values("date").copy()
    if dated.empty:
        return pd.Series(dtype="float64")
    dated["day"] = dated["date"].dt.normalize()
    daily = dated.groupby("day", observed=True)["balance"].last()
    return daily.reindex(pd.date_range(daily.index.min(), daily.index.max(), freq="D")).ffill().dropna()


def _month_coverage(transactions: pd.DataFrame) -> tuple[int, bool]:
    """Return observed months and whether either boundary month is incomplete."""
    dates = transactions["date"].dropna().sort_values()
    if dates.empty:
        return 0, False
    months = int(dates.dt.to_period("M").nunique())
    first_partial = dates.iloc[0].day > 5
    last_date = dates.iloc[-1]
    last_partial = last_date.day < (last_date.days_in_month - 5)
    return months, bool(first_partial or (last_partial and months > 1))


def build_monthly_statement_summary(transactions: pd.DataFrame) -> pd.DataFrame:
    """Build a month-level cash-flow view from categorised statement transactions."""
    result = annotate_income_evidence(transactions)
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result = result.dropna(subset=["date"])
    if result.empty:
        raise ValueError("No valid transaction dates were found.")

    result["month"] = result["date"].dt.to_period("M")
    grouped = result.groupby("month", observed=True)
    summary = pd.DataFrame({
        "income": result.loc[result["is_recognised_income"]].groupby("month", observed=True)["credit"].sum(),
        "gross_credits": grouped["credit"].sum(),
        "other_credits": result.loc[
            (result["credit"] > 0) & ~result["is_recognised_income"]
        ].groupby("month", observed=True)["credit"].sum(),
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


def build_statement_features(transactions: pd.DataFrame, monthly_emi: float = 0.0, requested_amount: float = 0.0, proposed_emi: float = 0.0) -> dict[str, object]:
    """Derive affordability features from normalised bank-statement transactions.

    `transactions` must contain `date`, `description`, `debit`, and `credit`.
    Credits are retained as inflows, but affordability income is restricted to
    recognised recurring income evidence rather than every credit transaction.
    """
    if transactions.empty:
        raise ValueError("At least one transaction is required for behavioural analysis.")

    result = annotate_income_evidence(transactions)
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result = result.dropna(subset=["date"])
    if result.empty:
        raise ValueError("No valid transaction dates were found.")

    result["credit"] = pd.to_numeric(result["credit"], errors="coerce").fillna(0.0)
    result["debit"] = pd.to_numeric(result["debit"], errors="coerce").fillna(0.0)
    result["month"] = result["date"].dt.to_period("M")
    monthly_summary = build_monthly_statement_summary(result)
    month_count, has_partial_boundary_month = _month_coverage(result)
    total_credits = float(result["credit"].sum())
    total_income = float(result.loc[result["is_recognised_income"], "credit"].sum())
    other_credits = total_credits - total_income
    uncertain_credit_amount = float(result.loc[
        (result["credit"] > 0) & result["category_review_status"].eq("Uncertain / needs review"), "credit"
    ].sum())
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
    trend_available = month_count >= 3 and not has_partial_boundary_month
    income_trend = (
        float((monthly_summary["income"].iloc[-1] - monthly_summary["income"].iloc[0]) / monthly_summary["income"].iloc[0])
        if trend_available and monthly_summary["income"].iloc[0] > 0
        else None
    )
    savings_trend = (
        float((monthly_summary["surplus"].iloc[-1] - monthly_summary["surplus"].iloc[0]) / average_income)
        if trend_available and average_income > 0
        else None
    )
    expense_variation = float(monthly_summary["expense"].std(ddof=0) / average_expense) if average_expense else 0.0
    nonzero_balances = monthly_summary["closing_balance"].dropna()
    balance_volatility = (
        float(nonzero_balances.std(ddof=0) / abs(nonzero_balances.mean()))
        if len(nonzero_balances) > 1 and nonzero_balances.mean() != 0
        else 0.0
    )
    low_balance_threshold = 0.10 * average_income
    daily_balances = _daily_balance_series(result)
    has_balance_history = not daily_balances.empty
    low_balance_days = int((daily_balances < low_balance_threshold).sum()) if has_balance_history else 0
    monthly_surplus = monthly_summary["surplus"]
    transaction_frequency = float(len(result) / month_count)
    cash_withdrawal_share = float(result.loc[result["category"].eq("Cash withdrawal"), "debit"].sum() / total_expense) if total_expense else 0.0
    recurring_rent = float((result.loc[result["category"].eq("Rent")].groupby("month")["debit"].sum() > 0).mean()) if (result["category"] == "Rent").any() else 0.0
    grocery_transport = result["category"].isin(["Groceries", "Transport/fuel"])
    grocery_transport_trend = float((result.loc[grocery_transport].groupby("month")["debit"].sum().reindex(result["month"].drop_duplicates(), fill_value=0).iloc[-1] - result.loc[grocery_transport].groupby("month")["debit"].sum().reindex(result["month"].drop_duplicates(), fill_value=0).iloc[0]) / average_income) if trend_available and average_income else None
    average_closing_balance = float(daily_balances.mean()) if has_balance_history else 0.0
    minimum_daily_balance = float(daily_balances.min()) if has_balance_history else None
    emergency_buffer_months = average_closing_balance / average_expense if average_expense else 0.0
    negative_balance_count = int((daily_balances < 0).sum()) if has_balance_history else 0
    low_balance_sequence = 0
    max_low_balance_sequence = 0
    if has_balance_history:
        for low in (daily_balances < low_balance_threshold):
            low_balance_sequence = low_balance_sequence + 1 if low else 0
            max_low_balance_sequence = max(max_low_balance_sequence, low_balance_sequence)
    salary_series = monthly_summary["salary_income"]
    missed_salary_months = int((salary_series == 0).sum())
    salary_frequency = "monthly" if salary_months >= max(month_count - 1, 1) else "irregular" if salary_months else "unknown"
    recognised_income_months = int((monthly_summary["income"] > 0).sum())
    income_sources = int(result.loc[result["is_recognised_income"], "description"].str.lower().str.replace(r"\d+", "", regex=True).nunique())
    uncertain_share = float(result["category_review_status"].eq("Uncertain / needs review").mean())
    proposed_emi_ratio = (effective_emi + proposed_emi) / average_income if average_income else 0.0
    discrepancy_base = max(float(monthly_emi), detected_emi, 1.0)
    emi_discrepancy_ratio = abs(float(monthly_emi) - detected_emi) / discrepancy_base
    emi_difference_amount = abs(float(monthly_emi) - detected_emi)
    typical_debit = float(result.loc[result["debit"] > 0, "debit"].median())
    large_spending_count = int((result["debit"] > max(2 * typical_debit, 0.15 * average_income)).sum()) if typical_debit else 0

    return {
        "months_observed": float(month_count),
        "partial_boundary_month": has_partial_boundary_month,
        "trend_available": trend_available,
        "gross_statement_credits": total_credits,
        "recognised_recurring_income": total_income,
        "other_statement_credits": other_credits,
        "uncertain_statement_credits": uncertain_credit_amount,
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
        "declared_monthly_emi": float(monthly_emi),
        "effective_monthly_emi": effective_emi,
        "emi_difference_amount": emi_difference_amount,
        "emi_discrepancy_ratio": emi_discrepancy_ratio,
        "salary_income_share": salary_income / total_income if total_income else 0.0,
        "salary_income_months": float(salary_months),
        "recognised_income_months": float(recognised_income_months),
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
        "balance_observed_days": float(len(daily_balances)),
        "balance_volatility_ratio": balance_volatility,
        "has_balance_history": float(has_balance_history),
        "large_spending_count": float(large_spending_count),
        "sudden_expense_spike_count": float((monthly_summary["expense"] > monthly_summary["expense"].median() * 1.5).sum()),
        "emergency_buffer_months": emergency_buffer_months,
        "minimum_daily_balance": minimum_daily_balance,
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
