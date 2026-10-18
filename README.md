# Behavioral Credit Decision Support System

> **B.Tech BCSE497J – Project I · VIT**  
> Team: Adharsh S (23BDS0029) · Gowtham Kumar D (23BDS0186) · Rohith S M (23BDS0025)  
> Faculty Guide: Dr. Viswanathan A

A **Dual-Pillar human-in-the-loop credit decision support platform** for bank loan officers. It combines a deterministic statement cash-flow affordability engine with a calibrated LightGBM default-risk benchmark, unified through a 2×2 decision matrix with SHA-256 tamper-evident audit trails (DPDP Act 2023 compliant). It does not make lending decisions.

![Tests](https://img.shields.io/badge/tests-63%20passing-brightgreen)
![ROC-AUC](https://img.shields.io/badge/LightGBM%20ROC--AUC-0.774-blue)
![PR-AUC](https://img.shields.io/badge/PR--AUC-0.266-blue)
![Categorisation](https://img.shields.io/badge/categorisation%20F1-0.985-brightgreen)

---

## What Is Included

### Pillar 1 — Deterministic Statement Affordability Engine
- Multi-format bank CSV parser (HDFC, ICICI, SBI, Axis, Kotak) with preamble-skip, BOM, lakh-comma amounts, Dr/Cr indicators, balance reconciliation, PII masking, and duplicate removal
- Digital native-text PDF statement parsing via `pdfplumber` (fail-closed on scanned images)
- 4-layer transaction categorisation: structured payment prefixes (NEFT/IMPS/UPI/NACH) → merchant normalisation → vernacular tokens (Kirana, Vetan, Kist) → Uncertain fallback; **98.7% accuracy on 75-case ground-truth fixture**
- Loan disbursals, self-transfers, refunds, and wallet top-ups explicitly separated from income
- 23+ behavioural features: savings ratio, EMI burden, income variation, salary frequency, utility regularity, emergency buffer, income trend, expense volatility
- 8-component transparent 0–100 affordability score with policy-version stamping and mandatory safeguard overrides
- Salary slip cross-document verification with 15% tolerance
- Actionable affordability metrics: max EMI, max indicative loan, stress scenarios, counterfactual guidance
- **Real-time Scenario Shock & Stress Testing Lab**: interactive Income Shock / Expense Inflation / Rate Hike sliders

### Pillar 2 — Home Credit LightGBM Default Risk Benchmark *(Separate Data Path)*
- Calibrated LightGBM trained on 196,806 Home Credit applicants; Platt-scaled probability outputs
- **Final-test ROC-AUC: 0.774** (95% CI: 0.767–0.781) · **PR-AUC: 0.266** (~3.3× lift) · **Brier: 0.067**
- Stratified 64/16/20 split with fixed random_state=42; imputer/scaler fit strictly on train partition
- Single-applicant bureau scoring via officer-entered CIBIL, age, employment tenure, active loans, overdue days
- Exact **Tree-SHAP** attributions via `booster_.predict(pred_contrib=True)` (Lundberg & Lee 2017)
- Input completeness ratio shown alongside every PD output
- **The model is never applied to raw uploaded statement transactions**

### Dual-Pillar Integration
- 2×2 decision matrix: Q1 (Approve), Q2 (Bureau Alert), Q3 (Cashflow Alert), Q4 (Decline)
- Interactive **Plotly 2D Risk Map**: applicant coordinates plotted on affordability vs PD axes
- 4 styled policy quadrant cards with dynamic active-state highlighting
- Salary slip failure overrides all matrix quadrants

### Persistence & Compliance
- SQLite with SHA-256 forward hash chain and external anchor (`data/HEAD_HASH.sha256`)
- DPDP Act 2023 compliant: PII stripped before hashing for Right to Erasure
- Tamper detection via `verify_hash_chain()`

### Evaluation & Quality
- **63 pytest tests passing** (0 failures)
- Monte Carlo policy stability: < 5% flip rate over 1,000 trials with ±10% weight perturbation
- Metamorphic tests: monotonicity and monetary scale invariance formally proved

## Quick start

```powershell
cd "C:\Users\rohit\Documents\Codex\2026-09-06\whi\credit_decision_system"
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Place the downloaded UCI Excel file in `data/raw/` and name it `uci_credit_default.xls` (or pass its path explicitly). Then run:

```powershell
python -m src.models.train_uci --input data/raw/uci_credit_default.xls
streamlit run app.py
```

To rerun the Home Credit candidate benchmark and select the saved model:

```powershell
python -m src.models.benchmark_home_credit --input data/home_credit
```

Run automated checks before presenting the prototype:

```powershell
pytest -q
```

## GitHub clone and data setup

The repository intentionally includes only small demo inputs, selected model artefacts, and evaluation reports. Downloaded UCI and Home Credit source datasets are excluded from Git to keep the repository lightweight and respect dataset distribution terms. See [docs/datasets.md](docs/datasets.md) for the expected locations and download sources.

After cloning, the dashboard can be started immediately with the included demo statement. Download the raw datasets only when you want to retrain models.

## Expected UCI result

Training writes:

- `models/uci_logistic_regression.joblib`
- `reports/uci_metrics.json`

The Home Credit benchmark uses reproducible 64% train, 16% validation, and untouched 20% final-test partitions. Candidate, calibration, and threshold choices are made only on validation data; the test partition is used once for final reporting. It writes comparison, threshold, calibration, training-configuration, and model-card reports in `reports/`. Logistic Regression and both LightGBM candidates train on the complete training partition; compute-intensive Random Forest and XGBoost baselines use a deterministic stratified 50,000-row cap. Candidate selection uses validation PR-AUC, then ROC-AUC, then lower Brier score. This is a single-dataset benchmark; Phase 1 will add repeated/nested validation and further leakage, ablation, and fairness checks.

The dashboard validates required fields, invalid dates, malformed amounts, duplicate rows, balance consistency, and coverage of at least three months. It then assigns visible rule-based categories and derives monthly affordability views. Its transparent statement policy can recommend approval, manual review, referral for additional documents, or decline; a human officer makes the final choice. The Home Credit model is not applied to incompatible raw transaction fields.

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

## Statement-compatible ML bridge (Phase 12)

The Home Credit benchmark is deliberately separate from uploaded statements. The future compatible-ML feature contract, safe applicant-data template, and data-readiness validator are documented in [docs/statement_ml_bridge.md](docs/statement_ml_bridge.md). No statement-based ML model is trained or used until consented, anonymised historical applicant data with repayment/default outcomes is available.

## Statement affordability policy

The uploaded-statement assessment uses `statement-affordability-v1` and is separate from the Home Credit model. It awards up to 25 points each for savings ratio and EMI burden, 20 for salary consistency, 15 for expense stability, 10 for utility regularity, and 5 for data quality. A score of 75 or higher indicates that available statement evidence meets indicative affordability criteria; 45–74 produces manual review; below 45 indicates that available evidence does not meet indicative criteria. The system always requires review or additional evidence when the statement has fewer than three months, data quality below 80%, no recognised recurring income, contradictory balance data, material EMI mismatch, or critical EMI burden.

## Synthetic behavioural-data integration

Use the [Bank Data Simulator integration guide](docs/bank_data_simulator.md) to import its `churn_feature_snapshot` Parquet output into `data/synthetic/simulator_behaviour_features.csv`. Synthetic churn labels are not used as loan-default labels.

## Privacy and scope

Use synthetic, anonymised, or consented documents only. This is a decision-support prototype: a human officer makes the final decision. Do not use it for real lending decisions.

## Evaluation artefacts

The presentation-ready artefact index is in [docs/evaluation_assets.md](docs/evaluation_assets.md). It links to the behavioural feature dictionary, model/threshold report, CSV parser test report, category-rule evaluation, architecture diagram, and limitations-and-ethics statement.
