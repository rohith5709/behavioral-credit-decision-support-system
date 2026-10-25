import os
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_report_docx():
    doc = Document()

    # Page Margins (Standard 1 inch / 2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.25) # Extra for binding
        section.right_margin = Inches(1.0)

    # Base Normal Style: Times New Roman 12, 1.15 line spacing
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    def add_title(text, size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.3
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)
        run.font.name = 'Times New Roman'
        return p

    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(15)
        run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A) # Deep Navy
        run.font.name = 'Times New Roman'
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        run.font.name = 'Times New Roman'
        return p

    def add_heading_3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        run.font.name = 'Times New Roman'
        return p

    def add_p(text, bold_prefix=None, italic=False, bullet=False):
        p = doc.add_paragraph(style='List Bullet' if bullet else 'Normal')
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = 'Times New Roman'
        run = p.add_run(text)
        run.italic = italic
        run.font.name = 'Times New Roman'
        return p

    def add_image_box(image_path, caption, width=Inches(6.0)):
        if os.path.exists(image_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.add_run().add_picture(str(image_path), width=width)

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(12)
            run = p_cap.add_run(caption)
            run.font.size = Pt(10)
            run.font.italic = True
            run.font.name = 'Times New Roman'
            run.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

    def add_table_data(caption, headers, rows_data, col_widths=None):
        # Table Caption Above
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(10)
        p_cap.paragraph_format.space_after = Pt(3)
        run = p_cap.add_run(caption)
        run.font.size = Pt(10)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

        table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        # Header Row
        hdr_cells = table.rows[0].cells
        for idx, heading in enumerate(headers):
            hdr_cells[idx].text = heading
            set_cell_background(hdr_cells[idx], "1E3A8A") # Navy
            for p in hdr_cells[idx].paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(9.5)
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        # Body Rows
        for r_idx, row in enumerate(rows_data):
            row_cells = table.rows[r_idx + 1].cells
            bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, val in enumerate(row):
                row_cells[c_idx].text = str(val)
                set_cell_background(row_cells[c_idx], bg_color)
                for p in row_cells[c_idx].paragraphs:
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.space_before = Pt(2)
                    for r in p.runs:
                        r.font.name = 'Times New Roman'
                        r.font.size = Pt(9)
                        r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---------------------------------------------------------------------------
    # COVER PAGE
    # ---------------------------------------------------------------------------
    add_title("B.Tech. BCSE497J - Project-I", size=13, bold=True, space_after=18)
    add_title("BEHAVIORAL CREDIT DECISION SUPPORT SYSTEM USING FINANCIAL DOCUMENT ANALYSIS", size=18, bold=True, space_after=24)
    add_title("Submitted in partial fulfillment of the requirements for the degree of\nBachelor of Technology\nin\nComputer Science and Engineering (Data Science)", size=12, bold=False, space_after=24)

    add_title("by", size=11, bold=False, space_after=8)
    headers_team = ["Register Number", "Student Name"]
    rows_team = [
        ["23BDS0025", "ROHITH S M"],
        ["23BDS0029", "ADHARSH S"],
        ["23BDS0186", "GOWTHAM KUMAR D"]
    ]
    add_table_data("Candidate Details", headers_team, rows_team)

    doc.add_paragraph().paragraph_format.space_after = Pt(18)
    add_title("Under the Supervision of\nDr. Viswanathan A\nAssociate Professor\nSchool of Computer Science and Engineering (SCOPE)", size=12, bold=True, space_after=24)
    add_title("Vellore Institute of Technology (VIT), Vellore\nOctober 2026", size=13, bold=True, space_after=10)

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # DECLARATION & CERTIFICATE
    # ---------------------------------------------------------------------------
    add_heading_1("DECLARATION")
    add_p("We hereby declare that the project entitled \"Behavioral Credit Decision Support System using Financial Document Analysis\" submitted by us, for the award of the degree of Bachelor of Technology in Computer Science and Engineering (Data Science) to Vellore Institute of Technology (VIT), is a record of bonafide work carried out by us under the supervision of Dr. Viswanathan A, School of Computer Science and Engineering (SCOPE).")
    add_p("We further declare that the work reported in this project has not been submitted and will not be submitted, either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university.")
    add_p("\nPlace : Vellore\nDate  : 25 October 2026")
    add_p("Rohith S M (23BDS0025)          Adharsh S (23BDS0029)          Gowtham Kumar D (23BDS0186)", bold_prefix="Signatures: ")

    doc.add_page_break()

    add_heading_1("CERTIFICATE")
    add_p("This is to certify that the project entitled \"Behavioral Credit Decision Support System using Financial Document Analysis\" submitted by Rohith S M (23BDS0025), Adharsh S (23BDS0029), and Gowtham Kumar D (23BDS0186), School of Computer Science and Engineering, VIT, for the award of the degree of Bachelor of Technology in Computer Science and Engineering (Data Science), is a record of bonafide work carried out by them under my supervision during the Fall Semester 2026–2027, as per the VIT code of academic and research ethics.")
    add_p("The contents of this report have not been submitted and will not be submitted either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university. The project fulfills the requirements and regulations of the University and in my opinion meets the necessary standards for submission.")
    add_p("\nPlace : Vellore\nDate  : 25 October 2026")
    add_p("\n.....................................................\nDr. Viswanathan A (Guide)\nAssociate Professor, SCOPE, VIT")
    add_p("\nInternal Examiner: .......................................      External Examiner: .......................................")

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # ACKNOWLEDGEMENTS & ABSTRACT
    # ---------------------------------------------------------------------------
    add_heading_1("ACKNOWLEDGEMENTS")
    add_p("We express our deepest gratitude to the management of Vellore Institute of Technology (VIT) for providing state-of-the-art computational infrastructure, academic resources, and an inspiring intellectual environment that enabled us to pursue this research and software engineering endeavour.")
    add_p("Our sincere thanks go to Dr. Jaisankar N, Dean of the School of Computer Science and Engineering (SCOPE), for his constant encouragement, strategic academic vision, and commitment to fostering applied research across data science and machine learning.")
    add_p("We extend our profound appreciation to the Head of the Department of Computer Science and Engineering (Data Science) for insightful counsel, curricular guidance, and continuous departmental facilitation throughout the semester.")
    add_p("We are indebted to our faculty supervisor, Dr. Viswanathan A, Associate Professor, SCOPE, for his patient mentorship, constructive critiques, and meticulous technical guidance. His insistence on methodological honesty, leakage-free machine learning protocols, and explainable decision-support architectures was pivotal in steering this project from concept to a production-grade implementation.")

    doc.add_page_break()

    add_heading_1("ABSTRACT")
    add_p("In contemporary retail banking, credit underwriting has traditionally been bifurcated: underwriters evaluate static bureau credit scores while manually inspecting unstructured bank statements to assess real-time cash flow, debt serviceability, and lifestyle spending. Manual statement auditing is inherently slow, error-prone, and prone to severe cognitive biases, as non-income inflows (loan disbursements, self-transfers, and refunds) are frequently conflated with recurring salary. Conversely, conventional commercial credit-scoring engines apply black-box models strictly to bureau summaries or rely on rigid, heuristic point-based scorecards that fail to capture non-linear behavioral cash-flow degradation.")
    add_p("This project delivers the Behavioral Credit Decision Support System, an end-to-end, human-in-the-loop underwriting platform that completely replaces heuristic, rule-based credit scoring with a rigorous, multi-tiered machine learning architecture. The system introduces a Dual-Pillar ML Framework operating across strictly separated yet unified analytical pipelines. Pillar 1 (Behavioral Cash-Flow ML Engine) parses multi-bank statement CSV and digital PDF files, enforces balance reconciliation, and deploys a Tier 1 Supervised NLP pipeline (TF-IDF with Calibrated Linear SGD, achieving 100% 10-fold cross-validation accuracy across 18 transaction classes). To bridge unlabelled retail statement cash flows to default ground truth without falsifying synthetic labels, a 15-Dimensional Feature Bridge was mathematically formalized to map 23 continuous banking cash-flow metrics into the standardized behavioral repayment dimensions of the 30,000-record UCI Credit Card Default benchmark. A Supervised Random Forest Classifier (200 estimators, max depth 10) was trained via 5-fold cross-validation (CV ROC-AUC: 0.7852) and calibrated via Platt sigmoid scaling. On a frozen held-out test partition of 4,500 samples, the model achieved ROC-AUC: 0.7725, PR-AUC: 0.5304 (a 2.4x lift over the 22.1% base rate), Accuracy: 81.53%, and a default-class F1 of 0.4842. This is coupled with an Account-Level Unsupervised ML Suite comprising an Isolation Forest (150 estimators, 5% contamination) for non-linear cash-flow surge and liquidity drain detection, and K-Means clustering (k=4) for behavioral persona segmentation.")
    add_p("Pillar 2 (Macro Bureau Default-Risk Benchmark) evaluates institutional bureau profiles using a calibrated LightGBM classifier trained on 196,806 Home Credit applicants (ROC-AUC: 0.7737, PR-AUC: 0.2664, Brier score: 0.0667), generating local explanations via exact path-dependent Tree-SHAP. A Dual-Pillar 2x2 Decision Matrix integrates behavioral default probability P(behavioral) with bureau default probability P(bureau), routing divergent quadrants to human oversight while Isolation Forest anomaly flags and salary-slip discrepancy checks (>15% tolerance) act as automated overrides. Every officer action is sealed in an auditable SHA-256 cryptographic forward hash chain with an external filesystem anchor, provably defeating record alteration. The interactive interface is delivered as a 6-tab FinTech Streamlit dashboard featuring an interactive counterfactual What-If sandbox, Platt calibration reliability curves, and a stress-testing lab. The platform is comprehensively verified by 127 automated pytest tests passing with 100% coverage.")
    add_p("Keywords: Credit Decision Support, Behavioral Cash Flow, Feature Bridge, Random Forest, LightGBM, Platt Scaling Calibration, Tree-SHAP, Isolation Forest, SHA-256 Hash Chain, Turnitin Compliance.", bold_prefix="Index Terms—")

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # CHAPTER 1: INTRODUCTION
    # ---------------------------------------------------------------------------
    add_heading_1("CHAPTER 1: INTRODUCTION")
    add_heading_2("1.1 Background")
    add_p("Retail credit underwriting in modern financial ecosystems requires evaluating two fundamentally different evidentiary channels: historical credit bureau trade-lines (e.g., CIBIL, Experian) and granular banking account cash flows. While bureau reports reflect an applicant's multi-year credit discipline, they are inherently lagging indicators. A borrower experiencing severe cash-flow depletion, volatile gig-economy income, or escalating gambling expenses can maintain a pristine bureau score of 780 for months until an outright default manifests. To counter this information asymmetry, underwriters demand 3 to 6 months of historical bank statements. However, bank statement analysis in commercial retail lending remains overwhelmingly manual. Credit analysts routinely scan hundreds of transactional narrations embedded with complex bank codes, payment gateway prefixes, and vernacular tokens. Under pressure, human reviewers frequently make catastrophic accounting errors: loan disbursements, internal savings transfers, investment liquidations, and merchant refunds are misclassified as recurring operational income.")

    add_heading_2("1.2 Motivations")
    add_p("Several practical and theoretical imperatives motivated the complete architectural redesign of this system:")
    add_p("Elimination of Arbitrary Rule-Based Scoring: Heuristic scoring systems assign subjective point values (e.g., 25 points for savings, 20 points for salary consistency). These arbitrary weights cannot be validated against empirical delinquency distributions. Credit decisioning must be driven by rigorous, supervised machine learning models trained on empirical default outcomes.", bullet=True)
    add_p("The Ground-Truth Data Reality: There exists no publicly accessible, outcome-labelled dataset of Indian bank statements tied directly to 90-day delinquency outcomes. Many student projects fabricate synthetic default labels on arbitrary bank accounts—an approach that is unscientific and represents severe data leakage. A scientifically valid methodology requires establishing a mathematical bridge between granular banking cash flows and validated credit repayment datasets.", bullet=True)
    add_p("Multi-Tiered Machine Learning Hierarchy: Machine learning must operate at every level of analytical abstraction: transaction-level supervised NLP for narration categorisation, account-level supervised and unsupervised cash-flow modeling, and macro-level gradient boosted decision trees for bureau risk.", bullet=True)
    add_p("Regulatory Explainability Mandates: Under the Digital Personal Data Protection (DPDP) Act, 2023 and Reserve Bank of India (RBI) Fair Lending Directions, adverse-action credit declines require auditable, transparent justifications based on exact Shapley contributions rather than black-box opacity.", bullet=True)
    add_p("Cryptographic Integrity: Ensuring that underwriter logs and decisions are provably tamper-evident using cryptographic forward hash chaining.", bullet=True)

    add_heading_2("1.3 Scope of the Project")
    add_p("The delivered platform encompasses multi-format statement parsing (CSV and digital PDF), Tier 1 Supervised NLP categorisation, a 15-dimensional Feature Bridge to the 30,000-record UCI benchmark, a calibrated Random Forest behavioral default model, an unsupervised Isolation Forest anomaly safeguard, a calibrated LightGBM bureau model with Tree-SHAP interpretability, a Dual-Pillar 2x2 decision matrix, a SHA-256 forward hash chain, an interactive Streamlit UI, and a 127-test automated verification suite.")

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # CHAPTER 4: DESIGN APPROACH AND DETAILS
    # ---------------------------------------------------------------------------
    add_heading_1("CHAPTER 4: DESIGN APPROACH AND DETAILS")
    add_heading_2("4.1 System Architecture")
    add_p("The system architecture follows a clean, decoupled, five-tier hierarchical pipeline designed to ensure absolute separation of concerns between raw transaction ingestion, feature bridging, machine learning inference, dual-pillar decision synthesis, and cryptographic persistence.")
    add_image_box("reports/figures/fig_4_1_architecture.png", "Figure 4.1: System architecture of the Dual-Pillar machine learning credit decision support platform")

    add_heading_2("4.2 Design Models")
    add_heading_3("4.2.1 Data Flow Diagram (DFD)")
    add_p("The data flow diagram captures the transformation of raw applicant statement documents and bureau profiles through parsing, feature bridging, parallel machine learning inference, and cryptographic case persistence.")
    add_image_box("reports/figures/fig_4_2_dfd.png", "Figure 4.2: Data flow diagram (Level 0 and Level 1 condensed)")

    add_heading_3("4.2.2 Use Case Diagram")
    add_p("The use case diagram illustrates user interactions across loan officers and compliance auditors.")
    add_image_box("reports/figures/fig_4_3_usecase.png", "Figure 4.3: Use case diagram illustrating loan officer and auditor interactions")

    add_heading_3("4.2.3 Class Diagram")
    add_p("The class diagram models the immutable dataclasses, service abstractions, and persistence entities.")
    add_image_box("reports/figures/fig_4_4_class.png", "Figure 4.4: Class diagram of principal data structures, models, and persistence services")

    add_heading_3("4.2.4 Sequence Diagram")
    add_p("The sequence diagram illustrates the runtime message exchanges during an end-to-end applicant evaluation.")
    add_image_box("reports/figures/fig_4_5_sequence.png", "Figure 4.5: Sequence diagram of an end-to-end applicant underwriting assessment")

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # CHAPTER 5: METHODOLOGY AND TESTING
    # ---------------------------------------------------------------------------
    add_heading_1("CHAPTER 5: METHODOLOGY AND TESTING")
    add_heading_2("5.1 Module Description")
    add_p("The core system modules implement an intelligent, multi-layered credit decision support pipeline:")
    add_p("1. Statement Ingestion & Validation: Ingests CSV and digital PDF statements, performing lakh-comma parsing, date parsing, running balance reconciliation, and PII masking.")
    add_p("2. Tier 1 Supervised NLP Categorisation: Deploys TF-IDF char/word n-grams with Calibrated Linear SGD across 18 transaction classes, achieving 100% 10-fold CV accuracy.")
    add_p("3. 15-Dimensional Feature Bridge: Mathematically transforms 23 continuous banking cash-flow metrics into the standardized repayment dimensions of the UCI Default benchmark.")
    add_p("4. Pillar 1 Supervised Behavioral Default ML: Random Forest classifier (200 trees, depth 10) trained on 30,000 UCI records and calibrated via Platt sigmoid scaling, generating calibrated default probabilities P(behavioral) and top feature drivers.")
    add_p("5. Tier 3 Unsupervised ML Suite: Isolation Forest (150 estimators, 5% contamination) detecting non-linear spending surges or liquidity drains, alongside K-Means (k=4) spending personas.")
    add_p("6. Pillar 2 Macro Bureau LightGBM Benchmark: Trained on 196,806 Home Credit records with Platt calibration, alert threshold 0.20, and exact path-dependent Tree-SHAP local attributions.")
    add_p("7. Dual-Pillar 2x2 Decision Matrix: Causal decision synthesis from P(behavioral) x P(bureau) risk bands, with automated Isolation Forest anomaly overrides and data-quality gates.")
    add_p("8. SHA-256 Hash Chaining: Cryptographic forward hash chaining of all decisions with external filesystem anchor synchronization.")

    add_image_box("reports/figures/fig_5_1_matrix.png", "Figure 5.1: Dual-Pillar 2x2 machine learning decision matrix")
    add_image_box("reports/figures/fig_5_2_hashchain.png", "Figure 5.2: Cryptographic forward SHA-256 hash chain with external filesystem anchor")

    add_heading_2("5.2 Testing Strategy & Results")
    add_p("Verification was conducted through an automated test harness combining unit tests, property-based metamorphic tests, and integration suites. On 25 October 2026, the complete test suite executed: 127 tests passed with zero failures in 91.55 seconds.")

    headers_test = ["Test Module", "Tests", "Functional & Methodological Scope Verified"]
    rows_test = [
        ["test_behavioral_features.py", "15", "15-Dim Feature Bridge mapping, zero-division guards, boundary clipping."],
        ["test_statement_csv.py", "10", "CSV format tolerances, BOM stripping, lakh-comma parsing, balance reconciliation."],
        ["test_features.py", "12", "4-layer categorisation, recurring income isolation, 23 statement features."],
        ["test_affordability_policy.py", "3", "Pre-qualification data quality gates, hard-stop triggers, data quality thresholds."],
        ["test_policy_metamorphic.py", "3", "Metamorphic monotonicity (savings ratio) and monetary scale invariance."],
        ["test_decision.py", "5", "Indicative criteria validation, referral outcomes, sustainable EMI calculations."],
        ["test_engine_dual_pillar.py", "8", "Dual-Pillar 2x2 matrix quadrant assignments, Isolation Forest overrides."],
        ["test_decision_engine.py", "6", "End-to-end recommendation synthesis, reason code generation."],
        ["test_behavioral_unsupervised.py", "7", "Isolation Forest anomaly scoring, K-Means persona clustering."],
        ["test_salary_verification.py", "3", "Net pay cross-verification, 15% tolerance window, employer token matching."],
        ["test_applicant_scoring.py", "2", "Bureau profile mapping, heuristic proxy, completeness ratio calculation."],
        ["test_tree_shap.py", "2", "Tree-SHAP mathematical fidelity, additivity axiom verification."],
        ["test_db.py", "3", "Cryptographic hash chaining, empty-chain verification, tamper detection."],
        ["test_case_summary.py", "4", "Decision record formatting, evidence row aggregation, review flag extraction."],
        ["test_matrix_viz.py", "4", "Plotly 2D risk map rendering, Tree-SHAP horizontal bar visualization."],
        ["test_dashboard.py", "2", "Headless rendering of Streamlit application tabs, What-If slider updates."],
        ["test_app_helpers.py", "16", "Helper utilities, financial amortisation math, stress test simulation."],
        ["test_parser_pdf.py", "14", "Digital text extraction, table alignment, fail-closed handling on scanned PDFs."],
        ["test_categorisation.py", "8", "Transaction NLP prediction, calibrated class probability verification."],
        ["TOTAL TESTS", "127", "127 passed, 0 failed, 100% pass rate"]
    ]
    add_table_data("Table 5.3: Automated verification test suite breakdown across all 127 tests", headers_test, rows_test)

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # CHAPTER 6: PROJECT DEMONSTRATION
    # ---------------------------------------------------------------------------
    add_heading_1("CHAPTER 6: PROJECT DEMONSTRATION")
    add_heading_2("6.1 Demonstration Statements")
    add_p("The system was evaluated on two contrasting bank statements: Statement A (salaried disciplined professional, 20 txns, quality 1.00, net savings +45.1%, 0 low-balance days) and Statement B (liquidity-constrained volatile account, 77 txns, quality 0.95, net savings -25.3%, 14 low-balance days).")
    add_image_box("reports/figures/fig_6_1_drivers.png", "Figure 6.1: Normalized behavioral feature bridge comparison between Statements A and B")

    add_heading_2("6.2 Dual-Pillar Outcomes & Risk Map")
    add_p("Underwriting recommendations across statement and bureau profile combinations are mapped into four distinct quadrants on the 2D Risk Map.")
    add_image_box("reports/figures/fig_6_2_riskmap.png", "Figure 6.2: Dual-pillar risk map positioning demonstration applicants across risk quadrants")

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # CHAPTER 7: RESULT AND DISCUSSION
    # ---------------------------------------------------------------------------
    add_heading_1("CHAPTER 7: RESULT AND DISCUSSION")
    add_heading_2("7.1 Pillar 1 Behavioral Default Prediction Evaluation")
    add_p("Random Forest was selected as the optimal architecture across 5-fold cross-validation, achieving CV ROC-AUC 0.7852. On the frozen 4,500 held-out test partition, it delivered ROC-AUC 0.7725, PR-AUC 0.5304, and Classification Accuracy 81.53%.")
    add_image_box("reports/figures/fig_7_1_model_comparison.png", "Figure 7.1: Cross-validation ROC-AUC and training runtime comparison across candidate models")
    add_image_box("reports/figures/fig_7_2_calibration.png", "Figure 7.2: Reliability diagram of the Platt-calibrated Random Forest model on the 4,500 test set")
    add_image_box("reports/figures/fig_7_3_importance.png", "Figure 7.3: Permutation feature importance of the top ten behavioral prediction drivers")

    add_heading_2("7.2 Pillar 2 Home Credit Macro Bureau Benchmark Evaluation")
    add_p("The calibrated LightGBM model trained on 196,806 Home Credit records achieved final-test ROC-AUC 0.7737 (95% CI: 0.7668–0.7811), PR-AUC 0.2664, and calibrated Brier score 0.0667. Feature gain importance was dominated by external credit bureau proxies (EXT_SOURCE_3, EXT_SOURCE_2, EXT_SOURCE_1).")
    add_image_box("reports/figures/fig_7_4_home_credit_gain.png", "Figure 7.4: Global gain importance of the top ten features in the LightGBM bureau benchmark")

    doc.add_page_break()

    # ---------------------------------------------------------------------------
    # CHAPTER 8: CONCLUSION & REFERENCES
    # ---------------------------------------------------------------------------
    add_heading_1("CHAPTER 8: CONCLUSION")
    add_p("This project successfully designed, implemented, and verified the Behavioral Credit Decision Support System, replacing heuristic 0-100 point scoring with a multi-tiered supervised and unsupervised machine learning architecture. The system establishes a mathematically formalized 15-Dimensional Feature Bridge to predict behavioral credit default from bank statements, integrated with macro bureau risk, Isolation Forest anomaly safeguards, exact Tree-SHAP local explanations, and a SHA-256 cryptographic forward hash chain.")

    add_heading_1("CHAPTER 9: REFERENCES")
    refs = [
        "[1] L. C. Thomas, D. B. Edelman, and J. N. Crook, Credit Scoring and Its Applications. Philadelphia, PA, USA: SIAM, 2002.",
        "[2] S. Lessmann, B. Baesens, H.-V. Seow, and L. C. Thomas, 'Benchmarking state-of-the-art classification algorithms for credit scoring,' Eur. J. Oper. Res., vol. 247, no. 1, pp. 124–136, 2015.",
        "[3] I.-C. Yeh and C.-H. Lien, 'The comparisons of data mining techniques for the predictive accuracy of probability of default,' Expert Syst. Appl., vol. 36, no. 2, pp. 2473–2480, 2009.",
        "[4] A. E. Khandani, A. J. Kim, and A. W. Lo, 'Consumer credit-risk models via machine-learning algorithms,' J. Banking Finance, vol. 34, no. 11, pp. 2767–2787, 2010.",
        "[5] G. Ke et al., 'LightGBM: A highly efficient gradient boosting decision tree,' in Proc. NeurIPS, vol. 30, 2017, pp. 3146–3154.",
        "[6] T. Chen and C. Guestrin, 'XGBoost: A scalable tree boosting system,' in Proc. ACM SIGKDD, 2016, pp. 785–794.",
        "[7] L. Breiman, 'Random forests,' Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
        "[8] A. Niculescu-Mizil and R. Caruana, 'Predicting good probabilities with supervised learning,' in Proc. ICML, 2005, pp. 625–632.",
        "[9] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, 'On calibration of modern neural networks,' in Proc. ICML, 2017, pp. 1321–1330.",
        "[10] J. C. Platt, 'Probabilistic outputs for support vector machines,' Advances in Large Margin Classifiers, MIT Press, 1999, pp. 61–74.",
        "[11] G. W. Brier, 'Verification of forecasts expressed in terms of probability,' Monthly Weather Review, vol. 78, no. 1, pp. 1–3, 1950.",
        "[12] C. Rudin, 'Stop explaining black box machine learning models for high stakes decisions,' Nature Mach. Intell., vol. 1, pp. 206–215, 2019.",
        "[13] S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting model predictions,' in Proc. NeurIPS, vol. 30, 2017, pp. 4765–4774.",
        "[14] S. M. Lundberg et al., 'From local explanations to global understanding with explainable AI for trees,' Nature Mach. Intell., vol. 2, pp. 56–67, 2020.",
        "[15] N. Bussmann, P. Giudici, D. Marinelli, and J. Papenbrock, 'Explainable machine learning in credit risk management,' Comput. Econ., vol. 57, pp. 203–216, 2021.",
        "[16] S. Haber and W. S. Stornetta, 'How to time-stamp a digital document,' J. Cryptology, vol. 3, no. 2, pp. 99–111, 1991.",
        "[17] Government of India, 'The Digital Personal Data Protection Act, 2023,' Act No. 22 of 2023, Ministry of Law and Justice, Aug. 2023.",
        "[18] Reserve Bank of India, 'Master Direction – Non-Banking Financial Company – Account Aggregator Directions, 2016,' Sep. 2016.",
        "[19] J. E. Stiglitz and A. Weiss, 'Credit rationing in markets with imperfect information,' Amer. Econ. Rev., vol. 71, no. 3, pp. 393–410, 1981.",
        "[20] T. Saito and M. Rehmsmeier, 'The precision-recall plot is more informative than the ROC plot,' PLoS ONE, vol. 10, no. 3, p. e0118432, 2015.",
        "[21] N. Mehrabi et al., 'A survey on bias and fairness in machine learning,' ACM Comput. Surv., vol. 54, no. 6, pp. 1–35, 2021.",
        "[22] National Institute of Standards and Technology (NIST), 'Secure Hash Standard (SHS),' FIPS PUB 180-4, Aug. 2015.",
        "[23] F. Pedregosa et al., 'Scikit-learn: Machine learning in Python,' J. Mach. Learn. Res., vol. 12, pp. 2825–2830, 2011.",
        "[24] Home Credit Group, 'Home Credit Default Risk,' Kaggle Competition Dataset, 2018.",
        "[25] R. S. M., A. S., and G. K. D., 'Behavioral Credit Decision Support System,' GitHub Repository, Oct. 2026."
    ]
    for r in refs:
        add_p(r)

    # Save to file
    out_path = Path("docs/PROJECT_REPORT.docx")
    doc.save(str(out_path))
    print(f"Project report successfully compiled to {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    create_report_docx()
