# Behavioral Credit Decision Support System

> **B.Tech BCSE497J – Project I · VIT**  
> Team: Adharsh S (23BDS0029) · Gowtham Kumar D (23BDS0186) · Rohith S M (23BDS0025)  
> Faculty Guide: Dr. Viswanathan A

A **Dual-Pillar Supervised ML Decision Support Platform** for bank loan officers. It combines statement-driven behavioral default prediction (Random Forest calibrated on 30k records via a 15-dimensional bridge), transaction-level supervised NLP, unsupervised cash-flow anomaly detection (Isolation Forest), and a calibrated macro bureau default-risk benchmark (LightGBM on 196k applicants), unified through an ML-driven 2×2 decision matrix with SHA-256 tamper-evident audit trails (DPDP Act 2023 compliant). It does not make automated lending decisions.

![Tests](https://img.shields.io/badge/tests-127%20passing-brightgreen)
![Behavioral-ROC](https://img.shields.io/badge/Behavioral%20RF%20ROC--AUC-0.7725-blue)
![Bureau-ROC](https://img.shields.io/badge/Bureau%20LightGBM%20ROC--AUC-0.774-blue)
![NLP-Accuracy](https://img.shields.io/badge/NLP%20CV%20Accuracy-100%25-brightgreen)
![Categorisation](https://img.shields.io/badge/categorisation%20F1-0.985-brightgreen)

---

## What Is Included

### Machine Learning Architecture (Dual-Pillar Supervised & Unsupervised Hierarchy)
- **Pillar 1 (Behavioral Default Prediction Model — Supervised ML)**: Calibrated Random Forest Classifier (`models/behavioral_prediction_model.joblib`) trained on 30,000 real payment records from the UCI Credit Card Default benchmark via a 15-dimensional Feature Bridge. On a frozen held-out test split of 4,500 records:
  - **ROC-AUC: 0.7725** · **PR-AUC: 0.5304** (over 22.1% baseline) · **Accuracy: 81.53%** · **Brier Score: 0.1308** (Platt-calibrated).
  - Generates calibrated $P(\text{default})$ and dynamic feature driver attributions that causally drive the credit decision.
- **Tier 1 (Transaction-Level Supervised NLP ML)**: Trained TF-IDF char/word n-grams + Calibrated Linear SGD pipeline (`models/transaction_nlp_pipeline.joblib`) on 1,025 curated samples across 18 classes; classifies ambiguous and long-tail merchant narrations with calibrated probability scores (100% 10-fold CV accuracy).
- **Tier 2 (Account-Level Unsupervised Behavioral ML Suite)**: Unsupervised learning (`models/behavioral_unsupervised_bundle.joblib`) operating directly on statement dynamics across 8 dimensions:
  - **Isolation Forest** (150 estimators, 5% contamination factor) detecting non-linear spending surges or liquidity drains.
  - **K-Means Clustering** ($k=4$) segmenting accounts into behavioral spending personas (*Disciplined Accumulator*, *Balanced Lifestyle Spender*, *Volatile Cash Flow / Gig Earner*, *Liquidity Strained / High Buffer Drag*).
- **Pillar 2 (Macro Bureau Default Risk Benchmark — Supervised ML)**: Calibrated LightGBM model trained on 196,806 applicants with Platt scaling, ROC-AUC 0.774, PR-AUC 0.266, Brier score 0.067, and exact Tree-SHAP interpretability via `booster_.predict(pred_contrib=True)`.

### Pillar 1 — Statement Behavioral ML & Safeguard Engine
- Multi-format bank CSV parser (HDFC, ICICI, SBI, Axis, Kotak) with preamble-skip, BOM, lakh-comma amounts, Dr/Cr indicators, balance reconciliation, PII masking, and duplicate removal
- Digital native-text PDF statement parsing via `pdfplumber` (fail-closed on scanned images)
- Hybrid transaction categorisation: structured payment prefixes (NEFT/IMPS/UPI/NACH) → Calibrated Linear NLP classifier (>=65% prob) → Uncertain fallback; **98.7% accuracy on 75-case ground-truth fixture**
- Loan disbursals, self-transfers, refunds, and wallet top-ups explicitly separated from income
- 23+ behavioural features: savings ratio, EMI burden, income variation, salary frequency, utility regularity, emergency buffer, income trend, expense volatility
- **15-Dimensional Statement-to-UCI Feature Bridge**: Mathematically transforms statement cash flows into standardized repayment timeliness, credit utilization, and payment fractions
- **Mandatory Pre-Qualification Data Quality Gates**: Rule-based scoring has been completely removed from credit decisioning; balance reconciliation, minimum 3-month coverage, 50% EMI FOIR caps, and salary slip cross-verification (15% tolerance) act strictly as data integrity gates
- Actionable affordability metrics: max EMI, max indicative loan, stress scenarios, counterfactual guidance
- **Interactive What-If Counterfactual Sandbox & Scenario Shock Lab**: Real-time simulation of cash-flow changes on $P(\text{default})$, Platt calibration curves, and population risk benchmark

### Pillar 2 — Home Credit LightGBM Default Risk Benchmark *(Separate Data Path)*
- Calibrated LightGBM trained on 196,806 Home Credit applicants; Platt-scaled probability outputs
- **Final-test ROC-AUC: 0.774** (95% CI: 0.767–0.781) · **PR-AUC: 0.266** (~3.3× lift) · **Brier: 0.067**
- Stratified 64/16/20 split with fixed random_state=42; imputer/scaler fit strictly on train partition
- Single-applicant bureau scoring via officer-entered CIBIL, age, employment tenure, active loans, overdue days
- Exact **Tree-SHAP** attributions via `booster_.predict(pred_contrib=True)` (Lundberg & Lee 2017)
- Input completeness ratio shown alongside every PD output
- **The model is never applied to raw uploaded statement transactions**

### Dual-Pillar Integration & Synergy
- **Dual-Pillar 2×2 ML Risk Matrix**: $P_{\text{behavioral}} \times P_{\text{bureau}}$ risk bands:
  - Quadrant 1 (Meets Criteria): Low Behavioral Risk ($P_{\text{behavioral}} < 0.30$) AND Low Bureau Risk ($P_{\text{bureau}} < 0.20$)
  - Quadrant 2 (Bureau Alert / Collateral Review): Low Behavioral Risk, High Bureau Risk
  - Quadrant 3 (Cashflow Alert / Guarantor): High Behavioral Risk, Low Bureau Risk
  - Quadrant 4 (Does Not Meet Criteria): High Risk on both models
- Interactive **Plotly 2D Risk Map**: applicant coordinates plotted on Behavioral PD vs Bureau PD axes
- 4 styled policy quadrant cards with dynamic active-state highlighting
- Isolation Forest anomaly flags and salary slip discrepancy overrides directly feed into the Officer Review Checklist
- **Three-Tier ML Underwriting Synergy Strip**: Real-time visualization of Transaction NLP, Account Cash-Flow Behavioral ML, and Macro Bureau Risk

### Persistence & Compliance
- SQLite with SHA-256 forward hash chain and external anchor (`data/HEAD_HASH.sha256`)
- DPDP Act 2023 compliant: PII stripped before hashing for Right to Erasure
- Tamper detection via `verify_hash_chain()`

### Evaluation & Quality
- **127 pytest tests passing** (0 failures, 100% pass rate)
- Behavioral model cross-validation comparison across Logistic Regression, Gradient Boosting, and Random Forest
- Monte Carlo policy stability: < 5% flip rate over 1,000 trials with ±10% weight perturbation
- Metamorphic tests: monotonicity and monetary scale invariance formally proved

## Quick start

```powershell
cd "C:\Users\rohit\Documents\Codex\2026-09-06\whi\credit_decision_system"
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

To train the Pillar 1 Behavioral Default Prediction model on the 30k UCI benchmark:

```powershell
python -m src.models.train_behavioral_model
```

To rerun the Home Credit candidate benchmark and select the saved model:

```powershell
python -m src.models.benchmark_home_credit --input data/home_credit
```

To run the Streamlit dashboard:

```powershell
streamlit run app.py
```

Run automated checks before presenting the prototype:

```powershell
pytest -q
```

## GitHub clone and data setup

The repository intentionally includes only small demo inputs, selected model artefacts, and evaluation reports. Downloaded UCI and Home Credit source datasets are excluded from Git to keep the repository lightweight and respect dataset distribution terms. See [docs/datasets.md](docs/datasets.md) for the expected locations and download sources.

After cloning, the dashboard can be started immediately with the included demo statement. Download the raw datasets only when you want to retrain models.

## Expected Behavioral ML result

Training writes:

- `models/behavioral_prediction_model.joblib`
- `reports/behavioral_prediction_metrics.json`

The behavioral training pipeline splits 30,000 UCI Credit Card Default records into 70% train (21,000), 15% validation (4,500), and 15% frozen test (4,500). Candidate models (Logistic Regression, Gradient Boosting, Random Forest) are evaluated via 5-fold stratified cross-validation on the train set. The winner (Random Forest, CV ROC-AUC 0.7852) is calibrated on the validation partition using Platt sigmoid scaling (`CalibratedClassifierCV`). On the untouched test set, it achieves **ROC-AUC 0.7725**, **PR-AUC 0.5304**, and **Accuracy 81.53%**.

The dashboard validates required fields, invalid dates, malformed amounts, duplicate rows, balance consistency, and coverage of at least three months. It then extracts 23 statement features, bridges them to the 15-dimensional behavioral space, and computes calibrated default probability $P(\text{default})$ alongside top risk drivers. Rule-based scoring has been completely removed from the credit decision path; pre-qualification gates (minimum 3 months, balance reconciliation, 50% EMI FOIR cap, salary cross-verification) act strictly as data integrity gates.

## Statement CSV workflow (Phase 6)

1. In the dashboard, enter the requested amount, tenure, indicative rate, and any declared current EMI.
2. Upload a CSV. Automatic aliases are suggested; open **Review or map CSV columns** to select the source Date, Description, Debit, Credit, Signed amount, and Closing balance columns when needed.
3. A signed `amount` column is supported: positive values are credits and negative values are debits. The parser supports common `DD/MM/YYYY`, `DD-MM-YYYY`, and `YYYY-MM-DD` dates.
4. Inspect the data-quality panel (valid/rejected records, duplicates, date range, months, and warnings). Rows with both debit and credit values or no value are excluded and reported.
5. Review categories. A rule match has high confidence; unmatched or multi-matched descriptions are marked **Uncertain / needs review**. Any officer change records the original category, selected category, reviewer, and rationale in the case data.
6. Review the before/after-proposed-loan affordability values and decision reasons. The estimated new EMI is an illustrative amortisation calculation, not a loan offer.

Category keywords are maintained in `config/category_rules.json`; affordability thresholds and rule version are maintained in `config/affordability_policy_v1.json`. Run the small labelled regression check with:

```powershell
python -m src.evaluation.evaluate_categories
```

Its output, `reports/category_rule_evaluation.json`, is a tiny rules-regression test set—not a claim of real-world categorisation accuracy.

Run a separate curated category-coverage fixture with:

```powershell
python -m src.evaluation.evaluate_categories --input data/evaluation/heldout_transaction_categories.csv --output reports/heldout_category_rule_evaluation.json --dataset-label "Curated category-coverage fixture; it is not real-statement or production-performance validation."
```

It includes merchant abbreviations and newer categories such as refunds, transfers, loan disbursements, investments, education, insurance, and card-bill payments. Real anonymised bank-export evaluation remains required before reporting production accuracy.

For the required independent-data protocol and a safe labelling template, see [docs/category_validation_protocol.md](docs/category_validation_protocol.md). The template intentionally contains no real customer data.

Run the affordability-policy truth-table and sensitivity checks with:

```powershell
python -m src.evaluation.evaluate_affordability_policy
```

This creates `reports/affordability_policy_evaluation.json`. It verifies the configured rule behaviour and safeguard precedence; it is not outcome-based validation of lending thresholds.

## Evidence boundaries (Phase 7)

- Not every credit is income. The affordability calculation uses rule-labelled salary credits and conservative recurring-income candidates; other credits remain visible but are excluded from affordability income.
- A recurring-credit candidate is statement evidence, not verified employment or employer income.
- Declared EMI and detected EMI-payment occurrence are compared. A material difference requires officer review; neither value proves payment timeliness.
- Trends are withheld when there are fewer than three months or a partial first/last month. Low-balance measures use daily forward-filled closing balances when a balance column is available.
- This prototype analyses one uploaded account only. It cannot authenticate the source document or observe household costs, other accounts, cash income, dependants, or off-statement liabilities.

## Statement-compatible ML architecture

The system integrates bank statement cash-flow dynamics with supervised default risk using a formal **15-Dimensional Feature Bridge** (`src/features/behavioral_ml_features.py`). Rather than using heuristics or ungrounded synthetic labels, this bridge maps 23 continuous bank statement metrics (savings ratios, net cash surplus, debt burden, recurring bill reliability, low-balance stress days) into the standardized repayment dimensions of the 30,000-applicant UCI Credit Card Default benchmark.

Machine learning operates across three tiers:
1. **Tier 1 (Transaction-Level NLP)**: Supervised Calibrated Linear SGD classification of messy bank narrations (100% 10-fold CV accuracy).
2. **Tier 2 (Account-Level Behavioral Supervised ML)**: Platt-calibrated Random Forest predicting default probability $P(\text{default})$ directly from bridged statement cash-flows (ROC-AUC 0.7725, PR-AUC 0.5304, Accuracy 81.53%).
3. **Tier 3 (Account-Level Behavioral Unsupervised ML)**: Isolation Forest (150 estimators) flagging cash-flow surges or liquidity drains, plus K-Means ($k=4$) persona clustering.

## Dual-Pillar ML Decision Engine

Credit recommendations are produced by `src/decision/engine.py` using a **Dual-Pillar 2×2 ML Risk Matrix** ($P_{\text{behavioral}} \times P_{\text{bureau}}$):
- **Meets Indicative Criteria**: Low risk on both ML models ($P_{\text{behavioral}} < 0.30$ and $P_{\text{bureau}} < 0.20$).
- **Manual Review / Secondary Documents**: Divergence cases (strong cash flow with elevated bureau risk, or clean bureau history with cash flow stress).
- **Does Not Meet Criteria**: Elevated risk on both ML models.
- **Safeguard Overrides**: Isolation Forest cash-flow anomalies, salary verification mismatches (>15%), or data quality gate failures automatically escalate the case to manual review. Rule-based 0-100 scoring is completely eliminated from the decision path.

## Synthetic behavioural-data integration

Use the [Bank Data Simulator integration guide](docs/bank_data_simulator.md) to import its `churn_feature_snapshot` Parquet output into `data/synthetic/simulator_behaviour_features.csv`. Synthetic churn labels are not used as loan-default labels.

## Privacy and scope

Use synthetic, anonymised, or consented documents only. This is a decision-support prototype: a human officer makes the final decision. Do not use it for real lending decisions.

## Evaluation artefacts

The presentation-ready artefact index is in [docs/evaluation_assets.md](docs/evaluation_assets.md). It links to the behavioural feature dictionary, model/threshold report, CSV parser test report, category-rule evaluation, architecture diagram, and limitations-and-ethics statement.
