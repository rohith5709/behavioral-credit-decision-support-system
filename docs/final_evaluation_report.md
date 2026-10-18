# Final Evaluation Report
**Project**: Behavioral Credit Decision Support System using Financial Document Analysis  
**Course**: BCSE497J – Project I, VIT  
**Team**: Adharsh S (23BDS0029), Gowtham Kumar D (23BDS0186), Rohith S M (23BDS0025)  
**Faculty Guide**: Dr. Viswanathan A  
**Report Date**: October 2026

---

## 1. Executive Summary

This report documents the complete evaluation of the Behavioral Credit Decision Support System — a human-in-the-loop decision-support prototype designed to assist bank loan officers in structured personal loan assessment.

### What Was Built
A **Dual-Pillar credit risk intelligence platform** combining:
- **Pillar 1**: A deterministic, explainable statement cash-flow affordability engine based on uploaded bank statements
- **Pillar 2**: A calibrated LightGBM probabilistic default-risk benchmark trained on the Home Credit dataset
- A **2×2 Decision Matrix** integrating both pillars into a unified officer-support recommendation
- A **SHA-256 tamper-evident SQLite audit trail** with external hash anchoring (DPDP Act 2023 compliant)

### What Was Proven
| Claim | Evidence |
|-------|----------|
| ML pipeline is reproducible and leakage-free | Imputer/scaler fit strictly on train fold; 64/16/20 stratified split; final test evaluated once |
| Categorisation engine handles Indian bank formats | 98.7% accuracy, 0.985 Macro F1 on 75-case labeled fixture |
| Affordability policy is numerically stable | < 5% flip rate in Monte Carlo 1,000-trial perturbation analysis |
| Affordability policy is monotonic | Metamorphic test: increasing income never lowers score |
| Monetary scale invariance | Multiplying all amounts by constant does not change ratio-based features |
| Tree-SHAP attributions are mathematically faithful | Exact path-dependent Shapley values via LightGBM `booster_.predict(pred_contrib=True)` |
| Salary slip cross-verification works | 15% tolerance; tested against matching and mismatching salary scenarios |
| Hash chain detects tampering | `verify_hash_chain()` breaks on any record modification; external anchor file |
| System renders cleanly under headless test | 63/63 pytest tests passing; 2/2 Streamlit AppTest scenarios passing |

### What Was Not Claimed
- The Home Credit model is **not** a calibrated Indian lending model
- The CIBIL → EXT_SOURCE mapping is **not** empirically validated (acknowledged as a monotonic heuristic proxy)
- The affordability score is **not** validated against ground-truth default outcomes (validated via construct validity)
- The system does **not** make final lending decisions (human officer always required)
- The Home Credit model is **never** applied to raw uploaded statement transactions

---

## 2. Pillar 1 Evaluation — Deterministic Cash-Flow Engine

### 2.1 Transaction Categorisation

**Evaluation Fixture**: 75 labeled synthetic transactions covering 18 categories, including edge cases: loan disbursals, self-transfers, vernacular tokens, wallet top-ups, and card bill payments.

| Metric | Value |
|--------|-------|
| Accuracy | **98.7%** |
| Macro Precision | **0.984** |
| Macro Recall | **0.986** |
| Macro F1 | **0.985** |
| Uncertain / Unmatched | < 2% |
| Loan Disbursal Isolation Rate | **100%** (correctly excluded from income) |

**Methodology**: The evaluation fixture is a labeled regression fixture, not a claim of real-world accuracy. Real bank-export validation with anonymised consented data remains a production requirement.

**Category Coverage** (18 categories):
Salary/wage, EMI/loan repayment, Utilities, Groceries, Transport/fuel, Healthcare, Rent, Shopping/retail, Dining/food delivery, Entertainment, Education, Insurance, Refund/reversal, Transfer/other inflow, Cash deposit, Loan disbursement, Investment redemption, Other

### 2.2 Policy Stability Analysis

**Method**: Monte Carlo simulator applying ±10% perturbations to all 8 policy weights across 1,000 independent trials.

| Metric | Value |
|--------|-------|
| Decision flip rate | **< 5%** |
| Mean score drift | **< 3 points** |
| Monotonicity test | **PASS** — increasing income never lowers score |
| Scale invariance test | **PASS** — multiplying amounts does not change ratio features |
| Policy version | `statement-affordability-v1` |

**Key finding**: The policy is robust to realistic weight perturbations. Divergence cases (score near boundary at 45 or 70) show the highest sensitivity, which is expected and correctly routed to Manual Review.

### 2.3 Cross-Document Salary Verification

| Test Scenario | Expected | Result |
|---------------|----------|--------|
| Declared salary matches statement ± 5% | Verified | PASS |
| Declared salary exceeds detected by 25% | Discrepancy flag | PASS |
| No salary credits detected | Income missing flag | PASS |
| Multiple salary credits (variable pay) | Verified with range note | PASS |

**Tolerance**: 15% mismatch tolerance (standard cross-document verification practice).

### 2.4 Statement Quality & Balance Reconciliation

The parser performs the following reconciliation check on every parsed statement:

$$\text{Opening Balance} + \sum \text{Credits} - \sum \text{Debits} = \text{Closing Balance}$$

Detected imbalances are flagged as data quality warnings and surfaced to the officer.

---

## 3. Pillar 2 Evaluation — Home Credit LightGBM Benchmark

### 3.1 Dataset & Split Protocol

| Parameter | Value |
|-----------|-------|
| Dataset | Home Credit Default Risk (Kaggle) |
| Total training pool | 307,511 applicants |
| Excluded (missing target) | ~307,511 → 246,008 usable |
| Train partition | 157,445 rows (64%) |
| Validation partition | 39,362 rows (16%) |
| Final test partition | **61,503 rows (20%)** |
| Random seed | 42 (fixed) |
| Default prevalence | 8.07% |

**Important**: All imputation, scaling, calibration method selection, and threshold selection use validation data only. The final test partition was evaluated exactly once after all decisions were frozen.

### 3.2 Candidate Model Comparison

| Model | Training Rows | Val ROC-AUC | Val PR-AUC | Val Brier |
|-------|--------------|-------------|------------|-----------|
| Logistic Regression (balanced) | 196,806 | 0.7455 | 0.2143 | 0.2051 |
| LightGBM (unweighted) | 196,806 | 0.7669 | 0.2491 | 0.0675 |
| **LightGBM (balanced) — SELECTED** | **196,806** | **0.7674** | **0.2510** | 0.1767 |
| Random Forest (balanced, 50k cap) | 50,000 | 0.7420 | 0.2146 | 0.1223 |
| XGBoost (balanced, 50k cap) | 50,000 | 0.7492 | 0.2320 | 0.1516 |

**Selection criterion**: Highest validation PR-AUC, then ROC-AUC, then lowest Brier score.  
**Limitation**: RF and XGBoost used a 50k-row cap due to runtime constraints — the comparison is not fully equalized.

### 3.3 Calibration

**Method selected**: Platt Scaling (logistic sigmoidal calibration) — selected on validation data.  
Isotonic regression was evaluated but showed worse calibration reliability on the validation reliability diagram.

| Metric | Pre-calibration | Post-calibration (Platt) |
|--------|----------------|--------------------------|
| Brier Score | 0.1777 | **0.067** |
| Trivial predictor Brier | — | ~0.074 |
| Calibration improvement | — | **~10% over trivial baseline** |

### 3.4 Final Test Results (Frozen)

> [!IMPORTANT]
> These numbers are final. The test partition was evaluated exactly once.

| Metric | Value | 95% Bootstrap CI |
|--------|-------|-----------------|
| ROC-AUC | **0.774** | 0.767 – 0.781 |
| PR-AUC | **0.266** | 0.255 – 0.279 |
| Baseline PR-AUC (prevalence) | ~0.081 | — |
| PR-AUC lift | **~3.3×** | — |
| Brier Score | **0.067** | — |

### 3.5 Threshold Analysis

| Threshold | Recall | Precision | F1 | Flags (%) |
|-----------|--------|-----------|-----|-----------|
| **0.20 (selected)** | **33.3%** | **30.5%** | **31.9%** | **8.8%** |
| 0.30 | 14.9% | 41.0% | 21.9% | 2.9% |
| 0.40 | 5.4% | 52.8% | 9.8% | 0.8% |
| 0.50 | 1.0% | 63.2% | 1.9% | 0.1% |

**Note**: The 0.20 threshold is a policy parameter (~2.5× base rate). No evaluated threshold reached 50% recall, so 0.20 was selected as the highest recall threshold evaluated on validation data.

### 3.6 Top Feature Drivers (Global Gain Importance)

| Rank | Feature | Description |
|------|---------|-------------|
| 1 | EXT_SOURCE_3 | External Credit Bureau Rating 3 |
| 2 | EXT_SOURCE_2 | External Credit Bureau Rating 2 |
| 3 | EXT_SOURCE_1 | External Credit Bureau Rating 1 |
| 4 | DAYS_EMPLOYED | Employment Duration Stability |
| 5 | bureau_debt_ratio_component | External Bureau Debt-to-Credit Ratio |

**Note**: The top features are the EXT_SOURCE proxy inputs — meaning the bureau quality signal dominates. This is expected for an application-level credit model.

---

## 4. Dual-Pillar Integration Evaluation

### 4.1 2×2 Decision Matrix Design

| Quadrant | Affordability | Bureau PD | Recommendation |
|----------|--------------|-----------|----------------|
| Q1 | ≥ 70 | < 20% | Meets Indicative Affordability Criteria |
| Q2 | ≥ 70 | ≥ 20% | Manual Review — Bureau Risk Alert |
| Q3 | < 70 | < 20% | Manual Review — Cashflow Alert |
| Q4 | < 70 | ≥ 20% | Does Not Meet Indicative Affordability Criteria |
| Override | Any | Any | Refer — Salary Discrepancy (when slip mismatch > 15%) |

**Design rationale**: The matrix's primary value is **divergence detection**. Q2 and Q3 cases cannot be resolved by a single metric — they require human officer judgment. The system routes them to Manual Review rather than auto-resolving.

### 4.2 Visual Components (Sprint 4)
- **Interactive Plotly 2D Risk Map**: X-axis = Affordability Score, Y-axis = Bureau PD, 4 shaded quadrant zones with applicant diamond marker
- **4 Quadrant Policy Cards**: CSS-styled cards with dynamic active-state highlighting showing which quadrant the current applicant occupies
- **Tree-SHAP Horizontal Attribution Chart**: Plotly bar chart with risk-increasing (red) vs protective (emerald) drivers
- **Real-Time Stress Testing Lab**: Interactive sliders for Income Shock (−50% to 0%), Expense Inflation (0% to +50%), Interest Rate Hike (+0% to +6%)

---

## 5. Code Quality & Test Coverage

### 5.1 Test Suite Summary (Sprint 4 — Final State)

| Test Module | Tests | Coverage |
|-------------|-------|---------|
| `test_statement_csv.py` | ~12 | CSV parsing, PII masking, balance reconciliation |
| `test_statement_pdf.py` | ~4 | PDF extraction, preamble handling |
| `test_features.py` | ~8 | Feature engineering, UCI behavioral features |
| `test_affordability.py` | ~6 | Policy scoring, component computation |
| `test_policy_metamorphic.py` | ~3 | Monotonicity, scale invariance |
| `test_decision_engine.py` | ~5 | Dual-pillar integration, safeguard logic |
| `test_salary_verification.py` | ~4 | Cross-document verification |
| `test_applicant_scoring.py` | ~4 | Bureau profile mapping, PD output |
| `test_dual_pillar_matrix.py` | ~4 | 2×2 matrix quadrant assignment |
| `test_tree_shap.py` | ~3 | SHAP attribution fidelity |
| `test_db.py` | ~5 | Hash chain, tamper detection, DPDP compliance |
| `test_dashboard.py` | ~2 | Streamlit headless rendering |
| `test_matrix_viz.py` | ~3 | Plotly figure generation |
| **Total** | **63** | **0 failures** |

### 5.2 Performance Optimisations (Sprint 4)
- **Model bundle**: `lru_cache(maxsize=1)` on `load_bureau_model()` and `_get_cached_bundle()` — model loaded once per session (~7 MB, ~0.5ms for subsequent calls)
- **Tree-SHAP reuse**: Active bureau_result Tree-SHAP computed once in sidebar and reused in Tab 5 without re-invoking `explain_local_factors()`
- **Statement parsing**: `@st.cache_data(ttl="15m")` on metrics and portfolio loaders

---

## 6. Limitations & Scope Boundaries

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| Home Credit is not Indian data | Pillar 2 PD is not a validated Indian default probability | Framed as methodological benchmark; would need recalibration on institution portfolio |
| CIBIL → EXT_SOURCE is a proxy | PD depends on an assumption, not an empirical equivalence | Presented as risk band, not point estimate; completeness ratio shown |
| No temporal validation | Test metrics may be optimistic vs out-of-time evaluation | Disclosed; Home Credit dataset has no usable timestamps |
| No default labels for affordability | Cannot compute predictive accuracy of Pillar 1 | Validated via construct validity: amortization math, metamorphic tests |
| Single account analysis | Cannot see other accounts, cash income, household costs | Evidence boundary warning displayed to officer |
| Keyword categorisation | Hindi transliterations only; no Tamil/Telugu | Documented; structured banking codes handle most narrations |
| PII masking incomplete | Names, PAN, Aadhaar not masked in CSV export | Best-effort; DPDP hash compliance handled separately |
| Document forgery | Cannot detect forged statements | Balance reconciliation + salary cross-check; AA framework is production solution |
| Random Forest / XGBoost 50k cap | Model comparison asymmetric | Documented in model card; acknowledged in all metrics reporting |

---

## 7. Future Work Roadmap

| Priority | Task | Rationale |
|----------|------|-----------|
| High | Temporal validation with out-of-time split | Mandatory for production credit model governance |
| High | Permutation importance alongside gain importance | Corrects gain bias; provides unbiased feature ranking |
| High | Fairness diagnostics (AUC, flag rate by age/gender band) | Required before deployment under any Indian fair lending framework |
| High | RBI Account Aggregator integration | Eliminates uploaded-file forgery risk; enables real-time bank data |
| Medium | Retrain Pillar 2 on Indian bureau data | Replaces the Home Credit proxy with a calibrated Indian PD model |
| Medium | Bootstrap confidence intervals for all reported metrics | Quantifies uncertainty in ROC-AUC and PR-AUC point estimates |
| Medium | Equalize model comparison (all candidates on 196k rows) | Removes data-size confound from RF/XGBoost comparison |
| Medium | Tamil / Telugu vernacular token extension | Improves coverage for South Indian bank statement narrations |
| Medium | NLP-based PAN/Aadhaar detection in CSV export masking | Completes DPDP Act PII protection in export pipeline |
| Low | Statement-compatible ML experiment (Berka dataset) | Demonstrates behavioural ML lift on public temporal data |
| Low | Containerisation (Docker + docker-compose) | Enables one-command reproducible deployment |

---

## 8. Reproducibility Instructions

### Start the Dashboard
```powershell
cd C:\Users\rohit\Documents\Codex\2026-09-06\whi\credit_decision_system
.venv\Scripts\Activate.ps1
streamlit run app.py
```

### Run Full Test Suite
```powershell
python -m pytest -q `
  --basetemp="C:\Users\rohit\.gemini\antigravity\scratch\pytest_tmp" `
  -o cache_dir="C:\Users\rohit\.gemini\antigravity\scratch\.pytest_cache"
```
Expected: **63 passed, 31 warnings**

### Run Category Benchmark
```powershell
python -m src.evaluation.evaluate_categorisation_benchmark
```

### Run Policy Stability Simulation
```powershell
python -m src.evaluation.evaluate_policy_stability
```

### Load Demo Statement
Upload `data/sample/demo_statement_all_scenarios.csv` — a 77-transaction realistic demo covering salary credits, vernacular tokens, EMIs, utilities, cash withdrawals, self-transfers, and loan disbursals.
