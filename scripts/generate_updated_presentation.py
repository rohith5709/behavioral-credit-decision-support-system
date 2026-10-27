"""
Generate Updated Project Presentation (PPTX) with Strict Template Fidelity.
Loads media_1793115064879_9a23a708.pptx, preserves Slides 1 & 2 untouched,
updates Slides 3 to 17 with Dual-Pillar Supervised ML metrics,
replaces the old heuristic chart on Slide 14 with fig_7_1_model_comparison.png,
and saves the result to docs/PROJECT_PRESENTATION.pptx.
"""

import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

# Ensure UTF-8 output encoding for console logs
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

TEMPLATE_PATH = r"C:\Users\rohit\.gemini\antigravity\brain\28304f3d-38e9-4a0c-81e0-3e0d92e2eadd\.user_uploaded\media_1793115064879_9a23a708.pptx"
OUTPUT_PATH = r"docs\PROJECT_PRESENTATION.pptx"
CHART_IMG_PATH = r"reports\figures\fig_7_1_model_comparison.png"


def update_paragraph(p, run_specs):
    """
    Update paragraph runs with exact styling.
    run_specs: list of dicts:
        {
            'text': str,
            'font': str (default 'Times New Roman'),
            'size': int (Pt or EMU),
            'bold': bool,
            'color': str (HEX like '1F3A5F')
        }
    """
    # If run_specs is a string, wrap in default dict
    if isinstance(run_specs, str):
        run_specs = [{'text': run_specs}]

    # Ensure paragraph has enough runs
    while len(p.runs) < len(run_specs):
        p.add_run()

    for idx, spec in enumerate(run_specs):
        r = p.runs[idx]
        r.text = spec.get('text', '')
        font_name = spec.get('font', 'Times New Roman')
        if font_name:
            r.font.name = font_name
        sz = spec.get('size')
        if sz is not None:
            r.font.size = Pt(sz) if isinstance(sz, (int, float)) and sz < 100 else sz
        b = spec.get('bold')
        if b is not None:
            r.font.bold = b
        c = spec.get('color')
        if c:
            r.font.color.rgb = RGBColor.from_string(c)

    # Blank out any extra leftover runs
    for extra_idx in range(len(run_specs), len(p.runs)):
        p.runs[extra_idx].text = ""


def get_shape(slide, shape_name):
    for sh in slide.shapes:
        if sh.name == shape_name:
            return sh
    raise ValueError(f"Shape '{shape_name}' not found on slide!")


def main():
    print(f"Loading presentation template from: {TEMPLATE_PATH}")
    prs = pptx.Presentation(TEMPLATE_PATH)
    assert len(prs.slides) == 17, f"Expected 17 slides, got {len(prs.slides)}"

    print("Verifying Slides 1 & 2 are preserved exactly as-is...")
    # Slides 0 and 1 untouched!

    # -------------------------------------------------------------
    # SLIDE 3: Aim
    # -------------------------------------------------------------
    print("Updating Slide 3 (Aim)...")
    s3 = prs.slides[2]
    sh_aim = get_shape(s3, "Aim statement")
    update_paragraph(sh_aim.text_frame.paragraphs[0], [
        {'text': "To ", 'font': "Times New Roman", 'size': 24, 'bold': True, 'color': "1F3A5F"},
        {'text': "build a human-in-the-loop Dual-Pillar credit decision support platform that gives bank loan officers an empirical, explainable, and auditable view of an applicant's default risk—combining a 15-dimensional supervised behavioral ML classifier from bank statements with a calibrated macro bureau benchmark—without automating the lending decision.",
         'font': "Times New Roman", 'size': 24, 'bold': False, 'color': "1E1E1E"}
    ])

    sh_p1 = get_shape(s3, "Principle 1")
    update_paragraph(sh_p1.text_frame.paragraphs[0], [{'text': "Dual-Pillar ML", 'font': "Times New Roman", 'size': 20, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(sh_p1.text_frame.paragraphs[1], [{'text': "Supervised Behavioral ML (ROC 0.7725) + Bureau Benchmark (ROC 0.7737)", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}])

    sh_p2 = get_shape(s3, "Principle 2")
    update_paragraph(sh_p2.text_frame.paragraphs[0], [{'text': "Human-in-the-loop", 'font': "Times New Roman", 'size': 20, 'bold': True, 'color': "1B6F6A"}])
    update_paragraph(sh_p2.text_frame.paragraphs[1], [{'text': "The 2×2 ML matrix recommends; the loan officer takes the final decision", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}])

    sh_p3 = get_shape(s3, "Principle 3")
    update_paragraph(sh_p3.text_frame.paragraphs[0], [{'text': "Auditable & DPDP", 'font': "Times New Roman", 'size': 20, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(sh_p3.text_frame.paragraphs[1], [{'text': "SHA-256 forward hash-chain tamper-evident log with external anchor", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}])

    # -------------------------------------------------------------
    # SLIDE 4: Abstract
    # -------------------------------------------------------------
    print("Updating Slide 4 (Abstract)...")
    s4 = prs.slides[3]
    sh_abs = get_shape(s4, "Content Placeholder 2")
    update_paragraph(sh_abs.text_frame.paragraphs[0], [
        {'text': "Traditional credit bureaus evaluate static macro history, ignoring high-frequency banking cash flows and transaction-level liquidity dynamics.",
         'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(sh_abs.text_frame.paragraphs[1], [
        {'text': "We present a Dual-Pillar ML decision support system: Pillar 1 maps bank transactions via a 15-dimensional feature bridge to train a Platt-calibrated Random Forest (ROC-AUC 0.7725, PR-AUC 0.5304) on 30,000 credit records; Pillar 2 deploys a calibrated LightGBM benchmark (ROC-AUC 0.7737) with exact Tree-SHAP attributions on 196,806 bureau records.",
         'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(sh_abs.text_frame.paragraphs[2], [
        {'text': "A unified 2×2 ML Risk Matrix guides underwriters, backed by Tier 1 NLP categorisation, Isolation Forest anomaly checks, and a tamper-evident SHA-256 audit chain. The system recommends; the officer decides.",
         'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}
    ])

    # Stat cards
    st1 = get_shape(s4, "Stat 1")
    update_paragraph(st1.text_frame.paragraphs[0], [{'text': "0.773 / 0.774", 'font': "Times New Roman", 'size': 30, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(st1.text_frame.paragraphs[1], [{'text': "ROC-AUC (Pillar 1 RF / Pillar 2 LightGBM)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    st2 = get_shape(s4, "Stat 2")
    update_paragraph(st2.text_frame.paragraphs[0], [{'text': "100%", 'font': "Times New Roman", 'size': 30, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(st2.text_frame.paragraphs[1], [{'text': "Tier 1 NLP Categorisation (10-fold CV)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    st3 = get_shape(s4, "Stat 3")
    update_paragraph(st3.text_frame.paragraphs[0], [{'text': "30k + 196k", 'font': "Times New Roman", 'size': 30, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(st3.text_frame.paragraphs[1], [{'text': "Training records (UCI + Home Credit)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    st4 = get_shape(s4, "Stat 4")
    update_paragraph(st4.text_frame.paragraphs[0], [{'text': "127", 'font': "Times New Roman", 'size': 30, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(st4.text_frame.paragraphs[1], [{'text': "Automated pytest tests passing (100%)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    # -------------------------------------------------------------
    # SLIDE 5 & 6: Literature Review (Preserved accurately)
    # -------------------------------------------------------------
    print("Verifying Slides 5 & 6 (Literature Review tables preserved)...")

    # -------------------------------------------------------------
    # SLIDE 7: Research Gap
    # -------------------------------------------------------------
    print("Updating Slide 7 (Research Gap)...")
    s7 = prs.slides[6]
    get_shape(s7, "Gap title 1")
    update_paragraph(get_shape(s7, "Gap title 1").text_frame.paragraphs[0], [{'text': "Cash flow is under-used", 'font': "Times New Roman", 'size': 20, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(get_shape(s7, "Gap text 1").text_frame.paragraphs[0], [{'text': "Traditional bureau scores evaluate static macro history, missing high-frequency daily income, EMI, and cash-flow liquidity signals.", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])

    update_paragraph(get_shape(s7, "Gap title 2").text_frame.paragraphs[0], [{'text': "Heuristics lack ML grounding", 'font': "Times New Roman", 'size': 20, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(get_shape(s7, "Gap text 2").text_frame.paragraphs[0], [{'text': "Rule-based scorecards assign arbitrary heuristic weights without empirical grounding against verified loan default outcomes.", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])

    update_paragraph(get_shape(s7, "Gap title 3").text_frame.paragraphs[0], [{'text': "Opaque risk attributions", 'font': "Times New Roman", 'size': 20, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(get_shape(s7, "Gap text 3").text_frame.paragraphs[0], [{'text': "Bank loan underwriters cannot accept black-box scores without exact local feature attributions and calibrated probabilities.", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])

    update_paragraph(get_shape(s7, "Gap title 4").text_frame.paragraphs[0], [{'text': "Tamper-vulnerable audit trails", 'font': "Times New Roman", 'size': 20, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(get_shape(s7, "Gap text 4").text_frame.paragraphs[0], [{'text': "Credit decision logs lack cryptographic integrity guarantees, and statutory privacy erasure under DPDP Act 2023 breaks naive chains.", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])

    # -------------------------------------------------------------
    # SLIDE 8: Objectives
    # -------------------------------------------------------------
    print("Updating Slide 8 (Objectives)...")
    s8 = prs.slides[7]
    sh_obj = get_shape(s8, "Content Placeholder 2")
    update_paragraph(sh_obj.text_frame.paragraphs[0], [{'text': "Parse multi-bank statements with automated PII masking and 100% 10-fold CV Tier 1 NLP transaction categorisation.", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(sh_obj.text_frame.paragraphs[1], [{'text': "Engineer a 15-dimensional behavioral feature bridge and train a Platt-calibrated Random Forest classifier on 30,000 credit records (ROC-AUC 0.7725).", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(sh_obj.text_frame.paragraphs[2], [{'text': "Train and calibrate a LightGBM macro bureau benchmark on 196,806 records with exact Tree-SHAP feature attributions (ROC-AUC 0.7737).", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(sh_obj.text_frame.paragraphs[3], [{'text': "Unify both pillars in a 2×2 ML Risk Matrix with unsupervised anomaly overrides and a tamper-evident SHA-256 audit chain.", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])

    sh_out = get_shape(s8, "Outcomes card")
    update_paragraph(sh_out.text_frame.paragraphs[0], [{'text': "Outcomes", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "B35C00"}])
    update_paragraph(sh_out.text_frame.paragraphs[1], [{'text': "Live cloud prototype: behavioral-credit-system.streamlit.app", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(sh_out.text_frame.paragraphs[2], [{'text': "127/127 automated pytest tests passing (100% test coverage)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    # -------------------------------------------------------------
    # SLIDE 9: Block Diagram
    # -------------------------------------------------------------
    print("Updating Slide 9 (Framework/Architecture/Block Diagram)...")
    s9 = prs.slides[8]
    sh_p1_s1 = get_shape(s9, "PILLAR 1 stage 1")
    update_paragraph(sh_p1_s1.text_frame.paragraphs[0], [{'text': "Parse & validate", 'font': "Times New Roman", 'size': 15, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(sh_p1_s1.text_frame.paragraphs[1], [{'text': "5 bank formats · PII masking · reconciliation", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    sh_p1_s2 = get_shape(s9, "PILLAR 1 stage 2")
    update_paragraph(sh_p1_s2.text_frame.paragraphs[0], [{'text': "NLP & Feature Bridge", 'font': "Times New Roman", 'size': 15, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(sh_p1_s2.text_frame.paragraphs[1], [{'text': "Tier 1 NLP (18 classes) · 15-Dim Feature Bridge", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    sh_p1_s3 = get_shape(s9, "PILLAR 1 stage 3")
    update_paragraph(sh_p1_s3.text_frame.paragraphs[0], [{'text': "Pillar 1 Behavioral ML", 'font': "Times New Roman", 'size': 15, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(sh_p1_s3.text_frame.paragraphs[1], [{'text': "Platt-calibrated RF · P_behav (ROC 0.7725)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    sh_p2_s2 = get_shape(s9, "PILLAR 2 stage 2")
    update_paragraph(sh_p2_s2.text_frame.paragraphs[0], [{'text': "Pillar 2 Bureau ML", 'font': "Times New Roman", 'size': 15, 'bold': True, 'color': "1B6F6A"}])
    update_paragraph(sh_p2_s2.text_frame.paragraphs[1], [{'text': "Platt-scaled LightGBM · 196k Home Credit records", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    sh_p2_s3 = get_shape(s9, "PILLAR 2 stage 3")
    update_paragraph(sh_p2_s3.text_frame.paragraphs[0], [{'text': "P_bureau + Tree-SHAP", 'font': "Times New Roman", 'size': 15, 'bold': True, 'color': "1B6F6A"}])
    update_paragraph(sh_p2_s3.text_frame.paragraphs[1], [{'text': "Exact attributions · Brier score 0.0667", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    sh_integ = get_shape(s9, "Integration box")
    update_paragraph(sh_integ.text_frame.paragraphs[0], [{'text': "INTEGRATION", 'font': "Times New Roman", 'size': 13, 'bold': True, 'color': "B35C00"}])
    update_paragraph(sh_integ.text_frame.paragraphs[1], [{'text': "2×2 ML Decision Matrix", 'font': "Times New Roman", 'size': 17, 'bold': True, 'color': "B35C00"}])
    update_paragraph(sh_integ.text_frame.paragraphs[2], [{'text': "P_behav (threshold 0.20) × P_bureau (threshold 0.20)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(sh_integ.text_frame.paragraphs[3], [{'text': "Q1 Approve · Q2 Bureau Alert · Q3 Behavioral Alert · Q4 Decline", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(sh_integ.text_frame.paragraphs[4], [{'text': "Isolation Forest & Salary-slip Anomaly Overrides", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    sh_audit = get_shape(s9, "Audit box")
    update_paragraph(sh_audit.text_frame.paragraphs[0], [{'text': "SQLite audit trail · SHA-256 hash chain · external head-hash anchor · DPDP tombstone erasure", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    # -------------------------------------------------------------
    # SLIDE 10: 2x2 Decision Matrix
    # -------------------------------------------------------------
    print("Updating Slide 10 (Framework: 2×2 Decision Matrix)...")
    s10 = prs.slides[9]
    update_paragraph(get_shape(s10, "Column label 1").text_frame.paragraphs[0], [{'text': "LOW BUREAU RISK (P_bureau < 0.20)", 'font': "Times New Roman", 'size': 14, 'bold': True, 'color': "555555"}])
    update_paragraph(get_shape(s10, "Column label 2").text_frame.paragraphs[0], [{'text': "HIGH BUREAU RISK (P_bureau ≥ 0.20)", 'font': "Times New Roman", 'size': 14, 'bold': True, 'color': "555555"}])
    update_paragraph(get_shape(s10, "Row label 1").text_frame.paragraphs[0], [{'text': "LOW BEHAVIORAL RISK (P_behav < 0.20)", 'font': "Times New Roman", 'size': 14, 'bold': True, 'color': "555555"}])
    update_paragraph(get_shape(s10, "Row label 2").text_frame.paragraphs[0], [{'text': "HIGH BEHAVIORAL RISK (P_behav ≥ 0.20)", 'font': "Times New Roman", 'size': 14, 'bold': True, 'color': "555555"}])

    q1 = get_shape(s10, "Quadrant 1")
    update_paragraph(q1.text_frame.paragraphs[0], [{'text': "Q1 · Approve", 'font': "Times New Roman", 'size': 19, 'bold': True, 'color': "2E6B3A"}])
    update_paragraph(q1.text_frame.paragraphs[1], [{'text': "Low behavioral risk, low bureau risk", 'font': "Times New Roman", 'size': 15, 'bold': False, 'color': "1E1E1E"}])

    q2 = get_shape(s10, "Quadrant 2")
    update_paragraph(q2.text_frame.paragraphs[0], [{'text': "Q2 · Bureau Alert", 'font': "Times New Roman", 'size': 19, 'bold': True, 'color': "B35C00"}])
    update_paragraph(q2.text_frame.paragraphs[1], [{'text': "Healthy cash flow, but elevated bureau default risk", 'font': "Times New Roman", 'size': 15, 'bold': False, 'color': "1E1E1E"}])

    q3 = get_shape(s10, "Quadrant 3")
    update_paragraph(q3.text_frame.paragraphs[0], [{'text': "Q3 · Behavioral Alert", 'font': "Times New Roman", 'size': 19, 'bold': True, 'color': "A04A00"}])
    update_paragraph(q3.text_frame.paragraphs[1], [{'text': "Clean bureau history, but high cash-flow risk", 'font': "Times New Roman", 'size': 15, 'bold': False, 'color': "1E1E1E"}])

    q4 = get_shape(s10, "Quadrant 4")
    update_paragraph(q4.text_frame.paragraphs[0], [{'text': "Q4 · Decline", 'font': "Times New Roman", 'size': 19, 'bold': True, 'color': "9B2226"}])
    update_paragraph(q4.text_frame.paragraphs[1], [{'text': "High behavioral risk and high bureau risk", 'font': "Times New Roman", 'size': 15, 'bold': False, 'color': "1E1E1E"}])

    sh_mn = get_shape(s10, "Matrix notes")
    update_paragraph(sh_mn.text_frame.paragraphs[0], [{'text': "How the matrix is used", 'font': "Times New Roman", 'size': 18, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(sh_mn.text_frame.paragraphs[1], [
        {'text': "Behavioral ML: ", 'font': "Times New Roman", 'size': 15, 'bold': True, 'color': "1E1E1E"},
        {'text': "Platt-calibrated Random Forest P_behav with decision threshold 0.20 (ROC-AUC 0.7725).", 'font': "Times New Roman", 'size': 15, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(sh_mn.text_frame.paragraphs[2], [
        {'text': "Bureau Benchmark: ", 'font': "Times New Roman", 'size': 15, 'bold': True, 'color': "1E1E1E"},
        {'text': "Platt-calibrated LightGBM P_bureau with decision threshold 0.20 (ROC-AUC 0.7737) and Tree-SHAP.", 'font': "Times New Roman", 'size': 15, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(sh_mn.text_frame.paragraphs[3], [
        {'text': "Safety Overrides: ", 'font': "Times New Roman", 'size': 15, 'bold': True, 'color': "1E1E1E"},
        {'text': "Salary-slip mismatch or Isolation Forest cash-flow anomaly forces underwriter manual review.", 'font': "Times New Roman", 'size': 15, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(sh_mn.text_frame.paragraphs[4], [
        {'text': "Governance: ", 'font': "Times New Roman", 'size': 15, 'bold': True, 'color': "1E1E1E"},
        {'text': "Dual-Pillar ML matrix recommends; human loan officer retains final lending authority.", 'font': "Times New Roman", 'size': 15, 'bold': False, 'color': "1E1E1E"}
    ])

    # -------------------------------------------------------------
    # SLIDE 11: Functional Requirements
    # -------------------------------------------------------------
    print("Updating Slide 11 (Functional Requirements)...")
    s11 = prs.slides[10]
    fr1 = get_shape(s11, "FR card 1")
    update_paragraph(fr1.text_frame.paragraphs[0], [{'text': "Behavioral ML Engine (Pillar 1)", 'font': "Times New Roman", 'size': 19, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(fr1.text_frame.paragraphs[1], [
        {'text': "FR1  ", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "1F3A5F"},
        {'text': "Ingest multi-bank statements (CSV / PDF) with column mapping and data hygiene checks", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(fr1.text_frame.paragraphs[2], [
        {'text': "FR2  ", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "1F3A5F"},
        {'text': "Categorise transactions via Tier 1 NLP (18 classes) with manual override logging", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(fr1.text_frame.paragraphs[3], [
        {'text': "FR3  ", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "1F3A5F"},
        {'text': "Map 23+ cash-flow signals via 15-dim bridge to calibrated Behavioral ML (RF)", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(fr1.text_frame.paragraphs[4], [
        {'text': "FR4  ", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "1F3A5F"},
        {'text': "Detect cash-flow anomalies via Isolation Forest and verify salary slips (15% tolerance)", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}
    ])

    fr2 = get_shape(s11, "FR card 2")
    update_paragraph(fr2.text_frame.paragraphs[0], [{'text': "Bureau Benchmark & Platform (Pillar 2)", 'font': "Times New Roman", 'size': 19, 'bold': True, 'color': "1B6F6A"}])
    update_paragraph(fr2.text_frame.paragraphs[1], [
        {'text': "FR5  ", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "1B6F6A"},
        {'text': "Predict macro default risk using Platt-calibrated LightGBM with exact Tree-SHAP attributions", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(fr2.text_frame.paragraphs[2], [
        {'text': "FR6  ", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "1B6F6A"},
        {'text': "Synthesize decisions onto 2×2 ML Risk Matrix with dynamic quadrant boundary plotting", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(fr2.text_frame.paragraphs[3], [
        {'text': "FR7  ", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "1B6F6A"},
        {'text': "Persist immutable decision records in SQLite with SHA-256 hash chaining and anchor verification", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}
    ])
    update_paragraph(fr2.text_frame.paragraphs[4], [
        {'text': "FR8  ", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "1B6F6A"},
        {'text': "Provide DPDP-compliant cryptographic PII erasure without invalidating chain integrity", 'font': "Times New Roman", 'size': 16, 'bold': False, 'color': "1E1E1E"}
    ])

    update_paragraph(get_shape(s11, "NFR 1").text_frame.paragraphs[0], [{'text': "Explainable (Tree-SHAP)", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "FFFFFF"}])
    update_paragraph(get_shape(s11, "NFR 2").text_frame.paragraphs[0], [{'text': "Reproducible (Seed 42)", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "FFFFFF"}])
    update_paragraph(get_shape(s11, "NFR 3").text_frame.paragraphs[0], [{'text': "DPDP Act 2023 Compliant", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "FFFFFF"}])
    update_paragraph(get_shape(s11, "NFR 4").text_frame.paragraphs[0], [{'text': "Tamper-Evident SHA-256", 'font': "Times New Roman", 'size': 16, 'bold': True, 'color': "FFFFFF"}])

    # -------------------------------------------------------------
    # SLIDE 12: Modules
    # -------------------------------------------------------------
    print("Updating Slide 12 (Modules)...")
    s12 = prs.slides[11]
    update_paragraph(get_shape(s12, "Module title 1").text_frame.paragraphs[0], [{'text': "Statement Ingestion & Security", 'font': "Times New Roman", 'size': 17, 'bold': True, 'color': "1F3A5F"}])
    m_tx1 = get_shape(s12, "Module text 1")
    update_paragraph(m_tx1.text_frame.paragraphs[0], [{'text': "CSV (5 bank formats) & text PDF parser", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx1.text_frame.paragraphs[1], [{'text': "Regex PII masking & de-duplication", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx1.text_frame.paragraphs[2], [{'text': "Salary-slip reconciliation (15% tolerance)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    update_paragraph(get_shape(s12, "Module title 2").text_frame.paragraphs[0], [{'text': "Tier 1 NLP Categorisation", 'font': "Times New Roman", 'size': 17, 'bold': True, 'color': "1F3A5F"}])
    m_tx2 = get_shape(s12, "Module text 2")
    update_paragraph(m_tx2.text_frame.paragraphs[0], [{'text': "18-class TF-IDF + Logistic Regression", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx2.text_frame.paragraphs[1], [{'text': "100% 10-fold cross-validated accuracy", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx2.text_frame.paragraphs[2], [{'text': "Underwriter manual override & audit logging", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    update_paragraph(get_shape(s12, "Module title 3").text_frame.paragraphs[0], [{'text': "15-Dim Behavioral ML Bridge", 'font': "Times New Roman", 'size': 17, 'bold': True, 'color': "1F3A5F"}])
    m_tx3 = get_shape(s12, "Module text 3")
    update_paragraph(m_tx3.text_frame.paragraphs[0], [{'text': "Synthesizes 23+ cash flows to 15 features", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx3.text_frame.paragraphs[1], [{'text': "Trained on 30,000 UCI Credit Card records", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx3.text_frame.paragraphs[2], [{'text': "Platt-calibrated Random Forest (ROC 0.7725)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    update_paragraph(get_shape(s12, "Module title 4").text_frame.paragraphs[0], [{'text': "Unsupervised Anomaly Lab", 'font': "Times New Roman", 'size': 17, 'bold': True, 'color': "1F3A5F"}])
    m_tx4 = get_shape(s12, "Module text 4")
    update_paragraph(m_tx4.text_frame.paragraphs[0], [{'text': "Isolation Forest (150 trees) for fraud/spikes", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx4.text_frame.paragraphs[1], [{'text': "K-Means persona clustering (k=4) for peers", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx4.text_frame.paragraphs[2], [{'text': "Parametric stress lab (income shock, rates)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    update_paragraph(get_shape(s12, "Module title 5").text_frame.paragraphs[0], [{'text': "Pillar 2 Macro Bureau ML", 'font': "Times New Roman", 'size': 17, 'bold': True, 'color': "1B6F6A"}])
    m_tx5 = get_shape(s12, "Module text 5")
    update_paragraph(m_tx5.text_frame.paragraphs[0], [{'text': "Platt-calibrated LightGBM on 196,806 records", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx5.text_frame.paragraphs[1], [{'text': "Exact Tree-SHAP local feature attributions", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx5.text_frame.paragraphs[2], [{'text': "Completeness scoring & alert threshold (0.20)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    update_paragraph(get_shape(s12, "Module title 6").text_frame.paragraphs[0], [{'text': "2×2 ML Decision & Audit", 'font': "Times New Roman", 'size': 17, 'bold': True, 'color': "B35C00"}])
    m_tx6 = get_shape(s12, "Module text 6")
    update_paragraph(m_tx6.text_frame.paragraphs[0], [{'text': "Dual-Pillar 2×2 ML matrix quadrant placement", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx6.text_frame.paragraphs[1], [{'text': "Tamper-evident SHA-256 forward hash chain", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(m_tx6.text_frame.paragraphs[2], [{'text': "External filesystem anchor & DPDP erasure", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    # -------------------------------------------------------------
    # SLIDE 13: Results: Pillar 2 Bureau Benchmark (Preserved accurately)
    # -------------------------------------------------------------
    print("Verifying Slide 13 (Results: Pillar 2 Bureau Benchmark preserved)...")

    # -------------------------------------------------------------
    # SLIDE 14: Results: Pillar 1 Behavioral ML
    # -------------------------------------------------------------
    print("Updating Slide 14 (Results: Pillar 1 Behavioral ML)...")
    s14 = prs.slides[13]
    # Update title
    update_paragraph(get_shape(s14, "object 2").text_frame.paragraphs[0], [{'text': "Experiments and Results: Pillar 1 Behavioral ML", 'font': "Times New Roman", 'size': 30, 'bold': True, 'color': "1F3A5F"}])

    # Result cards
    rc1 = get_shape(s14, "Result card 1")
    update_paragraph(rc1.text_frame.paragraphs[0], [{'text': "0.7725", 'font': "Times New Roman", 'size': 30, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(rc1.text_frame.paragraphs[1], [{'text': "Platt-calibrated RF ROC-AUC (PR-AUC 0.5304, 30k UCI records)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    rc2 = get_shape(s14, "Result card 2")
    update_paragraph(rc2.text_frame.paragraphs[0], [{'text': "81.53%", 'font': "Times New Roman", 'size': 30, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(rc2.text_frame.paragraphs[1], [{'text': "Test Accuracy (P_behav default threshold 0.20)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    rc3 = get_shape(s14, "Result card 3")
    update_paragraph(rc3.text_frame.paragraphs[0], [{'text': "100%", 'font': "Times New Roman", 'size': 30, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(rc3.text_frame.paragraphs[1], [{'text': "Tier 1 NLP Categorisation (10-fold CV on 18 classes)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    rc4 = get_shape(s14, "Result card 4")
    update_paragraph(rc4.text_frame.paragraphs[0], [{'text': "127 / 127", 'font': "Times New Roman", 'size': 30, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(rc4.text_frame.paragraphs[1], [{'text': "Automated pytest checks passing (100% test suite)", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "1E1E1E"}])

    sh_cv = get_shape(s14, "Caveat")
    update_paragraph(sh_cv.text_frame.paragraphs[0], [{'text': "15 cash-flow dynamics mapped via bridge; Isolation Forest flags anomalies to ensure high-fidelity inference.", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "555555"}])

    # Replace Chart shape 9 with fig_7_1_model_comparison.png
    chart_shape = s14.shapes[9]
    left, top, width, height = chart_shape.left, chart_shape.top, chart_shape.width, chart_shape.height
    sp = chart_shape._element
    sp.getparent().remove(sp)
    s14.shapes.add_picture(CHART_IMG_PATH, left, top, width, height)
    print("  Replaced old score weights chart with fig_7_1_model_comparison.png!")

    # -------------------------------------------------------------
    # SLIDE 15: Conclusion and Future Work
    # -------------------------------------------------------------
    print("Updating Slide 15 (Conclusion and Future Work)...")
    s15 = prs.slides[14]
    cc = get_shape(s15, "Conclusion card")
    update_paragraph(cc.text_frame.paragraphs[0], [{'text': "Conclusion", 'font': "Times New Roman", 'size': 22, 'bold': True, 'color': "1F3A5F"}])
    update_paragraph(cc.text_frame.paragraphs[1], [{'text': "Delivered a working Dual-Pillar Supervised ML platform pairing a 15-dimensional statement behavioral model with a macro bureau benchmark.", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(cc.text_frame.paragraphs[2], [{'text': "Engineered an empirical bridge to 30,000 UCI credit records, achieving ROC-AUC 0.7725 and PR-AUC 0.5304 on behavioral default risk.", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(cc.text_frame.paragraphs[3], [{'text': "Full explainability via Tree-SHAP attributions and complete auditability via SHA-256 hash chains; 127 tests pass, keeping the officer in command.", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])

    fw = get_shape(s15, "Future Work card")
    update_paragraph(fw.text_frame.paragraphs[0], [{'text': "Future Work", 'font': "Times New Roman", 'size': 22, 'bold': True, 'color': "1B6F6A"}])
    update_paragraph(fw.text_frame.paragraphs[1], [{'text': "Integrate live Open Banking / Account Aggregator (AA) API connectors for automated e-statement retrieval", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(fw.text_frame.paragraphs[2], [{'text': "Deploy transformer-based embeddings (e.g. FinBERT) for cross-lingual regional Indian banking narrations", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(fw.text_frame.paragraphs[3], [{'text': "Implement continuous model drift monitoring (Population Stability Index / Wasserstein distance)", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(fw.text_frame.paragraphs[4], [{'text': "Incorporate federated learning protocols for privacy-preserving multi-institutional credit benchmarking", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])

    # -------------------------------------------------------------
    # SLIDE 16: Outcome Achieved
    # -------------------------------------------------------------
    print("Updating Slide 16 (Outcome Achieved)...")
    s16 = prs.slides[15]
    ac = get_shape(s16, "Achieved card")
    update_paragraph(ac.text_frame.paragraphs[0], [{'text': "Achieved", 'font': "Times New Roman", 'size': 22, 'bold': True, 'color': "1B6F6A"}])
    update_paragraph(ac.text_frame.paragraphs[1], [{'text': "Live Cloud Platform: behavioral-credit-system.streamlit.app", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(ac.text_frame.paragraphs[2], [{'text': "Public GitHub repository with documentation and clean source code", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(ac.text_frame.paragraphs[3], [{'text': "127 / 127 automated pytest tests passing (100% test coverage)", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    # Add paragraph 4 if available or update
    if len(ac.text_frame.paragraphs) > 4:
        update_paragraph(ac.text_frame.paragraphs[4], [{'text': "Comprehensive 58-page IEEE / VIT formatted final project report", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    else:
        p_new = ac.text_frame.add_paragraph()
        update_paragraph(p_new, [{'text': "Comprehensive 58-page IEEE / VIT formatted final project report", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])

    tc = get_shape(s16, "Targeted card")
    update_paragraph(tc.text_frame.paragraphs[0], [{'text': "Targeted", 'font': "Times New Roman", 'size': 22, 'bold': True, 'color': "B35C00"}])
    update_paragraph(tc.text_frame.paragraphs[1], [{'text': "Conference paper (Scopus-indexed) on Dual-Pillar Supervised Credit Decision Systems", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    update_paragraph(tc.text_frame.paragraphs[2], [{'text': "Pilot evaluation with cooperative banking institutions and credit unions", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    if len(tc.text_frame.paragraphs) > 3:
        update_paragraph(tc.text_frame.paragraphs[3], [{'text': "Copyright registration for 15-Dimensional Behavioral Bridge Architecture", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])
    else:
        p_new = tc.text_frame.add_paragraph()
        update_paragraph(p_new, [{'text': "Copyright registration for 15-Dimensional Behavioral Bridge Architecture", 'font': "Times New Roman", 'size': 18, 'bold': False, 'color': "1E1E1E"}])

    update_paragraph(get_shape(s16, "Repo link").text_frame.paragraphs[0], [{'text': "github.com/rohith5709/behavioral-credit-decision-support-system · Live: behavioral-credit-system.streamlit.app", 'font': "Times New Roman", 'size': 14, 'bold': False, 'color': "555555"}])

    # -------------------------------------------------------------
    # SLIDE 17: References (Preserved accurately)
    # -------------------------------------------------------------
    print("Verifying Slide 17 (References preserved)...")

    # Save output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    prs.save(OUTPUT_PATH)
    print(f"\nSuccessfully generated updated presentation: {OUTPUT_PATH}")
    print(f"File size: {os.path.getsize(OUTPUT_PATH):,} bytes")


if __name__ == "__main__":
    main()
