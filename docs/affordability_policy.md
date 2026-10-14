# Affordability policy and safeguards

## Purpose

`statement-affordability-v1` is a transparent prototype policy for organising bank-statement affordability evidence. It is not a statistically validated credit-scorecard, a default-probability model, or an automated lending decision.

## Score components

| Component | Maximum points | Interpretation |
|---|---:|---|
| Savings ratio | 25 | Positive recurring-income surplus supports affordability evidence. |
| Existing EMI burden | 25 | Lower detected/declared EMI relative to recognised recurring income receives more points. |
| Salary consistency | 20 | Repeated salary/income evidence across months reduces uncertainty. |
| Expense stability | 15 | High monthly or balance variation reduces stability points. |
| Utility regularity | 10 | Descriptive continuity signal only; missing utility transactions are not adverse credit evidence. |
| Data quality | 5 | Completeness and consistency of the uploaded CSV. |

## Decision bands

- **75–100:** Meets indicative affordability criteria based on available statement evidence.
- **45–74:** Manual review.
- **0–44:** Does not meet indicative affordability criteria based on available statement evidence.

These bands do not authorise approval or decline. A loan officer remains accountable for the final decision.

## Safeguards take precedence over score

The system does not allow a high numerical score to bypass evidence problems. It requires additional documents or manual review for insufficient statement coverage, poor data quality, no recognised recurring income, balance contradictions, critical EMI burden, low emergency buffer, high uncertain-category share, or a material declared/detected EMI mismatch.

## Sensitivity and validation

`python -m src.evaluation.evaluate_affordability_policy` creates a deterministic scenario and sensitivity report. It verifies code and policy precedence; it does not validate the thresholds against real repayment or default outcomes. Outcome-based validation remains a later project phase.
