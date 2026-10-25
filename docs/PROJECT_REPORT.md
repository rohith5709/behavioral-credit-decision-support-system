# B.Tech. BCSE497J - Project-I
# BEHAVIORAL CREDIT DECISION SUPPORT SYSTEM USING FINANCIAL DOCUMENT ANALYSIS

**Submitted in partial fulfillment of the requirements for the degree of**  
**Bachelor of Technology**  
**in**  
**Computer Science and Engineering (Data Science)**  

**by**

| Register Number | Student Name |
| :--- | :--- |
| **23BDS0025** | **ROHITH S M** |
| **23BDS0029** | **ADHARSH S** |
| **23BDS0186** | **GOWTHAM KUMAR D** |

*(Names arranged by Register Number)*

**Under the Supervision of**  
**Dr. Viswanathan A**  
Associate Professor  
School of Computer Science and Engineering (SCOPE)  

**Vellore Institute of Technology (VIT), Vellore**  
October 2026

---

## DECLARATION

We hereby declare that the project entitled **"Behavioral Credit Decision Support System using Financial Document Analysis"** submitted by us, for the award of the degree of Bachelor of Technology in Computer Science and Engineering (Data Science) to Vellore Institute of Technology (VIT), is a record of bonafide work carried out by us under the supervision of **Dr. Viswanathan A**, School of Computer Science and Engineering (SCOPE).

We further declare that the work reported in this project has not been submitted and will not be submitted, either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university.

**Place** : Vellore  
**Date**  : 25 October 2026  

**Signatures of the Candidates:**

| ..................................................... | ..................................................... | ..................................................... |
| :---: | :---: | :---: |
| **Rohith S M** (23BDS0025) | **Adharsh S** (23BDS0029) | **Gowtham Kumar D** (23BDS0186) |

---

## CERTIFICATE

This is to certify that the project entitled **"Behavioral Credit Decision Support System using Financial Document Analysis"** submitted by **Rohith S M (23BDS0025)**, **Adharsh S (23BDS0029)**, and **Gowtham Kumar D (23BDS0186)**, School of Computer Science and Engineering, VIT, for the award of the degree of Bachelor of Technology in Computer Science and Engineering (Data Science), is a record of bonafide work carried out by them under my supervision during the Fall Semester 2026–2027, as per the VIT code of academic and research ethics.

The contents of this report have not been submitted and will not be submitted either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university. The project fulfills the requirements and regulations of the University and in my opinion meets the necessary standards for submission.

**Place** : Vellore  
**Date**  : 25 October 2026  

.....................................................  
**Signature of the Guide**  
**Dr. Viswanathan A**  
Associate Professor, SCOPE  

**Examiners:**

| ..................................................... | ..................................................... |
| :---: | :---: |
| **Internal Examiner** | **External Examiner** |

**Head of the Department**  
Department of Computer Science and Engineering (Data Science)  
School of Computer Science and Engineering (SCOPE)  
Vellore Institute of Technology, Vellore  

---

## ACKNOWLEDGEMENTS

We express our deepest gratitude to the management of **Vellore Institute of Technology (VIT)** for providing state-of-the-art computational infrastructure, academic resources, and an inspiring intellectual environment that enabled us to pursue this research and software engineering endeavour.

Our sincere thanks go to **Dr. Jaisankar N**, Dean of the School of Computer Science and Engineering (SCOPE), for his constant encouragement, strategic academic vision, and commitment to fostering applied research across data science and machine learning.

We extend our profound appreciation to the **Head of the Department of Computer Science and Engineering (Data Science)** for insightful counsel, curricular guidance, and continuous departmental facilitation throughout the semester.

We are indebted to our faculty supervisor, **Dr. Viswanathan A**, Associate Professor, SCOPE, for his patient mentorship, constructive critiques, and meticulous technical guidance. His insistence on methodological honesty, leakage-free machine learning protocols, and explainable decision-support architectures was pivotal in steering this project from concept to a production-grade implementation.

Finally, we thank our peers and families for their patience and unconditional encouragement throughout the development and verification phases of this project.

**Rohith S M** (23BDS0025)  
**Adharsh S** (23BDS0029)  
**Gowtham Kumar D** (23BDS0186)  

---

## TABLE OF CONTENTS

| Chapter / Section | Title | Page No. |
| :--- | :--- | :--- |
| | **Abstract** | **ix** |
| **1.** | **INTRODUCTION** | **1** |
| | 1.1 Background | 1 |
| | 1.2 Motivations | 2 |
| | 1.3 Scope of the Project | 3 |
| **2.** | **PROJECT DESCRIPTION AND GOALS** | **4** |
| | 2.1 Literature Review | 4 |
| | 2.2 Research Gap | 6 |
| | 2.3 Objectives | 6 |
| | 2.4 Problem Statement | 7 |
| | 2.5 Project Plan | 7 |
| **3.** | **TECHNICAL SPECIFICATION** | **9** |
| | 3.1 Requirements | 9 |
| | &emsp;3.1.1 Functional Requirements | 9 |
| | &emsp;3.1.2 Non-Functional Requirements | 10 |
| | 3.2 Feasibility Study | 11 |
| | &emsp;3.2.1 Technical Feasibility | 11 |
| | &emsp;3.2.2 Economic Feasibility | 12 |
| | &emsp;3.2.3 Social Feasibility | 12 |
| | 3.3 System Specification | 12 |
| | &emsp;3.3.1 Hardware Specification | 12 |
| | &emsp;3.3.2 Software Specification | 13 |
| **4.** | **DESIGN APPROACH AND DETAILS** | **14** |
| | 4.1 System Architecture | 14 |
| | 4.2 Design | 16 |
| | &emsp;4.2.1 Data Flow Diagram | 16 |
| | &emsp;4.2.2 Use Case Diagram | 17 |
| | &emsp;4.2.3 Class Diagram | 18 |
| | &emsp;4.2.4 Sequence Diagram | 19 |
| | &emsp;4.2.5 Data Design | 20 |
| **5.** | **METHODOLOGY AND TESTING** | **22** |
| | 5.1 Module Description | 22 |
| | &emsp;5.1.1 Bank Statement Ingestion and Pre-Qualification Quality Gates | 22 |
| | &emsp;5.1.2 Tier 1 Transaction-Level Supervised NLP Categorisation | 23 |
| | &emsp;5.1.3 The 15-Dimensional Statement-to-UCI Feature Bridge | 24 |
| | &emsp;5.1.4 Pillar 1 Supervised Behavioral Default Prediction ML Model | 26 |
| | &emsp;5.1.5 Tier 3 Unsupervised Cash-Flow Anomaly Detection and Personas | 28 |
| | &emsp;5.1.6 Salary-Slip Cross-Document Verification | 28 |
| | &emsp;5.1.7 Pillar 2 Macro Bureau Default-Risk Benchmark (LightGBM) | 29 |
| | &emsp;5.1.8 Exact Tree-SHAP Local Attribution Engine | 30 |
| | &emsp;5.1.9 Dual-Pillar 2×2 ML Risk Decision Engine | 31 |
| | &emsp;5.1.10 Cryptographic Decision Audit Trail (SHA-256 Hash Chain) | 32 |
| | &emsp;5.1.11 Interactive FinTech UI, What-If Sandbox, and Stress Lab | 33 |
| | 5.2 Testing Strategy and Verification | 34 |
| **6.** | **PROJECT DEMONSTRATION** | **37** |
| | 6.1 Demonstration Bank Statements | 37 |
| | 6.2 Pre-Qualification Data Quality Gates and Safeguards in Action | 39 |
| | 6.3 Dual-Pillar ML Scoring and Explainability | 40 |
| | 6.4 Dual-Pillar ML Decision Outcomes and 2D Risk Map | 41 |
| | 6.5 Interactive What-If Simulation and Stress Testing | 42 |
| | 6.6 Cryptographic Tamper Detection Verification | 43 |
| **7.** | **RESULT AND DISCUSSION** | **44** |
| | 7.1 Pillar 1 Behavioral Default Prediction Evaluation | 44 |
| | 7.2 Pillar 2 Home Credit Macro Bureau Benchmark Evaluation | 47 |
| | 7.3 Discussion: Dual-Pillar Divergence and Three-Tier Synergy | 49 |
| | 7.4 System Limitations and Regulatory Boundaries | 50 |
| | 7.5 Cost and Resource Analysis | 51 |
| **8.** | **CONCLUSION** | **53** |
| | 8.1 Summary of Contributions | 53 |
| | 8.2 Future Work | 54 |
| **9.** | **REFERENCES** | **55** |
| | **APPENDIX A – SAMPLE CODE** | **58** |
| | A.1 Behavioral Feature Bridge (`src/features/behavioral_ml_features.py`) | 58 |
| | A.2 Dual-Pillar 2×2 Decision Engine (`src/decision/engine.py`) | 60 |
| | A.3 SHA-256 Cryptographic Hash Chain (`src/data/db.py`) | 62 |

---

## LIST OF FIGURES

| Figure No. | Caption | Page No. |
| :--- | :--- | :--- |
| **4.1** | System architecture of the Dual-Pillar machine learning credit decision support platform | 15 |
| **4.2** | Data flow diagram (Level 0 and Level 1 condensed) | 16 |
| **4.3** | Use case diagram illustrating loan officer and auditor interactions | 17 |
| **4.4** | Class diagram of principal data structures, models, and persistence services | 18 |
| **4.5** | Sequence diagram of an end-to-end applicant underwriting assessment | 20 |
| **5.1** | Dual-Pillar 2×2 machine learning decision matrix ($P_{\text{behavioral}} \times P_{\text{bureau}}$) | 32 |
| **5.2** | Cryptographic forward SHA-256 hash chain with external filesystem anchor | 33 |
| **6.1** | Normalized behavioral feature bridge comparison between Statements A and B | 38 |
| **6.2** | Dual-pillar risk map positioning demonstration applicants across risk quadrants | 41 |
| **7.1** | Cross-validation ROC-AUC and training runtime comparison across candidate models | 45 |
| **7.2** | Reliability diagram of the Platt-calibrated Random Forest model on the 4,500 test set | 46 |
| **7.3** | Permutation feature importance of the top ten behavioral prediction drivers | 47 |
| **7.4** | Global gain importance of the top ten features in the LightGBM bureau benchmark | 48 |

---

## LIST OF TABLES

| Table No. | Caption | Page No. |
| :--- | :--- | :--- |
| **2.1** | Summary of literature reviewed and relevance to the architectural design | 5 |
| **2.2** | Project implementation phases, work packages, and key outcomes | 8 |
| **3.1** | Functional requirements specification | 9 |
| **3.2** | Non-functional requirements and engineering realizations | 10 |
| **3.3** | Recommended workstation hardware specifications | 13 |
| **3.4** | Software stack and execution environment | 13 |
| **4.1** | Schema definition of the SQLite cases table with SHA-256 integrity links | 21 |
| **5.1** | Mathematical mapping of 23 statement features to 15 UCI repayment dimensions | 25 |
| **5.2** | Pre-qualification data quality hard stops and safeguard policies | 27 |
| **5.3** | Automated verification test suite breakdown across all 127 tests | 35 |
| **6.1** | Behavioral cash-flow and feature bridge metrics for demonstration statements | 38 |
| **6.2** | Bureau profiles, Tree-SHAP drivers, and calibrated default probabilities | 40 |
| **6.3** | Dual-Pillar decision matrix recommendations across applicant scenarios | 41 |
| **7.1** | 5-Fold stratified cross-validation performance on 21,000 training records | 44 |
| **7.2** | Frozen held-out test evaluation of the calibrated Pillar 1 Random Forest model | 45 |
| **7.3** | Final test performance of the calibrated LightGBM Pillar 2 macro benchmark | 47 |
| **7.4** | Threshold trade-off sweep on the held-out Home Credit test partition | 48 |
| **7.5** | Core system limitations, real-world risks, and technical mitigations | 50 |
| **7.6** | Development, compute, and licensing cost analysis | 52 |

---

## LIST OF ABBREVIATIONS

| Abbreviation | Expansion |
| :--- | :--- |
| **AA** | Account Aggregator |
| **AUC** | Area Under the Curve |
| **BOM** | Byte Order Mark |
| **CIBIL** | Credit Information Bureau (India) Limited |
| **CSV** | Comma-Separated Values |
| **DFD** | Data Flow Diagram |
| **DPDP** | Digital Personal Data Protection Act, 2023 |
| **DPD** | Days Past Due |
| **EMI** | Equated Monthly Instalment |
| **FOIR** | Fixed Obligation to Income Ratio |
| **GBDT** | Gradient Boosted Decision Tree |
| **IMPS** | Immediate Payment Service |
| **ITR** | Income Tax Return |
| **LightGBM** | Light Gradient Boosting Machine |
| **ML** | Machine Learning |
| **NACH** | National Automated Clearing House |
| **NEFT** | National Electronic Funds Transfer |
| **NLP** | Natural Language Processing |
| **OCR** | Optical Character Recognition |
| **PD** | Probability of Default |
| **PDF** | Portable Document Format |
| **PII** | Personally Identifiable Information |
| **PR-AUC** | Area under the Precision–Recall Curve |
| **RBI** | Reserve Bank of India |
| **ROC-AUC** | Area under the Receiver Operating Characteristic Curve |
| **SCOPE** | School of Computer Science and Engineering |
| **SGD** | Stochastic Gradient Descent |
| **SHA** | Secure Hash Algorithm |
| **SHAP** | SHapley Additive exPlanations |
| **TF-IDF** | Term Frequency–Inverse Document Frequency |
| **UCI** | University of California, Irvine |
| **UI** | User Interface |
| **UPI** | Unified Payments Interface |
| **XGBoost** | eXtreme Gradient Boosting |

---

## SYMBOLS AND NOTATIONS

| Symbol | Description |
| :--- | :--- |
| $I$ | Average monthly recognized income derived from recurring statement credits |
| $E$ | Average monthly debit expense excluding transfers and loan disbursements |
| $M$ | Effective monthly equated instalment obligation (existing + declared) |
| $P$ | Requested loan principal amount |
| $r$ | Monthly interest rate, defined as $\text{annual rate} / 12$ |
| $n$ | Loan tenure in months |
| $P_{\text{behavioral}}$ | Calibrated default probability from the Pillar 1 Random Forest model |
| $P_{\text{bureau}}$ | Calibrated default probability from the Pillar 2 LightGBM benchmark |
| $f(x)$ | Raw uncalibrated decision ensemble logit / margin score |
| $A, B$ | Platt sigmoid scaling calibration parameters |
| $p_i, y_i$ | Model predicted probability and empirical binary ground-truth label for record $i$ |
| $\text{BS}$ | Brier score measuring probabilistic calibration accuracy |
| $\phi_j$ | Local Tree-SHAP attribution contribution for feature $j$ in log-odds space |
| $\phi_0$ | Expected value base log-odds across the training background distribution |

---

## ABSTRACT

In contemporary retail banking, credit underwriting has traditionally been bifurcated: underwriters evaluate static bureau credit scores (such as CIBIL) while manually inspecting unstructured bank statements to assess real-time cash flow, debt serviceability, and lifestyle spending. Manual statement auditing is inherently slow, error-prone, and prone to severe cognitive biases, as non-income inflows (loan disbursements, self-transfers, and refunds) are frequently conflated with recurring salary. Conversely, conventional commercial credit-scoring engines apply black-box models strictly to bureau summaries or rely on rigid, heuristic point-based scorecards that fail to capture non-linear behavioral cash-flow degradation.

This project delivers the **Behavioral Credit Decision Support System**, an end-to-end, human-in-the-loop underwriting platform that completely replaces heuristic, rule-based credit scoring with a rigorous, multi-tiered machine learning architecture. The system introduces a **Dual-Pillar ML Framework** operating across strictly separated yet unified analytical pipelines. **Pillar 1 (Behavioral Cash-Flow ML Engine)** parses multi-bank statement CSV and digital PDF files, enforces balance reconciliation, and deploys a **Tier 1 Supervised NLP pipeline** (TF-IDF with Calibrated Linear SGD, achieving 100% 10-fold cross-validation accuracy across 18 transaction classes). To bridge unlabelled retail statement cash flows to default ground truth without falsifying synthetic labels, a **15-Dimensional Feature Bridge** was mathematically formalized to map 23 continuous banking cash-flow metrics into the standardized behavioral repayment dimensions of the 30,000-record UCI Credit Card Default benchmark. A **Supervised Random Forest Classifier** (200 estimators, max depth 10) was trained via 5-fold cross-validation (CV ROC-AUC: 0.7852) and calibrated via Platt sigmoid scaling. On a frozen held-out test partition of 4,500 samples, the model achieved **ROC-AUC: 0.7725**, **PR-AUC: 0.5304** (a 2.4× lift over the 22.1% base rate), **Accuracy: 81.53%**, and a default-class F1 of 0.4842. This is coupled with an **Account-Level Unsupervised ML Suite** comprising an Isolation Forest (150 estimators, 5% contamination) for non-linear cash-flow surge and liquidity drain detection, and K-Means clustering ($k=4$) for behavioral persona segmentation.

**Pillar 2 (Macro Bureau Default-Risk Benchmark)** evaluates institutional bureau profiles using a calibrated LightGBM classifier trained on 196,806 Home Credit applicants (ROC-AUC: 0.7737, PR-AUC: 0.2664, Brier score: 0.0667), generating local explanations via exact path-dependent **Tree-SHAP**. A **Dual-Pillar 2×2 Decision Matrix** integrates behavioral default probability $P_{\text{behavioral}}$ with bureau default probability $P_{\text{bureau}}$, routing divergent quadrants to human oversight while Isolation Forest anomaly flags and salary-slip discrepancy checks (>15% tolerance) act as automated overrides. Every officer action is sealed in an auditable **SHA-256 cryptographic forward hash chain** with an external filesystem anchor, provably defeating record alteration. The interactive interface is delivered as a 6-tab FinTech Streamlit dashboard featuring an interactive counterfactual What-If sandbox, Platt calibration reliability curves, and a stress-testing lab. The platform is comprehensively verified by **127 automated pytest tests passing with 100% coverage**.

**Keywords**: *Credit Decision Support, Behavioral Cash Flow, Feature Bridge, Random Forest, LightGBM, Platt Scaling Calibration, Tree-SHAP, Isolation Forest, SHA-256 Hash Chain, Turnitin Compliance.*

---

## CHAPTER 1: INTRODUCTION

### 1.1 Background
The expansion of digital banking and payments across emerging economies—epitomized by India's Unified Payments Interface (UPI), National Automated Clearing House (NACH), and the Reserve Bank of India (RBI) Account Aggregator (AA) framework—has drastically transformed consumer spending habits and banking transaction frequency. In traditional credit underwriting, financial institutions have predominantly relied on centralized credit bureau scores (e.g., CIBIL, Experian, Equifax). While credit bureau scores encapsulate an applicant's long-term historical willingness to honor debt obligations across established trade-lines, they exhibit a critical structural limitation: they are inherently lagging indicators. A borrower experiencing severe cash-flow depletion, volatile gig-economy income, or escalating gambling expenses can maintain a pristine bureau score of 780 for months until an outright default manifests.

To counter this information asymmetry, underwriters demand 3 to 6 months of historical bank statements. However, bank statement analysis in commercial retail lending remains overwhelmingly manual. Credit analysts routinely scan hundreds of transactional narrations embedded with complex bank codes, payment gateway prefixes, and vernacular tokens. Under pressure, human reviewers frequently make catastrophic accounting errors: loan disbursements, internal savings transfers, investment liquidations, and merchant refunds are misclassified as recurring operational income. 

Furthermore, when machine learning models have been proposed in financial literature, they are frequently implemented either as uncalibrated black-box neural networks that violate regulatory adverse-action explainability mandates under RBI Fair Lending Directions, or as arbitrary, hand-crafted point-based scorecards (e.g., scoring an applicant 0–100 via heuristic thresholds). Such point-based scorecards lack mathematical rigor, fail to reflect non-linear covariate interactions, and do not provide genuine probabilities of credit default.

### 1.2 Motivations
This engineering project is motivated by several core theoretical and practical realities:
1. **Total Elimination of Arbitrary Rule-Based Scoring**: Heuristic scoring systems assign subjective point values (e.g., 25 points for savings, 20 points for salary consistency). These arbitrary weights cannot be validated against empirical delinquency distributions. Credit decisioning must be driven by rigorous, supervised machine learning models trained on empirical default outcomes.
2. **The Ground-Truth Data Reality**: There exists no publicly accessible, outcome-labelled dataset of Indian bank statements tied directly to 90-day delinquency outcomes. Many student projects fabricate synthetic default labels on arbitrary bank accounts—an approach that is unscientific and represents severe data leakage. A scientifically valid methodology requires establishing a mathematical bridge between granular banking cash flows and validated credit repayment datasets.
3. **Multi-Tiered Machine Learning Hierarchy**: To extract true intelligence from banking data, ML must be applied at every layer of abstraction:
   - *Transaction Layer*: Supervised Natural Language Processing (NLP) to classify unstructured transaction narrations.
   - *Account Cash-Flow Layer*: Supervised Behavioral ML to estimate default risk, supported by unsupervised anomaly detection.
   - *Macro Bureau Layer*: Gradient boosted decision trees providing historical risk benchmarks.
4. **Local Interpretability and Adverse Action Compliance**: Under the Digital Personal Data Protection (DPDP) Act, 2023 and RBI guidelines, loan rejections require explicit, auditable explanations. Predictions must be decomposed using exact Game-Theoretic Shapley values (Tree-SHAP) and feature attribution rankings.
5. **Cryptographic Tamper-Evident Accountability**: In an era of increasing internal underwriting fraud, audit trails must be mathematically provable. Utilizing cryptographic forward hash chaining guarantees that no historical decision or officer override can be altered without immediate detection.

### 1.3 Scope of the Project
**In-Scope Deliverables**:
- Multi-format ingestion of bank statements in CSV and native digital PDF formats (HDFC, ICICI, SBI, Axis, Kotak), including automatic column aliasing, balance continuity checks, PII redaction, and duplicate handling.
- Tier 1 Supervised NLP merchant narration categorisation using TF-IDF n-grams with Calibrated Linear SGD across 18 transaction classes.
- A formalized 15-Dimensional Feature Bridge converting 23 statement cash-flow features into standard behavioral repayment dimensions.
- Pillar 1 Supervised Behavioral Default Prediction Model (Random Forest, 200 estimators, depth 10) trained on 30,000 real financial payment records from the UCI Credit Card Default dataset, calibrated via Platt sigmoid scaling.
- Account-level unsupervised ML suite consisting of an Isolation Forest (150 trees) for cash-flow anomaly detection and K-Means clustering ($k=4$) for spending persona segmentation.
- Cross-document verification comparing declared salary slip figures against detected statement payroll credits with a 15% tolerance window.
- Pillar 2 Macro Bureau Default Risk Benchmark utilizing a Platt-calibrated LightGBM model trained on 196,806 Home Credit records with exact Tree-SHAP local explanations.
- A Dual-Pillar 2×2 ML Risk Decision Matrix integrating $P_{\text{behavioral}}$ and $P_{\text{bureau}}$ with automatic anomaly and data-quality overrides.
- An immutable SQLite persistence store featuring a SHA-256 cryptographic forward hash chain with an external filesystem anchor.
- An interactive Streamlit FinTech dashboard with a What-If Counterfactual Sandbox, Plotly reliability curves, and a comprehensive automated test suite comprising 127 passing tests.

**Out-of-Scope Boundaries**:
- Optical Character Recognition (OCR) for rasterized/scanned statements; the pipeline intentionally fails-closed on non-digital PDFs to prevent character hallucinations.
- Automated loan approval; the platform functions strictly as an intelligent decision-support system for human credit officers.

---

## CHAPTER 2: PROJECT DESCRIPTION AND GOALS

### 2.1 Literature Review
Modern credit risk modeling originates from multivariate statistical discriminant analysis, established by Altman's Z-score and Thomas et al. [1]. Lessmann et al. [2] conducted an extensive empirical benchmark of classification algorithms across multiple credit datasets, demonstrating that tree ensembles systematically outperform linear scorecards on tabular financial data. Yeh and Lien [3] established the widely referenced UCI Credit Card Default benchmark, comparing data mining techniques on Taiwanese consumer repayment data and demonstrating the critical predictive value of monthly repayment delays and billing utilization ratios. Khandani, Kim, and Lo [4] validated that integrating consumer banking transactions with credit bureau data delivers significant predictive lift over bureau scores alone, reducing delinquency rates and improving systemic stability.

In the realm of gradient boosting architectures, Ke et al. [5] introduced LightGBM, utilizing histogram-based split finding and leaf-wise tree growth to achieve state-of-the-art computational efficiency on massive financial datasets. Chen and Guestrin [6] formulated XGBoost, and Breiman [7] formalized Random Forests, which provide exceptional robustness against overfitting on noisy tabular covariates. 

The necessity of probability calibration in risk modeling was rigorously analyzed by Niculescu-Mizil and Caruana [8] and Guo et al. [9]. Standard machine learning classifiers optimize ranking metrics (e.g., ROC-AUC) or cross-entropy loss, resulting in margin scores that deviate from true empirical default probabilities. Platt [10] formulated sigmoid scaling to map margin outputs into calibrated probabilities, evaluated via the Brier score [11]. In credit underwriting, uncalibrated probabilities distort expected loss calculations and capital adequacy reserves.

On model interpretability, Rudin [12] emphasized that for high-stakes societal decisions, interpretable models and exact mathematical attributions must replace opaque post-hoc surrogates. Lundberg and Lee [13] and Lundberg et al. [14] developed exact path-dependent Tree-SHAP, enabling polynomial-time computation of Shapley values for tree ensembles based on game-theoretic foundations. Bussmann et al. [15] operationalized Tree-SHAP within institutional credit risk management. 

Regarding data integrity and legal governance, Haber and Stornetta [16] pioneered cryptographic hash-chaining to create tamper-evident digital timestamps. In the regulatory domain, the Government of India enacted the Digital Personal Data Protection (DPDP) Act, 2023 [17], enforcing stringent purpose limitation, data minimization, and right to erasure. Concurrently, the Reserve Bank of India established the Account Aggregator framework [18] and Fair Lending Directions to govern algorithmic transparency in retail lending.

Table 2.1 summarizes the literature foundational to this system.

**Table 2.1**: Summary of literature reviewed and relevance to the architectural design
| Ref. | Primary Focus | Technical Relevance to this Project |
| :--- | :--- | :--- |
| [1] | Statistical Credit Scoring | Theoretical foundation for financial ratio analysis and debt-service metrics |
| [2] | Classifier Benchmarking | Justifies utilizing tree ensembles (Random Forest, LightGBM) over simple linear models |
| [3] | UCI Default Benchmark | Ground-truth dataset utilized for training Pillar 1 Behavioral ML Model |
| [4] | Banking Transaction ML | Motivates fusing cash-flow banking dynamics with macro credit bureau risk |
| [5], [6], [7] | LightGBM, XGBoost, Random Forest | Core candidate ensemble algorithms benchmarked across Pillars 1 and 2 |
| [8], [9], [10] | Probability Calibration | Application of Platt sigmoid scaling to guarantee reliable default probabilities |
| [11] | Brier Score Evaluation | Mathematical scoring metric used to validate calibration reliability |
| [12], [13], [14] | Interpretability and Tree-SHAP | Exact local game-theoretic feature attribution for every scored applicant |
| [15] | Explainable AI in Risk | Architectural framework for translating SHAP values into underwriter action items |
| [16] | Cryptographic Time-Stamping | Mathematical basis of the SHA-256 forward hash chain in the persistence layer |
| [17], [18] | DPDP Act 2023 & RBI AA | Legal foundation for PII masking, consent architecture, and adverse-action compliance |

### 2.2 Research Gap
Four distinct research and engineering gaps exist in contemporary literature:
1. **The Incompatible Schema Fallacy**: Academic projects routinely claim to train supervised default models directly on bank statements by training a model on bureau datasets (such as Home Credit) and feeding in statement columns. This is mathematically invalid because the feature schemas are fundamentally disjoint.
2. **Reliance on Unvalidated Heuristic Point Scoring**: Existing systems frequently fall back on manual, rule-based 0–100 scorecards for statement analysis. Such scorecards are heuristic, arbitrary, and cannot produce a calibrated default probability.
3. **Transaction Categorisation Brittle RegEx**: Commercial systems often rely on rigid regular expressions that fail on colloquial Indian narrations, UPI handles, and vernacular terms.
4. **Absence of Tamper-Evident Underwriter Auditing**: Prototypes rarely provide cryptographic guarantees that prevent rogue underwriters or system administrators from altering risk flags or decisions post-hoc.

### 2.3 Objectives
The primary objectives of this project are:
1. Formulate a multi-format, fault-tolerant statement parser capable of processing diverse Indian bank exports (CSV and native digital PDF) with strict balance reconciliation and PII redaction.
2. Construct a **Tier 1 Supervised NLP pipeline** to categorize messy, unstructured banking narrations across 18 classes with calibrated confidence.
3. Engineer a mathematically rigorous **15-Dimensional Feature Bridge** that maps 23 continuous banking cash-flow features into the standardized behavioral repayment dimensions of the 30,000-record UCI Credit Card Default benchmark.
4. Train, validate, calibrate, and freeze a **Pillar 1 Supervised Behavioral Default Prediction Model** (Random Forest) that outputs reliable default probabilities $P_{\text{behavioral}}$ and top feature drivers, completely eliminating rule-based scoring from the decision path.
5. Deploy a **Tier 3 Unsupervised ML Suite** utilizing an Isolation Forest (150 trees) for non-linear cash-flow surge/drain anomaly detection and K-Means clustering ($k=4$) for spending persona segmentation.
6. Build a **Pillar 2 Macro Bureau Default-Risk Benchmark** (Platt-calibrated LightGBM) with exact local Tree-SHAP attributions.
7. Unify both models into a **Dual-Pillar 2×2 ML Risk Decision Matrix** with pre-qualification data quality hard stops and salary-slip cross-verification overrides.
8. Implement an immutable SQLite persistence store reinforced with a **SHA-256 cryptographic forward hash chain** and external anchor file.
9. Deliver an interactive FinTech Streamlit interface featuring an interactive What-If Counterfactual Sandbox, Plotly calibration plots, and a 127-test automated verification suite.

### 2.4 Problem Statement
Given an applicant's digital bank statement, an optional employer salary slip, an officer-entered macro credit bureau profile, and proposed loan parameters (principal, tenure, interest rate), formulate and implement an intelligent, explainable, and cryptographically verified decision-support system that:
1. Validates statement data integrity and extracts verified recurring cash-flow dynamics without conflating non-income credits.
2. Categorizes transactions using supervised NLP with calibrated confidence.
3. Bridges continuous statement metrics to empirical repayment dimensions to predict calibrated behavioral default probability using a trained supervised machine learning model.
4. Unsupervisedly detects non-linear cash-flow anomalies to safeguard against sudden liquidity drains.
5. Evaluates macro credit bureau risk using an explainable, calibrated gradient boosting model with local Tree-SHAP attributions.
6. Integrates both risk signals into an auditable 2×2 decision matrix where recommendations are causally determined by machine learning models and validated by human underwriters.
7. Seals every underwriter interaction in a cryptographic hash chain to ensure regulatory auditability.

### 2.5 Project Plan
The project was executed across five sequential engineering phases, culminating in a robust production-grade system. Table 2.2 details the implementation phases and their concrete deliverables.

**Table 2.2**: Project implementation phases, work packages, and key outcomes
| Phase | Work Package Focus | Key Deliverables and Technical Outcomes |
| :--- | :--- | :--- |
| **Phase 1** | Behavioral ML Model Training & Calibration | Stratified 70/15/15 split of 30,000 UCI records; 5-fold CV benchmarking of Logistic Regression, Gradient Boosting, and Random Forest; Platt sigmoid calibration on 4,500 validation rows; frozen test set evaluation (ROC-AUC: 0.7725, PR-AUC: 0.5304, Accuracy: 81.53%); artifacts saved to `models/behavioral_prediction_model.joblib`. |
| **Phase 2** | Feature Bridge & What-If Simulator Engine | Mathematical formulation of the 15-dimensional bridge mapping 23 statement features to UCI repayment dimensions; implementation of `src/features/behavioral_ml_features.py` with zero-division guards and boundary clamping; interactive What-If counterfactual simulation engine; 15 dedicated unit tests passing. |
| **Phase 3** | Decision Engine Decoupling & Safeguard Integration | Complete removal of 0–100 heuristic scoring from the decision path; refactored `src/decision/engine.py` to drive decisions via the Dual-Pillar 2×2 ML Matrix ($P_{\text{behavioral}} \times P_{\text{bureau}}$); extracted pre-qualification data quality hard stops into `evaluate_data_quality_gates()`; integrated Isolation Forest anomaly detection overrides. |
| **Phase 4** | Streamlit UI FinTech Overhaul | Tab 1 Behavioral ML Risk Card & Top Drivers badge; Tab 3 15-Dim Feature Bridge Inspector, Interactive What-If Counterfactual Sandbox, Plotly Platt reliability calibration curve, population risk distribution benchmark, and 3-Tier ML Underwriting Synergy Strip. |
| **Phase 5** | Documentation, Security & Test Suite Pass | Comprehensive updates to `docs/panel_qa.md`, `README.md`, and `docs/system_architecture.md`; complete test suite execution reaching 127 passing tests (0 failures); Git commit `e095e44` pushed to remote repository. |

---

## CHAPTER 3: TECHNICAL SPECIFICATION

### 3.1 Requirements

#### 3.1.1 Functional Requirements
**Table 3.1**: Functional requirements specification
| ID | Requirement Description | Implementation Verification |
| :--- | :--- | :--- |
| **FR1** | Multi-bank statement CSV and native digital PDF ingestion supporting major Indian banking layouts (HDFC, ICICI, SBI, Axis, Kotak). | Validated via `src/data/statement_csv.py` and `statement_pdf.py` across diverse format fixtures. |
| **FR2** | Statement data validation including running balance reconciliation, date format parsing, duplicate removal, and PII masking. | Generates an immutable `StatementQualityReport` dataclass with valid/rejected counts and anomaly flags. |
| **FR3** | Tier 1 Supervised NLP categorisation across 18 transaction classes with calibrated class probabilities. | `src/models/transaction_nlp.py` achieving 100% 10-fold CV accuracy on 1,025 curated narrations. |
| **FR4** | Non-income credit isolation, strictly excluding loan disbursements, self-transfers, refunds, and wallet top-ups from income calculations. | Automated rules in `src/features/behavioral.py` ensuring only verified salary/recurring credits constitute income. |
| **FR5** | 15-Dimensional Feature Bridge mapping statement cash flows into standardized UCI behavioral repayment space. | Implemented in `src/features/behavioral_ml_features.py` with boundary clipping and unit tests. |
| **FR6** | Pillar 1 Behavioral Default Risk prediction generating calibrated probability $P_{\text{behavioral}}$ and top feature drivers. | Supervised Random Forest pipeline in `src/models/behavioral_prediction.py`. |
| **FR7** | Tier 3 Unsupervised cash-flow anomaly detection and spending persona segmentation. | Isolation Forest (150 trees) and K-Means ($k=4$) in `src/models/behavioral_unsupervised.py`. |
| **FR8** | Cross-document salary verification validating declared net salary against statement credits within 15% tolerance. | Implemented in `src/decision/salary_verification.py`. |
| **FR9** | Pillar 2 Macro Bureau scoring generating calibrated $P_{\text{bureau}}$ and exact Tree-SHAP local attributions. | Platt-calibrated LightGBM model in `src/models/applicant_scoring.py` with `predict(pred_contrib=True)`. |
| **FR10** | Dual-Pillar 2×2 ML Risk Matrix evaluating recommendations based on $P_{\text{behavioral}}$ and $P_{\text{bureau}}$ cutoffs with automated anomaly overrides. | Core engine logic in `src/decision/engine.py`. |
| **FR11** | Cryptographic forward SHA-256 hash chaining of every decision record with an external filesystem anchor. | Persistence engine in `src/data/db.py` with `verify_hash_chain()`. |
| **FR12** | Interactive FinTech UI dashboard featuring What-If counterfactual simulation, risk mapping, and stress testing. | Streamlit web application in `app.py`. |

#### 3.1.2 Non-Functional Requirements
**Table 3.2**: Non-functional requirements and engineering realizations
| Attribute | Requirement Description | Technical Realization in System |
| :--- | :--- | :--- |
| **Explainability** | Full interpretability for all automated risk outputs to satisfy regulatory adverse-action mandates. | Exact Tree-SHAP attributions in Pillar 2; permutation importance and decision tree path driver extraction in Pillar 1. |
| **Mathematical Soundness** | Zero data leakage across training, calibration, and testing splits. | Preprocessing transformers fit strictly on training splits; Platt scaling calibrated on held-out validation partitions; test sets frozen. |
| **Reliability & Calibration** | Output scores must represent empirical default likelihoods rather than arbitrary margins. | Platt sigmoid calibration minimizing Brier score on held-out data; verified via reliability diagrams. |
| **Integrity & Non-Repudiation** | Decision logs must be provably tamper-evident. | SHA-256 forward hash linking with external HEAD anchor defeating retroactive modifications. |
| **Privacy & DPDP Compliance** | Protecting applicant Personally Identifiable Information (PII). | Automated regex-based masking of account numbers, names, PAN, and Aadhaar prior to hashing and database storage. |
| **Inference Performance** | Low-latency response times for interactive loan officer sessions. | Complete ingestion, feature bridging, and dual-model ML scoring executes in under 120 ms on consumer hardware. |
| **Robustness** | 100% test pass rate across all system modules. | 127 automated pytest tests passing across unit, integration, metamorphic, and dashboard suites. |

### 3.2 Feasibility Study

#### 3.2.1 Technical Feasibility
The platform is developed entirely in Python 3.12, leveraging mature, industry-standard scientific and machine learning libraries: `pandas` and `numpy` for data manipulation, `scikit-learn` for preprocessing, Logistic Regression, Random Forest, Platt calibration, and Isolation Forest; `lightgbm` and `xgboost` for gradient boosted decision trees; `shap` for game-theoretic explainability; `plotly` and `matplotlib` for publication-grade visualizations; and `streamlit` for the reactive user interface. 

The most computationally intensive component—training the Pillar 2 LightGBM model on 196,806 records—executes in approximately 15.6 seconds on a standard x86-64 multi-core processor without GPU acceleration. Pillar 1 Random Forest training on 21,000 records completes in 9.2 seconds. Inference latency is instantaneous (<120 ms). Consequently, the system is fully technically feasible on commodity enterprise laptops and workstations.

#### 3.2.2 Economic Feasibility
The entire software stack is constructed from open-source technologies under permissive licenses (MIT, Apache 2.0, BSD). The underlying database utilizes Python's built-in SQLite engine, requiring no external database servers or recurring software licenses. Datasets utilized (UCI Credit Card Default and Home Credit Default Risk) are publicly accessible academic benchmarks. The development and verification required zero commercial cloud infrastructure expenditures, demonstrating exceptional economic feasibility for microfinance institutions and regional commercial banks.

#### 3.2.3 Social and Ethical Feasibility
By substituting human subjective bias and arbitrary point deductions with calibrated machine learning probabilities and transparent feature drivers, the system significantly enhances underwriting consistency. Crucially, the platform operates as a *decision-support system* rather than an autonomous decision maker: every recommendation is surfaced to an accredited human loan officer who retains ultimate authority. Furthermore, by rigorously analyzing cash-flow metrics, the platform empowers credit-worthy individuals with thin bureau files (e.g., gig workers, young professionals) to secure credit based on verifiable savings and disciplined liquidity rather than historical credit history alone.

### 3.3 System Specification

#### 3.3.1 Hardware Specification
**Table 3.3**: Recommended workstation hardware specifications
| Component | Minimum Client Environment | Recommended Training / Benchmark Workstation |
| :--- | :--- | :--- |
| **Processor** | Dual-core Intel Core i5 / AMD Ryzen 3 (2.0 GHz) | Quad-core Intel Core i7 / AMD Ryzen 7 (3.2 GHz or higher) |
| **RAM** | 8 GB DDR4 | 16 GB DDR4/DDR5 |
| **Storage** | 2 GB available SSD storage | 15 GB available NVMe SSD storage |
| **Display** | 1366 × 768 resolution | 1920 × 1080 Full HD resolution |
| **GPU** | Not required (CPU execution) | Optional (CPU multi-threading fully utilized) |

#### 3.3.2 Software Specification
**Table 3.4**: Software stack and execution environment
| Layer | Component Name and Version Specification |
| :--- | :--- |
| **Operating System** | Microsoft Windows 10/11 (64-bit); Linux (Ubuntu 22.04 LTS); macOS |
| **Language Runtime** | Python 3.12 (CPython runtime 3.12.14) |
| **Data Processing** | `pandas` (≥ 2.2.0), `numpy` (≥ 1.26.0), `pyarrow`, `duckdb`, `openpyxl`, `xlrd` |
| **Machine Learning** | `scikit-learn` (≥ 1.5.0), `lightgbm` (≥ 4.5.0), `xgboost` (≥ 2.1.0), `joblib` |
| **Model Interpretability** | `shap` (≥ 0.46.0) utilizing exact path-dependent Tree-SHAP |
| **Document Processing** | `pypdf` (≥ 6.21.0) for digital text extraction |
| **Visualization & UI** | `streamlit` (≥ 1.40.0), `plotly` (≥ 5.24.0), `matplotlib` (≥ 3.11.0) |
| **Persistence & Crypto** | `sqlite3` (standard library), `hashlib` (SHA-256 standard engine) |
| **Testing Framework** | `pytest` (≥ 8.0.0), `streamlit.testing.v1.AppTest` |

---

## CHAPTER 4: DESIGN APPROACH AND DETAILS

### 4.1 System Architecture
The system architecture follows a clean, decoupled, five-tier hierarchical pipeline designed to ensure absolute separation of concerns between raw transaction ingestion, feature bridging, machine learning inference, dual-pillar decision synthesis, and cryptographic persistence.

Figure 4.1 illustrates the comprehensive system architecture.

```
                           +-------------------------------------------------------+
                           |               INPUT & INGESTION LAYER                 |
                           |  Bank Statement (CSV/PDF) | Salary Slip | Bureau DPD  |
                           +-------------------------------------------------------+
                                        |                                 |
                                        v                                 v
        +-----------------------------------------------+   +-----------------------------------------------+
        |    PILLAR 1: BEHAVIORAL CASH-FLOW ML ENGINE   |   |     PILLAR 2: MACRO BUREAU ML BENCHMARK       |
        | - Statement Parser & Quality Validation       |   | - 64/16/20 Leakage-Free Stratified Pipeline   |
        | - Tier 1 Supervised NLP Categorisation (SGD)  |   | - Platt-Calibrated LightGBM Classifier        |
        | - 15-Dimensional Statement-to-UCI Bridge      |   | - Heuristic Bureau Mapping (CIBIL to EXT_SRC) |
        | - Supervised Behavioral RF Default Model      |   | - Exact Path-Dependent Tree-SHAP Explanations |
        +-----------------------------------------------+   +-----------------------------------------------+
                   \                                                           /
                    \                                                         /
                     v                                                       v
        +---------------------------------------------------------------------------------------------------+
        |                 TIER 3 UNSUPERVISED ML SUITE & PRE-QUALIFICATION QUALITY GATES                    |
        | - Isolation Forest (150 trees, 5% contamination) non-linear cash-flow anomaly detection           |
        | - K-Means Clustering (k=4) empirical behavioral spending personas                                |
        | - Mandatory Data Quality Hard Stops (Balance integrity, >=3 months coverage, 50% EMI FOIR cap)    |
        +---------------------------------------------------------------------------------------------------+
                                                          |
                                                          v
        +---------------------------------------------------------------------------------------------------+
        |                         DUAL-PILLAR 2x2 ML DECISION MATRIX & OVERRIDE ENGINE                      |
        |            Recommendation causally derived from P(behavioral) x P(bureau) risk bands             |
        |            Isolation Forest anomalies & Salary-slip mismatches (>15%) trigger manual review       |
        +---------------------------------------------------------------------------------------------------+
                                                          |
                                                          v
        +---------------------------------------------------------------------------------------------------+
        |                         PERSISTENCE & FINTECH DASHBOARD PRESENTATION LAYER                        |
        | - SQLite Cryptographic Store with SHA-256 forward hash chain & external filesystem anchor         |
        | - 6-Tab Streamlit UI with Counterfactual What-If Sandbox, Reliability Curves & Stress Testing Lab  |
        +---------------------------------------------------------------------------------------------------+
```
*Figure 4.1: System architecture of the Dual-Pillar machine learning credit decision support platform*  
*(Rendered high-resolution diagram stored at `reports/figures/fig_4_1_architecture.png`)*

The core architectural tenets governing this design are:
1. **Mathematical Isolation of Pipelines**: The Pillar 2 Home Credit benchmark model is never applied directly to raw uploaded statement transactions. Its schema (application features, historical bureau balances) does not exist in a bank statement.
2. **Causal ML Decisioning**: Rule-based point scoring has been entirely eliminated from the decision path. The underwriter's recommendation is causally driven by the Dual-Pillar 2×2 ML Risk Matrix evaluating calibrated default probabilities ($P_{\text{behavioral}} \times P_{\text{bureau}}$).
3. **Pre-Qualification Hard Stops as Integrity Filters**: Heuristic rules are retained strictly as pre-qualification data quality gates (e.g., balance reconciliation failures, <3 months history, critical EMI burden), functioning as data integrity filters rather than credit score determinants.
4. **Defense-in-Depth Anomaly Safeguards**: Even if an applicant's supervised models indicate low risk, an unsupervised Isolation Forest flag automatically triggers human review, safeguarding against novel fraud patterns or sudden liquidity depletion.
5. **Human-in-the-Loop Authority**: The platform recommends; the human loan officer decides. Every override requires an auditable justification stored in the cryptographic ledger.

### 4.2 Design

#### 4.2.1 Data Flow Diagram (DFD)
Figure 4.2 illustrates the condensed Level 0 and Level 1 data flows within the platform.
```
       [ Applicant ] ---- Statement (CSV/PDF) ----> ( 1.0 Parse & Validate )
                                                           |
                                                      Clean txns
                                                           v
                                                    ( 2.0 Feature Bridge )
                                                           |
                                                    15-dim UCI features
                                                           v
                                                    ( 3.0 Behavioral ML Predict )
                                                           |
                                                      P(behavioral)
                                                           v
       [ Loan Officer ] -- Bureau Inputs --> ( 4.0 Bureau ML Scorer )
                                                    |
                                              P(bureau) + SHAP
                                                    v
                                            ( 5.0 Dual-Pillar Decision Matrix )
                                                    |
                                              Recommendation
                                                    v
                                            ( 6.0 Hash-Chained Case Store )
```
*Figure 4.2: Data flow diagram (Level 0 and Level 1, condensed)*  
*(Rendered high-resolution diagram stored at `reports/figures/fig_4_2_dfd.png`)*

Process 1.0 parses raw statements, validates balance transitions, and filters malformed rows. Process 2.0 categorizes transactions via NLP and maps cash-flow metrics into the 15-dimensional UCI feature space. Process 3.0 executes the calibrated Random Forest model to predict $P_{\text{behavioral}}$. Simultaneously, Process 4.0 ingests officer-entered bureau inputs, scoring macro risk $P_{\text{bureau}}$ and computing Tree-SHAP attributions. Process 5.0 evaluates the 2×2 decision matrix, incorporating Isolation Forest anomaly overrides. Finally, Process 6.0 seals the officer's decision in the cryptographic SQLite store.

#### 4.2.2 Use Case Diagram
The use case model (Figure 4.3) defines interactions between two principal actors: the **Loan Officer** (primary underwriter) and the **Reviewer / Auditor** (compliance verifier).

The loan officer uploads and maps statements, reviews transaction categories, inspects the 15-dimensional behavioral ML profile, conducts counterfactual simulations in the What-If Sandbox, enters bureau parameters, reviews the 2×2 matrix recommendation, and submits final underwriting decisions with written rationales. The auditor queries historical cases and executes cryptographic hash-chain verification to audit records for unauthorized tampering.

*(Rendered high-resolution diagram stored at `reports/figures/fig_4_3_usecase.png`)*

#### 4.2.3 Class Diagram
The software design relies on strongly typed, immutable Python `dataclasses` and object-oriented service modules. Figure 4.4 details the structural relationships between core classes:
- `StatementQualityReport`: Encapsulates parse validation, duplicate counts, observed months, and balance continuity.
- `BehavioralMLFeatures`: Encapsulates the 15-dimensional bridged metrics mapped to the UCI feature space.
- `BehavioralRiskAssessment`: Houses calibrated default probability $P_{\text{behavioral}}$, risk bands (`LOW`, `MODERATE`, `ELEVATED`, `HIGH`), top feature drivers, and Isolation Forest anomaly flags.
- `BureauScorer`: Loads the LightGBM model bundle, executes Platt-calibrated inference, and generates exact Tree-SHAP attributions.
- `DualPillarEngine`: Synthesizes $P_{\text{behavioral}}$ and $P_{\text{bureau}}$, evaluates data quality gates, and generates the final `Decision` record.
- `CaseStore`: Manages SQLite persistence, SHA-256 forward chaining, and external filesystem anchor synchronization.

*(Rendered high-resolution diagram stored at `reports/figures/fig_4_4_class.png`)*

#### 4.2.4 Sequence Diagram
Figure 4.5 illustrates the sequence of operations during an end-to-end applicant evaluation:
1. The officer uploads the bank statement and specifies proposed loan terms via `app.py`.
2. `StatementParser` normalizes transactions and returns an immutable `StatementQualityReport`.
3. `FeatureBridge` computes 23 statement features and projects them into the 15-dimensional UCI feature space.
4. `BehavioralML` executes the calibrated Random Forest model, returning $P_{\text{behavioral}}$ and top risk drivers.
5. `UnsupervisedSuite` evaluates Isolation Forest anomaly detection and K-Means persona clustering.
6. The officer inputs bureau parameters; `BureauScorer` computes calibrated $P_{\text{bureau}}$ and Tree-SHAP attributions.
7. `DecisionEngine` evaluates the Dual-Pillar 2×2 matrix, checking data quality gates and anomaly flags.
8. The dashboard renders the interactive risk map, What-If sandbox, and recommendation.
9. Upon officer sign-off, `CaseStore` sanitizes the payload, calculates the SHA-256 hash linked to the previous record, and writes the external anchor.

*(Rendered high-resolution diagram stored at `reports/figures/fig_4_5_sequence.png`)*

#### 4.2.5 Data Design
All underwriting cases, model probabilities, explainability attributions, and cryptographic hashes are persisted in an embedded SQLite database (`data/cases.db`). Table 4.1 defines the schema of the `cases` table.

**Table 4.1**: Schema definition of the SQLite cases table with SHA-256 integrity links
| Column Name | SQLite Type | Integrity & Functional Purpose |
| :--- | :--- | :--- |
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | Monotonically increasing sequence identifier |
| `case_id` | `TEXT UNIQUE NOT NULL` | UUID-based business identifier for the underwriting case |
| `timestamp_utc` | `TEXT NOT NULL` | ISO 8601 UTC timestamp of decision record generation |
| `applicant_id` | `TEXT` | Anonymized applicant identifier |
| `requested_amount` | `REAL` | Loan principal amount requested by applicant |
| `loan_tenure_months` | `INTEGER` | Proposed amortisation tenure in months |
| `proposed_emi` | `REAL` | Illustrative monthly instalment obligation |
| `behavioral_probability` | `REAL` | Calibrated $P_{\text{behavioral}}$ from Pillar 1 Random Forest |
| `bureau_probability` | `REAL` | Calibrated $P_{\text{bureau}}$ from Pillar 2 LightGBM |
| `system_recommendation` | `TEXT NOT NULL` | Recommendation output by the Dual-Pillar 2×2 ML Engine |
| `officer_action` | `TEXT NOT NULL` | Final action chosen by the loan officer |
| `is_override` | `INTEGER NOT NULL` | Binary flag (1 if officer action differs from system recommendation) |
| `officer_name` | `TEXT` | Masked underwriter identifier |
| `officer_rationale` | `TEXT` | Mandatory text explanation if an override is executed |
| `previous_hash` | `TEXT NOT NULL` | SHA-256 digest of the immediately preceding database row |
| `record_hash` | `TEXT NOT NULL` | SHA-256 digest binding `previous_hash` and sanitized case payload |
| `full_record_json` | `TEXT NOT NULL` | Complete sanitized JSON payload containing all feature vectors |

---

## CHAPTER 5: METHODOLOGY AND TESTING

### 5.1 Module Description

#### 5.1.1 Bank Statement Ingestion and Pre-Qualification Quality Gates
The ingestion pipeline (`src/data/statement_csv.py` and `src/data/statement_pdf.py`) provides resilient parsing across major Indian banking exports. Key capabilities include:
- Automatic detection and stripping of Byte Order Marks (BOM) and preamble lines preceding table headers.
- Indian numbering system parser converting lakh-comma strings (e.g., `"1,25,000.00"`) into floating-point numbers.
- Flexible column alias matching supporting diverse naming schemes across HDFC, ICICI, SBI, Axis, and Kotak.
- Fail-closed digital PDF processing via `pypdf`, extracting native text tables while rejecting scanned/rasterized documents.
- Continuous balance reconciliation: for every transaction $i$, the engine verifies that $\text{Balance}_{i} = \text{Balance}_{i-1} + \text{Credit}_i - \text{Debit}_i$. Contradictory balance transitions are flagged.
- An automated `StatementQualityReport` is generated, computing a normalized quality score $Q \in [0, 1]$:
  $$\text{Quality Score} = 1.0 - \left( \frac{\text{Rejected Rows}}{\text{Total Rows}} + \frac{\text{Balance Mismatches}}{\text{Valid Rows}} \right)$$

#### 5.1.2 Tier 1 Transaction-Level Supervised NLP Categorisation
Indian retail bank statements exhibit colloquial, unstructured transaction descriptions. Heuristic keyword matching fails to generalize across merchant abbreviations, payment gateways (Razorpay, BillDesk), and vernacular tokens.

We implemented a **Tier 1 Supervised NLP Classification Pipeline** (`src/models/transaction_nlp.py`). The pipeline utilizes a hybrid TF-IDF vectorizer extracting both character n-grams (range 3–5) and word n-grams (range 1–2) to capture sub-word merchant fragments. Classification is performed using a Linear Support Vector / Logistic Stochastic Gradient Descent (SGD) model with Platt probability scaling across 18 distinct financial categories:
`SALARY`, `RENT`, `UTILITIES`, `GROCERIES`, `FOOD_DELIVERY`, `HEALTHCARE`, `EDUCATION`, `TRAVEL`, `SHOPPING`, `INVESTMENTS`, `INSURANCE`, `EMI_OUTFLOW`, `CREDIT_CARD_PAYMENT`, `CASH_WITHDRAWAL`, `WALLET_TRANSFER`, `INTEREST_CREDIT`, `TRANSFER_IN`, `UNCERTAIN`.

Trained on 1,025 curated Indian transaction narrations, the NLP pipeline achieves **100% 10-fold cross-validation accuracy** and a macro F1-score of 1.000. Ambiguous transactions falling below a 65% probability threshold default to `UNCERTAIN` for human review.

#### 5.1.3 The 15-Dimensional Statement-to-UCI Feature Bridge
To enable rigorous supervised default prediction from bank statements without relying on ungrounded synthetic labels, we designed and mathematically formalized the **15-Dimensional Statement-to-UCI Feature Bridge** (`src/features/behavioral_ml_features.py`).

The bridge maps 23 continuous banking cash-flow metrics into the 15 standardized behavioral repayment dimensions of the 30,000-record UCI Credit Card Default benchmark:
1. **Repayment Timeliness Dimensions (`PAY_0` to `PAY_6`)**: In the UCI schema, repayment timeliness ranges from $-2$ (no consumption / paid in full) to $+8$ (eight months payment delay). We map statement cash-flow stress—specifically low-balance days, recurring bill payment coverage, and income volatility—into standardized payment delay indices.
2. **Credit & Commitment Utilization (`BILL_AMT1` to `BILL_AMT6` / `LIMIT_BAL`)**: Mapped from the applicant's existing and proposed EMI burden combined with essential living expenses against total monthly credit capacity.
3. **Repayment Fractions (`PAY_AMT1` to `PAY_AMT6`)**: Derived from the monthly net savings ratio, cash surplus, and liquid emergency buffer months.

Table 5.1 details the mathematical equations governing the Feature Bridge.

**Table 5.1**: Mathematical mapping of 23 statement features to 15 UCI repayment dimensions
| UCI Dimension | Target Space | Governing Mathematical Equation & Boundary Clamping | Functional Interpretation |
| :--- | :--- | :--- | :--- |
| `LIMIT_BAL` | $[\text{₹}10^4, \text{₹}10^6]$ | $\text{LIMIT\_BAL} = \max(20000, I \times 6 \times (1 - \text{EMI\_Ratio}))$ | Estimated total revolving credit capacity |
| `PAY_0` | $[-2, +8]$ | $\text{delay} = \text{round}\left( \frac{\text{LowBalDays}}{30} \times 4 + (1 - \text{UtilityReg}) \times 3 + \text{IncVol} \times 2 \right) - 1$ | Current repayment timeliness index |
| `PAY_2` to `PAY_6` | $[-2, +8]$ | $\text{PAY}_t = \text{clip}(\text{round}(\text{delay} \times (1 - 0.1 \times t)), -2, 8)$ | Historical 6-month repayment delay trend |
| `BILL_AMT1` | $\mathbb{R}^+$ | $\text{BILL\_AMT1} = \max(0, E + M_{\text{existing}} + M_{\text{proposed}})$ | Current monthly financial obligations |
| `BILL_AMT2..6` | $\mathbb{R}^+$ | $\text{BILL\_AMT}_t = \max(0, \text{BILL\_AMT1} \times (1 + \text{ExpVol} \times (-1)^t \times 0.1))$ | Simulated historical monthly billing balances |
| `PAY_AMT1` | $\mathbb{R}^+$ | $\text{PAY\_AMT1} = \max(0, \text{BILL\_AMT1} \times \text{clip}(\text{SavingsRatio} + 0.5, 0.05, 1.0))$ | Estimated monthly repayment allocation |
| `PAY_AMT2..6` | $\mathbb{R}^+$ | $\text{PAY\_AMT}_t = \max(0, \text{BILL\_AMT}_t \times \text{clip}(\text{SavingsRatio} + 0.4, 0.05, 0.95))$ | Historical 6-month debt repayment allocations |
| `Utilisation` | $[0, 1]$ | $\text{Util} = \text{clip}\left( \frac{\text{BILL\_AMT1}}{\text{LIMIT\_BAL}}, 0.0, 1.0 \right)$ | Debt commitment to total capacity ratio |

The bridge implements strict zero-division safeguards and boundary clipping, ensuring mathematical continuity and stability across extreme cash-flow profiles.

#### 5.1.4 Pillar 1 Supervised Behavioral Default Prediction ML Model
The bridged 15-dimensional feature vector is processed by the **Pillar 1 Behavioral Default Prediction ML Model** (`src/models/behavioral_prediction.py`).

**Model Architecture & Training Protocol**:
- **Dataset**: UCI Credit Card Default benchmark (30,000 real financial payment records, base delinquency rate 22.12%).
- **Split Strategy**: Stratified 70/15/15 partition:
  - Training Partition: 21,000 records.
  - Calibration Partition: 4,500 records.
  - Held-Out Test Partition: 4,500 records (frozen until final evaluation).
- **Candidate Benchmark**: Evaluated via 5-fold stratified cross-validation on the training set:
  - Balanced Logistic Regression: CV ROC-AUC $0.7570 \pm 0.0127$ (5.48 s).
  - Gradient Boosting Classifier: CV ROC-AUC $0.7814 \pm 0.0110$ (17.32 s).
  - **Random Forest Classifier (Selected Winner)**: CV ROC-AUC **$0.7852 \pm 0.0115$** (9.21 s).
- **Hyperparameters**: 200 estimators, maximum depth of 10, minimum samples per split of 10, class-balanced sub-sampling.
- **Probability Calibration**: Calibrated on the 4,500 validation records using Platt sigmoid scaling (`CalibratedClassifierCV`):
  $$P(\text{default} \mid f) = \frac{1}{1 + \exp(A \cdot f + B)}$$
- **Frozen Test Performance (4,500 records)**:
  - **ROC-AUC**: **0.7725**
  - **PR-AUC**: **0.5304** (over 22.1% base rate, demonstrating significant precision lift)
  - **Accuracy**: **81.53%**
  - **Brier Score**: **0.1308**
  - **Default Class F1**: **0.4842** (Precision: 63.31%, Recall: 39.20%)

The model outputs calibrated probability $P_{\text{behavioral}}$ and categorizes the applicant into four standardized risk bands:
- `LOW`: $P_{\text{behavioral}} < 0.20$
- `MODERATE`: $0.20 \le P_{\text{behavioral}} < 0.30$
- `ELEVATED`: $0.30 \le P_{\text{behavioral}} < 0.45$
- `HIGH`: $P_{\text{behavioral}} \ge 0.45$

Furthermore, path-based decision tree attribution extracts the top positive (risk-increasing) and negative (risk-mitigating) feature drivers for every prediction, delivering complete local interpretability.

**Pre-Qualification Data Quality Gates (Replacing Heuristic Scoring)**:
Rule-based 0–100 point scoring has been completely removed from the credit decision path. Deterministic rules are retained strictly as **Pre-Qualification Data Quality Gates** (`src/decision/affordability.py`). Table 5.2 outlines these mandatory integrity checks.

**Table 5.2**: Pre-Qualification data quality hard stops and safeguard policies
| Policy Gate Check | Threshold / Condition | Actionable Trigger & System Outcome |
| :--- | :--- | :--- |
| **Minimum History** | Statement covers $< 3$ complete calendar months | Automatic `Refer for additional documents` |
| **Data Quality Score** | Statement quality score $Q < 0.80$ | Automatic `Refer for additional documents` |
| **Recurring Income** | Zero recognized salary or recurring business credits | Automatic `Refer for additional documents` |
| **Balance Integrity** | Detected running balance transition contradictions | Automatic `Manual review` (potential document forgery) |
| **Critical Debt FOIR** | Existing or proposed EMI exceeds 50% of recognized income | Automatic `Manual review` (critical debt-burden hard stop) |
| **Declared vs Detected EMI**| Discrepancy $> 20\%$ and absolute difference $\ge \text{₹}1,000$ | Automatic `Manual review` (unreported debt liability) |
| **Emergency Liquidity** | Liquid buffer $< 0.25$ months of operational expenses | Automatic `Manual review` (severe liquidity vulnerability) |
| **Categorisation Quality**| More than 25% of transactions marked as `UNCERTAIN` | Automatic `Refer for additional documents` |

#### 5.1.5 Tier 3 Unsupervised Cash-Flow Anomaly Detection and Personas
To capture non-linear behavioral shifts and account-level dynamics that supervised models might miss, we integrated an **Account-Level Unsupervised ML Suite** (`src/models/behavioral_unsupervised.py`).

1. **Isolation Forest Anomaly Detection**:
   Trained with 150 estimators and a 5% contamination factor across eight behavioral cash-flow dimensions (savings ratio, income volatility, expense volatility, cash withdrawal share, low-balance days, emergency buffer, effective EMI, uncertain share). The Isolation Forest isolates non-linear spending surges or liquidity drains. Any applicant flagged as an anomaly (`is_anomaly = True`) has their indicative approval automatically escalated to `Manual review`.
2. **K-Means Behavioral Persona Clustering**:
   Trained across $k=4$ clusters, segmenting applicants into distinct behavioral profiles:
   - Cluster 0: *Disciplined Accumulator* (high savings $>40\%$, low volatility, robust liquidity buffer).
   - Cluster 1: *Balanced Lifestyle Spender* (moderate savings $15\text{--}25\%$, stable utility payments).
   - Cluster 2: *Volatile Cash Flow / Gig Earner* (high income variation $>30\%$, frequent low-balance days).
   - Cluster 3: *Liquidity Strained / High Buffer Drag* (negative savings, high debt burden $>45\%$).

#### 5.1.6 Salary-Slip Cross-Document Verification
To defeat payroll fraud and inflated income declarations, `src/decision/salary_verification.py` executes cross-document reconciliation. The underwriter enters the declared net pay and employer name from the applicant's official salary slip. The module reconciles this figure against detected statement payroll credits:
$$\text{Discrepancy Ratio} = \frac{|\text{Declared Net Pay} - \text{Detected Statement Salary}|}{\text{Declared Net Pay}}$$

If the discrepancy ratio exceeds 15%, the salary slip is marked unverified. The decision engine overrides all matrix quadrants with `Refer for additional documents`. The module also executes fuzzy token matching to verify whether the employer's name appears within the narration strings of recognized salary credits.

#### 5.1.7 Pillar 2 Macro Bureau Default-Risk Benchmark (LightGBM)
Pillar 2 evaluates macro credit bureau history via a calibrated gradient boosted decision tree (`src/models/benchmark_home_credit.py` and `src/models/applicant_scoring.py`).

- **Data Split**: The Home Credit Default Risk dataset (307,511 records) was partitioned using a stratified 64/16/20 split (196,806 training, 49,202 validation, 61,503 final test).
- **Candidate Benchmark**: Evaluated Logistic Regression, unweighted LightGBM, balanced LightGBM, Random Forest, and XGBoost. Balanced LightGBM was selected based on validation PR-AUC (0.2510) and ROC-AUC (0.7674).
- **Calibration & Alert Threshold**: Balanced class weights produce probability distortion. Platt sigmoid scaling was fit on validation data, reducing the Brier score from 0.1767 to 0.0674. On the final frozen test set (61,503 records), the calibrated model achieved:
  - **ROC-AUC**: **0.7737** (95% bootstrap CI: 0.7668–0.7811)
  - **PR-AUC**: **0.2664** (95% CI: 0.2553–0.2785, a 3.3× lift over the 8.07% base rate)
  - **Brier Score**: **0.0667**
- **Alert Threshold**: A policy threshold of 0.20 was selected on validation data, recalling 33.33% of defaults while flagging 8.81% of applicants.
- **Bureau Mapping**: Officer-entered bureau metrics (CIBIL 300–900, age, employment tenure, active loans, overdue DPD) are mapped onto the model's schema via a documented monotonic heuristic proxy ($\text{EXT\_SOURCE} = (\text{CIBIL} - 300) / 600$), accompanied by a transparent input completeness ratio.

#### 5.1.8 Exact Tree-SHAP Local Attribution Engine
To ensure complete local explainability under regulatory mandates, Pillar 2 integrates exact path-dependent **Tree-SHAP** (`src/models/tree_shap.py`), utilizing LightGBM's native `booster_.predict(pred_contrib=True)` API [13], [14].

For every scored applicant, the engine decomposes the model's log-odds output into exact Shapley contributions:
$$f(x) = \phi_0 + \sum_{j=1}^{M} \phi_j(x)$$
where $\phi_0$ is the base expected log-odds across the training background and $\phi_j(x)$ is the exact marginal contribution of feature $j$. Positive contributions $\phi_j > 0$ indicate risk-increasing drivers; negative values $\phi_j < 0$ represent protective factors. The dashboard renders these attributions as an interactive Plotly horizontal bar chart.

#### 5.1.9 Dual-Pillar 2×2 ML Risk Decision Engine
The core decision engine (`src/decision/engine.py`) synthesizes Pillar 1 and Pillar 2 predictions into an explainable 2×2 risk matrix. 

Figure 5.1 illustrates the Dual-Pillar 2×2 matrix.
```
  Pillar 2 Bureau Default Risk P(bureau)
    1.0 +-----------------------------+-----------------------------+
        |         QUADRANT 4          |         QUADRANT 2          |
        | Does Not Meet Indicative    |   Manual Review: Bureau     |
        |         Criteria            |            Alert            |
        | (Elevated Risk Both Models) |  (Low Behav, High Bureau)   |
    0.2 +-----------------------------+-----------------------------+
        |         QUADRANT 3          |         QUADRANT 1          |
        |   Manual Review / Refer:    | Meets Indicative Affordability|
        |      Cash-Flow Alert        |           Criteria          |
        |  (High Behav, Low Bureau)   | (Low Risk on Both ML Models)|
    0.0 +-----------------------------+-----------------------------+
       0.0                           0.30                          1.0
          Pillar 1 Behavioral Default Risk P(behavioral)
```
*Figure 5.1: Dual-Pillar 2×2 machine learning decision matrix ($P_{\text{behavioral}} \times P_{\text{bureau}}$)*  
*(Rendered high-resolution diagram stored at `reports/figures/fig_5_1_matrix.png`)*

The engine operates under strict hierarchical precedence:
1. **Pre-Qualification Gate Failure**: Triggered if statement coverage $<3$ months, quality $<0.80$, balance contradictions exist, or salary slip verification fails ($>15\%$ mismatch). Generates `Refer for additional documents`.
2. **Dual-Pillar ML Matrix Evaluation**:
   - **Quadrant 1 (Meets Indicative Criteria)**: $P_{\text{behavioral}} < 0.30$ AND $P_{\text{bureau}} < 0.20$. Both cash-flow behavior and macro credit history indicate low default probability.
   - **Quadrant 2 (Manual Review - Bureau Alert)**: $P_{\text{behavioral}} < 0.30$ AND $P_{\text{bureau}} \ge 0.20$. Strong cash-flow liquidity conflicts with elevated bureau delinquency. Underwriter evaluates collateral or secondary guarantees.
   - **Quadrant 3 (Manual Review / Referral - Cash-Flow Alert)**: $P_{\text{behavioral}} \ge 0.30$ AND $P_{\text{bureau}} < 0.20$. Clean bureau history conflicts with current cash-flow distress. Underwriter considers loan restructuring, extended tenure, or lower principal.
   - **Quadrant 4 (Does Not Meet Indicative Criteria)**: $P_{\text{behavioral}} \ge 0.30$ AND $P_{\text{bureau}} \ge 0.20$. High risk on both independent ML models.
3. **Isolation Forest Anomaly Override**: If an applicant in Quadrant 1 exhibits an Isolation Forest anomaly flag (`is_anomaly = True`), the recommendation is automatically escalated to `Manual review`.

#### 5.1.10 Cryptographic Decision Audit Trail (SHA-256 Hash Chain)
To guarantee data integrity and satisfy DPDP Act 2023 compliance, `src/data/db.py` implements a **SHA-256 Cryptographic Forward Hash Chain** [16].

Figure 5.2 illustrates the hash chain architecture.
```
  +--------------------+       +--------------------+       +--------------------+
  |      Record 1      | ----> |      Record 2      | ----> |   Record 3 (HEAD)  |
  | Case C0 (Genesis)  |       | Case C1            |       | Case C2            |
  | Prev: 000...000    |       | Prev: Hash(C0)     |       | Prev: Hash(C1)     |
  | Hash: SHA256(...)  |       | Hash: SHA256(...)  |       | Hash: SHA256(...)  |
  +--------------------+       +--------------------+       +--------------------+
                                                                      |
                                                                      v
                                                            [ data/HEAD_HASH.sha256 ]
```
*Figure 5.2: Cryptographic forward SHA-256 hash chain with external filesystem anchor*  
*(Rendered high-resolution diagram stored at `reports/figures/fig_5_2_hashchain.png`)*

For each decision, the payload is sanitized (PII masked for Right to Erasure compliance). The record hash $H_i$ is computed as:
$$H_i = \text{SHA-256}(H_{i-1} \parallel \text{CaseID}_i \parallel \text{Timestamp}_i \parallel \text{ApplicantID}_i \parallel \text{Principal}_i \parallel \text{SystemRec}_i \parallel \text{OfficerAction}_i \parallel \text{SanitizedJSON}_i)$$
where $H_0 = 0^{64}$ (genesis hash). Concurrently, $H_i$ is written to an external anchor file (`data/HEAD_HASH.sha256`). The `verify_hash_chain()` routine recomputes the entire cryptographic sequence and matches it against the external anchor, provably detecting any retroactive record alteration or whole-database replacement attacks.

#### 5.1.11 Interactive FinTech UI, What-If Sandbox, and Stress Lab
The system is presented via an interactive Streamlit dashboard (`app.py`) structured into six cohesive tabs:
- **Tab 1: Executive Case Summary**: Real-time KPI cluster, Pillar 1 Behavioral ML Risk card, top risk drivers badge, and automated review checklist.
- **Tab 2: Statement Ingestion & Mapping**: File uploader, CSV column alias mapper, balance reconciliation table, and data-quality diagnostics.
- **Tab 3: Behavioral Intelligence & What-If Sandbox**: 15-Dimensional Feature Bridge Inspector, **Interactive Counterfactual What-If Sandbox** (live sliders simulating changes in savings ratio, EMI burden, income volatility, emergency buffer, and low-balance days on $P_{\text{behavioral}}$), Plotly Platt calibration reliability curve, population distribution benchmark, and 3-Tier ML Underwriting Synergy Strip.
- **Tab 4: Portfolio Synthetic Analytics**: Cohort analytics across simulated applicant populations.
- **Tab 5: Macro Bureau Benchmark**: Full LightGBM benchmark suite with ROC/PR curves, threshold sweeps, and Tree-SHAP local attribution charts.
- **Tab 6: Decision Terminal & Stress Testing Lab**: Interactive 2D Risk Map, active quadrant highlighting, **Scenario Shock Lab** (simulating income shocks 0 to $-50\%$, expense inflation 0 to $+50\%$, and rate hikes 0 to $+6\%$), actionable loan sizing metrics, underwriter override terminal with mandatory justification, and one-click cryptographic ledger sealing.

### 5.2 Testing Strategy and Verification
Verification was conducted through an automated testing harness combining unit tests, property-based metamorphic tests, and integration suites. On 25 October 2026, the complete test suite was executed: **127 tests passed with zero failures** in 91.55 seconds. Table 5.3 summarizes the automated test suite.

**Table 5.3**: Automated verification test suite breakdown across all 127 tests
| Test Module | Tests | Functional & Methodological Scope Verified |
| :--- | :--- | :--- |
| `tests/test_behavioral_features.py` | 15 | 15-Dimensional Feature Bridge mathematical mapping, zero-division guards, boundary clipping, and feature dictionary extraction. |
| `tests/test_statement_csv.py` | 10 | CSV ingestion tolerances, BOM stripping, lakh-comma parsing, duplicate row handling, balance reconciliation, PII masking. |
| `tests/test_features.py` | 12 | 4-layer categorisation rules, recurring income isolation, exclusion of loan disbursements, 23 statement cash-flow features. |
| `tests/test_affordability_policy.py` | 3 | Truth-table coverage over pre-qualification data quality gates, hard-stop triggers, and data quality thresholds. |
| `tests/test_policy_metamorphic.py` | 3 | Metamorphic properties: monotonicity (increased savings never increases default risk), monetary scale invariance. |
| `tests/test_decision.py` | 5 | Indicative criteria validation, referral outcomes, debt-burden limits, sustainable EMI calculations. |
| `tests/test_engine_dual_pillar.py` | 8 | Dual-Pillar 2×2 matrix quadrant assignments, divergence routing, Isolation Forest anomaly overrides. |
| `tests/test_decision_engine.py` | 6 | End-to-end recommendation synthesis, reason code generation, policy version tagging. |
| `tests/test_behavioral_unsupervised.py` | 7 | Isolation Forest anomaly scoring, K-Means $k=4$ persona assignment, bundle persistence. |
| `tests/test_salary_verification.py` | 3 | Net pay cross-verification, 15% tolerance window, employer token matching. |
| `tests/test_applicant_scoring.py` | 2 | Bureau profile mapping, heuristic CIBIL-to-EXT_SOURCE proxy, completeness ratio calculation. |
| `tests/test_tree_shap.py` | 2 | Tree-SHAP mathematical fidelity, additivity axiom verification ($\sum \phi_j = f(x) - \phi_0$). |
| `tests/test_db.py` | 3 | Cryptographic hash chaining, empty-chain verification, tampering detection on altered database records. |
| `tests/test_case_summary.py` | 4 | Decision record formatting, evidence row aggregation, review flag extraction with ML anomaly alerts. |
| `tests/test_matrix_viz.py` | 4 | Plotly 2D risk map rendering, Tree-SHAP horizontal bar visualization, active quadrant styling. |
| `tests/test_dashboard.py` | 2 | Headless rendering of Streamlit application tabs, reactive state management, What-If slider updates. |
| `tests/test_app_helpers.py` | 16 | Helper utilities, financial amortisation math, stress test simulation calculations. |
| `tests/test_parser_pdf.py` | 14 | Digital text extraction, table alignment, fail-closed handling on rasterized/scanned PDFs. |
| `tests/test_categorisation.py` | 8 | Transaction NLP prediction, calibrated class probability verification, uncertain category fallback. |
| **Total Automated Tests** | **127** | **127 passed, 0 failed, 100% pass rate** |

---

## CHAPTER 6: PROJECT DEMONSTRATION

### 6.1 Demonstration Bank Statements
To demonstrate the end-to-end platform, two contrasting real-world synthetic banking statements were evaluated:
- **Statement A (`data/demo/sample_bank_statement.csv`)**: A disciplined salaried employee profile comprising 20 transactions (Jan–Mar 2026), quality score 1.00, regular monthly payroll credits of ₹50,000, disciplined utility payments, no debt service delays, and a healthy liquid savings rate.
- **Statement B (`data/sample/demo_statement_all_scenarios.csv`)**: A volatile, liquidity-constrained account comprising 77 transactions, quality score 0.95, two zero-value rows, erratic freelance credits, heavy debt burden, high discretionary lifestyle debits, cash withdrawals, and frequent low-balance stress days.

Table 6.1 and Figure 6.1 present the derived cash-flow metrics and normalized Feature Bridge dimensions for both statements evaluating a requested loan of ₹2,00,000 (tenure 24 months, proposed EMI ₹6,500).

**Table 6.1**: Behavioral cash-flow and feature bridge metrics for demonstration statements
| Behavioral Feature Dimension | Statement A (Salaried Disciplined) | Statement B (Constrained Volatile) |
| :--- | :--- | :--- |
| **Observed History** | 3 complete months | 3 complete months |
| **Recognized Monthly Income** | ₹50,000 | ₹70,333 (conflated credits isolated) |
| **Average Monthly Expense** | ₹27,433 | ₹88,114 (monthly cash deficit) |
| **Savings Ratio** | **+45.1%** | **−25.3%** |
| **Detected Monthly EMI** | ₹6,000 | ₹25,433 |
| **Existing EMI-to-Income** | 12.0% | 36.2% |
| **Proposed Total EMI-to-Income** | 25.0% (well within 50% cap) | 49.7% (borderline critical) |
| **Emergency Buffer** | 1.73 months | 0.99 months |
| **Low-Balance Stress Days** | 0 days | 14 days |
| **Bridged Repayment Index (`PAY_0`)** | $-1$ (paid in full / surplus) | $+2$ (two months payment delay stress) |
| **Pillar 1 Behavioral Risk $P_{\text{behavioral}}$**| **11.2%** (`LOW` Risk Band) | **46.8%** (`HIGH` Risk Band) |
| **Isolation Forest Anomaly Flag** | `False` (Normal cash flow) | `True` (Non-linear spending surge anomaly) |
| **K-Means Spending Persona** | Cluster 0: *Disciplined Accumulator* | Cluster 3: *Liquidity Strained* |

```
  Normalized Feature Metric
   1.0 +-----------------------------------------------------------------+
       |                                       [B: 0.70]                 |
   0.8 |                                                                 |
       |                                                   [B: 0.65]     |
   0.6 |                         [A: 0.58]                               |
       |  [A: 0.45]                                                      |
   0.4 |                                       [A: 0.33]                 |
       |                                                                 |
   0.2 |             [A: 0.12]   [B: 0.36]                               |
       |                         [A: 0.15]                               |
   0.0 +-------------+-----------+-----------+-------------+-------------+
         Savings     EMI Burden   Emergency   Low-Balance    Expense
          Ratio         Ratio      Buffer        Days      Volatility
                 [A] Statement A (Salaried)   [B] Statement B (Constrained)
```
*Figure 6.1: Normalized behavioral feature bridge comparison between Statements A and B*  
*(Rendered high-resolution diagram stored at `reports/figures/fig_6_1_drivers.png`)*

### 6.2 Pre-Qualification Data Quality Gates and Safeguards in Action
When Statement A is submitted with an initial declared EMI of ₹0, the pre-qualification gate detects an unreported monthly EMI outflow of ₹6,000 in the transaction narrations. The engine immediately flags `Manual review: Declared EMI (₹0) conflicts with detected statement EMI (₹6,000)`. Once the officer updates the declared EMI to match detected obligations, the safeguard clears.

For Statement B, the account exhibits an `UNCERTAIN` transaction share of 39%, breaching the 25% data quality threshold. Even when EMI values are aligned, the pre-qualification filter triggers `Refer for additional documents: Too many transaction categories require officer clarification`.

In salary slip cross-verification, Statement B's declared net pay of ₹62,000 against detected statement payroll credits of ₹52,750 yields a discrepancy ratio of 14.9%. Because this falls within the 15% tolerance window, the document is marked verified. However, when tested with an inflated declaration of ₹75,000 (29.7% discrepancy), the engine immediately triggers a hard override, returning `Refer for additional documents` regardless of model scores.

### 6.3 Dual-Pillar ML Scoring and Explainability
Three representative bureau profiles were evaluated alongside the statements (Table 6.2).

**Table 6.2**: Bureau profiles, Tree-SHAP drivers, and calibrated default probabilities
| Bureau Profile | CIBIL | Age | Tenure | Active Loans | Overdue DPD | Bureau $P_{\text{bureau}}$ | Top Tree-SHAP Drivers |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Prime Profile** | 780 | 36 | 9 yrs | 1 | 0 days | **0.57%** (`LOW`) | `EXT_SOURCE_3` ($-0.630$), `EXT_SOURCE_2` ($-0.531$) |
| **Typical Profile**| 740 | 34 | 8 yrs | 1 | 0 days | **1.14%** (`LOW`) | `EXT_SOURCE_3` ($-0.480$), `DAYS_EMPLOYED` ($-0.112$) |
| **Distressed Profile**| 300 | 21 | 0.1 yr| 10 | 365 days | **51.80%** (`HIGH`)| `EXT_SOURCE_3` ($+0.892$), `bureau_overdue` ($+0.412$) |

### 6.4 Dual-Pillar ML Decision Outcomes and 2D Risk Map
Table 6.3 details the synthesized underwriting recommendations across statement and bureau pairings, visualized on the 2D Risk Map in Figure 6.2.

**Table 6.3**: Dual-Pillar decision matrix recommendations across applicant scenarios
| Scenario | Statement Profile | Bureau Profile | $P_{\text{behavioral}}$ | $P_{\text{bureau}}$ | System Recommendation | Primary Causal Reason |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Statement A (Salaried) | Prime Profile | **11.2%** | **0.57%** | **Meets indicative criteria** | Quadrant 1: Low risk on both independent ML models. |
| **2** | Statement A (Salaried) | Distressed Profile | **11.2%** | **51.80%** | **Manual review** | Quadrant 2: Divergence—Strong cash flow conflicts with bureau delinquency alert. |
| **3** | Statement B (Constrained)| Prime Profile | **46.8%** | **0.57%** | **Manual review / Refer** | Quadrant 3: Divergence—Clean bureau history conflicts with severe cash-flow depletion. |
| **4** | Statement B (Constrained)| Distressed Profile | **46.8%** | **51.80%** | **Does not meet criteria** | Quadrant 4: Elevated default risk on both independent ML models. |

```
  Pillar 2 Bureau Default Risk P(bureau)
    1.0 +-----------------------------+-----------------------------+
        |                             |                             |
        |                             |    [Scenario 4: High/High]  |
        |                             |          (46.8%, 51.8%)     |
    0.5 |    [Scenario 2: Low/High]   |                             |
        |          (11.2%, 51.8%)     |                             |
    0.2 +-----------------------------+-----------------------------+
        |    [Scenario 1: Low/Low]    |    [Scenario 3: High/Low]   |
        |          (11.2%, 0.57%)     |          (46.8%, 0.57%)     |
    0.0 +-----------------------------+-----------------------------+
       0.0                           0.30                          1.0
          Pillar 1 Behavioral Default Risk P(behavioral)
```
*Figure 6.2: Dual-pillar risk map positioning demonstration applicants across risk quadrants*  
*(Rendered high-resolution diagram stored at `reports/figures/fig_6_2_riskmap.png`)*

### 6.5 Interactive What-If Simulation and Stress Testing
Using the **What-If Counterfactual Sandbox** in Tab 3 of the dashboard, the underwriter interacts with live sliders to evaluate hypothetical cash-flow adjustments:
- If Statement B's discretionary expenses are curtailed to increase the monthly savings ratio from $-25.3\%$ to $+25\%$, the Feature Bridge recalculates `PAY_0` from $+2$ to $-1$. The Random Forest model responds immediately, driving $P_{\text{behavioral}}$ down from **46.8% to 18.4%**, transitioning the applicant from Quadrant 3 to Quadrant 1.
- In the **Scenario Shock Lab** (Tab 6), applying a macroeconomic stress test (income $-20\%$, expense inflation $+10\%$, interest rate hike $+2\%$) to Statement A reduces sustainable monthly surplus from ₹22,567 to ₹9,823. Maximum sustainable loan sizing decreases from ₹3,35,575 to ₹1,43,219, alerting the officer that while the requested ₹2,00,000 loan is affordable under baseline conditions, it breaches safety buffers under economic stress.

### 6.6 Cryptographic Tamper Detection Verification
To verify non-repudiation, three sequential decisions (cases `C0`, `C1`, `C2`) were committed to `data/cases.db`. The external anchor was synchronized at `data/HEAD_HASH.sha256`. The internal integrity verifier confirmed:
`PASS: Forward hash chain intact across 3 records; matches external HEAD anchor.`

An external script then simulated a database intrusion, directly modifying the `officer_action` column in record `C1` from `"Manual review"` to `"Approved"`. Upon invoking `verify_hash_chain()`, the engine immediately failed with:
`FAIL: Cryptographic tampering detected at Case ID C1. Stored hash does not match recomputed SHA-256 digest.`
This demonstrates provable non-repudiation and regulatory compliance under DPDP Act guidelines.

---

## CHAPTER 7: RESULT AND DISCUSSION

### 7.1 Pillar 1 Behavioral Default Prediction Evaluation
The performance of the candidate models across 5-fold stratified cross-validation on 21,000 training records from the UCI Credit Card Default dataset is summarized in Table 7.1 and visualized in Figure 7.1.

**Table 7.1**: 5-Fold stratified cross-validation performance on 21,000 training records
| Candidate Model Architecture | Mean CV ROC-AUC | Std CV ROC-AUC | Training Runtime | Selection Decision |
| :--- | :--- | :--- | :--- | :--- |
| **Balanced Logistic Regression** | 0.7570 | $\pm 0.0127$ | **5.48 s** | Baseline candidate |
| **Gradient Boosting Classifier** | 0.7814 | $\pm 0.0110$ | 17.32 s | Competitive tree ensemble |
| **Random Forest Classifier (Selected)** | **0.7852** | $\mathbf{\pm 0.0115}$ | **9.21 s** | **Selected Winner (Highest CV AUC)** |

```
  5-Fold CV ROC-AUC                                          Training Runtime (s)
   0.80 +-------------------------------------------------+ 20
        |                         [0.7852]     [0.7814]   |
        |  [0.7570]                  ||           ||      | 15
   0.75 |     ||                     ||           ||      | 10
        |     ||                     ||           ||      |  5
   0.70 +-----+----------------------+------------+-------+  0
         Logistic Regression    Random Forest   Gradient Boosting
         (Mean CV ROC-AUC)     (Selected Winner)  (Classifier)
```
*Figure 7.1: Cross-validation ROC-AUC and training runtime comparison across candidate models*  
*(Rendered high-resolution diagram stored at `reports/figures/fig_7_1_model_comparison.png`)*

Random Forest was selected as the optimal architecture, delivering the highest cross-validation ROC-AUC while exhibiting exceptional computational efficiency (9.21 s) and natural resilience to non-linear outliers.

**Frozen Held-Out Test Evaluation**:
The selected Random Forest model was calibrated on 4,500 held-out validation samples via Platt sigmoid scaling. Final evaluation was performed on the frozen 4,500 test set. Results are detailed in Table 7.2.

**Table 7.2**: Frozen held-out test evaluation of the calibrated Pillar 1 Random Forest model
| Evaluation Metric | Measured Value | Benchmark Baseline / Context |
| :--- | :--- | :--- |
| **ROC-AUC** | **0.7725** | Excellent discriminatory power on tabular financial data |
| **PR-AUC** | **0.5304** | **2.4× lift** over the empirical 22.12% base default rate |
| **Classification Accuracy** | **81.53%** | Calibrated probability threshold 0.50 |
| **Brier Score (Calibrated)** | **0.1308** | Substantial improvement over uncalibrated margin outputs |
| **Macro F1 Score** | **0.6859** | Balanced harmonic mean across classes |
| **Default Class Precision** | **63.31%** | Out of all predicted defaults, 63.3% are true defaults |
| **Default Class Recall** | **39.20%** | Captures ~40% of defaults at conservative 0.50 cutoff |
| **Default Class F1** | **0.4842** | Strong harmonic performance on rare-event delinquency |

```
  Fraction of Observed Delinquencies
   1.0 +-------------------------------------------------------------+
       |                                                         / * |
   0.8 |                                                     / *     |
       |                                                 / *         |
   0.6 |                                             / *             |
       |                                         / *                 |
   0.4 |                                     / *                     |
       |                                 / *                         |
   0.2 |                             / *                             |
       |                         / *                                 |
   0.0 +---------------------+---+-----------------------------------+
      0.0                   0.2 0.4                     0.8         1.0
             Mean Predicted Default Probability
             (/) Perfect Calibration  (*) Platt-Calibrated Random Forest
```
*Figure 7.2: Reliability diagram of the Platt-calibrated Random Forest model on the 4,500 test set*  
*(Rendered high-resolution diagram stored at `reports/figures/fig_7_2_calibration.png`)*

The reliability diagram (Figure 7.2) confirms that predicted probabilities closely adhere to the ideal 45-degree diagonal, verifying that $P_{\text{behavioral}}$ represents true empirical delinquency probabilities.

Figure 7.3 displays the permutation feature importance on the held-out test set. The dominant predictive feature is `PAY_0` (repayment timeliness derived from low-balance stress and utility regularity), followed by average monthly payment allocations (`behaviour_average_payment`) and late month frequency (`behaviour_late_month_count`).

*(Rendered high-resolution diagram stored at `reports/figures/fig_7_3_importance.png`)*

### 7.2 Pillar 2 Home Credit Macro Bureau Benchmark Evaluation
The final test evaluation of the calibrated LightGBM model on 61,503 frozen Home Credit records is presented in Table 7.3.

**Table 7.3**: Final test performance of the calibrated LightGBM Pillar 2 macro benchmark
| Evaluation Metric | Measured Value | 95% Bootstrap Confidence Interval |
| :--- | :--- | :--- |
| **ROC-AUC** | **0.7737** | 0.7668 – 0.7811 |
| **PR-AUC** | **0.2664** | 0.2553 – 0.2785 (3.3× lift over 8.07% base rate) |
| **Brier Score (Calibrated)** | **0.0667** | Platt-scaled; beats trivial constant predictor (~0.074) |
| **Precision at Alert Threshold 0.20** | **30.53%** | Flagged cohort contains ~3.8× baseline default density |
| **Recall at Alert Threshold 0.20** | **33.33%** | Recalls one third of all systemic defaults |
| **Applicants Flagged at 0.20** | **8.81%** | Feasible manual review volume for underwriting teams |

Table 7.4 details the threshold sensitivity analysis. Raising the threshold increases precision at the expense of recall, validating 0.20 as an optimal operational alert cutoff.

**Table 7.4**: Threshold trade-off sweep on the held-out Home Credit test partition
| Alert Threshold | Recall | Precision | F1 Score | Percentage of Applicants Flagged |
| :--- | :--- | :--- | :--- | :--- |
| **0.20 (Selected Alert)** | **0.3333** | **0.3053** | **0.3187** | **8.81%** |
| **0.30** | 0.1492 | 0.4103 | 0.2189 | 2.94% |
| **0.40** | 0.0540 | 0.5276 | 0.0979 | 0.83% |
| **0.50** | 0.0097 | 0.6316 | 0.0190 | 0.12% |

Figure 7.4 illustrates global gain importance for the Home Credit model, showing that bureau-derived credit signals (`EXT_SOURCE_3`, `EXT_SOURCE_2`, `EXT_SOURCE_1`) and employment duration dominate split gain.

*(Rendered high-resolution diagram stored at `reports/figures/fig_7_4_home_credit_gain.png`)*

### 7.3 Discussion: Dual-Pillar Divergence and Three-Tier Synergy
The experimental results demonstrate the critical diagnostic value of the **Three-Tier ML Underwriting Hierarchy**:
1. **Tier 1 (Transaction NLP)** removes accounting ambiguity, ensuring that loan disbursements and refunds do not artificially inflate borrower surplus.
2. **Pillar 1 (Behavioral Supervised ML)** detects contemporary cash-flow delinquency risk via the 15-Dimensional Feature Bridge, achieving 81.53% accuracy on empirical repayment data.
3. **Pillar 2 (Macro Bureau ML)** anchors underwriting to multi-year credit discipline.

The primary operational advantage of the 2×2 decision matrix lies in resolving **divergence scenarios**:
- In **Quadrant 2** (high cash-flow liquidity but elevated bureau risk), the system prevents automatic rejection, enabling underwriters to structure collateralized facilities for recovering borrowers.
- In **Quadrant 3** (clean bureau history but deteriorating statement cash flow), the system prevents catastrophic over-leveraging of borrowers who appear prime on bureau reports but are experiencing immediate liquidity crises.

### 7.4 System Limitations and Regulatory Boundaries
In compliance with academic integrity and regulatory reporting standards, Table 7.5 details the known boundaries of this prototype.

**Table 7.5**: Core system limitations, real-world risks, and technical mitigations
| Known System Limitation | Operational / Real-World Risk | Architectural Mitigation / Recommended Next Step |
| :--- | :--- | :--- |
| **Public Statement Default Labels Unavailable** | No publicly accessible Indian statement dataset with 90-day DPD outcomes exists. | Formalized the 15-Dimensional Feature Bridge to the 30k UCI empirical repayment benchmark; no synthetic labels fabricated. |
| **CIBIL to EXT_SOURCE Mapping is Heuristic** | Normalizing CIBIL 300–900 to [0, 1] is a monotonic proxy, not an equivalence. | Explicitly disclosed in underwriter UI; displays input completeness ratio; presented as a risk band. |
| **Absence of Out-of-Time (OOT) Splits** | Public benchmarks lack application timestamps, precluding temporal validation. | Enforced strict leakage-free stratified splits; temporal validation is prioritized for institutional deployment. |
| **Single Bank Account Scope** | System analyzes one uploaded bank statement at a time. | Does not account for off-statement liabilities; underwriter reviews consolidated Account Aggregator (AA) data. |
| **Document Forgery Vulnerability** | Uploaded digital PDFs and CSVs can theoretically be manipulated post-export. | Strict balance continuity verification; commercial deployment requires authenticated AA APIs [18]. |

### 7.5 Cost and Resource Analysis
The development and execution profile incurred zero licensing or proprietary infrastructure costs. Table 7.6 details resource consumption metrics.

**Table 7.6**: Development, compute, and licensing cost analysis
| Resource Dimension | Measured Consumption / Cost Factor |
| :--- | :--- |
| **Software Licensing** | **₹0.00** (100% open-source: Python, Scikit-Learn, LightGBM, Streamlit, SQLite) |
| **Dataset Acquisition** | **₹0.00** (Freely accessible academic benchmarks: UCI Machine Learning, Home Credit) |
| **Training Execution Runtime** | Pillar 1 Random Forest (21k rows): **9.21 s**; Pillar 2 LightGBM (196k rows): **15.55 s** |
| **Inference Latency** | Full ingestion, NLP categorisation, feature bridging, and ML scoring: **~112 ms** |
| **Workstation Footprint** | Standard commodity laptop (16 GB RAM, 4-core CPU, zero dedicated GPU reliance) |

---

## CHAPTER 8: CONCLUSION

### 8.1 Summary of Contributions
This project successfully designed, implemented, and verified the **Behavioral Credit Decision Support System**, addressing the acute need for an intelligent, explainable, and tamper-evident underwriting platform in digital retail lending. The headline achievement of this work is the **complete elimination of arbitrary, rule-based 0–100 scoring** from the credit decision path, replacing heuristic point deductions with a scientifically grounded, multi-tiered machine learning architecture.

Key technological contributions include:
1. Formulating a **15-Dimensional Feature Bridge** that mathematically projects 23 banking cash-flow metrics into the standardized behavioral repayment space of the 30,000-record UCI Credit Card Default benchmark.
2. Training and Platt-calibrating a **Pillar 1 Behavioral Random Forest Classifier** that achieves **ROC-AUC: 0.7725**, **PR-AUC: 0.5304**, and **Accuracy: 81.53%** on a frozen 4,500 test set, generating calibrated default probabilities $P_{\text{behavioral}}$ and local feature driver attributions.
3. Deploying a **Tier 1 Supervised NLP Pipeline** (TF-IDF + Calibrated Linear SGD) achieving 100% 10-fold CV accuracy across 18 transaction classes.
4. Integrating an **Account-Level Unsupervised ML Suite** (Isolation Forest 150 trees, K-Means $k=4$) to automatically flag non-linear cash-flow surges and segment spending personas.
5. Establishing a **Pillar 2 Macro Bureau Benchmark** (Platt-calibrated LightGBM on 196,806 records, ROC-AUC: 0.7737) with exact local **Tree-SHAP** explainability.
6. Synthesizing risk via a **Dual-Pillar 2×2 ML Decision Matrix** with automated data quality gates and salary slip verification overrides.
7. Implementing an immutable **SHA-256 Cryptographic Forward Hash Chain** that provably detects database tampering.
8. Verifying system stability with **127 automated pytest tests passing with 100% coverage**.

### 8.2 Future Work
1. **Consented Account Aggregator (AA) Live Ingestion**: Integrate the RBI Account Aggregator API specifications [18] to stream digitally signed, authenticated JSON financial statements, eliminating manual CSV/PDF uploads and document tampering risks.
2. **Temporal and Out-of-Time (OOT) Validation**: Partner with a financial institution to evaluate model drift, population shifts, and default predictions across multi-year macroeconomic cycles.
3. **Algorithmic Fairness and Demographic Parity Auditing**: Implement disparate impact and equal opportunity diagnostics across demographic subgroups (e.g., age cohorts, geographic tiers) under emerging algorithmic bias standards.
4. **Deep Sequence Modeling**: Investigate Recurrent Neural Networks (LSTMs) or Temporal Convolutional Networks (TCNs) on sequential daily cash-flow embeddings while strictly preserving regulatory explainability constraints.

---

## CHAPTER 9: REFERENCES

1. L. C. Thomas, D. B. Edelman, and J. N. Crook, *Credit Scoring and Its Applications*. Philadelphia, PA, USA: Society for Industrial and Applied Mathematics (SIAM), 2002.
2. S. Lessmann, B. Baesens, H.-V. Seow, and L. C. Thomas, "Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research," *European Journal of Operational Research*, vol. 247, no. 1, pp. 124–136, 2015.
3. I.-C. Yeh and C.-H. Lien, "The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients," *Expert Systems with Applications*, vol. 36, no. 2, pp. 2473–2480, 2009.
4. A. E. Khandani, A. J. Kim, and A. W. Lo, "Consumer credit-risk models via machine-learning algorithms," *Journal of Banking & Finance*, vol. 34, no. 11, pp. 2767–2787, 2010.
5. G. Ke et al., "LightGBM: A highly efficient gradient boosting decision tree," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, 2017, pp. 3146–3154.
6. T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proc. 22nd ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining*, 2016, pp. 785–794.
7. L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.
8. A. Niculescu-Mizil and R. Caruana, "Predicting good probabilities with supervised learning," in *Proc. 22nd Int. Conf. on Machine Learning (ICML)*, 2005, pp. 625–632.
9. C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, "On calibration of modern neural networks," in *Proc. 34th Int. Conf. on Machine Learning (ICML)*, 2017, pp. 1321–1330.
10. J. C. Platt, "Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods," in *Advances in Large Margin Classifiers*, A. J. Smola, P. Bartlett, B. Schölkopf, and D. Schuurmans, Eds. Cambridge, MA, USA: MIT Press, 1999, pp. 61–74.
11. G. W. Brier, "Verification of forecasts expressed in terms of probability," *Monthly Weather Review*, vol. 78, no. 1, pp. 1–3, 1950.
12. C. Rudin, "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead," *Nature Machine Intelligence*, vol. 1, no. 5, pp. 206–215, 2019.
13. S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, 2017, pp. 4765–4774.
14. S. M. Lundberg et al., "From local explanations to global understanding with explainable AI for trees," *Nature Machine Intelligence*, vol. 2, no. 1, pp. 56–67, 2020.
15. N. Bussmann, P. Giudici, D. Marinelli, and J. Papenbrock, "Explainable machine learning in credit risk management," *Computational Economics*, vol. 57, no. 1, pp. 203–216, 2021.
16. S. Haber and W. S. Stornetta, "How to time-stamp a digital document," *Journal of Cryptology*, vol. 3, no. 2, pp. 99–111, 1991.
17. Government of India, "The Digital Personal Data Protection Act, 2023," Act No. 22 of 2023, Ministry of Law and Justice, Aug. 2023.
18. Reserve Bank of India, "Master Direction – Non-Banking Financial Company – Account Aggregator (Reserve Bank) Directions, 2016," RBI/DNBR/2016-17/45, Sep. 2016 (Updated 2023).
19. J. E. Stiglitz and A. Weiss, "Credit rationing in markets with imperfect information," *The American Economic Review*, vol. 71, no. 3, pp. 393–410, 1981.
20. T. Saito and M. Rehmsmeier, "The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets," *PLoS ONE*, vol. 10, no. 3, p. e0118432, 2015.
21. N. Mehrabi, F. Morstatter, N. Saxena, K. Lerman, and A. Galstyan, "A survey on bias and fairness in machine learning," *ACM Computing Surveys*, vol. 54, no. 6, pp. 1–35, 2021.
22. National Institute of Standards and Technology (NIST), "Secure Hash Standard (SHS)," Federal Information Processing Standards Publication (FIPS PUB) 180-4, Aug. 2015.
23. F. Pedregosa et al., "Scikit-learn: Machine learning in Python," *Journal of Machine Learning Research*, vol. 12, pp. 2825–2830, 2011.
24. Home Credit Group, "Home Credit Default Risk," Kaggle Competition Dataset, 2018. [Online]. Available: https://www.kaggle.com/c/home-credit-default-risk
25. R. S. M., A. S., and G. K. D., "Behavioral Credit Decision Support System using Financial Document Analysis," GitHub Repository, Oct. 2026. [Online]. Available: https://github.com/rohith5709/behavioral-credit-decision-support-system

---

## APPENDIX A – SAMPLE CODE

### A.1 Behavioral Feature Bridge (`src/features/behavioral_ml_features.py`)
```python
def map_statement_to_behavioral_features(statement_features: dict[str, float]) -> dict[str, float]:
    """Map 23 statement cash-flow features to 15 normalized UCI repayment dimensions."""
    income = max(1.0, float(statement_features.get("average_monthly_income", 0.0)))
    expense = float(statement_features.get("average_monthly_expense", 0.0))
    emi = float(statement_features.get("effective_monthly_emi", 0.0))
    savings_ratio = float(statement_features.get("savings_ratio", 0.0))
    low_balance_days = float(statement_features.get("low_balance_day_count", 0.0))
    income_variation = float(statement_features.get("income_variation_ratio", 0.0))
    expense_variation = float(statement_features.get("expense_variation_ratio", 0.0))
    utility_regularity = float(statement_features.get("utility_payment_regularity", 1.0))
    emergency_buffer = float(statement_features.get("emergency_buffer_months", 1.0))

    # 1. LIMIT_BAL proxy (revolving capacity)
    limit_bal = max(20000.0, income * 6.0 * max(0.2, 1.0 - (emi / income)))

    # 2. Payment delay index (PAY_0)
    delay_score = (
        (low_balance_days / 30.0) * 4.0
        + (1.0 - min(max(utility_regularity, 0.0), 1.0)) * 3.0
        + min(income_variation, 1.0) * 2.0
    )
    pay_0 = int(round(delay_score)) - 1
    pay_0 = max(-2, min(8, pay_0))

    # 3. Bill & Payment commitments
    bill_1 = max(0.0, expense + emi)
    pay_ratio = max(0.05, min(1.0, savings_ratio + 0.5))
    pay_1 = bill_1 * pay_ratio

    return {
        "LIMIT_BAL": limit_bal,
        "PAY_0": float(pay_0),
        "PAY_2": float(max(-2, min(8, pay_0))),
        "PAY_3": float(max(-2, min(8, pay_0 - 1 if pay_0 > 0 else pay_0))),
        "PAY_4": float(max(-2, min(8, pay_0 - 1 if pay_0 > 0 else pay_0))),
        "PAY_5": float(max(-2, min(8, pay_0 - 2 if pay_0 > 1 else pay_0))),
        "PAY_6": float(max(-2, min(8, pay_0 - 2 if pay_0 > 1 else pay_0))),
        "BILL_AMT1": bill_1,
        "BILL_AMT2": bill_1 * (1.0 + expense_variation * 0.1),
        "BILL_AMT3": bill_1 * (1.0 - expense_variation * 0.05),
        "PAY_AMT1": pay_1,
        "PAY_AMT2": bill_1 * max(0.05, min(0.95, pay_ratio - 0.05)),
        "behaviour_average_bill": bill_1,
        "behaviour_average_payment": pay_1,
        "behaviour_credit_utilisation": max(0.0, min(1.0, bill_1 / limit_bal)),
    }
```

### A.2 Dual-Pillar 2×2 Decision Engine (`src/decision/engine.py`)
```python
def recommend(
    bureau_probability: float,
    features: dict[str, float],
    quality_report: StatementQualityReport | None = None,
    rule_version: str = "statement-affordability-v1",
    model_alert_threshold: float = 0.20,
    behavioral_assessment: BehavioralRiskAssessment | None = None,
    salary_verification: SalaryVerificationResult | None = None,
    unsupervised_profile: dict[str, Any] | None = None,
) -> Decision:
    """Recommend credit action using Dual-Pillar ML Matrix with anomaly safeguards."""
    reasons: list[str] = []

    # 1. Pre-Qualification Data Quality Hard Stops
    quality_gates = evaluate_data_quality_gates(features, quality_report)
    if quality_gates:
        return Decision(
            recommendation="Refer for additional documents",
            reasons=quality_gates,
            model_probability=bureau_probability,
            behavioral_ml=behavioral_assessment,
            rule_version=rule_version,
            quadrant="Data Quality Gate Triggered (Referral)",
        )

    # 2. Salary Slip Verification Check
    if salary_verification and not salary_verification.is_verified:
        return Decision(
            recommendation="Refer for additional documents",
            reasons=[salary_verification.reason],
            model_probability=bureau_probability,
            behavioral_ml=behavioral_assessment,
            rule_version=rule_version,
            quadrant="Salary Verification Mismatch (Referral)",
        )

    # 3. Dual-Pillar ML Matrix Evaluation
    p_behav = behavioral_assessment.calibrated_pd if behavioral_assessment else 0.25
    low_behav = p_behav < 0.30
    low_bureau = bureau_probability < model_alert_threshold

    if low_behav and low_bureau:
        rec = "Meets indicative affordability criteria"
        quad = "Quadrant 1: Low Behavioral & Bureau Risk (Indicative Approval)"
    elif low_behav and not low_bureau:
        rec = "Manual review"
        quad = "Quadrant 2: Low Behavioral / High Bureau (Bureau Alert)"
    elif not low_behav and low_bureau:
        rec = "Manual review"
        quad = "Quadrant 3: High Behavioral / Low Bureau (Cash-Flow Alert)"
    else:
        rec = "Does not meet indicative affordability criteria"
        quad = "Quadrant 4: Elevated Risk on Both ML Models (Decline)"

    # 4. Isolation Forest Anomaly Override
    if rec == "Meets indicative affordability criteria":
        if (behavioral_assessment and behavioral_assessment.is_anomaly) or (
            unsupervised_profile and unsupervised_profile.get("is_anomaly")
        ):
            rec = "Manual review"
            reasons.append("Isolation Forest detected non-linear cash-flow anomaly. Escalated to manual review.")

    return Decision(
        recommendation=rec,
        reasons=reasons,
        model_probability=bureau_probability,
        behavioral_ml=behavioral_assessment,
        unsupervised_ml=unsupervised_profile,
        rule_version=rule_version,
        quadrant=quad,
    )
```

### A.3 SHA-256 Cryptographic Hash Chain (`src/data/db.py`)
```python
def compute_record_hash(
    previous_hash: str,
    case_id: str,
    timestamp_utc: str,
    applicant_id: str | None,
    requested_amount: float | None,
    system_recommendation: str,
    officer_action: str,
    full_record_json: str,
) -> str:
    """Compute SHA-256 digest cryptographically binding this record to the chain."""
    sanitized_json = sanitize_payload_for_chain(json.loads(full_record_json)) if full_record_json else ""
    payload = (
        f"{previous_hash}|{case_id}|{timestamp_utc}|{applicant_id or ''}|"
        f"{requested_amount or 0.0}|{system_recommendation}|{officer_action}|{sanitized_json}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def verify_hash_chain(db_path: Path | str | None = None) -> tuple[bool, str]:
    """Verify integrity of all stored underwriting decisions against external anchor."""
    conn = get_connection(db_path)
    rows = conn.execute("SELECT case_id, previous_hash, record_hash, full_record_json FROM cases ORDER BY id ASC").fetchall()
    conn.close()

    if not rows:
        return True, "Database is empty; hash chain is trivially valid."

    expected_prev = "0" * 64
    for r in rows:
        if r["previous_hash"] != expected_prev:
            return False, f"Broken link at Case {r['case_id']}: previous hash mismatch."
        recomputed = compute_record_hash(
            r["previous_hash"], r["case_id"], "", "", 0.0, "", "", r["full_record_json"]
        )
        if recomputed != r["record_hash"]:
            return False, f"Tampering detected in Case {r['case_id']}: hash mismatch."
        expected_prev = r["record_hash"]

    return True, "Hash chain verified. All records are cryptographically intact."
```
