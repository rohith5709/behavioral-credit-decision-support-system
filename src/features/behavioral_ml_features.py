"""Bridge layer: map statement-derived features to the UCI behavioral ML model input space.

The behavioral prediction model was trained on the UCI Credit Card Default dataset
using 15 features derived from 6 months of real payment-history and bill data.
This module maps the analogous signals from an uploaded bank statement into that
same feature space so that the trained model can score any applicant whose
statement is available.

Feature mapping rationale
--------------------------
UCI Feature                     Statement Analog
-------------------------------  -------------------------------------------------
behaviour_late_month_count      Months with missed salary / overdraft events
behaviour_max_payment_delay     Income variation ratio (stress proxy)
behaviour_average_bill          Average monthly expense (obligation level)
behaviour_average_payment       Average monthly income (repayment capacity)
behaviour_payment_to_bill_ratio Savings ratio (net coverage of obligations)
behaviour_credit_utilisation    EMI-to-income ratio (balance utilisation proxy)
behaviour_bill_change           Expense variation ratio (rising obligation proxy)
behaviour_debt_increasing       Binary flag: savings trend deteriorating
PAY_0                           Derived from salary consistency (0 = on-time proxy)
PAY_2                           Derived from utility regularity (0 = current proxy)
PAY_3                           Derived from missed salary months (0 = current)
LIMIT_BAL                       Emergency buffer months (capacity proxy, scaled)
PAY_AMT1                        Monthly surplus (most recent repayment ability)
PAY_AMT2                        Minimum monthly surplus (worst-month repayment)
BILL_AMT1                       Average monthly expense (most recent obligation)

All continuous features are on real-valued scales consistent with the UCI training
distribution after StandardScaler normalisation inside the model pipeline.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


# ── Feature names must exactly match the training feature list ────────────────
BEHAVIORAL_FEATURES: list[str] = [
    "behaviour_late_month_count",
    "behaviour_max_payment_delay",
    "behaviour_average_bill",
    "behaviour_average_payment",
    "behaviour_payment_to_bill_ratio",
    "behaviour_credit_utilisation",
    "behaviour_bill_change",
    "behaviour_debt_increasing",
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "LIMIT_BAL",
    "PAY_AMT1",
    "PAY_AMT2",
    "BILL_AMT1",
]

FEATURE_MAPPING_SPECS: dict[str, dict[str, str]] = {
    "behaviour_late_month_count": {
        "statement_source": "low_balance_day_count / 30",
        "description": "Months with liquidity stress or overdraft exposure",
        "rationale": "High low-balance day density directly reflects liquidity strain analogous to missed monthly billing cycles.",
        "bounds": "[0.0, 6.0]",
    },
    "behaviour_max_payment_delay": {
        "statement_source": "income_variation_ratio * 6.0",
        "description": "Maximum payment shock severity proxy",
        "rationale": "Income dispersion (coefficient of variation) models cash flow shock magnitude analogous to delinquency severity.",
        "bounds": "[0.0, 12.0]",
    },
    "behaviour_average_bill": {
        "statement_source": "average_monthly_expense",
        "description": "Average monthly expenditure obligations (INR)",
        "rationale": "Total monthly debits represent recurring consumption and contractual burden.",
        "bounds": "[0.0, inf)",
    },
    "behaviour_average_payment": {
        "statement_source": "average_monthly_income",
        "description": "Average monthly recurring income capacity (INR)",
        "rationale": "Verified monthly credits reflect capacity to service liabilities.",
        "bounds": "[0.0, inf)",
    },
    "behaviour_payment_to_bill_ratio": {
        "statement_source": "savings_ratio (clipped [-1.0, 2.0])",
        "description": "Monthly surplus coverage ratio",
        "rationale": "Savings ratio directly mirrors repayment coverage over recurring bill demands.",
        "bounds": "[-1.0, 2.0]",
    },
    "behaviour_credit_utilisation": {
        "statement_source": "emi_to_income_ratio (clipped [0.0, 2.0])",
        "description": "Contractual debt burden to income ratio",
        "rationale": "EMI-to-income represents proportion of cash flows committed to debt amortisation.",
        "bounds": "[0.0, 2.0]",
    },
    "behaviour_bill_change": {
        "statement_source": "expense_variation_ratio * average_monthly_expense",
        "description": "Expense escalation trend magnitude (INR)",
        "rationale": "Rapidly expanding debits indicate rising obligations and reduced safety margins.",
        "bounds": "(-inf, inf)",
    },
    "behaviour_debt_increasing": {
        "statement_source": "1 if savings_trend < 0 or expense_variation > 0.30 else 0",
        "description": "Deteriorating liquidity trajectory indicator",
        "rationale": "Binary flag signaling whether cash reserves and savings margins are actively eroding.",
        "bounds": "{0.0, 1.0}",
    },
    "PAY_0": {
        "statement_source": "round(min(salary_consistency_ratio * 3.0, 8.0))",
        "description": "Most recent payment regularity status (0 = pristine)",
        "rationale": "Salary receipt consistency models immediate-past contractual stability.",
        "bounds": "[0.0, 8.0]",
    },
    "PAY_2": {
        "statement_source": "round((1.0 - utility_payment_regularity) * 3.0)",
        "description": "Prior-cycle operational payment regularity status",
        "rationale": "Regular utility bill clearance demonstrates persistent payment discipline.",
        "bounds": "[0.0, 3.0]",
    },
    "PAY_3": {
        "statement_source": "min(missed_salary_months, 6.0)",
        "description": "Multi-month income interruption duration",
        "rationale": "Number of zero-salary months models prolonged credit stress and income disruption.",
        "bounds": "[0.0, 6.0]",
    },
    "LIMIT_BAL": {
        "statement_source": "emergency_buffer_months * average_monthly_income",
        "description": "Estimated liquid emergency reserve capacity (INR)",
        "rationale": "Liquid cushion accessible to the borrower to absorb unbudgeted shocks.",
        "bounds": "[0.0, inf)",
    },
    "PAY_AMT1": {
        "statement_source": "max(monthly_surplus, 0.0)",
        "description": "Recent monthly net disposable cash flow (INR)",
        "rationale": "Positive uncommitted cash available immediately for debt repayment.",
        "bounds": "[0.0, inf)",
    },
    "PAY_AMT2": {
        "statement_source": "max(minimum_monthly_surplus, 0.0)",
        "description": "Worst-observed single month net cash flow (INR)",
        "rationale": "Stress-floor cash flow representing repayment capacity during adverse months.",
        "bounds": "[0.0, inf)",
    },
    "BILL_AMT1": {
        "statement_source": "average_monthly_expense",
        "description": "Current monthly contractual expenditure benchmark (INR)",
        "rationale": "Baseline monthly burn rate against which surplus is evaluated.",
        "bounds": "[0.0, inf)",
    },
}


def get_feature_mapping_documentation() -> dict[str, dict[str, str]]:
    """Return dictionary of all 15 feature mappings with examiner rationale and bounds."""
    return FEATURE_MAPPING_SPECS


def map_statement_to_behavioral_features(features: dict[str, object]) -> pd.DataFrame:
    """Convert statement feature dict to a single-row DataFrame for the behavioral ML model.

    Parameters
    ----------
    features:
        Output of ``build_statement_features()`` — the full statement feature dictionary.

    Returns
    -------
    pd.DataFrame
        Shape (1, 15) with columns matching BEHAVIORAL_FEATURES and no NaN values.
    """
    # ── Safe numeric extraction with defensive fallbacks ─────────────────────
    try:
        savings_ratio = float(features.get("savings_ratio", 0.0) or 0.0)
    except (ValueError, TypeError):
        savings_ratio = 0.0

    try:
        emi_ratio = float(features.get("emi_to_income_ratio", 0.0) or 0.0)
    except (ValueError, TypeError):
        emi_ratio = 0.0

    try:
        avg_income = max(float(features.get("average_monthly_income", 0.0) or 0.0), 0.0)
    except (ValueError, TypeError):
        avg_income = 0.0

    try:
        avg_expense = max(float(features.get("average_monthly_expense", 0.0) or 0.0), 0.0)
    except (ValueError, TypeError):
        avg_expense = 0.0

    try:
        income_variation = max(float(features.get("income_variation_ratio", 0.0) or 0.0), 0.0)
    except (ValueError, TypeError):
        income_variation = 0.0

    try:
        salary_consistency = max(float(features.get("salary_consistency_ratio", 1.0) or 1.0), 0.0)
    except (ValueError, TypeError):
        salary_consistency = 1.0

    try:
        utility_regularity = max(min(float(features.get("utility_payment_regularity", 0.0) or 0.0), 1.0), 0.0)
    except (ValueError, TypeError):
        utility_regularity = 0.0

    try:
        low_balance_days = max(float(features.get("low_balance_day_count", 0.0) or 0.0), 0.0)
    except (ValueError, TypeError):
        low_balance_days = 0.0

    try:
        emergency_buffer = max(float(features.get("emergency_buffer_months", 0.0) or 0.0), 0.0)
    except (ValueError, TypeError):
        emergency_buffer = 0.0

    try:
        missed_salary = max(float(features.get("missed_salary_months", 0.0) or 0.0), 0.0)
    except (ValueError, TypeError):
        missed_salary = 0.0

    try:
        monthly_surplus = float(features.get("monthly_surplus", 0.0) or 0.0)
    except (ValueError, TypeError):
        monthly_surplus = 0.0

    try:
        min_surplus = float(features.get("minimum_monthly_surplus", 0.0) or 0.0)
    except (ValueError, TypeError):
        min_surplus = 0.0

    try:
        expense_variation = max(float(features.get("expense_variation_ratio", 0.0) or 0.0), 0.0)
    except (ValueError, TypeError):
        expense_variation = 0.0

    try:
        raw_trend = features.get("savings_trend_ratio")
        savings_trend = float(raw_trend) if raw_trend is not None else 0.0
    except (ValueError, TypeError):
        savings_trend = 0.0

    # ── Feature mappings with strict domain bounds ───────────────────────────
    late_month_count = min(low_balance_days / 30.0, 6.0)
    max_payment_delay = min(income_variation * 6.0, 12.0)
    average_bill = avg_expense
    average_payment = avg_income
    payment_to_bill_ratio = max(min(savings_ratio, 2.0), -1.0)
    credit_utilisation = max(min(emi_ratio, 2.0), 0.0)
    bill_change = expense_variation * avg_expense
    debt_increasing = 1.0 if (savings_trend < 0.0 or expense_variation > 0.30) else 0.0
    pay_0 = float(int(round(min(salary_consistency * 3.0, 8.0))))
    pay_2 = float(int(round((1.0 - utility_regularity) * 3.0)))
    pay_3 = float(int(min(missed_salary, 6.0)))
    limit_bal = emergency_buffer * avg_income
    pay_amt1 = max(monthly_surplus, 0.0)
    pay_amt2 = max(min_surplus, 0.0)
    bill_amt1 = avg_expense

    row = {
        "behaviour_late_month_count": late_month_count,
        "behaviour_max_payment_delay": max_payment_delay,
        "behaviour_average_bill": average_bill,
        "behaviour_average_payment": average_payment,
        "behaviour_payment_to_bill_ratio": payment_to_bill_ratio,
        "behaviour_credit_utilisation": credit_utilisation,
        "behaviour_bill_change": bill_change,
        "behaviour_debt_increasing": debt_increasing,
        "PAY_0": pay_0,
        "PAY_2": pay_2,
        "PAY_3": pay_3,
        "LIMIT_BAL": limit_bal,
        "PAY_AMT1": pay_amt1,
        "PAY_AMT2": pay_amt2,
        "BILL_AMT1": bill_amt1,
    }

    frame = pd.DataFrame([row], columns=BEHAVIORAL_FEATURES)
    return frame.fillna(0.0).replace([np.inf, -np.inf], 0.0)
