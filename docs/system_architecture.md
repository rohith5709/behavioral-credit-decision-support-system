# System Architecture — Behavioral Credit Decision Support System

> **Project**: B.Tech BCSE497J – Project I (VIT)  
> **Team**: Adharsh S (23BDS0029), Gowtham Kumar D (23BDS0186), Rohith S M (23BDS0025)  
> **Faculty Guide**: Dr. Viswanathan A

> [!IMPORTANT]
> The statement data pipeline and the Home Credit model pipeline are **completely separate by design**. The LightGBM benchmark model is **never** applied to raw uploaded bank-statement transactions. This architectural separation is intentional and required for regulatory compliance.

---

## 1. Full System Architecture (Tri-Tier ML & Deterministic Safeguards)

```mermaid
flowchart TD
    subgraph Inputs["Inputs"]
        CSV["Bank Statement (CSV / Digital PDF)"]
        SLIP["Salary Slip (Net pay + Employer)"]
        BUREAU["Officer Bureau Profile (CIBIL, Age, Tenure, Active Loans, Overdue Days)"]
        HC["Home Credit Dataset (246k applicants, 61 features)"]
    end

    subgraph Pillar1["Pillar 1 — Statement Cash-Flow Affordability & Behavioral ML"]
        PARSE["statement_csv.py / statement_pdf.py\nParse -> Normalize -> Validate\nBalance reconciliation | PII masking | Duplicate removal"]
        
        CAT["behavioral.py -> categorise_statement_transactions()\nHybrid Categorisation Engine:\n1. Deterministic accounting rules (salary, loan, tax)\n2. Tier 1 Supervised NLP Classifier (TF-IDF + Calibrated SGD)\n3. Fallback to officer review for ambiguous items"]
        
        FEAT["behavioral.py -> build_statement_features()\nExtracts 23+ behavioral & cash-flow indicators\nsavings_ratio, income_variation, emi_burden, emergency_buffer"]
        
        UNSUP["behavioral_unsupervised.py -> score_behavioral_profile()\nTier 2 Account-Level Unsupervised ML Suite:\n1. Isolation Forest (n=150, contamination=0.05) -> Cash flow anomaly check\n2. K-Means (k=4) -> Behavioral spending persona clustering"]
        
        AFF["affordability.py -> calculate_score()\n8 Transparent Policy Components (0-100 pts)\nMandatory safeguard hard stops override the score"]
        
        VERIFY["salary_verification.py -> verify_salary_slip_cross_document()\nSalary slip vs detected statement credits (15% tolerance)"]
    end

    subgraph Pillar2["Pillar 2 — Tier 3 Macro Bureau Default Risk Benchmark"]
        TRAIN["benchmark_home_credit.py\nTraining Pipeline:\n64% train / 16% val / 20% final-test\nStratified split, random_state=42\nImputer fit strictly on train partition"]
        
        MODEL["home_credit_lightgbm.joblib\nSelected: LightGBM (balanced)\nPlatt Scaling calibration (sigmoidal)\nROC-AUC: 0.774 | PR-AUC: 0.266 | Brier: 0.067\nAlert Threshold: 0.20"]
        
        SCORE["applicant_scoring.py -> predict_applicant_risk()\nBureau Profile Mapping:\nCIBIL 300-900 -> EXT_SOURCE (monotonic proxy)\nOutputs: PD, risk_band, completeness_ratio"]
        
        SHAP["explain_home_credit.py\nExact Tree-SHAP via booster_.predict(pred_contrib=True)\nGlobal gain importance and local Shapley attribution"]
    end

    subgraph Integration["Dual-Pillar Integration & Safeguard Engine"]
        ENGINE["engine.py -> recommend()\nUnified 2x2 Decision Matrix:\nAffordability Score vs Bureau PD\nAnomaly & Salary Safeguard Overrides\nRule version stamped on every case"]
    end

    subgraph Persistence["Persistence & Audit Trail"]
        DB["data/db.py -> SQLite Ledger\nSHA-256 Forward Hash Chain\nprev_hash -> SHA-256(record_json) -> record_hash\nExternal anchor: data/HEAD_HASH.sha256\nDPDP Act 2023 compliance (PII stripped before hashing)\nverify_hash_chain() detects tampering"]
    end

    subgraph UI["UI Layer — Streamlit Dashboard (app.py)"]
        T1["Tab 1: Case Summary & Review Checklist\nAffordability score, surplus before/after, Isolation Forest flags"]
        T2["Tab 2: Statement Upload & NLP Categorisation\nColumn mapping, NLP confidence pills, officer overrides"]
        T3["Tab 3: Behaviour Profile & Persona Clusters\nK-Means persona cards, centroid diagnostics, cash-flow charts"]
        T4["Tab 4: Synthetic Portfolio Simulation\nsimulator_behaviour_features.csv cohort analysis"]
        T5["Tab 5: ML Benchmark & Explainability\nModel metrics, Platt calibration curve, Tree-SHAP attributions"]
        T6["Tab 6: Officer Decision & Tamper-Evident Ledger\nPlotly 2x2 Risk Map, stress testing lab, SHA-256 sealed record"]
    end

    CSV --> PARSE
    SLIP --> VERIFY
    PARSE --> CAT --> FEAT --> UNSUP
    FEAT --> AFF
    UNSUP --> AFF
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
| Transaction NLP Trainer | `src/models/train_transaction_nlp.py` | Tier 1 Supervised NLP model training; TF-IDF n-grams + Calibrated Linear SGD over 1,025 curated samples across 18 classes |
| Feature Engineer | `src/features/behavioral.py` | Hybrid transaction categorization (exact rules + Calibrated NLP classifier); 23+ behavioral & cash-flow metrics |
| Behavioral Unsupervised Suite | `src/models/behavioral_unsupervised.py` | Tier 2 Unsupervised ML Suite; Isolation Forest (n=150, contamination=0.05) anomaly detection and K-Means (k=4) spending persona clustering |
| Affordability Policy | `src/decision/affordability.py` | 8-component deterministic 0–100 score; safeguard override logic; actionable metric calculations |
| Decision Engine | `src/decision/engine.py` | Unified Dual-Pillar recommend() integrating both pillars and unsupervised anomaly safeguards into the 2×2 matrix |
| Bureau Scorer | `src/models/applicant_scoring.py` | Maps officer-entered bureau profile to Home Credit model features; runs calibrated PD; returns Tree-SHAP |
| SHAP Explainer | `src/models/explain_home_credit.py` | Exact Tree-SHAP via booster_.predict(pred_contrib=True); global gain importance; lru_cache bundle |
| HC Trainer | `src/models/benchmark_home_credit.py` | Full Home Credit training pipeline; stratified 64/16/20 splits; candidate selection; Platt calibration |
| Database | `src/data/db.py` | SQLite with SHA-256 forward hash chain; external anchor; DPDP Act 2023 compliance; tamper detection |
| Matrix Viz | `src/reporting/matrix_viz.py` | Plotly 2×2 decision matrix chart; Tree-SHAP horizontal attribution chart |
| Case Summary | `src/reporting/case_summary.py` | Decision record builder; evidence row aggregation; review flag extractor with unsupervised anomaly integration |
| App | `app.py` | 6-tab Streamlit UI; FinTech dark CSS; all Plotly integrations; stress testing lab; centroid diagnostics |
| Config | `config/category_rules.json` | Version-controlled keyword rules for 18 transaction categories |
| Config | `config/affordability_policy_v1.json` | Versioned policy component weights and thresholds |

---

## 4. Evidence Boundaries (Critical Constraints)

> [!IMPORTANT]
> These boundaries are by design. Violating them would make the system scientifically invalid.

| Boundary | What It Prevents |
|----------|-----------------|
| Home Credit model != Statement analyser | Prevents applying features engineered for European credit bureau data to Indian cash-flow transactions |
| Affordability score is rule-based | Enables adverse-action explanation (required by RBI Fair Lending Directions) |
| CIBIL -> EXT_SOURCE is a monotonic proxy | Conceded explicitly; marked as "indicative secondary signal" not "validated Indian default probability" |
| Salary credits != all credits | Loan disbursals, refunds, and self-transfers are explicitly excluded from income calculation |
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
    App-->>Officer: Sealed Case ID + Hash prefix

    Note over DB,File: To verify: verify_hash_chain()\nComputes chain of all stored hashes\nReturns FAIL if any record was altered
```

---

## 6. Key Performance Numbers (Final-Test — Frozen)

| Metric | Value | Note |
|--------|-------|------|
| LightGBM ROC-AUC (Tier 3) | **0.774** | 95% CI: 0.767–0.781 |
| LightGBM PR-AUC (Tier 3) | **0.266** | ~3.3x lift over 8.07% base rate |
| Brier Score (calibrated) | **0.067** | Platt-scaled; trivial predictor ≈ 0.074 |
| Brier Score (raw) | 0.1777 | Pre-calibration, class-weighted output |
| Alert Threshold | **0.20** | Policy parameter; recall 33.3%, precision 30.5% |
| Transaction NLP Accuracy (Tier 1) | **100%** | 10-fold CV on 1,025 curated samples across 18 classes |
| Transaction NLP Macro F1 (Tier 1) | **1.000** | Calibrated Linear SGD + TF-IDF n-grams |
| Behavioral Clustering (Tier 2) | **k=4 Personas** | Trained across 2,000 synthetic account profiles |
| Anomaly Detection (Tier 2) | **5% Contamination** | Isolation Forest (n=150 estimators) on 8 behavioral dimensions |
| Categorisation Benchmark Accuracy | **98.7%** | 75-case ground-truth fixture |
| Categorisation Macro F1 | **0.985** | Per-category evaluation |
| Pytest Automated Tests | **71 passing** | 0 failures, 100% passing across full test suite |
| Policy Stability | **< 5% flip rate** | Monte Carlo, 1,000 trials, ±10% perturbation |
