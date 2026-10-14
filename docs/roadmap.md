# Project Roadmap

This is the authoritative remaining-work plan for the Behavioral Credit Decision Support System. It replaces earlier Phase 9R-14 and Phase 13-21 plans.

## Current baseline

The current prototype supports CSV statement mapping and validation, configurable rule-based categorisation, behavioural affordability features, proposed-EMI analysis, a transparent affordability policy, officer review, exports, a separate Home Credit ML benchmark, and a synthetic portfolio demonstration.

It does **not** yet use an ML model to score uploaded statements, and it does **not** yet support OCR, salary slips, ITRs, authentication, a database, or deployment. The statement affordability recommendation is a transparent policy aid for officer review, not a validated default prediction.

## Planned dataset register

| Phase | Planned dataset/source | Intended use | Evidence boundary |
| --- | --- | --- | --- |
| 0 | None | Create `DATASETS.md` with licence, provenance, whether data is real/synthetic, and limitations. | Documentation only. |
| 1 | Home Credit Default Risk (Kaggle; already in use) | Repeated validation, calibration, `EXT_SOURCE_*` ablation, and proxy/group checks. | Separate benchmark on another market; not statement scoring. |
| 2 | Seeded statement generator; limited public Agami Indian-bank-statement examples, subject to licence review | Parser, encoding, amount-format, preamble, date, formula-injection, PII-masking, and layout-inspired fixture tests. | Constructed/synthetic parser coverage, not a claim about all banks. |
| 3 | Agami statement examples; a Kaggle UPI set only if its labels pass inspection; seeded generator | Frozen-rule categorisation evaluation, uncertainty/error rates, and transfer/card-bill/self-transfer checks. | Public/synthetic evaluation only; real-world category accuracy remains unmeasured. |
| 4 | Seeded personas: salaried, gig, pension, cash-heavy, thin-file, and high-EMI | Policy sensitivity, metamorphic, stress, maximum-EMI, and matched fairness tests. | Code stability and behaviour only; not real-world policy validity. |
| 5 | Berka / PKDD'99 Financial dataset (CTU relational repository), subject to licence/provenance verification | Request-only versus request-plus-behaviour experiment at loan-start date with customer-level splits. | Methodology demonstration on an old Czech dataset; not applicable to Indian uploaded statements. |
| 6 | Seeded personas for safeguards; Phase-5 Berka model for SHAP only if it beats the request-only baseline | Scripted independent-view, override, and second-review flows; model explanation. | No user study yet; benefit remains untested. |
| 7 | Generator statements rendered as digital text PDFs; Agami examples for structured JSON only if licensed | Digital-PDF parser, row correction, authentication, and database tests. | Synthetic/illustrative layouts, not validated real bank PDF coverage. |
| 8 | The sources above | Claims matrix, evidence-limits page, reports, and demo assets. | Every claim must trace to a verified source and stated limitation. |

No external dataset may be downloaded, retained, or used in reports until Phase 0 documents its licence, provenance, access terms, schema, and suitability.

## Phase 0 - Freeze baseline and clean claims

**Goal:** ensure every public claim is no stronger than its evidence.

### Batch 0.1 - Claims matrix

1. Create `CLAIMS.md`.
2. List every dashboard, README, presentation, and report claim.
3. Link each claim to code, tests, or evaluation evidence.
4. Replace unsupported wording:
   - `100% F1` becomes `all curated regression-fixture cases pass`.
   - `scientific evaluation` becomes `held-out, leakage-controlled benchmark`.
   - `audit trail` becomes `decision record`.
   - `decision support` becomes `intended to support officer review`.

### Batch 0.2 - Decision register and freeze

1. Create `DECISIONS.md`.
2. Record policy thresholds, model threshold choice, dataset boundaries, label definitions, and known limitations.
3. Review all current changes and create a Git baseline commit/tag.

**Exit:** no claim is stronger than the evidence.

## Phase 1 - Repair and harden the ML benchmark

**Goal:** make the separate Home Credit benchmark technically sound, reproducible, and correctly presented.

### Batch 1.1 - Evaluation protocol

1. Separate calibration selection from model and threshold selection, or use nested/repeated stratified cross-validation.
2. Keep every transform fitted only on training folds.
3. Save split IDs and protocol configuration.
4. Confirm no post-split leakage.

### Batch 1.2 - Benchmark reporting

1. Add class-prevalence baseline and PR-AUC lift over prevalence.
2. Add Brier Skill Score and Expected Calibration Error.
3. Report repeated-CV or split-variation results.
4. Remove `recall-first` wording unless a documented target recall is actually reached.
5. Show feasible operating points for 50%, 60%, and 70% recall targets.

### Batch 1.3 - Ablation and fairness

1. Benchmark with and without `EXT_SOURCE_*` features.
2. Report dependence on external-source scores.
3. Audit age, family, and other sensitive/proxy fields.
4. Report group-wise recall, precision, calibration, and false-positive rate where responsible and supported by the data.
5. Remove or justify problematic features.

**Exit:** the benchmark is honest, reproducible, calibrated, and does not overstate transferability to uploaded statements.

## Phase 2 - Parser robustness and privacy/security hygiene

**Goal:** make uploaded CSV statements safer and more realistic.

### Batch 2.1 - Bank-format parser hardening

1. Support lakh-style amounts such as `1,00,000.00`, `Dr`, `Cr`, parentheses, BOM, and common encodings.
2. Detect preamble rows before the true header and ambiguous dates such as `03/04/2026`.
3. Improve same-day transaction ordering and running-balance checks.
4. Add fully synthetic HDFC-, SBI-, ICICI-, Axis-, and Kotak-like fixtures.

### Batch 2.2 - Export and privacy safety

1. Prevent CSV formula injection for values beginning with `=`, `+`, `-`, or `@`.
2. Mask PII-like account numbers, UPI IDs, phone numbers, and names in exports where practical.
3. Ensure uploaded contents are not globally cached or written to logs.
4. Add trusted-model checksum verification.
5. Continue using `decision record`, not `audit log`.

**Exit:** parser tests cover hostile and irregular formats, and exports are safer.

## Phase 3 - Categorisation quality and real evaluation

**Goal:** make category performance evidence-based rather than fixture-based.

### Batch 3.1 - Categorisation logic

1. Add merchant normalisation and improved UPI narration parsing.
2. Detect own-account transfers, wallet top-ups, card bills, refunds, and reversals.
3. Avoid counting transfers as income or spending twice.
4. Support multilingual category configuration while preserving uncertain outcomes for low-confidence matches.
5. Freeze the reviewed category-rule file.

### Batch 3.2 - Human data task

1. Collect 300-500 anonymised transactions from 4-5 bank-export formats.
2. Remove personal and account details before sharing or storing them.
3. Obtain independent labels from two people for a subset.
4. Freeze a held-out test set before further rule changes.

### Batch 3.3 - Evaluation

1. Calculate held-out precision, recall, F1, confusion matrix, uncertain share, and reviewer agreement.
2. Optionally compare a TF-IDF character n-gram plus Logistic Regression baseline.
3. Keep ML category suggestions officer-review-only; they must not make lending decisions.

**Exit:** category metrics come from independent data rather than self-authored examples.

## Phase 4 - Policy robustness, fairness, and officer usefulness

**Goal:** strengthen the rule-based affordability layer without presenting it as a default predictor.

### Batch 4.1 - Policy validity

1. Perturb weights and thresholds by plus/minus 10-20% and measure recommendation-flip rate.
2. Add metamorphic tests: higher income must not lower the score; ratio-driven outcomes must be stable after equal monetary scaling; row order must not matter; duplicates must be detected.
3. Check for double counting of data quality as both a score component and a hard gate.

### Batch 4.2 - Useful affordability outputs

1. Add maximum sustainable EMI and maximum indicative loan amount for a given tenure/rate.
2. Show stress cases: income minus 20%, expenses plus 10%, and interest rate plus 2%.
3. Provide counterfactual guidance that explains what affordability change or evidence could move a case to the next band.

### Batch 4.3 - Rule fairness

1. Add matched persona-pair tests: monthly salary versus weekly gig income, cash-heavy versus UPI-heavy spending, and pension versus salary income with equal totals.
2. Report score and recommendation differences.
3. Make unsupported pattern differences result in review rather than unjustified decline.

**Exit:** the policy is transparent, stability-tested, fairness-aware, and more useful to officers.

## Phase 5 - Statement-compatible ML research experiment

**Goal:** demonstrate the intended behavioural-ML methodology without pretending public data represents lender data.

1. Verify legal terms, availability, and provenance before using a public behavioural loan dataset such as Berka/PKDD'99.
2. Document that any such dataset may be old, geographically different, small, and not representative of Indian borrowers.
3. End each feature window before loan outcome/disbursement; prevent temporal leakage.
4. Use customer-level splits where repeat customers exist.
5. Compare request-only against request-plus-behavioural features.
6. Start with Logistic Regression and repeated stratified CV.
7. Report uncertainty, sample size, class balance, and limitations.
8. Do not connect results to Indian uploaded-statement recommendations.

**Exit:** a genuine behavioural-ML research experiment exists with explicit caveats.

## Phase 6 - Explainability and human-review safeguards

**Goal:** demonstrate responsible decision support.

1. Add SHAP only to a meaningful public-data or statement-compatible ML model.
2. Show global importance and carefully worded local explanations.
3. Distinguish observed statement facts from model inference.
4. Capture an officer's independent initial view before revealing the recommendation.
5. Record override rate and rationale; require second review for borderline, overridden, or high-impact cases.
6. Run a formative usability study with 5-10 participants using mock cases.
7. Measure task completion time, agreement, override behaviour, and SUS usability score.
8. Do not claim the study proves lending effectiveness.

**Exit:** the system has meaningful explainability and evidence that it can support, rather than replace, human review.

## Phase 7 - Practical platform extension

**Goal:** add the highest-value production-like capabilities.

1. Add basic authentication, SQLite case storage, tamper-evident/hash-chained decision records, and practical role separation.
2. Add Docker and reproducible local setup.
3. Add native digital-PDF statement text extraction first, with officer correction for parsed rows.

**Deferred beyond this phase:** scanned-image OCR, salary-slip and ITR parsing, full deployment governance, data/model-drift monitoring, and enterprise production deployment.

**Exit:** safer prototype with realistic digital-PDF support.

## Phase 8 - Final evaluation package

**Goal:** make the project review-ready.

1. Create architecture and data-flow diagrams.
2. Finalise claims/evidence matrix, parser robustness report, category report, policy stability/fairness report, and ML model card.
3. Add usability-study summary, limitations and ethics section, panel Q&A document, screenshots, and a demo script.
4. Freeze new features 4-6 weeks before final submission.

**Exit:** a complete, evidence-backed final report and presentation package.

## Required order

`Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 5 -> Phase 6 -> Phase 7 -> Phase 8`

Phase 3 requires independently labelled anonymised transactions from the project team. Phase 5 requires verified public-data terms. A real production-quality statement-scoring model requires consented historical applicant outcomes and is outside the current prototype until that data exists.
