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
    # ── Raw statement signals ────────────────────────────────────────────────
    savings_ratio: float = float(features.get("savings_ratio", 0.0))
    emi_ratio: float = float(features.get("emi_to_income_ratio", 0.0))
    avg_income: float = max(float(features.get("average_monthly_income", 0.0)), 0.0)
    avg_expense: float = max(float(features.get("average_monthly_expense", 0.0)), 0.0)
    income_variation: float = float(features.get("income_variation_ratio", 0.0))
    salary_consistency: float = float(features.get("salary_consistency_ratio", 1.0))
    utility_regularity: float = float(features.get("utility_payment_regularity", 0.0))
    low_balance_days: float = float(features.get("low_balance_day_count", 0.0))
    emergency_buffer: float = float(features.get("emergency_buffer_months", 0.0))
    missed_salary: float = float(features.get("missed_salary_months", 0.0))
    monthly_surplus: float = float(features.get("monthly_surplus", 0.0))
    min_surplus: float = float(features.get("minimum_monthly_surplus", 0.0))
    expense_variation: float = float(features.get("expense_variation_ratio", 0.0))
    savings_trend: float = float(features.get("savings_trend_ratio") or 0.0)

    # ── Feature mappings ─────────────────────────────────────────────────────

    # behaviour_late_month_count: months with potential cash stress.
    # Low-balance days / 30 days gives a fractional month count; cap at 6 for
    # consistency with the UCI 6-month window.
    late_month_count = min(low_balance_days / 30.0, 6.0)

    # behaviour_max_payment_delay: worst single-period stress magnitude.
    # Income variation ratio (σ/μ) captures volatility of income — a high value
    # means the borrower had income shocks similar to payment delays.
    max_payment_delay = income_variation * 6.0  # scale to UCI delay range [0, ~8]

    # behaviour_average_bill / behaviour_average_payment: use raw INR amounts.
    # UCI training data used actual NT dollar amounts; model pipeline applies
    # StandardScaler, so the absolute scale is handled at inference time.
    average_bill = avg_expense
    average_payment = avg_income

    # behaviour_payment_to_bill_ratio: savings ratio is a direct analog.
    payment_to_bill_ratio = max(min(savings_ratio, 2.0), -1.0)

    # behaviour_credit_utilisation: EMI burden is the closest analog to
    # outstanding balance / credit limit utilisation.
    credit_utilisation = max(min(emi_ratio, 2.0), 0.0)

    # behaviour_bill_change: expense variation captures rising obligations.
    # Positive = expenses increasing (bills growing), negative = shrinking.
    bill_change = expense_variation * avg_expense

    # behaviour_debt_increasing: binary flag for deteriorating savings trend.
    debt_increasing = 1 if (savings_trend < 0.0 or expense_variation > 0.30) else 0

    # PAY_0 (most recent payment status): salary consistency is our best proxy.
    # 0 = on-time in UCI; here 0 = highly consistent salary (variation ≈ 0).
    # Scale: 0 (very consistent) → 3 (very inconsistent), rounded to integer.
    pay_0 = int(round(min(salary_consistency * 3.0, 8.0)))

    # PAY_2 (t-2 status): utility regularity is a second behavioral signal.
    # High utility regularity → low payment delay proxy.
    pay_2 = int(round((1.0 - utility_regularity) * 3.0))

    # PAY_3 (t-3 status): missed salary months → prolonged stress signal.
    pay_3 = int(min(missed_salary, 6))

    # LIMIT_BAL: emergency buffer as capacity signal.
    # 3 months buffer ≈ moderate limit; scale to a synthetic limit figure.
    limit_bal = max(emergency_buffer, 0.0) * avg_income

    # PAY_AMT1 (most recent payment): monthly surplus as repayment ability.
    pay_amt1 = max(monthly_surplus, 0.0)

    # PAY_AMT2 (second most recent payment): minimum-month surplus is the
    # worst-case repayment signal — aligns with PAY_AMT2 being the prior month.
    pay_amt2 = max(min_surplus, 0.0)

    # BILL_AMT1 (most recent bill): current expense level.
    bill_amt1 = avg_expense

    row = {
        "behaviour_late_month_count": late_month_count,
        "behaviour_max_payment_delay": max_payment_delay,
        "behaviour_average_bill": average_bill,
        "behaviour_average_payment": average_payment,
        "behaviour_payment_to_bill_ratio": payment_to_bill_ratio,
        "behaviour_credit_utilisation": credit_utilisation,
        "behaviour_bill_change": bill_change,
        "behaviour_debt_increasing": float(debt_increasing),
        "PAY_0": float(pay_0),
        "PAY_2": float(pay_2),
        "PAY_3": float(pay_3),
        "LIMIT_BAL": limit_bal,
        "PAY_AMT1": pay_amt1,
        "PAY_AMT2": pay_amt2,
        "BILL_AMT1": bill_amt1,
    }

    frame = pd.DataFrame([row], columns=BEHAVIORAL_FEATURES)
    return frame.fillna(0.0).replace([np.inf, -np.inf], 0.0)
