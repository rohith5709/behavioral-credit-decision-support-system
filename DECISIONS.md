# Decision register

## Scope and evidence boundaries

| Decision | Current choice | Reason and consequence |
| --- | --- | --- |
| Primary statement assessment | Transparent `statement-affordability-v1` policy | Statement features lack consented historical repayment/default labels. The result is evidence for officer review, not a probability of default. |
| Final decision authority | Human officer | The system must not make final lending decisions. Overrides require written rationale in the dashboard. |
| Statement income | Recognised recurring salary/income evidence only | Other credits can be transfers, refunds, cash deposits, loan disbursements, or investments and must not be assumed to be income. |
| EMI statement evidence | `detected EMI payment occurrence` | The statement does not reveal contractual due dates or lateness, so it cannot prove repayment history or timeliness. |
| Mandatory review | Missing recurring income, fewer than three months, low quality, contradictory balances, material EMI mismatch, critical burden, or excessive uncertainty | Missing/contradictory data should trigger review rather than an adverse inference. |
| Affordability policy | `config/affordability_policy_v1.json` | The policy version records score weights, thresholds, and safeguards. Its cut-offs are prototype review safeguards, not empirically validated lending cut-offs. |
| Home Credit benchmark | Separate ML evaluation only | The Home Credit feature schema is incompatible with raw uploaded statement transactions. The model is intentionally not used for applicant scoring. |
| Benchmark split | Stratified 64% train, 16% validation, 20% final test; seed 42 | Candidate, calibration, and threshold choices are made using validation data before final-test reporting. Phase 1 will strengthen this with repeated/nested validation. |
| Benchmark alert threshold | 0.20 after validation selection | It is an officer-review alert threshold. Its final-test recall is 33.3%, so it must not be presented as satisfying a 50% recall target. |
| Category evaluation | Curated rule-regression and coverage fixtures | These fixtures prevent regressions but do not measure real-world accuracy. Independent anonymised labels are required in Phase 3. |
| Synthetic simulator | Demonstration/portfolio analysis only | Synthetic churn-oriented output cannot act as a loan-default outcome or direct applicant evidence. |

## Known limitations

The system currently has no applicant-level statement-compatible ML model, OCR/PDF workflow, salary-slip/ITR verification, real outcome validation, user study, authentication, database, immutable audit store, or deployment controls.
