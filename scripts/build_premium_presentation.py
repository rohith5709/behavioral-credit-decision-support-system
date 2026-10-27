"""
Build Premium, Professional, High-End Project Presentation.
Designed to look like a bespoke executive/engineering slide deck (not generic AI slop).
Incorporates:
- Modern typography (Segoe UI / Calibri)
- Refined color palette (Obsidian Slate, Cobalt Blue, Forest Emerald, Coral Crimson, Warm Amber)
- Category badges / pills and high-contrast metric callouts
- High-resolution system figures: fig_4_1_architecture, fig_5_1_matrix, fig_7_1_model_comparison, fig_7_4_home_credit_gain
- Preserves exact student & guide credentials, guide approval mail screenshot, SDG/TRL badges
- Saves to docs/PROJECT_PRESENTATION.pptx
"""

import sys
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_PATH = r"docs\PROJECT_PRESENTATION_PREMIUM.pptx"
TARGET_MAIN = r"docs\PROJECT_PRESENTATION.pptx"
BACKUP_PATH = r"docs\PROJECT_PRESENTATION_template_v1.pptx"

# Color Palette Constants
C_NAVY_DARK = RGBColor(0x0F, 0x17, 0x2A)   # #0F172A - Obsidian Dark Slate
C_NAVY_MID  = RGBColor(0x1E, 0x29, 0x3B)   # #1E293B - Dark Slate Mid
C_BLUE_ACC  = RGBColor(0x25, 0x63, 0xEB)   # #2563EB - Royal Cobalt Blue
C_TEAL_ACC  = RGBColor(0x0F, 0x76, 0x6E)   # #0F766E - Deep Forest Teal
C_GREEN_ACC = RGBColor(0x05, 0x96, 0x69)   # #059669 - Emerald Success Green
C_AMBER_ACC = RGBColor(0xD9, 0x77, 0x06)   # #D97706 - Warm Amber Alert
C_RED_ACC   = RGBColor(0xDC, 0x26, 0x26)   # #DC2626 - Carmine Red Decline
C_CARD_BG   = RGBColor(0xF8, 0xFA, 0xFC)   # #F8FAFC - Ultra Light Slate Card
C_CARD_BG2  = RGBColor(0xF1, 0xF5, 0xF9)   # #F1F5F9 - Alternate Card Fill
C_BORDER    = RGBColor(0xCB, 0xD5, 0xE1)   # #CBD5E1 - Crisp Hairline Border
C_TEXT_DARK = RGBColor(0x0F, 0x17, 0x2A)   # #0F172A - Deep Heading Text
C_TEXT_BODY = RGBColor(0x33, 0x41, 0x55)   # #334155 - Slate Body Text
C_TEXT_MUTED= RGBColor(0x64, 0x74, 0x8B)   # #64748B - Muted Slate Text
C_WHITE     = RGBColor(0xFF, 0xFF, 0xFF)   # #FFFFFF - White

FONT_FAMILY = "Segoe UI"


def create_deck():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # completely blank layout
    return prs, blank_layout


def add_header(slide, category_text, title_text, category_color=C_BLUE_ACC):
    """Modern header with category badge/pill and bold executive title."""
    # Top Category Pill text
    tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(11.733), Inches(0.3))
    p_cat = tb_cat.text_frame.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.name = FONT_FAMILY
    p_cat.font.size = Pt(9.5)
    p_cat.font.bold = True
    p_cat.font.color.rgb = category_color

    # Title
    tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.733), Inches(0.55))
    p_title = tb_title.text_frame.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = FONT_FAMILY
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = C_NAVY_DARK

    # Subtle divider rule
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.32), Inches(11.733), Inches(0.015))
    line.fill.solid()
    line.fill.fore_color.rgb = C_BORDER
    line.line.color.rgb = C_BORDER


def add_footer(slide, current_slide, total_slides=17):
    """Clean, subtle professional footer."""
    tb_left = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(3.0), Inches(0.3))
    p_l = tb_left.text_frame.paragraphs[0]
    p_l.text = "05/10/2026 · Project Review"
    p_l.font.name = FONT_FAMILY
    p_l.font.size = Pt(9)
    p_l.font.color.rgb = C_TEXT_MUTED

    tb_mid = slide.shapes.add_textbox(Inches(4.0), Inches(7.05), Inches(5.333), Inches(0.3))
    p_m = tb_mid.text_frame.paragraphs[0]
    p_m.alignment = PP_ALIGN.CENTER
    p_m.text = "BCSE497J · Behavioral Credit Decision Support System · SCOPE"
    p_m.font.name = FONT_FAMILY
    p_m.font.size = Pt(9)
    p_m.font.color.rgb = C_TEXT_MUTED

    tb_right = slide.shapes.add_textbox(Inches(9.533), Inches(7.05), Inches(3.0), Inches(0.3))
    p_r = tb_right.text_frame.paragraphs[0]
    p_r.alignment = PP_ALIGN.RIGHT
    p_r.text = f"{current_slide} / {total_slides}"
    p_r.font.name = FONT_FAMILY
    p_r.font.size = Pt(9)
    p_r.font.bold = True
    p_r.font.color.rgb = C_TEXT_MUTED


def add_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_BORDER):
    """Draws a clean modern rounded card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(0.75)
    return card


def add_metric_box(slide, left, top, width, height, value_text, label_text, val_color=C_NAVY_DARK, bg_color=C_CARD_BG):
    """Draws a high-impact metric KPI box."""
    add_card(slide, left, top, width, height, bg_color=bg_color)
    tb = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.08), width - Inches(0.3), height - Inches(0.16))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_val = tf.paragraphs[0]
    p_val.text = value_text
    p_val.font.name = FONT_FAMILY
    p_val.font.size = Pt(24)
    p_val.font.bold = True
    p_val.font.color.rgb = val_color

    p_lbl = tf.add_paragraph()
    p_lbl.text = label_text
    p_lbl.font.name = FONT_FAMILY
    p_lbl.font.size = Pt(9.5)
    p_lbl.font.color.rgb = C_TEXT_MUTED
    p_lbl.space_before = Pt(2)


# =========================================================================
# SLIDE BUILDERS
# =========================================================================

def build_slide_1(prs, layout):
    """Slide 1: Cover / Title Slide"""
    s = prs.slides.add_slide(layout)

    # University Logo Banner (Centered)
    logo_path = 'reports/figures/extracted/slide_1_Picture 4.png'
    if os.path.exists(logo_path):
        s.shapes.add_picture(logo_path, Inches(4.6), Inches(0.65), Inches(4.13), Inches(1.2))

    # Decorative Badge Pill
    pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.9), Inches(2.1), Inches(5.53), Inches(0.35))
    pill.fill.solid()
    pill.fill.fore_color.rgb = RGBColor(0xEE, 0xF2, 0xFF) # Light Indigo
    pill.line.color.rgb = C_BLUE_ACC
    pill.line.width = Pt(1)
    p_pill = pill.text_frame.paragraphs[0]
    p_pill.text = "B.TECH CAPSTONE PROJECT I  ·  BCSE497J"
    p_pill.alignment = PP_ALIGN.CENTER
    p_pill.font.name = FONT_FAMILY
    p_pill.font.size = Pt(10)
    p_pill.font.bold = True
    p_pill.font.color.rgb = C_BLUE_ACC

    # Main Title
    tb_t = s.shapes.add_textbox(Inches(1.0), Inches(2.6), Inches(11.333), Inches(0.9))
    p_t = tb_t.text_frame.paragraphs[0]
    p_t.alignment = PP_ALIGN.CENTER
    p_t.text = "Behavioral Credit Decision Support System"
    p_t.font.name = FONT_FAMILY
    p_t.font.size = Pt(30)
    p_t.font.bold = True
    p_t.font.color.rgb = C_NAVY_DARK

    # Subtitle
    tb_sub = s.shapes.add_textbox(Inches(1.0), Inches(3.55), Inches(11.333), Inches(0.5))
    p_sub = tb_sub.text_frame.paragraphs[0]
    p_sub.alignment = PP_ALIGN.CENTER
    p_sub.text = "A Dual-Pillar Supervised Machine Learning & Cryptographic Audit Architecture for Retail Lending"
    p_sub.font.name = FONT_FAMILY
    p_sub.font.size = Pt(13)
    p_sub.font.color.rgb = C_TEXT_MUTED

    # Team Card (Left)
    add_card(s, Inches(1.5), Inches(4.45), Inches(4.9), Inches(2.3), bg_color=C_CARD_BG)
    tb_team = s.shapes.add_textbox(Inches(1.75), Inches(4.6), Inches(4.4), Inches(2.0))
    tf_team = tb_team.text_frame
    tf_team.word_wrap = True
    p0 = tf_team.paragraphs[0]
    p0.text = "PROJECT TEAM MEMBERS"
    p0.font.name = FONT_FAMILY
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = C_BLUE_ACC

    members = [
        ("Adharsh S", "23BDS0029"),
        ("Gowtham Kumar D", "23BDS0186"),
        ("Rohith S M", "23BDS0025")
    ]
    for name, reg in members:
        p = tf_team.add_paragraph()
        p.text = f"•  {name}   ({reg})"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(11.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(3)

    p_sch = tf_team.add_paragraph()
    p_sch.text = "School of Computer Science and Engineering (SCOPE)"
    p_sch.font.name = FONT_FAMILY
    p_sch.font.size = Pt(9.5)
    p_sch.font.color.rgb = C_TEXT_MUTED
    p_sch.space_before = Pt(6)

    # Faculty Guide Card (Right)
    add_card(s, Inches(6.9), Inches(4.45), Inches(4.9), Inches(2.3), bg_color=C_CARD_BG)
    tb_guide = s.shapes.add_textbox(Inches(7.15), Inches(4.6), Inches(4.4), Inches(2.0))
    tf_guide = tb_guide.text_frame
    tf_guide.word_wrap = True
    pg0 = tf_guide.paragraphs[0]
    pg0.text = "FACULTY SUPERVISOR"
    pg0.font.name = FONT_FAMILY
    pg0.font.size = Pt(10)
    pg0.font.bold = True
    pg0.font.color.rgb = C_TEAL_ACC

    pg1 = tf_guide.add_paragraph()
    pg1.text = "Dr. Viswanathan A"
    pg1.font.name = FONT_FAMILY
    pg1.font.size = Pt(15)
    pg1.font.bold = True
    pg1.font.color.rgb = C_NAVY_DARK
    pg1.space_before = Pt(8)

    pg2 = tf_guide.add_paragraph()
    pg2.text = "School of Computer Science and Engineering"
    pg2.font.name = FONT_FAMILY
    pg2.font.size = Pt(11.5)
    pg2.font.color.rgb = C_TEXT_BODY
    pg2.space_before = Pt(2)

    pg3 = tf_guide.add_paragraph()
    pg3.text = "Vellore Institute of Technology, Chennai  ·  October 2026"
    pg3.font.name = FONT_FAMILY
    pg3.font.size = Pt(9.5)
    pg3.font.color.rgb = C_TEXT_MUTED
    pg3.space_before = Pt(4)


def build_slide_2(prs, layout):
    """Slide 2: Guide Approval Mail"""
    s = prs.slides.add_slide(layout)
    add_header(s, "PROJECT GOVERNANCE · REVIEW ENDORSEMENT", "Faculty Guide Approval & Verification")
    add_footer(s, 2)

    # Left Column: Endorsement Checklist Card
    add_card(s, Inches(0.8), Inches(1.5), Inches(4.4), Inches(5.3), bg_color=C_CARD_BG)
    tb = s.shapes.add_textbox(Inches(1.05), Inches(1.75), Inches(3.9), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "FACULTY ENDORSEMENT"
    p0.font.name = FONT_FAMILY
    p0.font.size = Pt(10.5)
    p0.font.bold = True
    p0.font.color.rgb = C_GREEN_ACC

    p1 = tf.add_paragraph()
    p1.text = "Formal Review Status: Approved"
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = C_NAVY_DARK
    p1.space_before = Pt(4)

    p2 = tf.add_paragraph()
    p2.text = "All project review criteria and methodological specifications have been verified and endorsed through official mail by Faculty Guide Dr. Viswanathan A before the milestone deadline (21-10-2026)."
    p2.font.name = FONT_FAMILY
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_TEXT_BODY
    p2.space_before = Pt(8)

    checkpoints = [
        "Problem Statement & Dual-Pillar Scope",
        "Empirical 15-Dim Bridge Architecture",
        "Platt Calibration & Tree-SHAP Integration",
        "DPDP Act 2023 Cryptographic Audit Protocol",
        "Streamlit Cloud Platform Deployment"
    ]
    for cp in checkpoints:
        p = tf.add_paragraph()
        p.text = f"✓  {cp}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_TEAL_ACC
        p.space_before = Pt(6)

    p_ft = tf.add_paragraph()
    p_ft.text = "All aspects addressed & ready for evaluation."
    p_ft.font.name = FONT_FAMILY
    p_ft.font.size = Pt(10)
    p_ft.font.italic = True
    p_ft.font.color.rgb = C_TEXT_MUTED
    p_ft.space_before = Pt(10)

    # Right Column: Approval Mail Screenshot Image Framed
    mail_img = 'reports/figures/extracted/slide_2_Picture 6.png'
    if os.path.exists(mail_img):
        add_card(s, Inches(5.4), Inches(1.5), Inches(7.133), Inches(5.3), bg_color=C_WHITE)
        s.shapes.add_picture(mail_img, Inches(5.5), Inches(1.6), Inches(6.933), Inches(5.1))


def build_slide_3(prs, layout):
    """Slide 3: Aim & Principles"""
    s = prs.slides.add_slide(layout)
    add_header(s, "FOUNDATIONAL SCOPE · CORE OBJECTIVE", "Project Aim & Architectural Principles")
    add_footer(s, 3)

    # Top Banner Callout (Aim Statement)
    add_card(s, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.7), bg_color=C_NAVY_DARK, border_color=C_NAVY_DARK)
    tb_aim = s.shapes.add_textbox(Inches(1.1), Inches(1.65), Inches(11.133), Inches(1.4))
    tf_aim = tb_aim.text_frame
    tf_aim.word_wrap = True

    p0 = tf_aim.paragraphs[0]
    p0.text = "PROJECT AIM & MISSION"
    p0.font.name = FONT_FAMILY
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = RGBColor(0x38, 0xBD, 0xF8) # Sky blue

    p1 = tf_aim.add_paragraph()
    p1.text = "To build a human-in-the-loop Dual-Pillar credit decision support platform that gives bank loan officers an empirical, explainable, and auditable view of an applicant's default risk—combining a 15-dimensional supervised behavioral ML classifier from bank statements with a calibrated macro bureau benchmark—without automating the lending decision."
    p1.font.name = FONT_FAMILY
    p1.font.size = Pt(13.5)
    p1.font.color.rgb = C_WHITE
    p1.space_before = Pt(4)

    # 3 Principle Cards
    pillars = [
        ("01 · DUAL-PILLAR SUPERVISED ML", C_BLUE_ACC, [
            "Empirical Feature Bridge: Synthesizes 23+ cash-flow dynamics into 15 bridge features.",
            "Trained on 30,000 real-world credit default records (UCI Taiwan benchmark).",
            "Pillar 1 Behavioral RF (ROC 0.7725) + Pillar 2 Bureau LightGBM (ROC 0.7737).",
            "Replaces arbitrary heuristic rules with mathematically calibrated probabilities."
        ]),
        ("02 · HUMAN-IN-THE-LOOP GOVERNANCE", C_TEAL_ACC, [
            "2×2 ML Risk Matrix: Discretizes dual probabilities into 4 actionable underwriter quadrants.",
            "Local Explainability: Exact Tree-SHAP Shapley attributions explain every recommendation.",
            "Underwriter Autonomy: System recommends; loan officer retains final lending authority.",
            "Automated Safety Overrides: Salary mismatch or Isolation Forest anomalies force review."
        ]),
        ("03 · AUDITABILITY & DPDP COMPLIANCE", C_NAVY_MID, [
            "Cryptographic Integrity: SQLite audit ledger structured with forward SHA-256 hash chains.",
            "External Head-Hash Anchor: Detects unauthorized database modifications or tampering.",
            "DPDP Act 2023 Compliant: Cryptographic tombstoning enables statutory PII erasure.",
            "Deterministic Verification: Chain integrity verified in sub-second execution."
        ])
    ]

    card_w = Inches(3.75)
    card_gap = Inches(0.24)
    start_x = Inches(0.8)
    for idx, (title, color, bullets) in enumerate(pillars):
        x = start_x + idx * (card_w + card_gap)
        add_card(s, x, Inches(3.35), card_w, Inches(3.45), bg_color=C_CARD_BG)
        tb_p = s.shapes.add_textbox(x + Inches(0.2), Inches(3.5), card_w - Inches(0.4), Inches(3.15))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True

        pt0 = tf_p.paragraphs[0]
        pt0.text = title
        pt0.font.name = FONT_FAMILY
        pt0.font.size = Pt(11)
        pt0.font.bold = True
        pt0.font.color.rgb = color

        for b in bullets:
            pb = tf_p.add_paragraph()
            pb.text = f"•  {b}"
            pb.font.name = FONT_FAMILY
            pb.font.size = Pt(10)
            pb.font.color.rgb = C_TEXT_BODY
            pb.space_before = Pt(4)


def build_slide_4(prs, layout):
    """Slide 4: Executive Abstract & Key Metrics"""
    s = prs.slides.add_slide(layout)
    add_header(s, "EXECUTIVE SUMMARY · PERFORMANCE HIGHLIGHTS", "Abstract & Key Quantitative Milestones")
    add_footer(s, 4)

    # Left: Abstract Narrative Card
    add_card(s, Inches(0.8), Inches(1.5), Inches(7.0), Inches(5.3), bg_color=C_CARD_BG)
    tb_abs = s.shapes.add_textbox(Inches(1.1), Inches(1.75), Inches(6.4), Inches(4.8))
    tf = tb_abs.text_frame
    tf.word_wrap = True

    sections = [
        ("THE PROBLEM: BLINDSPOTS IN RETAIL UNDERWRITING",
         "Traditional credit bureaus rely strictly on static macro history, missing high-frequency banking cash flows and day-to-day liquidity dynamics. Conversely, commercial statement scorecards rely on arbitrary heuristic point systems with zero mathematical validation against default outcomes."),
        ("THE SOLUTION: DUAL-PILLAR SUPERVISED ML",
         "We present a Dual-Pillar decision support platform: Pillar 1 maps bank statement transactions via a 15-dimensional feature bridge to train a Platt-calibrated Random Forest (ROC-AUC 0.7725, PR-AUC 0.5304) on 30,000 credit records; Pillar 2 deploys a calibrated LightGBM benchmark (ROC-AUC 0.7737) with exact Tree-SHAP attributions on 196,806 bureau records."),
        ("THE GOVERNANCE: SYNTHESIS & AUDIT",
         "A unified 2×2 ML Risk Matrix guides underwriters, backed by Tier 1 NLP categorisation (100% 10-fold CV), Isolation Forest anomaly checks, and a tamper-evident SHA-256 audit chain. The machine recommends; the officer decides.")
    ]

    for idx, (head, body) in enumerate(sections):
        p_h = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p_h.text = head
        p_h.font.name = FONT_FAMILY
        p_h.font.size = Pt(10.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_BLUE_ACC
        if idx > 0:
            p_h.space_before = Pt(10)

        p_b = tf.add_paragraph()
        p_b.text = body
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = C_TEXT_BODY
        p_b.space_before = Pt(3)

    # Right: 4 High-Contrast KPI Cards
    kpis = [
        ("0.7725 / 0.7737", "ROC-AUC BENCHMARK", "Pillar 1 RF (0.7725) & Pillar 2 LightGBM (0.7737) test set performance", C_BLUE_ACC),
        ("100.0%", "TIER 1 NLP CATEGORISATION", "10-fold cross-validated accuracy across 18 banking transaction classes", C_GREEN_ACC),
        ("226,806", "EMPIRICAL TRAINING RECORDS", "30,000 UCI Credit Card + 196,806 Home Credit default records", C_NAVY_DARK),
        ("127 / 127", "AUTOMATED PYTEST CHECKS", "100% passing test suite covering ML, bridge, matrix, and cryptographic chain", C_TEAL_ACC)
    ]

    card_h = Inches(1.22)
    card_gap = Inches(0.14)
    start_y = Inches(1.5)
    for idx, (val, title, desc, color) in enumerate(kpis):
        y = start_y + idx * (card_h + card_gap)
        add_card(s, Inches(8.0), y, Inches(4.533), card_h, bg_color=C_CARD_BG)
        tb_k = s.shapes.add_textbox(Inches(8.2), y + Inches(0.1), Inches(4.133), card_h - Inches(0.2))
        tf_k = tb_k.text_frame
        tf_k.word_wrap = True

        pk0 = tf_k.paragraphs[0]
        pk0.text = f"{val}  ·  {title}"
        pk0.font.name = FONT_FAMILY
        pk0.font.size = Pt(12.5)
        pk0.font.bold = True
        pk0.font.color.rgb = color

        pk1 = tf_k.add_paragraph()
        pk1.text = desc
        pk1.font.name = FONT_FAMILY
        pk1.font.size = Pt(9.5)
        pk1.font.color.rgb = C_TEXT_MUTED
        pk1.space_before = Pt(2)


def build_slide_table(slide, table_data, col_widths, top_y=Inches(1.5), height=Inches(5.3)):
    """Helper to draw professional, beautifully formatted academic literature tables."""
    rows = len(table_data)
    cols = len(col_widths)
    table_shape = slide.shapes.add_table(rows, cols, Inches(0.8), top_y, sum(col_widths), height)
    table = table_shape.table

    for c_idx, w in enumerate(col_widths):
        table.columns[c_idx].width = w

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.margin_left = Inches(0.1)
            cell.margin_right = Inches(0.1)
            cell.margin_top = Inches(0.08)
            cell.margin_bottom = Inches(0.08)

            # Styling
            p = cell.text_frame.paragraphs[0]
            p.font.name = FONT_FAMILY

            if r_idx == 0:
                # Header row
                cell.fill.solid()
                cell.fill.fore_color.rgb = C_NAVY_MID
                p.font.size = Pt(10)
                p.font.bold = True
                p.font.color.rgb = C_WHITE
            else:
                # Body rows
                cell.fill.solid()
                if r_idx % 2 == 1:
                    cell.fill.fore_color.rgb = C_CARD_BG
                else:
                    cell.fill.fore_color.rgb = C_WHITE
                p.font.size = Pt(9)
                p.font.color.rgb = C_TEXT_BODY


def build_slide_5(prs, layout):
    """Slide 5: Literature Review Part 1"""
    s = prs.slides.add_slide(layout)
    add_header(s, "THEORETICAL FOUNDATION · BENCHMARK ANALYSIS", "Literature Review: Credit Risk & Behavioral Modeling")
    add_footer(s, 5)

    headers = ["Paper & Author", "Objective", "Methodology", "Pros / Cons", "Key Findings"]
    data = [
        headers,
        [
            "Yeh & Lien (2009)\n[Expert Syst. Appl.] [1]",
            "Predict default probability of credit card clients",
            "Evaluated 6 machine learning classifiers on UCI Taiwan benchmark (30,000 clients)",
            "Pro: Authoritative public benchmark\nCon: Single market; lacks cash-flow data",
            "Ensembles and neural networks achieve superior probability estimation over linear models"
        ],
        [
            "Lessmann et al. (2015)\n[Eur. J. Oper. Res.] [2]",
            "Update state-of-the-art classifier benchmark in credit scoring",
            "Extensive empirical comparison of 41 classifiers across 8 credit datasets",
            "Pro: Rigorous statistical comparison\nCon: Static application bureau data only",
            "Tree ensembles (GBDT, Random Forest) systematically outperform logistic regression"
        ],
        [
            "Khandani et al. (2010)\n[J. Bank. Financ.] [3]",
            "Forecast consumer credit delinquency from transactions",
            "Nonlinear classification trees on customer transaction and bureau records",
            "Pro: Confirms cash flows add predictive power\nCon: Proprietary bank data; not reproducible",
            "Transaction-level cash flow dynamics improve delinquency forecasts by 6–25%"
        ],
        [
            "Bhatore et al. (2020)\n[J. Bank. Fin. Tech.] [4]",
            "Comprehensive survey of ML in credit risk evaluation",
            "Systematic literature review mapping ML techniques and deployment paradigms",
            "Pro: Maps architectural trends\nCon: Survey only; no implementation",
            "Highlights urgent industry need for interpretable, deployable, human-governed models"
        ]
    ]

    col_widths = [Inches(2.2), Inches(2.2), Inches(2.5), Inches(2.4), Inches(2.433)]
    build_slide_table(s, data, col_widths, top_y=Inches(1.6), height=Inches(5.1))


def build_slide_6(prs, layout):
    """Slide 6: Literature Review Part 2"""
    s = prs.slides.add_slide(layout)
    add_header(s, "THEORETICAL FOUNDATION · ALGORITHMS & EXPLAINABILITY", "Literature Review (contd.): Ensembles, Interpretability & Calibration")
    add_footer(s, 6)

    headers = ["Paper & Author", "Objective", "Methodology", "Pros / Cons", "Key Findings"]
    data = [
        headers,
        [
            "Ke et al. (2017)\n[Proc. NeurIPS] [5]",
            "Accelerate gradient boosting on large tabular data",
            "LightGBM: Gradient-based One-Side Sampling (GOSS) and Exclusive Feature Bundling",
            "Pro: Extreme training efficiency on 200k+ rows\nCon: Raw scores require calibration",
            "Delivers up to 20× faster training than conventional GBDT with identical predictive accuracy"
        ],
        [
            "Lundberg & Lee (2017)\n[Proc. NeurIPS] [6]",
            "Provide unified local model interpretability",
            "SHAP: Additive feature attributions based on game-theoretic Shapley values",
            "Pro: Mathematically consistent local explanations\nCon: High computation for arbitrary models",
            "Tree-SHAP achieves polynomial-time exact feature attributions for decision tree ensembles"
        ],
        [
            "Platt (1999)\n[Adv. Large Margin] [7]",
            "Calibrate uncalibrated classifier outputs into true probabilities",
            "Sigmoid (Platt) scaling fitted via maximum likelihood on held-out validation predictions",
            "Pro: Low complexity, prevents overconfidence\nCon: Assumes monotonic sigmoid distortion",
            "Transforms decision margins into well-calibrated posterior default probabilities"
        ]
    ]

    col_widths = [Inches(2.2), Inches(2.2), Inches(2.5), Inches(2.4), Inches(2.433)]
    build_slide_table(s, data, col_widths, top_y=Inches(1.8), height=Inches(4.5))


def build_slide_7(prs, layout):
    """Slide 7: Research Gap"""
    s = prs.slides.add_slide(layout)
    add_header(s, "PROBLEM FORMULATION · RESEARCH JUSTIFICATION", "Critical Research Gaps in Contemporary Credit Systems")
    add_footer(s, 7)

    gaps = [
        ("GAP 01: CASH-FLOW LIQUIDITY UNDER-UTILIZATION", C_NAVY_DARK,
         "Traditional bureau scores (e.g. CIBIL, FICO) evaluate static debt repayment histories, remaining blind to high-frequency monthly income consistency, volatile expense spikes, and intra-month liquidity cushions.",
         "Our Solution: Ingests 6+ months of bank statements to extract 23+ granular behavioral features."),

        ("GAP 02: UNSUPERVISED HEURISTIC SCORECARD DISCONNECT", C_AMBER_ACC,
         "Commercial statement analyzers rely on arbitrary 0–100 heuristic scoring point systems without mathematical grounding or empirical calibration against actual borrower loan default outcomes.",
         "Our Solution: Engineers a 15-dimensional bridge linking statement features to 30,000 UCI default outcomes."),

        ("GAP 03: UNDERWRITER EXPLAINABILITY GAP (BLACK-BOX OPACITY)", C_RED_ACC,
         "Credit underwriters and regulatory authorities reject complex black-box machine learning predictions without local, verifiable feature attributions and mathematically calibrated probabilities.",
         "Our Solution: Deploys exact Tree-SHAP Shapley attributions and Platt probability calibration."),

        ("GAP 04: AUDIT TAMPER VULNERABILITY & PRIVACY CONFLICT", C_TEAL_ACC,
         "Standard database case logs are vulnerable to administrator tampering. Furthermore, statutory 'right to be forgotten' erasures under DPDP Act 2023 break naive cryptographic hash chains.",
         "Our Solution: Immutable forward SHA-256 hash chains with external filesystem anchor and tombstone erasure.")
    ]

    w = Inches(5.75)
    h = Inches(2.55)
    coords = [
        (Inches(0.8), Inches(1.55)),
        (Inches(6.783), Inches(1.55)),
        (Inches(0.8), Inches(4.3)),
        (Inches(6.783), Inches(4.3))
    ]

    for (title, col, problem, sol), (x, y) in zip(gaps, coords):
        add_card(s, x, y, w, h, bg_color=C_CARD_BG)
        tb = s.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), w - Inches(0.4), h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = FONT_FAMILY
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = col

        p1 = tf.add_paragraph()
        p1.text = problem
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = C_TEXT_BODY
        p1.space_before = Pt(4)

        p2 = tf.add_paragraph()
        p2.text = f"💡  {sol}"
        p2.font.name = FONT_FAMILY
        p2.font.size = Pt(9.5)
        p2.font.bold = True
        p2.font.color.rgb = C_BLUE_ACC
        p2.space_before = Pt(5)


def build_slide_8(prs, layout):
    """Slide 8: Objectives, SDGs & TRL"""
    s = prs.slides.add_slide(layout)
    add_header(s, "PROJECT SCOPE · ALIGNMENT & TARGETS", "Engineering Objectives & Sustainable Development Goals")
    add_footer(s, 8)

    # Left: 4 Milestone Cards
    objs = [
        ("OBJECTIVE 1: INGESTION & NLP CATEGORISATION",
         "Develop multi-bank parsers (CSV/PDF) for 5 Indian banks with regex PII masking and a 100% 10-fold CV Tier 1 NLP transaction classifier across 18 classes."),
        ("OBJECTIVE 2: 15-DIMENSIONAL BRIDGE & BEHAVIORAL ML",
         "Engineer an empirical 15-dimensional bridge linking statement features to 30,000 UCI credit default records; train a Platt-calibrated Random Forest (ROC-AUC 0.7725)."),
        ("OBJECTIVE 3: PILLAR 2 BUREAU BENCHMARK & TREE-SHAP",
         "Train and calibrate a LightGBM macro bureau benchmark on 196,806 records (ROC-AUC 0.7737) with exact local Tree-SHAP Shapley feature attributions."),
        ("OBJECTIVE 4: 2×2 RISK MATRIX & CRYPTOGRAPHIC AUDIT",
         "Synthesize dual predictions into a 2×2 Risk Matrix with Isolation Forest anomaly overrides and an immutable SHA-256 hash-chain ledger with external anchor.")
    ]

    card_h = Inches(1.22)
    card_gap = Inches(0.14)
    start_y = Inches(1.5)
    for idx, (title, desc) in enumerate(objs):
        y = start_y + idx * (card_h + card_gap)
        add_card(s, Inches(0.8), y, Inches(7.0), card_h, bg_color=C_CARD_BG)
        tb = s.shapes.add_textbox(Inches(1.0), y + Inches(0.1), Inches(6.6), card_h - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = FONT_FAMILY
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = C_BLUE_ACC

        p1 = tf.add_paragraph()
        p1.text = desc
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(9.5)
        p1.font.color.rgb = C_TEXT_BODY
        p1.space_before = Pt(3)

    # Right Top: SDG Alignment Card
    add_card(s, Inches(8.0), Inches(1.5), Inches(4.533), Inches(2.55), bg_color=C_CARD_BG)
    tb_sdg = s.shapes.add_textbox(Inches(8.2), Inches(1.65), Inches(2.5), Inches(2.2))
    tf_sdg = tb_sdg.text_frame
    tf_sdg.word_wrap = True
    ps0 = tf_sdg.paragraphs[0]
    ps0.text = "SUSTAINABLE DEVELOPMENT GOALS"
    ps0.font.name = FONT_FAMILY
    ps0.font.size = Pt(10)
    ps0.font.bold = True
    ps0.font.color.rgb = C_GREEN_ACC

    sdgs = [
        "SDG 8: Decent Work & Economic Growth",
        "SDG 9: Industry, Innovation & Infrastructure",
        "SDG 10: Reduced Inequalities"
    ]
    for item in sdgs:
        p = tf_sdg.add_paragraph()
        p.text = f"• {item}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(3)

    sdg_img = 'reports/figures/extracted/slide_8_Picture 7.jpg'
    if os.path.exists(sdg_img):
        s.shapes.add_picture(sdg_img, Inches(10.8), Inches(1.65), Inches(1.5), Inches(1.2))

    # Right Bottom: TRL Readiness Card
    add_card(s, Inches(8.0), Inches(4.25), Inches(4.533), Inches(2.55), bg_color=C_CARD_BG)
    tb_trl = s.shapes.add_textbox(Inches(8.2), Inches(4.4), Inches(2.5), Inches(2.2))
    tf_trl = tb_trl.text_frame
    tf_trl.word_wrap = True
    pt0 = tf_trl.paragraphs[0]
    pt0.text = "TARGET READINESS LEVEL: TRL 4"
    pt0.font.name = FONT_FAMILY
    pt0.font.size = Pt(10)
    pt0.font.bold = True
    pt0.font.color.rgb = C_NAVY_DARK

    trl_points = [
        "Component & pipeline validation in laboratory/cloud environment.",
        "Live deployed Streamlit prototype.",
        "127 passing automated tests.",
        "Targeted Scopus conference publication."
    ]
    for pt in trl_points:
        p = tf_trl.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(3)

    trl_img = 'reports/figures/extracted/slide_8_Picture 8.jpg'
    if os.path.exists(trl_img):
        s.shapes.add_picture(trl_img, Inches(10.8), Inches(4.4), Inches(1.5), Inches(1.37))


def build_slide_9(prs, layout):
    """Slide 9: System Architecture with Embedded Diagram"""
    s = prs.slides.add_slide(layout)
    add_header(s, "SYSTEM DESIGN · PIPELINE TOPOLOGY", "Dual-Pillar End-to-End System Architecture")
    add_footer(s, 9)

    # Left: Architectural Descriptions
    add_card(s, Inches(0.8), Inches(1.5), Inches(4.8), Inches(5.3), bg_color=C_CARD_BG)
    tb = s.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(4.4), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    tiers = [
        ("TIER 1: STATEMENT INGESTION & NLP",
         "Ingests 5 Indian bank CSVs + PDFs. Applies regex PII redaction (PAN, Aadhaar). Classifies transactions into 18 categories using TF-IDF + Logistic Regression (100% 10-fold CV). Cross-checks salary slips with 15% tolerance."),
        ("TIER 2: DUAL SUPERVISED ML INFERENCE",
         "• Pillar 1 (Behavioral): 15-Dim Feature Bridge maps statement dynamics to Platt-calibrated Random Forest (ROC-AUC 0.7725, PR-AUC 0.5304).\n• Pillar 2 (Macro Bureau): Platt-calibrated LightGBM on 196k applicants (ROC-AUC 0.7737) with exact Tree-SHAP local explanations."),
        ("TIER 3: DECISION MATRIX & CRYPTOGRAPHIC AUDIT",
         "Synthesizes dual probabilities into a 2×2 Risk Matrix. Isolation Forest flags distributional anomalies. Decision records persisted in SQLite forward SHA-256 hash chain with external filesystem anchor.")
    ]

    for idx, (head, body) in enumerate(tiers):
        p_h = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p_h.text = head
        p_h.font.name = FONT_FAMILY
        p_h.font.size = Pt(10.5)
        p_h.font.bold = True
        p_h.font.color.rgb = C_BLUE_ACC
        if idx > 0:
            p_h.space_before = Pt(8)

        p_b = tf.add_paragraph()
        p_b.text = body
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = C_TEXT_BODY
        p_b.space_before = Pt(3)

    # Right: High-Res Architecture Diagram
    arch_img = 'reports/figures/fig_4_1_architecture.png'
    if os.path.exists(arch_img):
        add_card(s, Inches(5.8), Inches(1.5), Inches(6.733), Inches(5.3), bg_color=C_WHITE)
        s.shapes.add_picture(arch_img, Inches(5.9), Inches(1.6), Inches(6.533), Inches(5.1))


def build_slide_10(prs, layout):
    """Slide 10: 2x2 Decision Matrix with Embedded Graphic"""
    s = prs.slides.add_slide(layout)
    add_header(s, "DECISION SYNTHESIS · UNDERWRITING LOGIC", "Dual-Pillar 2×2 ML Risk Decision Matrix")
    add_footer(s, 10)

    # Left: High-Res 2x2 Matrix Graphic
    mat_img = 'reports/figures/fig_5_1_matrix.png'
    if os.path.exists(mat_img):
        add_card(s, Inches(0.8), Inches(1.5), Inches(5.4), Inches(5.3), bg_color=C_WHITE)
        s.shapes.add_picture(mat_img, Inches(0.9), Inches(1.6), Inches(5.2), Inches(5.1))

    # Right: Underwriting Rules Card
    add_card(s, Inches(6.4), Inches(1.5), Inches(6.133), Inches(5.3), bg_color=C_CARD_BG)
    tb = s.shapes.add_textbox(Inches(6.65), Inches(1.65), Inches(5.633), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    quads = [
        ("Q1 · APPROVE (Low P_behav, Low P_bureau)", C_GREEN_ACC,
         "Both behavioral cash flow and bureau risk fall below 0.20 alert threshold. Recommended for standard loan approval at competitive rate."),
        ("Q2 · BUREAU ALERT (Low P_behav, High P_bureau)", C_AMBER_ACC,
         "Clean statement cash flows, but macro bureau history indicates elevated default risk. Requires underwriter scrutiny of historical bureau defaults."),
        ("Q3 · BEHAVIORAL ALERT (High P_behav, Low P_bureau)", RGBColor(0xEA, 0x58, 0x0C),
         "Clean macro bureau record, but high-frequency banking reveals liquidity stress, irregular income, or high EMI burden. Requires manual debt-to-income check."),
        ("Q4 · DECLINE (High P_behav, High P_bureau)", C_RED_ACC,
         "Compounding default risk across both pillars. Recommended for immediate rejection."),
        ("SAFETY OVERRIDES & GOVERNANCE", C_NAVY_DARK,
         "• Salary Mismatch: Discrepancy > 15% forces underwriter review.\n• Isolation Forest Outlier: Cash-flow spikes trigger manual verification.\n• Governance: Machine recommends; officer retains final authority.")
    ]

    for idx, (title, color, text) in enumerate(quads):
        p_t = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_FAMILY
        p_t.font.size = Pt(10)
        p_t.font.bold = True
        p_t.font.color.rgb = color
        if idx > 0:
            p_t.space_before = Pt(6)

        p_b = tf.add_paragraph()
        p_b.text = text
        p_b.font.name = FONT_FAMILY
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = C_TEXT_BODY
        p_b.space_before = Pt(2)


def build_slide_11(prs, layout):
    """Slide 11: Functional & Non-Functional Requirements"""
    s = prs.slides.add_slide(layout)
    add_header(s, "ENGINEERING SPECIFICATIONS · SYSTEM REQUIREMENTS", "Functional Requirements & Non-Functional Guarantees")
    add_footer(s, 11)

    # Left: Pillar 1 Behavioral Card
    add_card(s, Inches(0.8), Inches(1.5), Inches(5.75), Inches(3.95), bg_color=C_CARD_BG)
    tb_l = s.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(5.35), Inches(3.65))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p0 = tf_l.paragraphs[0]
    p0.text = "PILLAR 1: BEHAVIORAL ML ENGINE"
    p0.font.name = FONT_FAMILY
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = C_BLUE_ACC

    frs_1 = [
        ("FR1  Statement Ingestion", "Upload bank statements (CSV/PDF) across 5 Indian bank formats; map columns, perform balance reconciliation, and mask PII."),
        ("FR2  Tier 1 NLP Categorisation", "Classify transactions into 18 categories using TF-IDF + Logistic Regression; log officer manual overrides with rationale."),
        ("FR3  15-Dim Behavioral ML Bridge", "Map 23+ cash-flow signals via 15-dimensional bridge to Platt-calibrated Random Forest (ROC-AUC 0.7725)."),
        ("FR4  Anomaly & Salary Checks", "Detect cash-flow anomalies using Isolation Forest (150 trees) and verify salary slips within 15% tolerance.")
    ]
    for tag, desc in frs_1:
        p = tf_l.add_paragraph()
        p.text = f"{tag}: {desc}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(5)

    # Right: Pillar 2 Bureau & Platform Card
    add_card(s, Inches(6.783), Inches(1.5), Inches(5.75), Inches(3.95), bg_color=C_CARD_BG)
    tb_r = s.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.35), Inches(3.65))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    pr0 = tf_r.paragraphs[0]
    pr0.text = "PILLAR 2: BUREAU BENCHMARK & PLATFORM"
    pr0.font.name = FONT_FAMILY
    pr0.font.size = Pt(11)
    pr0.font.bold = True
    pr0.font.color.rgb = C_TEAL_ACC

    frs_2 = [
        ("FR5  Bureau Default Scoring", "Predict default risk using Platt-calibrated LightGBM on 196k records; generate exact Tree-SHAP attributions."),
        ("FR6  2×2 Matrix Synthesis", "Place applicant on 2×2 ML Risk Matrix; generate interactive risk map with dynamic decision boundary plotting."),
        ("FR7  Tamper-Evident Ledger", "Persist decision records in SQLite with forward SHA-256 hash chaining; verify external head-hash anchor."),
        ("FR8  DPDP Act 2023 Privacy", "Erase personal data upon statutory request via cryptographic tombstoning without invalidating ledger integrity.")
    ]
    for tag, desc in frs_2:
        p = tf_r.add_paragraph()
        p.text = f"{tag}: {desc}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(5)

    # Bottom: 4 Non-Functional Guarantee Badges
    nfrs = [
        ("EXPLAINABLE", "Tree-SHAP Shapley attributions explain every prediction", C_BLUE_ACC),
        ("REPRODUCIBLE", "Deterministic seed (Seed 42) across all splits and models", C_NAVY_DARK),
        ("DPDP COMPLIANT", "Section 12 statutory cryptographic personal data erasure", C_TEAL_ACC),
        ("TAMPER-EVIDENT", "SHA-256 forward hash chain anchored to external storage", C_GREEN_ACC)
    ]
    bw = Inches(2.78)
    bgap = Inches(0.2)
    start_bx = Inches(0.8)
    for idx, (title, desc, col) in enumerate(nfrs):
        bx = start_bx + idx * (bw + bgap)
        add_card(s, bx, Inches(5.6), bw, Inches(1.2), bg_color=C_CARD_BG)
        tb_n = s.shapes.add_textbox(bx + Inches(0.12), Inches(5.68), bw - Inches(0.24), Inches(1.0))
        tf_n = tb_n.text_frame
        tf_n.word_wrap = True
        pn0 = tf_n.paragraphs[0]
        pn0.text = title
        pn0.font.name = FONT_FAMILY
        pn0.font.size = Pt(10.5)
        pn0.font.bold = True
        pn0.font.color.rgb = col

        pn1 = tf_n.add_paragraph()
        pn1.text = desc
        pn1.font.name = FONT_FAMILY
        pn1.font.size = Pt(8.5)
        pn1.font.color.rgb = C_TEXT_MUTED
        pn1.space_before = Pt(2)


def build_slide_12(prs, layout):
    """Slide 12: Modules (3x2 Grid)"""
    s = prs.slides.add_slide(layout)
    add_header(s, "SOFTWARE ARCHITECTURE · SUBSYSTEM BREAKDOWN", "Six-Module Decoupled Production Architecture")
    add_footer(s, 12)

    modules = [
        ("MODULE 01", "Statement Ingestion & Security", C_BLUE_ACC, [
            "Parsers for 5 Indian bank formats + text PDF.",
            "Regex PII masking & transaction de-duplication.",
            "Balance reconciliation & 15% salary tolerance check."
        ]),
        ("MODULE 02", "Tier 1 NLP Categorisation", C_NAVY_DARK, [
            "18-class TF-IDF + Logistic Regression engine.",
            "100% 10-fold cross-validated test accuracy.",
            "Underwriter manual override & rationale audit logger."
        ]),
        ("MODULE 03", "15-Dim Behavioral ML Bridge", C_BLUE_ACC, [
            "Synthesizes 23+ statement cash flows to 15 features.",
            "Trained on 30,000 UCI Credit Card Default records.",
            "Platt-calibrated Random Forest (ROC-AUC 0.7725)."
        ]),
        ("MODULE 04", "Unsupervised Anomaly Lab", C_AMBER_ACC, [
            "Isolation Forest (150 estimators) for cash spikes.",
            "K-Means persona clustering (k=4) for peer benchmarking.",
            "Parametric stress-testing (income shock, rate hike)."
        ]),
        ("MODULE 05", "Pillar 2 Macro Bureau ML", C_TEAL_ACC, [
            "Platt-calibrated LightGBM on 196,806 applicants.",
            "Exact Tree-SHAP local feature attributions.",
            "Completeness scoring & alert threshold (0.20)."
        ]),
        ("MODULE 06", "2×2 Decision & Audit Engine", C_GREEN_ACC, [
            "Dual-Pillar 2×2 ML matrix risk quadrant placement.",
            "Tamper-evident SHA-256 forward hash-chain ledger.",
            "External filesystem anchor & DPDP erasure protocol."
        ])
    ]

    cw = Inches(3.75)
    ch = Inches(2.55)
    cgap_x = Inches(0.24)
    cgap_y = Inches(0.2)
    start_x = Inches(0.8)
    start_y = Inches(1.55)

    for idx, (mod_id, title, color, points) in enumerate(modules):
        col_idx = idx % 3
        row_idx = idx // 3
        x = start_x + col_idx * (cw + cgap_x)
        y = start_y + row_idx * (ch + cgap_y)

        add_card(s, x, y, cw, ch, bg_color=C_CARD_BG)
        tb = s.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), cw - Inches(0.4), ch - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p0 = tf.paragraphs[0]
        p0.text = mod_id
        p0.font.name = FONT_FAMILY
        p0.font.size = Pt(9.5)
        p0.font.bold = True
        p0.font.color.rgb = color

        p1 = tf.add_paragraph()
        p1.text = title
        p1.font.name = FONT_FAMILY
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = C_NAVY_DARK
        p1.space_before = Pt(2)

        for pt in points:
            pb = tf.add_paragraph()
            pb.text = f"• {pt}"
            pb.font.name = FONT_FAMILY
            pb.font.size = Pt(9.5)
            pb.font.color.rgb = C_TEXT_BODY
            pb.space_before = Pt(3)


def build_slide_13(prs, layout):
    """Slide 13: Results Pillar 2 Bureau Benchmark"""
    s = prs.slides.add_slide(layout)
    add_header(s, "EXPERIMENTAL RESULTS · PILLAR 2 VALIDATION", "Empirical Evaluation: Macro Bureau Benchmark")
    add_footer(s, 13)

    # Left: 3 Metric Cards + Methodology
    add_metric_box(s, Inches(0.8), Inches(1.5), Inches(5.2), Inches(1.05), "0.7737", "ROC-AUC (95% CI: 0.767–0.781)", val_color=C_BLUE_ACC)
    add_metric_box(s, Inches(0.8), Inches(2.68), Inches(5.2), Inches(1.05), "0.2664", "PR-AUC (3.3× Lift over 0.0807 baseline)", val_color=C_GREEN_ACC)
    add_metric_box(s, Inches(0.8), Inches(3.86), Inches(5.2), Inches(1.05), "0.0667", "Brier Calibration Score (Platt Scaling)", val_color=C_NAVY_DARK)

    # Benchmark Methodology Card
    add_card(s, Inches(0.8), Inches(5.05), Inches(5.2), Inches(1.75), bg_color=C_CARD_BG)
    tb = s.shapes.add_textbox(Inches(1.0), Inches(5.15), Inches(4.8), Inches(1.55))
    tf = tb.text_frame
    tf.word_wrap = True
    p0 = tf.paragraphs[0]
    p0.text = "BENCHMARK SPECIFICATIONS"
    p0.font.name = FONT_FAMILY
    p0.font.size = Pt(10)
    p0.font.bold = True
    p0.font.color.rgb = C_TEAL_ACC

    points = [
        "Dataset: 196,806 real-world Home Credit applicants.",
        "Stratified Split: 64% Train, 16% Validation, 20% Held-Out Test (Seed 42).",
        "LightGBM selected over Logistic Regression, Random Forest, & XGBoost.",
        "Platt sigmoid scaling transforms raw logits into true probabilities."
    ]
    for pt in points:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(2)

    # Right: High-Res Bureau Model Gain / Cumulative Lift Curve
    gain_img = 'reports/figures/fig_7_4_home_credit_gain.png'
    if os.path.exists(gain_img):
        add_card(s, Inches(6.3), Inches(1.5), Inches(6.233), Inches(5.3), bg_color=C_WHITE)
        s.shapes.add_picture(gain_img, Inches(6.4), Inches(1.6), Inches(6.033), Inches(5.1))


def build_slide_14(prs, layout):
    """Slide 14: Results Pillar 1 Behavioral ML with Model Comparison Plot"""
    s = prs.slides.add_slide(layout)
    add_header(s, "EXPERIMENTAL RESULTS · PILLAR 1 VALIDATION", "Empirical Evaluation: Behavioral Machine Learning")
    add_footer(s, 14)

    # Left: 4 Metric Cards
    add_metric_box(s, Inches(0.8), Inches(1.5), Inches(5.2), Inches(1.15), "0.7725", "ROC-AUC on Held-Out Test Set (30k UCI records)", val_color=C_BLUE_ACC)
    add_metric_box(s, Inches(0.8), Inches(2.78), Inches(5.2), Inches(1.15), "0.5304", "PR-AUC (Substantial Lift over 0.22 Baseline)", val_color=C_GREEN_ACC)
    add_metric_box(s, Inches(0.8), Inches(4.06), Inches(5.2), Inches(1.15), "81.53%", "Test Accuracy at Decision Threshold 0.20", val_color=C_NAVY_DARK)
    add_metric_box(s, Inches(0.8), Inches(5.34), Inches(5.2), Inches(1.15), "127 / 127", "Automated Pytest Checks Passing (100% Suite)", val_color=C_TEAL_ACC)

    # Right: High-Res Candidate Model Comparison Bar Chart
    comp_img = 'reports/figures/fig_7_1_model_comparison.png'
    if os.path.exists(comp_img):
        add_card(s, Inches(6.3), Inches(1.5), Inches(6.233), Inches(5.3), bg_color=C_WHITE)
        s.shapes.add_picture(comp_img, Inches(6.4), Inches(1.6), Inches(6.033), Inches(5.1))


def build_slide_15(prs, layout):
    """Slide 15: Conclusions & Future Work"""
    s = prs.slides.add_slide(layout)
    add_header(s, "SUMMARY & ROADMAP · RESEARCH IMPACT", "Key Conclusions & Future Engineering Roadmap")
    add_footer(s, 15)

    # Left Card: Conclusions
    add_card(s, Inches(0.8), Inches(1.5), Inches(5.75), Inches(5.3), bg_color=C_CARD_BG)
    tb_c = s.shapes.add_textbox(Inches(1.05), Inches(1.75), Inches(5.25), Inches(4.8))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    pc0 = tf_c.paragraphs[0]
    pc0.text = "RESEARCH CONCLUSIONS & CONTRIBUTIONS"
    pc0.font.name = FONT_FAMILY
    pc0.font.size = Pt(11)
    pc0.font.bold = True
    pc0.font.color.rgb = C_BLUE_ACC

    conclusions = [
        ("Dual-Pillar Supervised ML Platform",
         "Successfully eliminated reliance on arbitrary heuristic point cards by engineering an empirical 15-dimensional bridge linking statement features to 30,000 UCI default outcomes."),
        ("Empirical Performance Parity",
         "Achieved ROC-AUC 0.7725 and PR-AUC 0.5304 on behavioral default risk, paired with ROC-AUC 0.7737 on macro bureau benchmark with 100% 10-fold CV on transaction NLP."),
        ("Verifiable Explainability & Governance",
         "Delivered local interpretability via exact Tree-SHAP Shapley attributions, ensuring loan officers understand feature contributions before making decisions."),
        ("Cryptographic Integrity & DPDP Compliance",
         "Architected an immutable SHA-256 forward hash-chain ledger with external filesystem anchor and compliant tombstone PII erasure protocol.")
    ]
    for tag, desc in conclusions:
        p = tf_c.add_paragraph()
        p.text = f"•  {tag}: {desc}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(6)

    # Right Card: Future Work
    add_card(s, Inches(6.783), Inches(1.5), Inches(5.75), Inches(5.3), bg_color=C_CARD_BG)
    tb_f = s.shapes.add_textbox(Inches(7.033), Inches(1.75), Inches(5.25), Inches(4.8))
    tf_f = tb_f.text_frame
    tf_f.word_wrap = True

    pf0 = tf_f.paragraphs[0]
    pf0.text = "FUTURE ENGINEERING ROADMAP"
    pf0.font.name = FONT_FAMILY
    pf0.font.size = Pt(11)
    pf0.font.bold = True
    pf0.font.color.rgb = C_TEAL_ACC

    future_points = [
        ("Account Aggregator (AA) API Integration",
         "Integrate live RBI-regulated Account Aggregator connectors for automated, consent-based, tamper-proof electronic bank statement fetching."),
        ("Transformer-Based Vernacular NLP",
         "Deploy fine-tuned multilingual transformer models (FinBERT / IndicBERT) for deep semantic comprehension of regional Indian banking narrations."),
        ("Continuous Model Drift Tracking",
         "Implement real-time Population Stability Index (PSI) and Wasserstein distance monitoring to alert underwriters of macroeconomic distributional shifts."),
        ("Privacy-Preserving Federated Learning",
         "Establish secure federated learning protocols enabling multiple banking institutions to collaboratively train credit models without centralizing borrower data.")
    ]
    for tag, desc in future_points:
        p = tf_f.add_paragraph()
        p.text = f"•  {tag}: {desc}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(6)


def build_slide_16(prs, layout):
    """Slide 16: Tangible Outcomes Achieved & Deployment"""
    s = prs.slides.add_slide(layout)
    add_header(s, "DELIVERABLES · DEPLOYED ARTIFACTS", "Tangible Outcomes & Production Deployment")
    add_footer(s, 16)

    # Top Banner: Live Deployed Platform
    add_card(s, Inches(0.8), Inches(1.5), Inches(11.733), Inches(1.6), bg_color=C_NAVY_DARK, border_color=C_NAVY_DARK)
    tb_live = s.shapes.add_textbox(Inches(1.1), Inches(1.65), Inches(11.133), Inches(1.3))
    tf_l = tb_live.text_frame
    tf_l.word_wrap = True

    pl0 = tf_l.paragraphs[0]
    pl0.text = "PRODUCTION DEPLOYMENT & OPEN SOURCE"
    pl0.font.name = FONT_FAMILY
    pl0.font.size = Pt(10)
    pl0.font.bold = True
    pl0.font.color.rgb = RGBColor(0x38, 0xBD, 0xF8)

    pl1 = tf_l.add_paragraph()
    pl1.text = "Live Decision Support System:  https://behavioral-credit-system.streamlit.app"
    pl1.font.name = FONT_FAMILY
    pl1.font.size = Pt(14)
    pl1.font.bold = True
    pl1.font.color.rgb = C_WHITE
    pl1.space_before = Pt(3)

    pl2 = tf_l.add_paragraph()
    pl2.text = "Public GitHub Repository:  https://github.com/rohith5709/behavioral-credit-decision-support-system"
    pl2.font.name = FONT_FAMILY
    pl2.font.size = Pt(11)
    pl2.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
    pl2.space_before = Pt(3)

    # Bottom Left: Tangible Achievements
    add_card(s, Inches(0.8), Inches(3.3), Inches(5.75), Inches(3.5), bg_color=C_CARD_BG)
    tb_ach = s.shapes.add_textbox(Inches(1.05), Inches(3.45), Inches(5.25), Inches(3.2))
    tf_a = tb_ach.text_frame
    tf_a.word_wrap = True

    pa0 = tf_a.paragraphs[0]
    pa0.text = "COMPLETED ENGINEERING DELIVERABLES"
    pa0.font.name = FONT_FAMILY
    pa0.font.size = Pt(11)
    pa0.font.bold = True
    pa0.font.color.rgb = C_GREEN_ACC

    achievements = [
        "Live Production Dashboard: Deployed on Streamlit Cloud with Linux runtime and libgomp1 support.",
        "127 Passing Automated Pytest Tests: 100% test suite passing with zero failures across ML, bridge, & crypto logic.",
        "Comprehensive 58-Page Project Report: Formatted strictly according to IEEE/VIT standards with 24 tables & 13 figures.",
        "Reproducible Data Pipelines: Fully frozen random seeds (Seed 42) for deterministic model verification."
    ]
    for ach in achievements:
        p = tf_a.add_paragraph()
        p.text = f"✓  {ach}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(5)

    # Bottom Right: Targeted Outcomes
    add_card(s, Inches(6.783), Inches(3.3), Inches(5.75), Inches(3.5), bg_color=C_CARD_BG)
    tb_tgt = s.shapes.add_textbox(Inches(7.033), Inches(3.45), Inches(5.25), Inches(3.2))
    tf_t = tb_tgt.text_frame
    tf_t.word_wrap = True

    pt0 = tf_t.paragraphs[0]
    pt0.text = "TARGETED SCHOLARLY & INSTITUTIONAL OUTCOMES"
    pt0.font.name = FONT_FAMILY
    pt0.font.size = Pt(11)
    pt0.font.bold = True
    pt0.font.color.rgb = C_AMBER_ACC

    targets = [
        "Scopus-Indexed Conference Paper: Submission targeting international conference on AI in Financial Technology.",
        "Institutional IP & Copyright: Filing copyright protection for the proprietary 15-dimensional behavioral bridge architecture.",
        "Cooperative Banking Pilot: Initiating proof-of-concept evaluation with regional cooperative credit societies.",
        "Startup / Incubator Evaluation: Exploring commercial viability under university innovation incubators."
    ]
    for tgt in targets:
        p = tf_t.add_paragraph()
        p.text = f"🎯  {tgt}"
        p.font.name = FONT_FAMILY
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_TEXT_BODY
        p.space_before = Pt(5)


def build_slide_17(prs, layout):
    """Slide 17: References"""
    s = prs.slides.add_slide(layout)
    add_header(s, "SCHOLARLY CITATIONS · BIBLIOGRAPHY", "References & Foundational Literature")
    add_footer(s, 17)

    # Left Column: References 1-5
    add_card(s, Inches(0.8), Inches(1.5), Inches(5.75), Inches(5.3), bg_color=C_CARD_BG)
    tb_l = s.shapes.add_textbox(Inches(1.05), Inches(1.65), Inches(5.25), Inches(5.0))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    refs_1 = [
        "[1] I.-C. Yeh and C. Lien, “The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients,” Expert Syst. Appl., vol. 36, no. 2, pp. 2473–2480, 2009.",
        "[2] S. Lessmann, B. Baesens, H.-V. Seow, and L. C. Thomas, “Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research,” Eur. J. Oper. Res., vol. 247, no. 1, pp. 124–136, 2015.",
        "[3] A. E. Khandani, A. J. Kim, and A. W. Lo, “Consumer credit-risk models via machine-learning algorithms,” J. Bank. Financ., vol. 34, no. 11, pp. 2767–2787, 2010.",
        "[4] S. Bhatore, L. Mohan, and Y. R. Reddy, “Machine learning techniques for credit risk evaluation: A systematic literature review,” J. Bank. Financ. Technol., vol. 4, pp. 111–138, 2020.",
        "[5] G. Ke et al., “LightGBM: A highly efficient gradient boosting decision tree,” in Proc. NeurIPS, 2017, pp. 3146–3154."
    ]
    for idx, ref in enumerate(refs_1):
        p = tf_l.paragraphs[0] if idx == 0 else tf_l.add_paragraph()
        p.text = ref
        p.font.name = FONT_FAMILY
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_TEXT_BODY
        if idx > 0:
            p.space_before = Pt(6)

    # Right Column: References 6-9
    add_card(s, Inches(6.783), Inches(1.5), Inches(5.75), Inches(5.3), bg_color=C_CARD_BG)
    tb_r = s.shapes.add_textbox(Inches(7.033), Inches(1.65), Inches(5.25), Inches(5.0))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    refs_2 = [
        "[6] S. M. Lundberg and S.-I. Lee, “A unified approach to interpreting model predictions,” in Proc. NeurIPS, 2017, pp. 4765–4774.",
        "[7] J. C. Platt, “Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods,” in Advances in Large Margin Classifiers, MIT Press, 1999, pp. 61–74.",
        "[8] Home Credit Group, “Home Credit Default Risk,” Kaggle benchmark dataset, 2018.",
        "[9] Government of India, “The Digital Personal Data Protection Act, 2023,” Act No. 22 of 2023."
    ]
    for idx, ref in enumerate(refs_2):
        p = tf_r.paragraphs[0] if idx == 0 else tf_r.add_paragraph()
        p.text = ref
        p.font.name = FONT_FAMILY
        p.font.size = Pt(8.5)
        p.font.color.rgb = C_TEXT_BODY
        if idx > 0:
            p.space_before = Pt(8)


# =========================================================================
# MAIN EXECUTION
# =========================================================================

def main():
    print("Initializing Premium Presentation Deck...")
    prs, layout = create_deck()

    # Backup existing presentation if present
    if os.path.exists(OUTPUT_PATH):
        try:
            import shutil
            shutil.copyfile(OUTPUT_PATH, BACKUP_PATH)
            print(f"Backed up previous template to: {BACKUP_PATH}")
        except Exception as e:
            print(f"Backup notice: {e}")

    print("Building Slide 01: Cover...")
    build_slide_1(prs, layout)

    print("Building Slide 02: Guide Approval Mail...")
    build_slide_2(prs, layout)

    print("Building Slide 03: Aim & Principles...")
    build_slide_3(prs, layout)

    print("Building Slide 04: Executive Abstract & Metrics...")
    build_slide_4(prs, layout)

    print("Building Slide 05: Literature Review Part 1...")
    build_slide_5(prs, layout)

    print("Building Slide 06: Literature Review Part 2...")
    build_slide_6(prs, layout)

    print("Building Slide 07: Research Gaps...")
    build_slide_7(prs, layout)

    print("Building Slide 08: Objectives & SDGs...")
    build_slide_8(prs, layout)

    print("Building Slide 09: System Architecture with Embedded Diagram...")
    build_slide_9(prs, layout)

    print("Building Slide 10: 2x2 Decision Matrix with Embedded Graphic...")
    build_slide_10(prs, layout)

    print("Building Slide 11: Functional & Non-Functional Specifications...")
    build_slide_11(prs, layout)

    print("Building Slide 12: Modules (3x2 Production Grid)...")
    build_slide_12(prs, layout)

    print("Building Slide 13: Results Pillar 2 Bureau Benchmark...")
    build_slide_13(prs, layout)

    print("Building Slide 14: Results Pillar 1 Behavioral ML with Comparison Plot...")
    build_slide_14(prs, layout)

    print("Building Slide 15: Conclusions & Future Work...")
    build_slide_15(prs, layout)

    print("Building Slide 16: Tangible Outcomes & Deployment...")
    build_slide_16(prs, layout)

    print("Building Slide 17: References...")
    build_slide_17(prs, layout)

    assert len(prs.slides) == 17, f"Expected 17 slides, got {len(prs.slides)}"

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    prs.save(OUTPUT_PATH)
    print(f"\nSuccessfully generated premium presentation at: {OUTPUT_PATH}")
    print(f"File size: {os.path.getsize(OUTPUT_PATH):,} bytes")

    # Try updating main TARGET_MAIN as well if not locked
    try:
        import shutil
        shutil.copyfile(OUTPUT_PATH, TARGET_MAIN)
        print(f"Also updated main presentation file: {TARGET_MAIN}")
    except PermissionError:
        print(f"Notice: {TARGET_MAIN} is currently open in PowerPoint. Premium version saved to {OUTPUT_PATH}.")


if __name__ == "__main__":
    main()
