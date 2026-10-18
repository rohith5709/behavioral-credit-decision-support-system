# System Architecture — Behavioral Credit Decision Support System

> **Project**: B.Tech BCSE497J – Project I (VIT)  
> **Team**: Adharsh S (23BDS0029), Gowtham Kumar D (23BDS0186), Rohith S M (23BDS0025)  
> **Faculty Guide**: Dr. Viswanathan A

> [!IMPORTANT]
> The statement data pipeline and the Home Credit model pipeline are **completely separate by design**. The LightGBM benchmark model is **never** applied to raw uploaded bank-statement transactions. This architectural separation is intentional and required for regulatory compliance.

---

## 1. Full System Architecture

```mermaid
flowchart TD
    subgraph Inputs["Inputs"]
        CSV["🗂️ Bank Statement\n(CSV / Digital PDF)"]
        SLIP["📄 Salary Slip\n(Net pay + Employer)"]
        BUREAU["👤 Officer Bureau Profile\n(CIBIL, Age, Tenure, Active Loans, Overdue Days)"]
        HC["🏦 Home Credit Dataset\n(246k applicants, 61 features)"]
    end

    subgraph Pillar1["Pillar 1 — Deterministic Cash-Flow Affordability Engine"]
        PARSE["statement_csv.py / statement_pdf.py\nParse → Normalize → Validate\n• Balance reconciliation\n• PII masking\n• Duplicate removal"]
        CAT["behavioral.py → categorise_statement_transactions()\n4-Layer Categorisation:\n① NEFT/UPI/IMPS/NACH regex\n② Merchant normalisation\n③ Vernacular tokens (Kirana, Vetan, Kist)\n④ Uncertain fallback → Officer review"]
        FEAT["behavioral.py → build_statement_features()\n• avg_monthly_income, avg_monthly_expense\n• savings_ratio, emi_to_income_ratio\n• income_variation, utility_regularity\n• emergency_buffer, income_trend, 23+ features"]
        AFF["affordability.py → calculate_score()\n8 Policy Components:\n• Savings ratio      25 pts\n• EMI burden         25 pts\n• Salary consistency 20 pts\n• Expense stability  15 pts\n• Utility regularity 10 pts\n• Data quality        5 pts\nTotal: 0–100 pts\nVersion: statement-affordability-v1"]
        VERIFY["salary_verification.py\nverify_salary_slip_cross_document()\n• Detected salary vs declared slip\n• Tolerance: 15%\n• Override safeguard on >15% mismatch"]
    end

    subgraph Pillar2["Pillar 2 — LightGBM Default Risk Benchmark (Home Credit)"]
        TRAIN["benchmark_home_credit.py\nTraining Pipeline:\n• 64% train / 16% val / 20% final-test\n• Stratified split, random_state=42\n• Imputer + optional scaler fit on train only\n• Candidates: LR, LightGBM, RF (50k cap), XGBoost (50k cap)"]
        MODEL["home_credit_lightgbm.joblib\nSelected: LightGBM (balanced)\nCalibration: Platt Scaling (logistic sigmoidal)\nFinal-test ROC-AUC: 0.774 (CI: 0.767–0.781)\nFinal-test PR-AUC: 0.266 (~3.3× lift)\nBrier Score: 0.067 (post-calibration)\nAlert Threshold: 0.20 (policy parameter)"]
        SCORE["applicant_scoring.py → predict_applicant_risk()\nBureau Profile Mapping:\n• CIBIL 300–900 → EXT_SOURCE 0–1 (monotonic proxy)\n• age_years → DAYS_BIRTH\n• years_employed → DAYS_EMPLOYED\n• active_loans → bureau_record_count\n• overdue_days → installment_days_late\nOutputs: PD, risk_band, completeness_ratio, Tree-SHAP"]
        SHAP["explain_home_credit.py\nexact Tree-SHAP via booster_.predict(pred_contrib=True)\n• Global gain importance\n• Local Shapley values in log-odds space\n• Top risk-increasing vs protective factors\n• lru_cache: model loaded once per session"]
    end

    subgraph Integration["Dual-Pillar Integration Engine"]
        ENGINE["engine.py → recommend()\nDual-Pillar 2×2 Matrix:\n• Affordability Score vs Bureau PD\n• 4 Quadrants → Recommendation\n• Salary-slip failure → Override ALL quadrants\n• Rule version stamped on every decision"]
    end

    subgraph Persistence["Persistence & Audit Trail"]
        DB["data/db.py → SQLite\nSHA-256 Forward Hash Chain\n• prev_hash → SHA-256(record_json) → next_hash\n• External anchor: data/HEAD_HASH.sha256\n• DPDP Act 2023: PII stripped before hashing\n• verify_hash_chain() detects any tampering"]
    end

    subgraph UI["UI Layer — Streamlit Dashboard (app.py)"]
        T1["Tab 1: Case Summary\n• Quality score, Affordability score\n• Surplus before/after new loan\n• Officer review checklist"]
        T2["Tab 2: Upload & Parse\n• CSV/PDF upload\n• Column mapping\n• Salary slip cross-verification\n• Categorised transactions + overrides"]
        T3["Tab 3: Behaviour Profile\n• 23+ feature metrics\n• Monthly cash-flow chart\n• Balance trend, category breakdown"]
        T4["Tab 4: Synthetic Portfolio\n• simulator_behaviour_features.csv view"]
        T5["Tab 5: ML Benchmark (Separate)\n• Model metrics, threshold curve\n• Calibration reliability diagram\n• Global gain importance chart\n• Plotly Tree-SHAP horizontal attribution"]
        T6["Tab 6: Officer Decision\n• Plotly 2×2 Visual Matrix Map\n• 4 Quadrant Policy Cards\n• Real-Time Stress Testing Lab\n• Actionable metrics + counterfactuals\n• Officer override + rationale\n• SHA-256 sealed decision record"]
    end

    CSV --> PARSE
    SLIP --> VERIFY
    PARSE --> CAT --> FEAT --> AFF
    FEAT --> AFF
    AFF --> ENGINE
    VERIFY --> ENGINE

    BUREAU --> SCORE
    HC --> TRAIN --> MODEL
    MODEL --> SCORE --> SHAP
    SCORE --> ENGINE

    ENGINE --> T6
    ENGINE --> T1
    FEAT --> T3
    PARSE --> T2
    MODEL --> T5
    SHAP --> T5

    T6 --> DB

    style Pillar1 fill:#0F3460,color:#E2E8F0,stroke:#38BDF8
    style Pillar2 fill:#1A1A2E,color:#E2E8F0,stroke:#F59E0B
    style Integration fill:#16213E,color:#E2E8F0,stroke:#10B981
    style Persistence fill:#0D1117,color:#E2E8F0,stroke:#8B5CF6
    style UI fill:#1E293B,color:#E2E8F0,stroke:#64748B
```

---

## 2. Dual-Pillar Decision Matrix Logic

```mermaid
flowchart LR
    S1{"Affordability\nScore ≥ 70?"}
    S2{"Bureau PD\n< 20%?"}
    SF{"Salary Slip\nMismatch > 15%?"}

    SF -->|"YES — OVERRIDE"| OVERRIDE["❌ Refer: Salary\nDiscrepancy Detected\n(Overrides All Quadrants)"]
    SF -->|No| S1

    S1 -->|Yes — High Cashflow| S2
    S1 -->|No — Low Cashflow| S3{"Bureau PD\n< 20%?"}

    S2 -->|Yes — Low Risk| Q1["✅ Q1: Meets Indicative\nAffordability Criteria\nStrong cashflow + Low PD"]
    S2 -->|No — High Risk| Q2["⚠️ Q2: Manual Review\nBureau Risk Alert\nGood cashflow, elevated PD"]

    S3 -->|Yes — Low Risk| Q3["⚠️ Q3: Manual Review\nCashflow Alert\nClean history, thin margin"]
    S3 -->|No — High Risk| Q4["❌ Q4: Decline\nDual Risk Elevation\nLow cashflow + High PD"]

    style Q1 fill:#064E3B,color:#34D399,stroke:#10B981
    style Q2 fill:#78350F,color:#FBBF24,stroke:#F59E0B
    style Q3 fill:#78350F,color:#FBBF24,stroke:#F59E0B
    style Q4 fill:#7F1D1D,color:#F87171,stroke:#EF4444
    style OVERRIDE fill:#7F1D1D,color:#F87171,stroke:#EF4444
```

---

## 3. Module Responsibility Table

| Module | File | Responsibility |
|--------|------|----------------|
| CSV Parser | `src/documents/statement_csv.py` | Multi-format bank CSV parsing with preamble skip, BOM, lakh-commas, Dr/Cr, balance reconciliation, PII masking |
| PDF Parser | `src/documents/statement_pdf.py` | Digital native-text PDF extraction via `pdfplumber`. Fail-closed on scanned/image PDFs |
| Salary Verifier | `src/documents/salary_verification.py` | Cross-document salary vs statement credit comparison; 15% tolerance; flags as officer safeguard |
| Feature Engineer | `src/features/behavioral.py` | 23+ behavioural features; 4-layer categorisation; merchant group builder; officer override tracker |
| Affordability Policy | `src/decision/affordability.py` | 8-component deterministic 0–100 score; safeguard override logic; actionable metric calculations |
| Decision Engine | `src/decision/engine.py` | Unified Dual-Pillar recommend() integrating both pillars into the 2×2 matrix |
| Bureau Scorer | `src/models/applicant_scoring.py` | Maps officer-entered bureau profile to Home Credit model features; runs calibrated PD; returns Tree-SHAP |
| SHAP Explainer | `src/models/explain_home_credit.py` | Exact Tree-SHAP via booster_.predict(pred_contrib=True); global gain importance; lru_cache bundle |
| HC Trainer | `src/models/benchmark_home_credit.py` | Full Home Credit training pipeline; stratified 64/16/20 splits; candidate selection; calibration |
| Database | `src/data/db.py` | SQLite with SHA-256 forward hash chain; external anchor; DPDP Act 2023 compliance; tamper detection |
| Matrix Viz | `src/reporting/matrix_viz.py` | Plotly 2×2 decision matrix chart; Tree-SHAP horizontal attribution chart |
| Case Summary | `src/reporting/case_summary.py` | Decision record builder; evidence row aggregation; review flag extractor |
| App | `app.py` | 6-tab Streamlit UI; FinTech dark CSS; all Plotly integrations; stress testing lab |
| Config | `config/category_rules.json` | Version-controlled keyword rules for 18 transaction categories |
| Config | `config/affordability_policy_v1.json` | Versioned policy component weights and thresholds |

---

## 4. Evidence Boundaries (Critical Constraints)

> [!IMPORTANT]
> These boundaries are by design. Violating them would make the system scientifically invalid.

| Boundary | What It Prevents |
|----------|-----------------|
| Home Credit model ≠ Statement analyser | Prevents applying features engineered for European credit bureau data to Indian cash-flow transactions |
| Affordability score is rule-based | Enables adverse-action explanation (required by RBI Fair Lending Directions) |
| CIBIL→EXT_SOURCE is a monotonic proxy | Conceded explicitly; marked as "indicative secondary signal" not "validated Indian default probability" |
| Salary credits ≠ all credits | Loan disbursals, refunds, and self-transfers are explicitly excluded from income calculation |
| No temporal split on Home Credit | Home Credit has no usable application dates; must not be claimed as out-of-time validated |
| One uploaded account only | Cannot verify household costs, other accounts, or off-statement liabilities |

---

## 5. SHA-256 Tamper-Evident Audit Trail

```mermaid
sequenceDiagram
    participant Officer
    participant App as app.py
    participant DB as db.py (SQLite)
    participant File as data/HEAD_HASH.sha256

    Officer->>App: Click "Create Decision Record"
    App->>DB: save_case_record(record)
    DB->>DB: sanitize_payload_for_chain(record)\n(strip PII for DPDP compliance)
    DB->>DB: record_hash = SHA-256(sanitized_json + prev_hash)
    DB->>DB: INSERT INTO cases (record_hash, ...)
    DB->>File: Write HEAD_HASH = record_hash
    DB-->>App: {case_id, record_hash}
    App-->>Officer: ✅ Sealed Case ID + Hash prefix

    Note over DB,File: To verify: verify_hash_chain()\nComputes chain of all stored hashes\nReturns FAIL if any record was altered
```

---

## 6. Key Performance Numbers (Final-Test — Frozen)

| Metric | Value | Note |
|--------|-------|------|
| LightGBM ROC-AUC | **0.774** | 95% CI: 0.767–0.781 |
| LightGBM PR-AUC | **0.266** | ~3.3× lift over 8.07% base rate |
| Brier Score (calibrated) | **0.067** | Platt-scaled; trivial predictor ≈ 0.074 |
| Brier Score (raw) | 0.1777 | Pre-calibration, class-weighted output |
| Alert Threshold | **0.20** | Policy parameter; recall 33.3%, precision 30.5% |
| Categorisation Accuracy | **98.7%** | 75-case ground-truth fixture |
| Categorisation Macro F1 | **0.985** | Per-category evaluation |
| Pytest Tests | **63 passing** | 0 failures, 31 harmless deprecation warnings |
| Policy Stability | **< 5% flip rate** | Monte Carlo, 1,000 trials, ±10% perturbation |
