# Claims and evidence matrix

This register defines the strongest wording permitted in the repository, dashboard, reports, and presentations. A claim must not be stronger than the cited evidence.

| Claim | Evidence | Approved wording | Boundary / limitation |
| --- | --- | --- | --- |
| CSV statement workflow | `src/documents/statement_csv.py`, `tests/test_statement_csv.py`, `app.py` | The prototype maps and validates uploaded CSV statement data, then produces reviewable transaction evidence. | It does not authenticate a statement, account holder, employer, income, or identity. |
| Transaction categorisation | `config/category_rules.json`, `src/features/behavioral.py`, `data/evaluation/labelled_transactions.csv` | The prototype uses configurable rules to categorise recognised transaction descriptions and marks ambiguous cases for review. | The 12-row labelled file and 19-row coverage fixture are curated regression checks, not production-accuracy validation. |
| Behavioural affordability assessment | `src/features/behavioral.py`, `src/decision/affordability.py`, `config/affordability_policy_v1.json` | The prototype provides a transparent, policy-based affordability assessment intended to support officer review. | It is not a statistically validated probability of repayment, a credit scorecard, or an automated lending decision. |
| Proposed-loan EMI calculation | `src/decision/affordability.py`, `tests/test_decision.py` | The dashboard estimates an illustrative EMI and displays before/after-loan affordability evidence. | It is not a loan offer; actual lender terms and eligibility can differ. |
| Officer review | `app.py`, `src/reporting/case_summary.py`, `tests/test_case_summary.py` | The dashboard captures an officer action, override rationale, and downloadable decision record. | A local downloadable record is not an immutable audit log or institutional case-management system. |
| Home Credit benchmark | `src/models/benchmark_home_credit.py`, `reports/home_credit_model_card.json`, `docs/model_and_threshold_report.md` | A separate Home Credit default-risk benchmark is evaluated using a stratified train/validation/untouched-test split. | It is a single-dataset benchmark, not evidence of performance for uploaded statements, Indian borrowers, or a lender population. |
| Final benchmark metrics | `reports/home_credit_model_card.json` | The selected calibrated LightGBM benchmark achieved final-test ROC-AUC 0.7737 and PR-AUC 0.2664 on Home Credit. | The 0.20 alert threshold achieved 33.3% final-test recall and is an officer-review alert, not an automated decision threshold. |
| Synthetic portfolio | `src/data/simulator_adapter.py`, `data/synthetic/simulator_behaviour_features.csv` | The simulator integration demonstrates portfolio-level synthetic behavioural data. | Synthetic churn-oriented labels are not applicant evidence or loan-default labels. |
| Test coverage | `tests/` and `pytest -q` | Automated tests verify implemented parser, feature, policy, reporting, dashboard, and ML-bridge behaviour. | Passing software tests do not establish real-world lending validity, fairness, security certification, or user benefit. |
| Presentation deck | `Final Project Presentation (2).pdf`, this register, and the evidence files above | The presentation may describe the implemented CSV affordability-support prototype and separately evaluated Home Credit benchmark. | OCR, salary-slip/ITR parsing, applicant-level statement ML, SHAP, real-world validation, deployment, and an audit store are future work, not completed deliverables. |

## Prohibited wording

- Do not call the statement affordability score an AI prediction, default probability, validated credit score, or final lending decision.
- Do not say the Home Credit model scores uploaded CSV statements.
- Do not report curated category-fixture F1 as real-world or production accuracy.
- Do not call detected EMI payment occurrences repayment history or on-time repayment evidence.
- Do not call the local downloadable decision record an audit trail.
