# Evaluation assets index

Use these artefacts for the final project report or presentation.

| Asset | File | Evidence source |
|---|---|---|
| Behavioural-feature dictionary | `docs/behavioural_feature_dictionary.md` | Feature-engineering rules in `src/features/behavioral.py` |
| Model comparison, threshold, calibration, and model card | `docs/model_and_threshold_report.md` | Saved benchmark, threshold, calibration, training-configuration, and model-card JSON reports |
| Statement-compatible ML bridge contract | `docs/statement_ml_bridge.md` | `config/statement_ml_feature_contract_v1.json`, safe data template, and readiness validator; no model training without real consented outcome labels |
| Automated software test suite | `tests/` | `pytest -q`; validates implemented parser, feature, policy, reporting, dashboard, and ML-bridge behaviour, not real-world lending validity |
| Category-rule regression evaluation | `reports/category_rule_evaluation.json` | `data/evaluation/labelled_transactions.csv` and `src/evaluation/evaluate_categories.py` |
| Category-rule coverage fixture | `reports/heldout_category_rule_evaluation.json` | `data/evaluation/heldout_transaction_categories.csv`; curated coverage only, not real-statement validation |
| Independent category-validation protocol | `docs/category_validation_protocol.md` | `data/evaluation/independent_category_labels_template.csv`; requires consented anonymised external data before real metrics can be reported |
| Affordability policy truth table and sensitivity report | `reports/affordability_policy_evaluation.json` | `src/evaluation/evaluate_affordability_policy.py` |
| Officer case summary and decision-log fields | Dashboard Case summary and Officer decision tabs | `src/reporting/case_summary.py` |
| System architecture | `docs/system_architecture.md` | Current processing and review pipeline |
| Limitations and ethics | `docs/limitations_and_ethics.md` | Prototype scope and safeguards |
| Dashboard screenshots | Capture Upload, Behaviour profile, Synthetic portfolio, Model validation, and Officer decision after analysing `data/demo/sample_bank_statement.csv` | Live Streamlit app |

## Screenshot procedure

1. Run `streamlit run app.py`.
2. In **1. Upload statement**, upload `data/demo/sample_bank_statement.csv` and select **Analyse statement**.
3. Capture one screenshot in each of the five tabs. Keep the model-validation screenshot high enough to show the selected model metrics; capture the officer-decision screenshot after completing the sidebar request details and consent checkbox.

The local application was last verified after Phase 12 with 37 passing automated tests and a headless Streamlit application check with no exceptions. Passing software tests do not establish real-world lending validity, security certification, fairness, or user benefit.
