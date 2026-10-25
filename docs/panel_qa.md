# Viva Panel Q&A Preparation Guide
**Project**: Behavioral Credit Decision Support System using Financial Document Analysis  
**Team**: Adharsh S (23BDS0029), Gowtham Kumar D (23BDS0186), Rohith S M (23BDS0025)  
**Faculty Guide**: Dr. Viswanathan A | **Course**: BCSE497J – Project I, VIT

> [!NOTE]
> **The Golden Rule**: Never bluff. Deliver a calm, structured concession before pivoting to your defence. The formula:  
> *"You are completely right, Sir/Ma'am. In our design, [**Concede the Limitation**]. That is why we deliberately [**Technical Mitigation**], because [**Architectural / Regulatory Reason**]."*

---

## Section A: Fundamental Architecture Questions

### Q1. "Why call this AI or intelligent when your headline idea is behavioral statement analysis?"

**Expected Probe**: *"The statement analysis claims to be behavioral credit assessment, but you're just computing account balance ratios and simple rules. Where is the actual Machine Learning in statement analysis?"*

**Defense**:
> "You are raising a critical architectural point. In our system, Machine Learning is deeply integrated across three distinct hierarchical tiers — including directly within statement analysis:
>
> 1. **Tier 1 (Transaction-Level Supervised NLP ML)**: Bank statement narrations in India are unstructured, colloquial, and messy. Exact regex cannot cover the long tail of UPI and merchant strings. We deploy a trained TF-IDF + Calibrated Linear SGD classification pipeline across 18 transaction classes with probabilistic confidence scoring. Unlabelled merchant debits are classified with genuine probabilities, replacing rigid heuristics.
> 2. **Tier 2 (Account-Level Unsupervised Behavioral ML)**: Even without outcome labels (loan defaults on individual bank statements), machine learning belongs in statement analysis. We deploy an Unsupervised ML Suite directly on statement cash-flows: an **Isolation Forest** (150 estimators) detects non-linear cash flow anomalies, and **K-Means clustering** ($k=4$) assigns applicants into empirically derived spending personas (such as *Disciplined Accumulator* vs *Volatile Cash Flow / Gig Earner*).
> 3. **Tier 3 (Macro Bureau Supervised Default Risk Benchmark)**: A calibrated LightGBM model trained on 196k applicants with exact Tree-SHAP interpretability provides the macro credit-history risk signal.
>
> Meanwhile, deterministic scoring is strictly preserved for the **Affordability Engine** (0-100 policy score). Under RBI Fair Lending Directions, adverse-action notice mandates require that applicants receive transparent, non-probabilistic explanations for decline reasons. Black-box supervised scoring on statements would violate regulatory explainability mandates."

---

### Q1b. "Examiner Critique: ML is absent where it matters most: statement analysis is just rules, and ML is only in the bureau benchmark. Why didn't you train a supervised model to predict defaults directly from statements?"

**Expected Probe**: *"A project judged on ML should have ML at its core. If statement analysis is your main contribution, why didn't you train a supervised default-prediction model directly on bank statements?"*

**Defense**:
> "You are completely right, Sir/Ma'am. In our design, **we deliberately chose not to train a supervised default model directly on bank statement cash-flows**. That limitation stems from a fundamental scientific and ethical constraint:
>
> **The Data Reality**: There is **no publicly available, outcome-labelled Indian bank statement dataset** linking individual bank statements to 90-day loan delinquency (DPD). Any project claiming to train a supervised default-prediction model on bank statements without ground-truth loan delinquency labels is either fabricating synthetic default labels or suffering from unscientific leakage. As an engineering team, we refused to falsify default labels to force ML where ground truth does not exist.
>
> **Our Methodological Solution (Tri-Tier ML Architecture)**:
> Rather than pretending we had default labels, we applied Machine Learning where it is mathematically sound and scientifically honest:
> - **Supervised ML where ground truth exists**: We trained a Supervised NLP Classification pipeline on merchant narrations, achieving 100% 10-fold CV accuracy and generating calibrated class probabilities.
> - **Unsupervised ML for unlabeled behavioral patterns**: For account-level statement dynamics, the scientifically rigorous approach to unlabeled data is **unsupervised learning**. We deployed an **Isolation Forest** to catch outlier cash-flow volatility and **K-Means clustering** to segment accounts into behavioral spending personas.
> - **Supervised Benchmark for Macro Default Risk**: We trained our calibrated LightGBM classifier on the 246,000-applicant Home Credit benchmark, complete with Platt probability scaling and Tree-SHAP attributions.
>
> This gives us a mathematically honest, production-grade tri-tier system: NLP at the transaction level, Unsupervised ML at the account cash-flow level, and Supervised ML at the bureau level — with auditable deterministic safeguards satisfying RBI compliance."

---

### Q2. "Home Credit is European financial data, not Indian. Why should its default probability mean anything here?"

**Expected Probe**: *"Your model is trained on Polish/Eastern European consumer finance data. A CIBIL of 750 in India is not the same as a credit score in Slovakia."*

**Defense**:
> "You are absolutely correct. Home Credit is a European consumer finance benchmark dataset and the model's probability output should **not** be interpreted as a calibrated Indian PD.
>
> We use it as a **methodological benchmark** — to demonstrate that the entire ML pipeline works end-to-end: feature engineering, Platt scaling, threshold optimisation, and Tree-SHAP attribution. The PD shown to the officer is framed explicitly as an 'indicative secondary signal with a configurable threshold', never as an approval probability.
>
> In commercial deployment, Pillar 2 would be retrained on the institution's own historical loan portfolio under RBI model-risk guidelines. The prototype exists so the officer can explore Dual-Pillar divergence today."

---

### Q3. "Mapping CIBIL 300–900 to EXT_SOURCE 0–1 is a made-up assumption. The EXT_SOURCE values were never disclosed by Home Credit."

**Expected Probe**: *"EXT_SOURCE is an anonymised, normalised score whose definition was never revealed. Mapping CIBIL to it is not scientifically valid."*

**Defense**:
> "You are right. EXT_SOURCE values are anonymised. Our mapping is a **documented monotonic heuristic proxy**, not an equivalence.
>
> CIBIL score and EXT_SOURCE both represent credit-bureau quality signals — they move in the same direction (higher = better credit history). We normalise CIBIL linearly into the [0, 1] range (300 maps to 0, 900 maps to 1) to provide a plausible directionally consistent input.
>
> We acknowledge this is an assumption. Concretely, the sensitivity of the PD output to this proxy can be demonstrated by examining the Tree-SHAP attributions — EXT_SOURCE_3 is the dominant driver. We recommend presenting the output as a risk-band (Low / Moderate / High) rather than a point estimate, and always showing the input completeness ratio alongside it."

**Numbers to know**: EXT_SOURCE_3 typically has the highest gain importance in the model.

---

### Q4. "The two pillars both use EMI. Isn't that double-counting?"

**Expected Probe**: *"Pillar 1's EMI burden score and Pillar 2's AMT_ANNUITY feature both incorporate EMI. You are weighting EMI twice in the final matrix."*

**Defense**:
> "There is a partial overlap in debt information, but the two pillars evaluate fundamentally different dimensions:
>
> - **Pillar 1 measures cash-flow liquidity**: Can this applicant's monthly bank-statement surplus absorb one more EMI today?
> - **Pillar 2 measures historical willingness to repay**: Has this applicant honoured past credit obligations across bureau trade-lines historically?
>
> The primary value of the 2×2 matrix is detecting **divergence cases** — Quadrants 2 and 3 — where the two pillars disagree. A borrower in Q2 (good cashflow, high bureau PD) is a different risk profile from a Q3 borrower (poor cashflow, clean bureau history). Both route to a human officer rather than auto-resolving. The matrix is a conflict-detection device, not a weighted sum."

---

## Section B: ML Model Questions

### Q5. "PR-AUC of 0.266 looks very low."

**Expected Probe**: *"A PR-AUC of 0.266 means your model has poor precision-recall performance."*

**Defense**:
> "PR-AUC must be interpreted against the **class prevalence baseline**. At our 8.07% default rate, the baseline PR-AUC for a random classifier equals the prevalence — approximately 0.081. Our 0.266 represents a **3.3× lift over that baseline**, which is consistent with published results on the Home Credit Kaggle benchmark at this data size.
>
> ROC-AUC of 0.774 also places us in line with published benchmarks for this dataset. We are not claiming state-of-the-art performance — we are demonstrating a reproducible, leakage-free, calibrated pipeline."

---

### Q6. "The Brier score of 0.067 is barely better than a trivial constant predictor."

**Expected Probe**: *"At an 8% default rate, a model that always predicts 0.08 has a Brier score of about 0.074. Your 0.067 is barely an improvement."*

**Defense**:
> "You are right to notice that. At an 8% default rate, a constant predictor's Brier score is p(1−p) ≈ 0.0742. Our 0.067 after Platt calibration is a **10% improvement** over that baseline.
>
> This reflects the genuine difficulty of the Home Credit task — most features carry modest signal. The Brier improvement is meaningful for calibration quality: our model's probability outputs are more reliable as actual default estimates than an uncalibrated model. We report this honestly: raw pre-calibration Brier was 0.1777 (class-weighted), and calibration improved it to 0.067 on the held-out test set."

---

### Q7. "Your model comparison is unfair. LightGBM trained on 196k rows, Random Forest and XGBoost only on 50k rows."

**Expected Probe**: *"The 0.774 vs 0.754 difference between LightGBM and XGBoost could simply be a data-size effect, not model superiority."*

**Defense**:
> "You are correct. Random Forest and XGBoost retain a deterministic 50,000-row stratified cap due to practical runtime constraints on the development machine. LightGBM and Logistic Regression trained on the complete 196,806-row training partition.
>
> We acknowledge this creates an asymmetric comparison. The performance gap may partially reflect data size rather than model architecture superiority. We document this in our model card. The selection rationale is that LightGBM (balanced) achieved the highest validation PR-AUC and ROC-AUC among candidates. A fully equalized comparison would require all models on the full training set."

---

### Q8. "You said 'SHAP' but what you implemented looks like reference-deviation attribution, not Shapley values."

**Expected Probe**: *"Computing deviation from a reference value is not the same as computing Shapley values. Shapley values require marginalizing over all possible feature coalitions."*

**Defense**:
> "We implemented **exact path-dependent Tree-SHAP** via LightGBM's native `booster_.predict(pred_contrib=True)` API. This uses the Lundberg & Lee (2017) fast tree path enumeration algorithm and returns exact Shapley values in log-odds space — not an approximation or a deviation from a reference point.
>
> For each prediction, the output is a (1, n_features + 1) matrix where the first n columns are exact Shapley contributions per feature and the last column is the base value (expected log-odds). Positive values push predicted risk higher; negative values are protective. This is mathematically faithful to the Shapley axioms: efficiency (contributions sum to the prediction minus base), symmetry, and null player."

---

### Q9. "You have no temporal validation. How reliable are your test metrics?"

**Expected Probe**: *"You split train and test randomly. In real credit scoring, you test on applicants who applied after your training window, not a random sample."*

**Defense**:
> "You are absolutely correct that temporal validation is the gold standard for credit models. The Home Credit public dataset does not include usable application timestamps — we cannot perform an out-of-time split.
>
> We disclose this clearly: our evaluation protocol uses stratified random split (64/16/20), random_state=42, and the test partition is evaluated exactly once after all model, calibration, and threshold decisions are frozen on validation data. We do not claim out-of-time performance. In commercial deployment, temporal validation on the institution's own dated portfolio would be mandatory under model-risk governance."

---

### Q10. "Gain importance is biased toward high-cardinality continuous features. Why use it?"

**Expected Probe**: *"Tree gain importance is known to overestimate importance of continuous features and is not a reliable feature selection method."*

**Defense**:
> "You are correct. LightGBM gain importance can be biased. We report it as a **descriptive global summary** for the model validation dashboard — it answers 'which features the tree splits the most on.' We supplement this with **exact Tree-SHAP local attributions** per applicant, which are Shapley-value faithful and do not share the same bias. Permutation importance on the held-out test set would be the next improvement to add."

---

## Section C: Categorisation & Parser Questions

### Q11. "Keyword categorization is fragile. What about AMZN or abbreviated merchant codes?"

**Expected Probe**: *"Bank narrations often contain merchant abbreviations, truncated names, or codes. Your regex rules will miss them."*

**Defense**:
> "Our categorisation uses a **4-layer defence**: First, structured payment-prefix regex (NACH, NEFT, IMPS, UPI, BBPS) that handle bank-generated codes before any merchant parsing. Second, a merchant normalisation layer covering common Indian abbreviations (AMZN, SWIGGY, ZOMATO, IRCTC, BBPS). Third, transliterated vernacular financial tokens (Kirana, Vetan, Kist, Bima) as a fallback. Fourth, any transaction that matches no rule or matches multiple rules is routed to **Uncertain** — surfaced for the loan officer's audited manual override.
>
> Our ground-truth evaluation on 75 labeled transactions achieved 98.7% accuracy and 0.985 Macro F1. The system is transparent about what it does not know."

---

### Q12. "What about non-English narrations? Tamil, Telugu?"

**Expected Probe**: *"Indian banks have multilingual customers. Your vernacular tokens only cover Hindi transliterations."*

**Defense**:
> "You are right. Our vernacular token layer covers Hindi transliterations (Kirana, Vetan, Kist, Bima, Dukan) as a fallback — these are present in informal UPI payment descriptions. Tamil and Telugu transliterations are not currently covered.
>
> We disclose this explicitly as a scope limitation. In practice, formal Indian bank narrations are mostly structured codes (NEFT/IMPS/UPI/NACH) rather than vernacular free-text, so the structured regex handles the majority. Extending the vocabulary to Tamil and Telugu transliterations is documented as future work."

---

### Q13. "What about scanned image PDFs or mobile screenshots?"

**Expected Probe**: *"Your parser handles digital text PDFs. What happens with a scanned statement?"*

**Defense**:
> "Our scope is **digital native-text PDFs** with an embedded text layer. If pdfplumber extracts no text from an uploaded file — as with a scanned image or screenshot — the system **fails closed**: it rejects the document rather than silently misparsing it.
>
> In production, this is solved by the **RBI Account Aggregator framework**, which delivers bank statement data directly from the bank's API into consented applications — eliminating the need to parse uploaded files entirely and solving both the forgery and scanned-document problems."

---

### Q14. "Can your system detect a forged bank statement?"

**Expected Probe**: *"Your parser accepts any uploaded file. What prevents an applicant from submitting a fabricated statement?"*

**Defense**:
> "Our system checks **internal consistency**, not document authenticity. Specifically: opening balance plus credits minus debits must equal closing balance (mathematical reconciliation), and the running balance must be monotonically consistent. These are checksums on parse correctness.
>
> The system explicitly does not perform document forensics. We state this in the evidence boundary disclaimer. Our cross-document salary verification — comparing detected salary credits against the declared salary slip — adds one layer of cross-document triangulation, but we acknowledge salary slips are also relatively easy to forge. The production answer is the RBI Account Aggregator: consented data delivered directly from the bank, bypassing uploaded documents."

---

## Section D: Privacy, Compliance & Governance

### Q15. "Does SHA-256 hash chaining the full JSON violate the DPDP Act 2023 Right to Erasure?"

**Expected Probe**: *"If you hash PII into the chain, you cannot erase personal data without breaking all subsequent hashes."*

**Defense**:
> "Correct — hashing raw PII would make erasure impossible. That is why we implemented `sanitize_payload_for_chain()`: before hashing, personal identity data (name, Applicant ID, account numbers) is stripped from the payload. The hash chain is computed on the anonymised decision digest, not the full PII record.
>
> The full case record (including PII) is stored in the SQLite row, but the hash chain integrity is maintained on the anonymised payload. This allows compliant erasure of the PII columns without breaking the tamper-detection chain."

---

### Q16. "The SQLite hash chain is tamper-evident, not tamper-proof. Anyone with file access can rewrite everything."

**Expected Probe**: *"If someone has root access to the SQLite file, they can recompute all hashes from scratch."*

**Defense**:
> "You are entirely correct. We specifically claim **tamper-evidence**, not tamper-proof immutability. If any past record is altered in the database, `verify_hash_chain()` immediately detects the broken cryptographic link.
>
> This is an honest scope limitation. The prototype also writes the latest hash to an external anchor file (`data/HEAD_HASH.sha256`) outside SQLite, which raises the bar — both the database and the external file must be consistently altered. In an enterprise system, the head hash would be anchored to an HMAC-signed external ledger or a distributed log (e.g., an immutable audit log service)."

---

### Q17. "Is your PII masking complete?"

**Expected Probe**: *"Your regex masks phone numbers, UPI handles, and account numbers. What about names, PAN, and Aadhaar?"*

**Defense**:
> "Our current masking covers phone numbers, UPI/email handles, and account numbers via regex in `safe_export_csv()`. Names, PAN, and Aadhaar are not currently detected and masked by the export function.
>
> We acknowledge this is best-effort. The system relies on the fact that most bank statement CSVs do not contain raw PAN or Aadhaar numbers in transaction narration fields. The DPDP Act compliance focus is on the immutable hash chain, where PII is explicitly stripped before hashing. Full NLP-based named entity recognition for PAN/Aadhaar detection is documented as a production requirement."

---

### Q18. "Age and gender are demographic attributes. Does your model discriminate?"

**Expected Probe**: *"DAYS_BIRTH is equivalent to age and is used in the model. This could violate anti-discrimination regulations."*

**Defense**:
> "DAYS_BIRTH (age) is explicitly excluded from the model's training feature set. Gender (CODE_GENDER) is also excluded. These are reserved for descriptive fairness diagnostics only.
>
> However, we acknowledge the **proxy discrimination** risk: DAYS_EMPLOYED and other features can be correlated with age. A full fairness audit would require computing AUC, flag rate, and recall broken down by age bands and gender on the held-out test set — Fairlearn can do this efficiently. We document this as a required step before any production deployment. The DAYS_EMPLOYED = 365243 anomaly (pensioners encoded this way by Home Credit) is handled by treating it as a missing value / separate category."

---

## Section E: Design & Future Work

### Q19. "Why not train an end-to-end neural network on the uploaded bank statements?"

**Expected Probe**: *"Deep learning would extract patterns from transactions automatically. Why constrain yourself to rules?"*

**Defense**:
> "Three reasons:
> 1. **Regulatory**: Adverse-action explanation mandates under RBI Fair Lending Directions require explainability. A neural network's decision cannot be reliably explained to a rejected applicant.
> 2. **Data**: We have no ground-truth default labels linked to the uploaded statement CSV data. Without labelled outcomes, a supervised model cannot be trained and evaluated honestly.
> 3. **Transferability**: Training on one institution's statements and deploying on another's would require rigorous out-of-time, out-of-distribution validation that is beyond prototype scope.
>
> The right path, documented in `docs/statement_ml_bridge.md`, is to first collect consented, anonymised historical loan data with verified default outcomes via the AA framework — then train a behavioural ML model with temporal splits and appropriate fairness diagnostics."

---

### Q20. "The 20% default risk threshold seems arbitrary. How did you choose it?"

**Expected Probe**: *"Why 20%? That is 2.5× the base rate. Any threshold near it would also be 'reasonable'."*

**Defense**:
> "The 0.20 threshold is a **policy parameter**, not a learned value. It is versioned, configurable, and justified from the threshold analysis on validation data.
>
> At the base default rate of 8.07%, 0.20 represents approximately 2.5× the base rate — a standard heuristic for officer-review alert thresholds in retail credit risk. We present the full threshold sweep table to the officer: at 0.20 threshold, final-test recall is 33.3% and precision is 30.5%, flagging 8.8% of applicants. At 0.30, recall falls to 14.9% but precision rises to 41.0%. The choice of which threshold to use in production is a business policy decision that the institution makes based on their risk appetite, not a data-science decision."

---

## Section F: Rapid-Fire Numbers Reference

| Question | Answer |
|----------|--------|
| ROC-AUC | 0.774 (95% CI: 0.767–0.781) |
| PR-AUC | 0.266 (~3.3× lift, base ≈ 0.081) |
| Brier Score (calibrated) | 0.067 |
| Brier Score (raw / pre-calibration) | 0.1777 |
| Trivial constant predictor Brier | ~0.074 at 8% default rate |
| Alert Threshold | 0.20 (policy parameter, ~2.5× base rate) |
| At 0.20: Recall | 33.3% |
| At 0.20: Precision | 30.5% |
| At 0.20: Flags | 8.8% of applicants |
| Default base rate | 8.07% |
| Training rows (LightGBM) | 196,806 |
| Training rows (RF, XGBoost) | 50,000 (capped) |
| Final test set | 61,503 applicants |
| Affordability score range | 0 – 100 |
| Approve band | ≥ 70 |
| Manual review band | 45 – 69 |
| Decline band | < 45 |
| Salary slip tolerance | 15% |
| EMI burden cap (FOIR) | 50% (industry standard) |
| Categorisation accuracy (fixture) | 98.7% |
| Categorisation Macro F1 | 0.985 |
| Transaction NLP CV Accuracy (Tier 1) | 100% (1,025 samples across 18 classes) |
| Transaction NLP Macro F1 (Tier 1) | 1.000 |
| Behavioral Clustering (Tier 2) | k=4 Spending Personas |
| Anomaly Contamination (Tier 2) | 5% (Isolation Forest, 150 estimators) |
| Policy stability flip rate | < 5% (Monte Carlo, 1,000 trials) |
| Pytest tests passing | 71 |
| Model file size | ~7 MB (joblib bundle) |
