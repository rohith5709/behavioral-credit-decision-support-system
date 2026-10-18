# B.Tech Capstone Viva Defense Cheat Sheet
**Project**: Behavioral Credit Decision Support System using Financial Document Analysis  
**Team**: Adharsh S (23BDS0029), Gowtham Kumar D (23BDS0186), Rohith S M (23BDS0025) | **Faculty Guide**: Dr. Viswanathan A

---

## 1. Golden Rule for the Viva: "Concede First, Pivot Second"
> Never bluff. In credit risk, a calm concession of scope boundaries scores maximum marks because model governance is about knowing your boundaries.
> **The Formula**: *"You are completely right, Sir/Ma'am. In our design, [Concede Limitation]. That is why we deliberately implemented [Technical Mitigation], and why [Architectural Reason]."*

---

## 2. Reconciled Metrics & Numbers (Know These Cold)

| Metric | Value | What to Say When Asked |
|---|---|---|
| **ROC-AUC** | **0.774** | Held-out test set performance on 61,503 applicants. |
| **PR-AUC** | **0.266** | Baseline default prevalence is 8.07%. A PR-AUC of 0.266 represents a **3.3× lift over random chance**, consistent with published benchmarks. |
| **Brier Score (Raw)** | **0.1777** | Raw class-weighted probability output before calibration. |
| **Brier Score (Calibrated)** | **0.067** | Achieved via **Platt Scaling (Logistic Sigmoidal Calibration)** on the validation set. (Note: A trivial constant predictor has a Brier score of $p(1-p) \approx 0.074$; our 0.067 reflects genuine calibration refinement). |
| **Default Threshold** | **0.20** | **Officer-Review Alert Threshold**, not an automatic rejection rule. At 0.20, recall is 33.3% and precision is 30.5%. |
| **Affordability Score** | **0 – 100** | Transparent policy score based on 8 components. Thresholds: $\ge 70$ (Approve Band), $45-69$ (Manual Review Band), $< 45$ (Decline Band). |
| **DTI / FOIR Cap** | **50%** | Prevailing retail banking industry standard (not an RBI statutory mandate). |
| **Salary Tolerance** | **15%** | Cross-document mismatch cap between declared salary slip and detected statement credits. |

---

## 3. The 6 Critical Defense Scripts

### Probe 1: "Why call it AI when the bank statement part is just rules?"
> **The Defense**:
> *"In enterprise credit underwriting, running an unconstrained black-box ML model directly on raw cash-flows violates regulatory adverse-action mandates (such as RBI Fair Lending Directions). Banks must explain exactly why credit was declined. We deliberately engineered a **Dual-Pillar architecture**: Pillar 1 is an explainable, deterministic cash-flow engine that prevents algorithmic hallucination, while Pillar 2 uses a calibrated LightGBM model for default probability. They unite in our 2×2 decision matrix."*

### Probe 2: "Home Credit is not Indian data. And mapping CIBIL to EXT_SOURCE is an unverified assumption."
> **The Defense**:
> *"We concede that Home Credit is a European consumer finance dataset and that mapping CIBIL (300–900) to EXT_SOURCE percentiles is a **monotonic heuristic proxy**, not an empirical equivalence. Home Credit serves as a **methodological benchmark** to prove the pipeline: feature engineering, Platt scaling, threshold optimization, and gain attribution. In commercial deployment, Pillar 2 would be retrained on the lending institution's historical bureau portfolio. The proxy exists so the officer can explore dual-pillar divergence in the prototype."*

### Probe 3: "Keyword categorization is fragile. What about AMZN or non-English narrations?"
> **The Defense**:
> *"Our categorization uses a 4-layer defense: First, regex tokenization for standard banking payment prefixes (NACH, NEFT, IMPS, UPI, BBPS); second, merchant normalization (AMZN, SWIGGY, ZOMATO); third, transliterated vernacular financial tokens (Kirana, Vetan, Kist, Bima) as a fallback layer; and fourth, an explicit **Transfer Safeguard** that detects self-transfers and wallet top-ups to prevent double-counting income. Any ambiguous transaction is flagged as 'Uncertain' and routed to the loan officer for audited manual override."*

### Probe 4: "You have no default labels for bank statements. How do you know the affordability score is valid?"
> **The Defense**:
> *"In banking, financial institutions do not deliberately approve unaffordable loans to collect default labels. Therefore, we validate affordability through **construct validity and policy robustness**: (1) mathematical amortization matching 50% FOIR caps, (2) cross-document verification with salary slips (15% tolerance), (3) sensitivity testing under economic shock scenarios (-20% income, +10% expenses, +2% interest), and (4) mathematical balance reconciliation ($Opening + Credits - Debits = Closing$) as a checksum against parsing errors."*

### Probe 5: "Your SQLite hash chain is tamper-evident, not tamper-proof."
> **The Defense**:
> *"That is correct, Sir/Ma'am. Anyone with direct root write-access to the SQLite file could recalculate the hashes. That is why we specifically claim **tamper-evidence**, not tamper-proof immutability. If any past record or decision is altered directly in the database, our `verify_hash_chain()` function detects the broken cryptographic link immediately. In an enterprise system, the head hash would be anchored externally via an HMAC key or an external ledger."*

### Probe 6: "The 2×2 matrix uses EMI in both pillars. Isn't that double-counting?"
> **The Defense**:
> *"There is partial overlap in debt information, but the two pillars evaluate fundamentally different dimensions: Pillar 1 measures **cash-flow liquidity** (can the borrower's monthly cash surplus absorb another EMI today?), whereas Pillar 2 measures **historical willingness to repay** (has the borrower defaulted across credit bureaus historically?). The primary value of the matrix is detecting **divergence cases** (Quadrants 2 & 3)—for example, an applicant with a clean CIBIL who has over-leveraged their bank account."*

---

## 4. Rapid-Fire Technical FAQ

- **Q: What about scanned image statements or mobile screenshots?**  
  *A*: *"Our prototype scope is digital text PDFs and CSVs with fail-closed behavior. If a file has no extractable text layer, it is safely rejected rather than misparsed. In production, this is solved by the RBI Account Aggregator (AA) framework."*
- **Q: Does hash-chaining the full JSON violate the DPDP Act 2023 (Right to Erasure)?**  
  *A*: *"A full production chain would hash anonymized transaction digests rather than plaintext PII, allowing personal data redaction without breaking block integrity."*
- **Q: Why LightGBM over Random Forest or XGBoost?**  
  *A*: *"LightGBM balanced achieved the highest PR-AUC (0.251 on validation, 0.266 on final test) and ROC-AUC (0.774), while executing in 15 seconds compared to significantly higher training overhead for Random Forest."*
- **Q: Did you do SHAP?**  
  *A*: *"We extract global feature gain from the LightGBM booster and use **reference-deviation risk factor attribution** for local explanations, translating quantitative deviations into plain-English risk drivers vs protective factors."*
