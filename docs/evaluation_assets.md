# Evaluation assets index

Use these artefacts for the final project report or presentation.

| Asset | File | Evidence source |
|---|---|---|
| Behavioural-feature dictionary | `docs/behavioural_feature_dictionary.md` | Feature-engineering rules in `src/features/behavioral.py` |
| Model comparison and threshold report | `docs/model_and_threshold_report.md` | Saved benchmark, threshold, and calibration JSON reports |
| CSV parser test report | `docs/csv_parser_test_report.md` | `tests/test_statement_csv.py`, `tests/test_features.py`, `tests/test_decision.py` |
| Category-rule regression evaluation | `reports/category_rule_evaluation.json` | `data/evaluation/labelled_transactions.csv` and `src/evaluation/evaluate_categories.py` |
| System architecture | `docs/system_architecture.md` | Current processing and review pipeline |
| Limitations and ethics | `docs/limitations_and_ethics.md` | Prototype scope and safeguards |
| Dashboard screenshots | Capture Upload, Behaviour profile, Synthetic portfolio, Model validation, and Officer decision after analysing `data/demo/sample_bank_statement.csv` | Live Streamlit app |

## Screenshot procedure

1. Run `streamlit run app.py`.
2. In **1. Upload statement**, upload `data/demo/sample_bank_statement.csv` and select **Analyse statement**.
3. Capture one screenshot in each of the five tabs. Keep the model-validation screenshot high enough to show the selected model metrics; capture the officer-decision screenshot after completing the sidebar request details and consent checkbox.

The local application was verified after the Phase 6 changes with 15 passing automated tests and a headless Streamlit application check with no exceptions.
