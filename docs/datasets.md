# Dataset and artifact guide

The repository includes small demo data, evaluation data, selected model artifacts, and saved evaluation reports so that the dashboard can demonstrate completed work. It deliberately excludes downloaded raw datasets and large simulator output.

## Included in the repository

| Item | Location | Purpose |
|---|---|---|
| Demo bank statement | `data/demo/sample_bank_statement.csv` | Exercises the CSV statement workflow. |
| Labelled category sample | `data/evaluation/labelled_transactions.csv` | Regression test for transaction-category rules. |
| Synthetic feature snapshot | `data/synthetic/simulator_behaviour_features.csv` | Demonstrates the synthetic portfolio tab. |
| Selected LightGBM model | `models/home_credit_lightgbm.joblib` | Enables the saved model-validation dashboard. |
| Evaluation reports | `reports/*.json` | Stores benchmark, threshold, calibration, and category-rule evidence. |

## Download separately

| Dataset | Destination | Source |
|---|---|---|
| UCI Default of Credit Card Clients | `data/raw/uci_credit_default.xls` | https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients |
| Home Credit Default Risk | `data/home_credit/` | https://www.kaggle.com/competitions/home-credit-default-risk/data |
| Bank Data Simulator raw output | Outside the repository or `external/` | https://github.com/kannanjayachandran/bank-data-simulator |

Do not commit real bank statements, identity documents, API keys, or downloaded public datasets that have their own redistribution terms.
