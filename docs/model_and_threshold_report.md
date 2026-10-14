# Home Credit model and threshold report

Dataset: Home Credit Default Risk. The Phase 11 benchmark uses stratified 64% training, 16% validation, and untouched 20% final-test partitions, all generated with `random_state=42`. Candidate selection, calibration-method selection, and alert-threshold selection use validation data only. The final test set is evaluated only after those choices are frozen. The uploaded-statement assessment is separate and does not use this model.

## Candidate comparison

| Candidate | Train rows | Train seconds | Validation ROC-AUC | Validation PR-AUC | Recall @ 0.50 | Precision @ 0.50 | F1 @ 0.50 | Brier score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression (balanced) | 196,806 | 6.73 | 0.7455 | 0.2143 | 0.6707 | 0.1600 | 0.2584 | 0.2051 |
| LightGBM (unweighted) | 196,806 | 8.51 | 0.7669 | 0.2491 | 0.0257 | 0.5543 | 0.0491 | 0.0675 |
| **LightGBM (balanced), selected** | **196,806** | **15.55** | **0.7674** | **0.2510** | **0.6528** | **0.1821** | **0.2848** | 0.1767 |
| Random Forest (balanced, 50k cap) | 50,000 | 25.00 | 0.7420 | 0.2146 | 0.3781 | 0.2284 | 0.2848 | 0.1223 |
| XGBoost (balanced, 50k cap) | 50,000 | 4.03 | 0.7492 | 0.2320 | 0.5418 | 0.1945 | 0.2863 | 0.1516 |

Selection order is validation PR-AUC, then validation ROC-AUC, then lower validation Brier score. Random Forest and XGBoost retain their deterministic 50,000-row training cap for practical runtime. The selected model is used for evaluation artefacts only; it is not scored against raw uploaded transactions.

## Calibrated threshold analysis

Uncalibrated, Platt-scaled, and isotonic-calibrated probabilities are compared on validation data. The chosen method is refit on combined development data and evaluated once on the untouched final test partition. Reliability rows and final-test Brier score are saved in the calibration report.

| Threshold | Final-test recall | Final-test precision | Final-test F1 | Flagged applicant rate |
|---:|---:|---:|---:|---:|
| **0.20 (validation-selected)** | **0.3333** | **0.3053** | **0.3187** | **0.0881** |
| 0.30 | 0.1492 | 0.4103 | 0.2189 | 0.0294 |
| 0.40 | 0.0540 | 0.5276 | 0.0979 | 0.0083 |
| 0.50 | 0.0097 | 0.6316 | 0.0190 | 0.0012 |

## Sealed final-test result

The validation-selected, Platt-calibrated LightGBM achieved final-test ROC-AUC **0.7737** (bootstrap 95% CI **0.7668–0.7811**) and PR-AUC **0.2664** (bootstrap 95% CI **0.2553–0.2785**). At the validation-selected 0.20 alert threshold, it achieved recall **0.3333**, precision **0.3053**, and F1 **0.3187**. These are benchmark results only, not lending-decision performance claims.

Threshold choice is a policy decision: lower thresholds identify more potential defaults but flag more applicants; higher thresholds increase precision but miss more defaults. The configured validation policy attempted to select the most precise threshold reaching at least 50% validation recall; no evaluated threshold reached that target, so it selected the threshold with the highest evaluated validation recall. On the final test partition, the selected 0.20 alert threshold reached 33.3% recall. It must be presented as a prototype officer-review alert, not as a recall-target-achieving policy or an automated decision threshold.

Machine-readable sources: `reports/home_credit_model_comparison.json`, `reports/home_credit_threshold_analysis.json`, `reports/home_credit_calibration.json`, `reports/home_credit_training_config.json`, and `reports/home_credit_model_card.json`.
