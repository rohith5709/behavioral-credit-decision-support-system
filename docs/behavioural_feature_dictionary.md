# Behavioural feature dictionary

This dictionary describes the indicators derived from an uploaded CSV bank statement. They are evidence for human review, not proof of income, identity, or creditworthiness.

| Feature | Derivation | Review interpretation |
|---|---|---|
| Average monthly income | Total statement credits divided by observed months | Context for affordability; does not verify income source. |
| Average monthly expense | Total debits divided by observed months | Typical cash outflow. |
| Monthly surplus | Average income minus average expense | Positive value supports capacity; negative value is a caution signal. |
| Savings ratio | Monthly surplus divided by average income | Used in the affordability score (25 points maximum). |
| Salary consistency ratio | Standard deviation of detected salary credits divided by their mean | Lower variation suggests more regular detected salary credits. |
| Income trend ratio | Change from first to last month’s income relative to first-month income | Descriptive change, not a forecast. |
| Savings trend ratio | Change from first to last monthly surplus relative to average income | Descriptive change, not a forecast. |
| Expense variation ratio | Standard deviation of monthly expenses divided by mean expense | Lower variation contributes to expense stability. |
| Essential-expense ratio | Rent, EMI, utilities, groceries, transport, and healthcare debit divided by total debit | Shows how much spend was rule-labelled essential. |
| Discretionary-expense ratio | Rule-labelled shopping/discretionary debit divided by total debit | Shows relative discretionary spend. |
| EMI-to-income ratio | Higher of declared or detected monthly EMI divided by average monthly income | Used in the affordability score (25 points maximum). Over 50% forces manual review. |
| Utility-payment regularity | Months containing a rule-labelled utility debit divided by observed months | Used as an affordability evidence signal. |
| Cash withdrawals per month | Cash-withdrawal transaction count divided by observed months | Descriptive cash-use signal. |
| Low-balance day count | Statement rows with balance below 10% of average income | Available only if balances are supplied. |
| Balance volatility ratio | Standard deviation of monthly closing balance divided by mean closing balance | Used with expense variation in stability assessment. |
| Large-spending count | Debit transactions exceeding both two times median debit and 15% of average income | Prompt for review, not a conclusion about risk. |
| Salary frequency and missed months | Presence of rule-labelled salary credits across observed months | Indicates monthly, irregular, or unavailable statement evidence; it does not verify employment. |
| Detected EMI payment occurrence | Months containing rule-labelled EMI/loan-payment transactions | This is not called repayment history because due dates and lateness are unknown. |
| Emergency buffer | Average month-end balance divided by average monthly expense | Shown as unavailable when the statement has no balance history. |
| Proposed-EMI-to-income ratio | Existing detected/declared EMI plus illustrative new EMI divided by average income | Supports affordability review for the requested loan; not a loan offer. |
| Post-loan monthly surplus | Average income minus expense minus illustrative new EMI | Helps compare before/after request affordability. |
| Uncertain transaction share | Transactions that were unmatched or matched multiple category rules divided by all transactions | High uncertainty triggers an evidence-review safeguard. |

## Rule-based categories

Descriptions are classified locally using transparent keywords: Salary/income, Rent, EMI/loan repayment, Utilities, Groceries, Transport/fuel, Healthcare, Shopping/discretionary, Cash withdrawal, Other, and Income/other. A reviewer must verify transactions that are ambiguous or labelled Other.
