# Statement-compatible ML bridge

## Current status

The dashboard produces transparent statement-derived affordability evidence.
It does **not** produce an ML risk score for uploaded statements. The Home
Credit benchmark remains separate because its applicant and bureau features are
not available in a raw bank-statement CSV.

## Phase 12 feature contract

`config/statement_ml_feature_contract_v1.json` defines the compatible future
model inputs: loan request terms plus statement-derived income, expense,
savings, volatility, liquidity, EMI, uncertainty, and post-loan-surplus
indicators. It deliberately excludes Home Credit-only external-source and
bureau-history features, protected characteristics, and unverified claims.

`src.models.statement_compatible.statement_model_feature_row` maps a parsed
statement plus the loan request into that contract. Missing balance evidence is
preserved as unavailable; a later model pipeline must learn imputation from
training data only.

## Required labelled data

Use `data/evaluation/statement_compatible_applicant_template.csv` only as a
schema template. Do not add real applicant records to Git. A training dataset
must be consented, anonymised, applicant-level, and include:

- a unique non-identifying case ID;
- application date for temporal validation;
- statement-compatible features derived before the loan outcome;
- requested amount, tenure, and interest rate;
- a defined repayment/default outcome label and outcome window.

Before training, validate it with:

```powershell
python -m src.evaluation.evaluate_statement_ml_readiness `
  --input path/to/consented_anonymised_applicant_outcomes.csv `
  --output reports/statement_ml_data_readiness.json
```

The minimum readiness gate is 1,000 labelled cases, 100 positive outcomes,
unique case IDs, valid binary outcomes, and valid application dates. These are
minimum engineering checks, not proof that the data is representative.

## Planned ablations after the gate passes

1. Loan-request fields only.
2. Loan-request fields plus statement-compatible behavioural features.
3. A separately governed compatible credit-history group, only if it is truly
   available at application time and supported by consent/legal review.

Compare PR-AUC, ROC-AUC, recall, precision, calibration, temporal stability,
and applicable fairness checks. Never train or deploy the bridge on synthetic
Bank Data Simulator outcomes or Home Credit labels as substitutes for the
intended statement-based applicant population.
