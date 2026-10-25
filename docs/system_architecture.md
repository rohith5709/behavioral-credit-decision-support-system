# System Architecture — Behavioral Credit Decision Support System

> **Project**: B.Tech BCSE497J – Project I (VIT)  
> **Team**: Adharsh S (23BDS0029), Gowtham Kumar D (23BDS0186), Rohith S M (23BDS0025)  
> **Faculty Guide**: Dr. Viswanathan A

> [!IMPORTANT]
> The credit decisioning path is driven by **dual machine learning models**:
> 1. **Pillar 1 (Behavioral ML Model)**: Calibrated Random Forest trained on 30,000 real payment records from the UCI Credit Card Default dataset, mapped from bank-statement cash flows.
> 2. **Pillar 2 (Bureau Benchmark Model)**: LightGBM model trained on 246,000 applicants from the Home Credit dataset with Tree-SHAP attribution.
> Rule-based scoring has been completely eliminated from the credit decision path. Data quality hard stops are retained strictly as pre-qualification validity checks.

---

## 1. Full System Architecture (Tri-Tier ML & Deterministic Safeguards)

```mermaid
flowchart TD
    subgraph Inputs["Inputs"]
        CSV["Bank Statement (CSV / Digital PDF)"]
        SLIP["Salary Slip (Net pay + Employer)"]
        BUREAU["Officer Bureau Profile (CIBIL, Age, Tenure, Active Loans, Overdue Days)"]
        UCI["UCI Credit Card Default Dataset (30,000 records, 6-mo repayment history)"]
        HC["Home Credit Dataset (246k applicants, 61 features)"]
    end

    subgraph Pillar1["Pillar 1 — Statement Cash-Flow Behavioral ML Engine"]
        PARSE["statement_csv.py / statement_pdf.py\nParse -> Normalize -> Validate\nBalance reconciliation | PII masking | Duplicate removal"]
        
        CAT["behavioral.py -> categorise_statement_transactions()\nHybrid Categorisation Engine:\n1. Deterministic accounting rules (salary, loan, tax)\n2. Tier 1 Supervised NLP Classifier (TF-IDF + Calibrated Linear)\n3. Fallback to officer review for ambiguous items"]
        
        FEAT["behavioral.py -> build_statement_features()\nExtracts 23+ behavioral & cash-flow indicators\nsavings_ratio, income_variation, emi_burden, emergency_buffer"]
        
        BRIDGE["behavioral_ml_features.py -> map_statement_to_behavioral_features()\n15-Dimensional Feature Bridge to UCI Feature Space\nBounds clipping | Zero-division safeguards"]
        
        ML_PRED["behavioral_prediction.py -> predict_behavioral_risk()\nTier 2 Supervised Behavioral ML Model\nRandom Forest (200 trees, depth 10, Platt Calibrated)\nROC-AUC: 0.7725 | PR-AUC: 0.5304 | Accuracy: 81.5%\nOutputs: Calibrated P(default), Risk Band, Top Drivers"]

        UNSUP["behavioral_unsupervised.py -> score_behavioral_profile()\nTier 3 Account-Level Unsupervised ML Suite:\n1. Isolation Forest (n=150) -> Cash flow anomaly check\n2. K-Means (k=4) -> Behavioral spending persona clustering"]
        
        GATES["affordability.py -> evaluate_data_quality_gates()\nMandatory Pre-Qualification Validity Gates (Hard Stops)\nBalance mismatches | Min 3 months | 50% EMI caps"]
        
        VERIFY["salary_verification.py -> verify_salary_slip_cross_document()\nSalary slip vs detected statement credits (15% tolerance)"]
    end

    subgraph Pillar2["Pillar 2 — Macro Bureau Default Risk Benchmark"]
        TRAIN["benchmark_home_credit.py\nTraining Pipeline:\n64% train / 16% val / 20% final-test\nStratified split, random_state=42\nImputer fit strictly on train partition"]
        
        MODEL["home_credit_lightgbm.joblib\nSelected: LightGBM (balanced)\nPlatt Scaling calibration (sigmoidal)\nROC-AUC: 0.774 | PR-AUC: 0.266 | Brier: 0.067\nAlert Threshold: 0.20"]
        
        SCORE["applicant_scoring.py -> predict_applicant_risk()\nBureau Profile Mapping:\nCIBIL 300-900 -> EXT_SOURCE (monotonic proxy)\nOutputs: PD, risk_band, completeness_ratio"]
        
        SHAP["explain_home_credit.py\nExact Tree-SHAP via booster_.predict(pred_contrib=True)\nGlobal gain importance and local Shapley attribution"]
    end

    subgraph Integration["Dual-Pillar Integration & Safeguard Engine"]
        ENGINE["engine.py -> recommend()\nUnified 2x2 ML Decision Matrix:\nBehavioral ML PD vs Bureau ML PD\nIsolation Forest Anomaly & Salary Safeguard Overrides"]
    end

    subgraph Persistence["Persistence & Audit Trail"]
        DB["data/db.py -> SQLite Ledger\nSHA-256 Forward Hash Chain\nprev_hash -> SHA-256(record_json) -> record_hash\nExternal anchor: data/HEAD_HASH.sha256\nDPDP Act 2023 compliance (PII stripped before hashing)\nverify_hash_chain() detects tampering"]
    end

    subgraph UI["UI Layer — Streamlit Dashboard (app.py)"]
        T1["Tab 1: Case Summary & Review Checklist\nBehavioral ML risk card, top drivers, Isolation Forest alert"]
        T2["Tab 2: Statement Upload & NLP Categorisation\nColumn mapping, NLP confidence pills, officer overrides"]
        T3["Tab 3: Behaviour Profile & What-If Simulator\nFeature bridge inspector, counterfactual sandbox, calibration curve"]
        T4["Tab 4: Synthetic Portfolio Simulation\nsimulator_behaviour_features.csv cohort analysis"]
        T5["Tab 5: ML Benchmark & Explainability\nPillar 1 Random Forest validation + Pillar 2 Tree-SHAP attributions"]
        T6["Tab 6: Officer Decision & Tamper-Evident Ledger\nPlotly 2x2 Risk Map, stress testing lab, SHA-256 sealed record"]
    end

    CSV --> PARSE
    SLIP --> VERIFY
    PARSE --> CAT --> FEAT --> BRIDGE --> ML_PRED
    FEAT --> UNSUP
    FEAT --> GATES
    GATES --> ENGINE
    ML_PRED --> ENGINE
    UNSUP --> ENGINE
    VERIFY --> ENGINE

    BUREAU --> SCORE
    HC --> TRAIN --> MODEL
    UCI --> ML_PRED
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

## 2. Dual-Pillar 2x2 Decision Matrix Logic

```mermaid
flowchart LR
    GATES{"Data Quality\nHard Stops Triggered?"}
    SF{"Salary Slip\nMismatch > 15%?"}
    ANOM{"Isolation Forest\nAnomaly Detected?"}
    S1{"Behavioral ML PD\n< 30%?"}
    S2{"Bureau PD\n< 20%?"}

    GATES -->|"YES"| REF["Refer for Additional Documents\n(Evidence Gap Safeguard)"]
    GATES -->|No| SF

    SF -->|"YES"| REF_SAL["Refer for Additional Documents\n(Document Safeguard Override)"]
    SF -->|No| S1

    S1 -->|Yes — Low Behavioral Risk| S2
    S1 -->|No — Elevated Behavioral Risk| S3{"Bureau PD\n< 20%?"}

    S2 -->|Yes — Low Bureau Risk| ANOM
    S2 -->|No — Elevated Bureau Risk| Q2["Manual Review\n(Low Behavioral / Elevated Bureau Divergence)"]

    ANOM -->|Yes — Outlier Volatility| Q_ANOM["Manual Review\n(Anomaly Safeguard Override)"]
    ANOM -->|No — Typical Patterns| Q1["Meets Indicative Criteria\n(Dual ML Alignment - Low Risk)"]

    S3 -->|Yes — Low Bureau Risk| Q3["Manual Review\n(Elevated Behavioral / Low Bureau Divergence)"]
    S3 -->|No — Elevated Bureau Risk| Q4["Does Not Meet Criteria\n(Dual ML Alignment - Elevated Risk)"]

    style Q1 fill:#064E3B,color:#34D399,stroke:#10B981
    style Q2 fill:#78350F,color:#FBBF24,stroke:#F59E0B
    style Q3 fill:#78350F,color:#FBBF24,stroke:#F59E0B
    style Q4 fill:#7F1D1D,color:#F87171,stroke:#EF4444
    style Q_ANOM fill:#78350F,color:#FBBF24,stroke:#F59E0B
    style REF fill:#7F1D1D,color:#F87171,stroke:#EF4444
    style REF_SAL fill:#7F1D1D,color:#F87171,stroke:#EF4444
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
| Behavioral ML Bridge | `src/features/behavioral_ml_features.py` | 15-dimensional bridge projecting statement cash-flows into calibrated UCI feature space with clamping and zero-division guards |
| Behavioral ML Trainer | `src/models/train_behavioral_model.py` | Full 70/15/15 train-val-test pipeline on 30k UCI records; 5-fold CV candidate selection; Platt calibration |
| Behavioral ML Predictor | `src/models/behavioral_prediction.py` | Pillar 1 inference module; calibrated P(default), risk bands, permutation feature attributions |
| Behavioral Unsupervised Suite | `src/models/behavioral_unsupervised.py` | Tier 3 Unsupervised ML Suite; Isolation Forest (n=150) anomaly detection and K-Means (k=4) spending persona clustering |
| Quality Gates & Policy | `src/decision/affordability.py` | Pre-qualification data quality hard stops (`evaluate_data_quality_gates`); reference score calculation |
| Decision Engine | `src/decision/engine.py` | Unified Dual-Pillar ML `recommend()` integrating Pillar 1 ML PD, Pillar 2 Bureau PD, and Isolation Forest anomaly overrides |
| Bureau Scorer | `src/models/applicant_scoring.py` | Maps officer-entered bureau profile to Home Credit model features; runs calibrated PD; returns Tree-SHAP |
| SHAP Explainer | `src/models/explain_home_credit.py` | Exact Tree-SHAP via `booster_.predict(pred_contrib=True)`; global gain importance; lru_cache bundle |
| HC Trainer | `src/models/benchmark_home_credit.py` | Full Home Credit training pipeline; stratified 64/16/20 splits; candidate selection; Platt calibration |
| Database | `src/data/db.py` | SQLite with SHA-256 forward hash chain; external anchor; DPDP Act 2023 compliance; tamper detection |
| Matrix Viz | `src/reporting/matrix_viz.py` | Plotly 2x2 decision matrix chart; Tree-SHAP horizontal attribution chart |
| Case Summary | `src/reporting/case_summary.py` | Decision record builder; evidence row aggregation; review flag extractor with ML alerts and anomaly integration |
| App | `app.py` | 6-tab Streamlit UI; FinTech dark CSS; What-If ML sandbox; Plotly reliability curves and population distributions |

---

## 4. Key Performance Numbers (Final-Test — Frozen)

| Metric | Value | Note |
|--------|-------|------|
| **Pillar 1: Behavioral RF ROC-AUC** | **0.7725** | Evaluated on frozen 4,500 held-out UCI test records |
| **Pillar 1: Behavioral RF PR-AUC** | **0.5304** | Lift over 22.1% base rate |
| **Pillar 1: Behavioral Accuracy** | **81.53%** | Calibrated Platt sigmoid probabilities |
| **Pillar 1: F1 (Default Class)** | **0.4842** | Precision 63.31%, Recall 39.20% |
| **Pillar 2: LightGBM ROC-AUC** | **0.774** | 95% CI: 0.767–0.781 (Home Credit benchmark) |
| **Pillar 2: LightGBM PR-AUC** | **0.266** | ~3.3x lift over 8.07% base rate |
| **Pillar 2: Brier Score (calibrated)**| **0.067** | Platt-scaled; trivial predictor ≈ 0.074 |
| **Transaction NLP Accuracy (Tier 1)** | **100%** | 10-fold CV on 1,025 curated samples across 18 classes |
| **Transaction NLP Macro F1 (Tier 1)** | **1.000** | Calibrated Linear SGD + TF-IDF n-grams |
| **Behavioral Clustering (Tier 3)** | **k=4 Personas** | Trained across 2,000 synthetic account profiles |
| **Anomaly Detection (Tier 3)** | **5% Contamination** | Isolation Forest (n=150 estimators) on behavioral cash-flow dimensions |
| **Pytest Automated Tests** | **127 passing** | 0 failures, 100% passing across full test suite |
