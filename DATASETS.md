# Dataset register

This register records data provenance, permitted project use, and evidence limits. No external dataset should be downloaded, retained, or used in reports until its licence, access terms, schema, and suitability have been checked in the applicable phase.

| Source | Status | Intended project use | Evidence limit |
| --- | --- | --- | --- |
| Demo bank statement (`data/demo/sample_bank_statement.csv`) | Included, synthetic/demo | Demonstrate CSV parsing, behavioural features, policy flow, and dashboard. | Not real applicant data; cannot validate creditworthiness or repayment. |
| Labelled category sample and held-out coverage fixture (`data/evaluation/`) | Included, curated | Rule-regression and category-coverage checks. | Self-authored/curated examples; not production category validation. |
| Seeded statement generator/personas | Planned, repository-controlled | Parser edge cases, policy sensitivity, stress scenarios, and fairness persona pairs. | Tests code behaviour and stability only, not real-world validity. |
| Home Credit Default Risk | Already used; Kaggle competition data | Separate model benchmark, calibration, threshold evaluation, ablation, and group checks. | Different market and feature schema; not used to score uploaded statements. Respect Kaggle terms and do not redistribute raw files. |
| UCI Default of Credit Card Clients | Optional baseline; UCI repository | Legacy baseline training/demo only. | Credit-card dataset; not a bank-statement outcome dataset. Respect source terms. |
| Bank Data Simulator | Included derived synthetic snapshot; upstream GitHub project | Synthetic portfolio demonstration. | Churn-oriented synthetic labels are not loan-default labels or applicant evidence. |
| Agami Indian statement examples | Planned; Hugging Face/public source subject to review | Parser layouts and categorisation evaluation. | Use only after licence, privacy, and label inspection; any result remains public-data evaluation. |
| Kaggle UPI dataset | Planned; only if labels pass inspection | Categorisation experiment. | Labels and licence must be verified before use; not a lending-outcome dataset. |
| Berka / PKDD'99 Financial dataset | Planned; CTU repository subject to review | Phase-5 behavioural-ML methodology experiment. | Old Czech data; not representative of Indian borrowers or valid for uploaded-statement decisions. |

## Data handling rule

Do not commit real statements, identity documents, account numbers, API keys, or downloaded datasets with restricted redistribution terms. Use only synthetic, anonymised, or consented data for demonstrations and evaluation.
