# Home Credit model and threshold report

Dataset: Home Credit Default Risk. Split: one stratified 80/20 hold-out set with `random_state=42`. The uploaded-statement assessment is separate and does not use this model.

## Candidate comparison

| Candidate | Train rows | Train seconds | ROC-AUC | PR-AUC | Recall @ 0.50 | Precision @ 0.50 | Brier score |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression (balanced) | 246,008 | 3.80 | 0.7490 | 0.2244 | 0.6794 | 0.1624 | 0.2026 |
| LightGBM (unweighted) | 246,008 | 5.71 | 0.7711 | 0.2623 | 0.0278 | 0.5520 | 0.0668 |
| **LightGBM (balanced), selected** | **246,008** | **9.47** | **0.7730** | **0.2660** | **0.6632** | **0.1822** | 0.1777 |
| Random Forest (balanced, 50k cap) | 50,000 | 15.94 | 0.7424 | 0.2216 | 0.3791 | 0.2342 | 0.1218 |
| XGBoost (balanced, 50k cap) | 50,000 | 2.29 | 0.7540 | 0.2400 | 0.5428 | 0.1982 | 0.1488 |

Selection order is ROC-AUC, then PR-AUC, then lower Brier score. The selected balanced LightGBM is used for evaluation artefacts only; it is not scored against raw uploaded transactions.

## Calibrated threshold analysis

The selected model uses Platt scaling (three-fold sigmoid calibration). Its Brier score improved from 0.1777 to 0.0667 after calibration.

| Threshold | Recall | Precision | Flagged applicant rate |
|---:|---:|---:|---:|
| 0.20 | 0.3351 | 0.3067 | 0.0882 |
| 0.30 | 0.1519 | 0.4161 | 0.0295 |
| 0.40 | 0.0530 | 0.5260 | 0.0081 |
| 0.50 | 0.0109 | 0.6207 | 0.0014 |

Threshold choice is a policy decision: lower thresholds identify more potential defaults but flag more applicants; higher thresholds increase precision but miss more defaults.

Machine-readable sources: `reports/home_credit_model_comparison.json`, `reports/home_credit_threshold_analysis.json`, and `reports/home_credit_calibration.json`.
