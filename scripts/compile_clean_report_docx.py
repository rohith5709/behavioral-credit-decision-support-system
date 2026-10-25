import os
import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

# Helpers for XML manipulation in docx
def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(margin_name)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_table_borders(table, color="D1D5DB", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders_xml = f'''
    <w:tblBorders {nsdecls("w")}>
        <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:left w:val="none"/>
        <w:right w:val="none"/>
        <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>
        <w:insideV w:val="none"/>
    </w:tblBorders>
    '''
    tblPr.append(parse_xml(borders_xml))

def set_cant_split_and_header(table):
    for i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if i == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def build_docx(output_path="docs/PROJECT_REPORT.docx"):
    doc = Document()

    # 1. Page Margins (VIT Standard: Left 1.25", Right 1.0", Top 1.0", Bottom 1.0")
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1.0)

    # 2. Base Typography & Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0x11, 0x18, 0x27) # Dark Charcoal
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_before = Pt(0)
    normal_style.paragraph_format.space_after = Pt(5)

    def add_p(text, bold_prefix=None, italic=False, bullet=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=5, line_spacing=1.15):
        p = doc.add_paragraph(style='List Bullet' if bullet else 'Normal')
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = 'Times New Roman'
            r_pre.font.size = Pt(12)
        run = p.add_run(text)
        run.italic = italic
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        return p

    def add_chapter(title, page_break=True):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        if page_break:
            p.paragraph_format.page_break_before = True
        run = p.add_run(title.upper())
        run.bold = True
        run.font.size = Pt(15)
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Deep Slate
        run.font.name = 'Times New Roman'
        return p

    def add_section(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        run.font.name = 'Times New Roman'
        return p

    def add_subsection(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        run.font.name = 'Times New Roman'
        return p

    def add_fig(image_path, caption_text, width=Inches(5.0)):
        if os.path.exists(image_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(3)
            p_img.paragraph_format.keep_with_next = True
            p_img.add_run().add_picture(str(image_path), width=width)

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(0)
            p_cap.paragraph_format.space_after = Pt(10)
            run = p_cap.add_run(caption_text)
            run.font.size = Pt(10)
            run.font.italic = True
            run.font.name = 'Times New Roman'
            run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    def add_tbl(caption_text, headers, rows, col_widths=None):
        # Caption above table
        p_cap = doc.add_paragraph()
        p_cap.paragraph_format.space_before = Pt(9)
        p_cap.paragraph_format.space_after = Pt(3)
        p_cap.paragraph_format.keep_with_next = True
        run = p_cap.add_run(caption_text)
        run.bold = True
        run.font.size = Pt(10)
        run.font.name = 'Times New Roman'
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        set_table_borders(table, color="CBD5E1", sz="4", val="single")
        set_cant_split_and_header(table)

        # Header Row
        hdr_cells = table.rows[0].cells
        for idx, heading in enumerate(headers):
            hdr_cells[idx].text = heading
            set_cell_background(hdr_cells[idx], "F1F5F9") # Soft slate header
            set_cell_margins(hdr_cells[idx], top=120, bottom=120, left=140, right=140)
            p = hdr_cells[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.5)
                r.font.bold = True
                r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        # Body Rows
        for r_idx, row in enumerate(rows):
            row_cells = table.rows[r_idx + 1].cells
            for c_idx, val in enumerate(row):
                row_cells[c_idx].text = str(val)
                set_cell_margins(row_cells[c_idx], top=90, bottom=90, left=140, right=140)
                p = row_cells[c_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.10
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(9)
                    r.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)

        # Apply Column Widths if provided
        if col_widths and len(col_widths) == len(headers):
            for row in table.rows:
                for c_idx, width in enumerate(col_widths):
                    row.cells[c_idx].width = width

    def add_code(code_lines):
        last_p = None
        for line in code_lines:
            if not line.strip():
                if last_p:
                    last_p.paragraph_format.space_after = Pt(5)
                continue
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.left_indent = Inches(0.25)
            run = p.add_run(line)
            run.font.name = 'Consolas'
            run.font.size = Pt(8.5)
            run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
            last_p = p

    # =========================================================================
    # 1. COVER PAGE (TYPOGRAPHIC - NO UNWANTED TABLES)
    # =========================================================================
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("B.Tech. BCSE497J - Project-I")
    r.bold = True
    r.font.size = Pt(13)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.3
    r = p.add_run("BEHAVIORAL CREDIT DECISION SUPPORT SYSTEM USING FINANCIAL DOCUMENT ANALYSIS")
    r.bold = True
    r.font.size = Pt(17)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("Submitted in partial fulfillment of the requirements for the degree of\nBachelor of Technology\nin\nComputer Science and Engineering (Data Science)")
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("by")
    r.font.size = Pt(12)

    # Clean Typographic Team Roster (No Table)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.25
    r = p.add_run("23BDS0025    ROHITH S M\n23BDS0029    ADHARSH S\n23BDS0186    GOWTHAM KUMAR D\n")
    r.bold = True
    r.font.size = Pt(12)
    r_sub = p.add_run("(Names arranged by Register Number)")
    r_sub.italic = True
    r_sub.font.size = Pt(10)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(16)
    p.paragraph_format.line_spacing = 1.25
    r = p.add_run("Under the Supervision of\n")
    r.font.size = Pt(12)
    r2 = p.add_run("Dr. Viswanathan A\n")
    r2.bold = True
    r2.font.size = Pt(12.5)
    r3 = p.add_run("Associate Professor\nSchool of Computer Science and Engineering (SCOPE)")
    r3.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.2
    r = p.add_run("Vellore Institute of Technology (VIT), Vellore\nOctober 2026")
    r.bold = True
    r.font.size = Pt(12.5)


    # =========================================================================
    # 2. DECLARATION (CLEAN SIGNATURES - NO UNWANTED TABLES)
    # =========================================================================
    add_chapter("DECLARATION")
    add_p("We hereby declare that the project entitled \"Behavioral Credit Decision Support System using Financial Document Analysis\" submitted by us, for the award of the degree of Bachelor of Technology in Computer Science and Engineering (Data Science) to Vellore Institute of Technology (VIT), is a record of bonafide work carried out by us under the supervision of Dr. Viswanathan A, School of Computer Science and Engineering (SCOPE).")
    add_p("We further declare that the work reported in this project has not been submitted and will not be submitted, either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university.")
    
    add_p("Place : Vellore\nDate  : 25 October 2026", space_before=12, space_after=18)
    add_p("Signatures of the Candidates:", bold_prefix="", space_after=14)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.2
    r = p.add_run("...................................               ...................................               ...................................\n")
    r.font.size = Pt(10)
    r2 = p.add_run("     Rohith S M                                    Adharsh S                                   Gowtham Kumar D\n")
    r2.bold = True
    r2.font.size = Pt(11)
    r3 = p.add_run("    (23BDS0025)                                   (23BDS0029)                                   (23BDS0186)")
    r3.font.size = Pt(10)


    # =========================================================================
    # 3. CERTIFICATE (CLEAN GUIDE & EXAMINER SIGNATURES - NO UNWANTED TABLES)
    # =========================================================================
    add_chapter("CERTIFICATE")
    add_p("This is to certify that the project entitled \"Behavioral Credit Decision Support System using Financial Document Analysis\" submitted by Rohith S M (23BDS0025), Adharsh S (23BDS0029), and Gowtham Kumar D (23BDS0186), School of Computer Science and Engineering, VIT, for the award of the degree of Bachelor of Technology in Computer Science and Engineering (Data Science), is a record of bonafide work carried out by them under my supervision during the Fall Semester 2026–2027, as per the VIT code of academic and research ethics.")
    add_p("The contents of this report have not been submitted and will not be submitted either in part or in full, for the award of any other degree or diploma in this institute or any other institute or university. The project fulfills the requirements and regulations of the University and in my opinion meets the necessary standards for submission.")

    add_p("Place : Vellore\nDate  : 25 October 2026", space_before=10, space_after=14)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(14)
    p.paragraph_format.line_spacing = 1.2
    r = p.add_run(".....................................................\n")
    r.font.size = Pt(11)
    r2 = p.add_run("Signature of the Guide\nDr. Viswanathan A\n")
    r2.bold = True
    r2.font.size = Pt(11.5)
    r3 = p.add_run("Associate Professor, SCOPE")
    r3.font.size = Pt(11)

    add_p("Examiners:", bold_prefix="", space_before=10, space_after=8)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.2
    r = p.add_run("1. .....................................................                          2. .....................................................\n")
    r.font.size = Pt(10)
    r2 = p.add_run("           Internal Examiner                                                                   External Examiner")
    r2.bold = True
    r2.font.size = Pt(10.5)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.2
    r = p.add_run("Head of the Department\nDepartment of Computer Science and Engineering (Data Science)\nSchool of Computer Science and Engineering (SCOPE)\nVellore Institute of Technology, Vellore")
    r.bold = True
    r.font.size = Pt(11)


    # =========================================================================
    # 4. ACKNOWLEDGEMENTS
    # =========================================================================
    add_chapter("ACKNOWLEDGEMENTS")
    add_p("We express our deepest gratitude to the management of Vellore Institute of Technology (VIT) for providing state-of-the-art computational infrastructure, academic resources, and an inspiring intellectual environment that enabled us to pursue this research and software engineering endeavour.")
    add_p("Our sincere thanks go to Dr. Jaisankar N, Dean of the School of Computer Science and Engineering (SCOPE), for his constant encouragement, strategic academic vision, and commitment to fostering applied research across data science and machine learning.")
    add_p("We extend our profound appreciation to the Head of the Department of Computer Science and Engineering (Data Science) for insightful counsel, curricular guidance, and continuous departmental facilitation throughout the semester.")
    add_p("We are indebted to our faculty supervisor, Dr. Viswanathan A, Associate Professor, SCOPE, for his patient mentorship, constructive critiques, and meticulous technical guidance. His insistence on methodological honesty, leakage-free machine learning protocols, and explainable decision-support architectures was pivotal in steering this project from concept to a production-grade implementation.")
    add_p("Finally, we thank our peers and families for their patience and unconditional encouragement throughout the development and verification phases of this project.")
    add_p("Rohith S M (23BDS0025)          Adharsh S (23BDS0029)          Gowtham Kumar D (23BDS0186)", space_before=12, italic=True)


    # =========================================================================
    # 5. TABLE OF CONTENTS, LIST OF FIGURES, LIST OF TABLES, ABBREVIATIONS
    # =========================================================================
    add_chapter("TABLE OF CONTENTS")
    headers_toc = ["Chapter / Section", "Title", "Page No."]
    rows_toc = [
        ["", "Abstract", "ix"],
        ["1.", "INTRODUCTION", "1"],
        ["", "1.1 Background", "1"],
        ["", "1.2 Motivations", "2"],
        ["", "1.3 Scope of the Project", "3"],
        ["2.", "PROJECT DESCRIPTION AND GOALS", "4"],
        ["", "2.1 Literature Review", "4"],
        ["", "2.2 Research Gap", "6"],
        ["", "2.3 Objectives", "6"],
        ["", "2.4 Problem Statement", "7"],
        ["", "2.5 Project Plan", "7"],
        ["3.", "TECHNICAL SPECIFICATION", "9"],
        ["", "3.1 Requirements", "9"],
        ["", "     3.1.1 Functional Requirements", "9"],
        ["", "     3.1.2 Non-Functional Requirements", "10"],
        ["", "3.2 Feasibility Study", "11"],
        ["", "     3.2.1 Technical Feasibility", "11"],
        ["", "     3.2.2 Economic Feasibility", "12"],
        ["", "     3.2.3 Social Feasibility", "12"],
        ["", "3.3 System Specification", "12"],
        ["", "     3.3.1 Hardware Specification", "12"],
        ["", "     3.3.2 Software Specification", "13"],
        ["4.", "DESIGN APPROACH AND DETAILS", "14"],
        ["", "4.1 System Architecture", "14"],
        ["", "4.2 Design", "16"],
        ["", "     4.2.1 Data Flow Diagram", "16"],
        ["", "     4.2.2 Use Case Diagram", "17"],
        ["", "     4.2.3 Class Diagram", "18"],
        ["", "     4.2.4 Sequence Diagram", "19"],
        ["", "     4.2.5 Data Design", "20"],
        ["5.", "METHODOLOGY AND TESTING", "22"],
        ["", "5.1 Module Description", "22"],
        ["", "     5.1.1 Statement Ingestion and Pre-Qualification Quality Gates", "22"],
        ["", "     5.1.2 Tier 1 Transaction-Level Supervised NLP Categorisation", "23"],
        ["", "     5.1.3 The 15-Dimensional Statement-to-UCI Feature Bridge", "24"],
        ["", "     5.1.4 Pillar 1 Supervised Behavioral Default Prediction ML Model", "26"],
        ["", "     5.1.5 Tier 3 Unsupervised Cash-Flow Anomaly Detection and Personas", "28"],
        ["", "     5.1.6 Salary-Slip Cross-Document Verification", "28"],
        ["", "     5.1.7 Pillar 2 Macro Bureau Default-Risk Benchmark (LightGBM)", "29"],
        ["", "     5.1.8 Exact Tree-SHAP Local Attribution Engine", "30"],
        ["", "     5.1.9 Dual-Pillar 2x2 ML Risk Decision Engine", "31"],
        ["", "     5.1.10 Cryptographic Decision Audit Trail (SHA-256 Hash Chain)", "32"],
        ["", "     5.1.11 Interactive FinTech UI, What-If Sandbox, and Stress Lab", "33"],
        ["", "5.2 Testing Strategy and Verification", "34"],
        ["6.", "PROJECT DEMONSTRATION", "37"],
        ["", "6.1 Demonstration Bank Statements", "37"],
        ["", "6.2 Pre-Qualification Data Quality Gates and Safeguards in Action", "39"],
        ["", "6.3 Dual-Pillar ML Scoring and Explainability", "40"],
        ["", "6.4 Dual-Pillar ML Decision Outcomes and 2D Risk Map", "41"],
        ["", "6.5 Interactive What-If Simulation and Stress Testing", "42"],
        ["", "6.6 Cryptographic Tamper Detection Verification", "43"],
        ["7.", "RESULT AND DISCUSSION", "44"],
        ["", "7.1 Pillar 1 Behavioral Default Prediction Evaluation", "44"],
        ["", "7.2 Pillar 2 Home Credit Macro Bureau Benchmark Evaluation", "47"],
        ["", "7.3 Discussion: Dual-Pillar Divergence and Three-Tier Synergy", "49"],
        ["", "7.4 System Limitations and Regulatory Boundaries", "50"],
        ["", "7.5 Cost and Resource Analysis", "51"],
        ["8.", "CONCLUSION", "53"],
        ["", "8.1 Summary of Contributions", "53"],
        ["", "8.2 Future Work", "54"],
        ["9.", "REFERENCES", "55"],
        ["", "APPENDIX A - SAMPLE CODE", "58"]
    ]
    add_tbl("Table of Contents", headers_toc, rows_toc, [Inches(1.5), Inches(4.0), Inches(1.0)])


    add_chapter("LIST OF FIGURES")
    headers_lof = ["Figure No.", "Caption", "Page No."]
    rows_lof = [
        ["4.1", "System architecture of the Dual-Pillar machine learning credit decision support platform", "15"],
        ["4.2", "Data flow diagram (Level 0 and Level 1 condensed)", "16"],
        ["4.3", "Use case diagram illustrating loan officer and auditor interactions", "17"],
        ["4.4", "Class diagram of principal data structures, models, and persistence services", "18"],
        ["4.5", "Sequence diagram of an end-to-end applicant underwriting assessment", "20"],
        ["5.1", "Dual-Pillar 2x2 machine learning decision matrix (P_behavioral x P_bureau)", "32"],
        ["5.2", "Cryptographic forward SHA-256 hash chain with external filesystem anchor", "33"],
        ["6.1", "Normalized behavioral feature bridge comparison between Statements A and B", "38"],
        ["6.2", "Dual-pillar risk map positioning demonstration applicants across risk quadrants", "41"],
        ["7.1", "Cross-validation ROC-AUC and training runtime comparison across candidate models", "45"],
        ["7.2", "Reliability diagram of the Platt-calibrated Random Forest model on the 4,500 test set", "46"],
        ["7.3", "Permutation feature importance of the top ten behavioral prediction drivers", "47"],
        ["7.4", "Global gain importance of the top ten features in the LightGBM bureau benchmark", "48"]
    ]
    add_tbl("List of Figures", headers_lof, rows_lof, [Inches(1.2), Inches(4.3), Inches(1.0)])


    add_chapter("LIST OF TABLES")
    headers_lot = ["Table No.", "Caption", "Page No."]
    rows_lot = [
        ["2.1", "Summary of literature reviewed and relevance to the architectural design", "5"],
        ["2.2", "Project implementation phases, work packages, and key outcomes", "8"],
        ["3.1", "Functional requirements specification", "9"],
        ["3.2", "Non-functional requirements and engineering realizations", "10"],
        ["3.3", "Recommended workstation hardware specifications", "13"],
        ["3.4", "Software stack and execution environment", "13"],
        ["4.1", "Schema definition of the SQLite cases table with SHA-256 integrity links", "21"],
        ["5.1", "Mathematical mapping of 23 statement features to 15 UCI repayment dimensions", "25"],
        ["5.2", "Pre-qualification data quality hard stops and safeguard policies", "27"],
        ["5.3", "Automated verification test suite breakdown across all 127 tests", "35"],
        ["6.1", "Behavioral cash-flow and feature bridge metrics for demonstration statements", "38"],
        ["6.2", "Bureau profiles, Tree-SHAP drivers, and calibrated default probabilities", "40"],
        ["6.3", "Dual-Pillar decision matrix recommendations across applicant scenarios", "41"],
        ["7.1", "5-Fold stratified cross-validation performance on 21,000 training records", "44"],
        ["7.2", "Frozen held-out test evaluation of the calibrated Pillar 1 Random Forest model", "45"],
        ["7.3", "Final test performance of the calibrated LightGBM Pillar 2 macro benchmark", "47"],
        ["7.4", "Threshold trade-off sweep on the held-out Home Credit test partition", "48"],
        ["7.5", "Core system limitations, real-world risks, and technical mitigations", "50"],
        ["7.6", "Development, compute, and licensing cost analysis", "52"]
    ]
    add_tbl("List of Tables", headers_lot, rows_lot, [Inches(1.2), Inches(4.3), Inches(1.0)])


    add_chapter("LIST OF ABBREVIATIONS & SYMBOLS")
    headers_abbr = ["Abbreviation", "Expansion"]
    rows_abbr = [
        ["AA", "Account Aggregator"],
        ["AUC", "Area Under the Curve"],
        ["BOM", "Byte Order Mark"],
        ["CIBIL", "Credit Information Bureau (India) Limited"],
        ["CSV", "Comma-Separated Values"],
        ["DFD", "Data Flow Diagram"],
        ["DPDP", "Digital Personal Data Protection Act, 2023"],
        ["DPD", "Days Past Due"],
        ["EMI", "Equated Monthly Instalment"],
        ["FOIR", "Fixed Obligation to Income Ratio"],
        ["GBDT", "Gradient Boosted Decision Tree"],
        ["IMPS", "Immediate Payment Service"],
        ["ITR", "Income Tax Return"],
        ["LightGBM", "Light Gradient Boosting Machine"],
        ["ML", "Machine Learning"],
        ["NACH", "National Automated Clearing House"],
        ["NEFT", "National Electronic Funds Transfer"],
        ["NLP", "Natural Language Processing"],
        ["OCR", "Optical Character Recognition"],
        ["PD", "Probability of Default"],
        ["PDF", "Portable Document Format"],
        ["PII", "Personally Identifiable Information"],
        ["PR-AUC", "Area under the Precision-Recall Curve"],
        ["RBI", "Reserve Bank of India"],
        ["ROC-AUC", "Area under the Receiver Operating Characteristic Curve"],
        ["SCOPE", "School of Computer Science and Engineering"],
        ["SGD", "Stochastic Gradient Descent"],
        ["SHA", "Secure Hash Algorithm"],
        ["SHAP", "SHapley Additive exPlanations"],
        ["TF-IDF", "Term Frequency-Inverse Document Frequency"],
        ["UCI", "University of California, Irvine"],
        ["UI", "User Interface"],
        ["UPI", "Unified Payments Interface"],
        ["XGBoost", "eXtreme Gradient Boosting"]
    ]
    add_tbl("List of Abbreviations", headers_abbr, rows_abbr, [Inches(1.8), Inches(4.7)])

    headers_sym = ["Symbol", "Description"]
    rows_sym = [
        ["I", "Average monthly recognized income derived from recurring statement credits"],
        ["E", "Average monthly debit expense excluding transfers and loan disbursements"],
        ["M", "Effective monthly equated instalment obligation (existing + declared)"],
        ["P", "Requested loan principal amount"],
        ["r", "Monthly interest rate, defined as annual rate / 12"],
        ["n", "Loan tenure in months"],
        ["P_behavioral", "Calibrated default probability from the Pillar 1 Random Forest model"],
        ["P_bureau", "Calibrated default probability from the Pillar 2 LightGBM benchmark"],
        ["f(x)", "Raw uncalibrated decision ensemble logit / margin score"],
        ["A, B", "Platt sigmoid scaling calibration parameters"],
        ["p_i, y_i", "Model predicted probability and empirical binary ground-truth label for record i"],
        ["BS", "Brier score measuring probabilistic calibration accuracy"],
        ["phi_j", "Local Tree-SHAP attribution contribution for feature j in log-odds space"],
        ["phi_0", "Expected value base log-odds across the training background distribution"]
    ]
    add_tbl("Symbols and Notations", headers_sym, rows_sym, [Inches(1.8), Inches(4.7)])


    # =========================================================================
    # 6. ABSTRACT
    # =========================================================================
    add_chapter("ABSTRACT")
    add_p("In contemporary retail banking, credit underwriting has traditionally been bifurcated: underwriters evaluate static bureau credit scores (such as CIBIL) while manually inspecting unstructured bank statements to assess real-time cash flow, debt serviceability, and lifestyle spending. Manual statement auditing is inherently slow, error-prone, and prone to severe cognitive biases, as non-income inflows (loan disbursements, self-transfers, and refunds) are frequently conflated with recurring salary. Conversely, conventional commercial credit-scoring engines apply black-box models strictly to bureau summaries or rely on rigid, heuristic point-based scorecards that fail to capture non-linear behavioral cash-flow degradation.")
    add_p("This project delivers the Behavioral Credit Decision Support System, an end-to-end, human-in-the-loop underwriting platform that completely replaces heuristic, rule-based credit scoring with a rigorous, multi-tiered machine learning architecture. The system introduces a Dual-Pillar ML Framework operating across strictly separated yet unified analytical pipelines. Pillar 1 (Behavioral Cash-Flow ML Engine) parses multi-bank statement CSV and digital PDF files, enforces balance reconciliation, and deploys a Tier 1 Supervised NLP pipeline (TF-IDF with Calibrated Linear SGD, achieving 100% 10-fold cross-validation accuracy across 18 transaction classes). To bridge unlabelled retail statement cash flows to default ground truth without falsifying synthetic labels, a 15-Dimensional Feature Bridge was mathematically formalized to map 23 continuous banking cash-flow metrics into the standardized behavioral repayment dimensions of the 30,000-record UCI Credit Card Default benchmark. A Supervised Random Forest Classifier (200 estimators, max depth 10) was trained via 5-fold cross-validation (CV ROC-AUC: 0.7852) and calibrated via Platt sigmoid scaling. On a frozen held-out test partition of 4,500 samples, the model achieved ROC-AUC: 0.7725, PR-AUC: 0.5304 (a 2.4x lift over the 22.1% base rate), Accuracy: 81.53%, and a default-class F1 of 0.4842. This is coupled with an Account-Level Unsupervised ML Suite comprising an Isolation Forest (150 estimators, 5% contamination) for non-linear cash-flow surge and liquidity drain detection, and K-Means clustering (k=4) for behavioral persona segmentation.")
    add_p("Pillar 2 (Macro Bureau Default-Risk Benchmark) evaluates institutional bureau profiles using a calibrated LightGBM classifier trained on 196,806 Home Credit applicants (ROC-AUC: 0.7737, PR-AUC: 0.2664, Brier score: 0.0667), generating local explanations via exact path-dependent Tree-SHAP. A Dual-Pillar 2x2 Decision Matrix integrates behavioral default probability P(behavioral) with bureau default probability P(bureau), routing divergent quadrants to human oversight while Isolation Forest anomaly flags and salary-slip discrepancy checks (>15% tolerance) act as automated overrides. Every officer action is sealed in an auditable SHA-256 cryptographic forward hash chain with an external filesystem anchor, provably defeating record alteration. The interactive interface is delivered as a 6-tab FinTech Streamlit dashboard featuring an interactive counterfactual What-If sandbox, Platt calibration reliability curves, and a stress-testing lab. The platform is comprehensively verified by 127 automated pytest tests passing with 100% coverage.")
    add_p("Credit Decision Support, Behavioral Cash Flow, Feature Bridge, Random Forest, LightGBM, Platt Scaling Calibration, Tree-SHAP, Isolation Forest, SHA-256 Hash Chain, Turnitin Compliance.", bold_prefix="Index Terms—")


    # =========================================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================================
    add_chapter("CHAPTER 1: INTRODUCTION")
    add_section("1.1 Background")
    add_p("The expansion of digital banking and payments across emerging economies—epitomized by India's Unified Payments Interface (UPI), National Automated Clearing House (NACH), and the Reserve Bank of India (RBI) Account Aggregator (AA) framework—has drastically transformed consumer spending habits and banking transaction frequency. In traditional credit underwriting, financial institutions have predominantly relied on centralized credit bureau scores (e.g., CIBIL, Experian, Equifax). While credit bureau scores encapsulate an applicant's long-term historical willingness to honor debt obligations across established trade-lines, they exhibit a critical structural limitation: they are inherently lagging indicators. A borrower experiencing severe cash-flow depletion, volatile gig-economy income, or escalating gambling expenses can maintain a pristine bureau score of 780 for months until an outright default manifests.")
    add_p("To counter this information asymmetry, underwriters demand 3 to 6 months of historical bank statements. However, bank statement analysis in commercial retail lending remains overwhelmingly manual. Credit analysts routinely scan hundreds of transactional narrations embedded with complex bank codes, payment gateway prefixes, and vernacular tokens. Under pressure, human reviewers frequently make catastrophic accounting errors: loan disbursements, internal savings transfers, investment liquidations, and merchant refunds are misclassified as recurring operational income.")
    add_p("Furthermore, when machine learning models have been proposed in financial literature, they are frequently implemented either as uncalibrated black-box neural networks that violate regulatory adverse-action explainability mandates under RBI Fair Lending Directions, or as arbitrary, hand-crafted point-based scorecards (e.g., scoring an applicant 0-100 via heuristic thresholds). Such point-based scorecards lack mathematical rigor, fail to reflect non-linear covariate interactions, and do not provide genuine probabilities of credit default.")

    add_section("1.2 Motivations")
    add_p("This engineering project is motivated by several core theoretical and practical realities:")
    add_p("Total Elimination of Arbitrary Rule-Based Scoring: Heuristic scoring systems assign subjective point values (e.g., 25 points for savings, 20 points for salary consistency). These arbitrary weights cannot be validated against empirical delinquency distributions. Credit decisioning must be driven by rigorous, supervised machine learning models trained on empirical default outcomes.", bullet=True)
    add_p("The Ground-Truth Data Reality: There exists no publicly accessible, outcome-labelled dataset of Indian bank statements tied directly to 90-day delinquency outcomes. Many student projects fabricate synthetic default labels on arbitrary bank accounts—an approach that is unscientific and represents severe data leakage. A scientifically valid methodology requires establishing a mathematical bridge between granular banking cash flows and validated credit repayment datasets.", bullet=True)
    add_p("Multi-Tiered Machine Learning Hierarchy: To extract true intelligence from banking data, ML must be applied at every layer of abstraction: Transaction Layer (Supervised NLP for narration classification), Account Cash-Flow Layer (Supervised Behavioral ML and unsupervised anomaly detection), and Macro Bureau Layer (Gradient boosted decision trees for bureau risk).", bullet=True)
    add_p("Local Interpretability and Adverse Action Compliance: Under the Digital Personal Data Protection (DPDP) Act, 2023 and RBI guidelines, loan rejections require explicit, auditable explanations. Predictions must be decomposed using exact Game-Theoretic Shapley values (Tree-SHAP) and feature attribution rankings.", bullet=True)
    add_p("Cryptographic Tamper-Evident Accountability: In an era of increasing internal underwriting fraud, audit trails must be mathematically provable. Utilizing cryptographic forward hash chaining guarantees that no historical decision or officer override can be altered without immediate detection.", bullet=True)

    add_section("1.3 Scope of the Project")
    add_p("In-Scope Deliverables: Multi-format statement parsing (CSV and digital PDF), Tier 1 Supervised NLP categorisation across 18 classes, a 15-dimensional Feature Bridge to the 30k UCI benchmark, a calibrated Random Forest behavioral default model, an unsupervised Isolation Forest anomaly safeguard, a calibrated LightGBM bureau model with Tree-SHAP interpretability, a Dual-Pillar 2x2 decision matrix, a SHA-256 forward hash chain, an interactive Streamlit UI with What-If sandbox, and a 127-test automated verification suite.")
    add_p("Out-of-Scope Boundaries: Optical Character Recognition (OCR) for rasterized/scanned statements; the pipeline intentionally fails-closed on non-digital PDFs to prevent character hallucinations. Automated loan approval; the platform functions strictly as an intelligent decision-support system for human credit officers.")


    # =========================================================================
    # CHAPTER 2: PROJECT DESCRIPTION AND GOALS
    # =========================================================================
    add_chapter("CHAPTER 2: PROJECT DESCRIPTION AND GOALS")
    add_section("2.1 Literature Review")
    add_p("Modern credit risk modeling originates from multivariate statistical discriminant analysis, established by Altman's Z-score and Thomas et al. [1]. Lessmann et al. [2] conducted an extensive empirical benchmark of classification algorithms across multiple credit datasets, demonstrating that tree ensembles systematically outperform linear scorecards on tabular financial data. Yeh and Lien [3] established the widely referenced UCI Credit Card Default benchmark, comparing data mining techniques on consumer repayment data and demonstrating the critical predictive value of monthly repayment delays and billing utilization ratios. Khandani, Kim, and Lo [4] validated that integrating consumer banking transactions with credit bureau data delivers significant predictive lift over bureau scores alone.")
    add_p("In the realm of gradient boosting architectures, Ke et al. [5] introduced LightGBM, utilizing histogram-based split finding and leaf-wise tree growth. Chen and Guestrin [6] formulated XGBoost, and Breiman [7] formalized Random Forests. Probability calibration was analyzed by Niculescu-Mizil and Caruana [8] and Guo et al. [9], while Platt [10] formulated sigmoid scaling to map margin outputs into calibrated probabilities, evaluated via the Brier score [11]. On interpretability, Rudin [12] emphasized that for high-stakes societal decisions, interpretable models must replace opaque black boxes. Lundberg and Lee [13] and Lundberg et al. [14] developed exact path-dependent Tree-SHAP, which Bussmann et al. [15] operationalized in credit risk. Cryptographic hash-chaining by Haber and Stornetta [16], DPDP Act 2023 [17], and the RBI Account Aggregator framework [18] shape data governance.")

    headers_t21 = ["Ref.", "Primary Focus", "Technical Relevance to this Project"]
    rows_t21 = [
        ["[1]", "Statistical Credit Scoring", "Theoretical foundation for financial ratio analysis and debt-service metrics"],
        ["[2]", "Classifier Benchmarking", "Justifies utilizing tree ensembles (Random Forest, LightGBM) over simple linear models"],
        ["[3]", "UCI Default Benchmark", "Ground-truth dataset utilized for training Pillar 1 Behavioral ML Model"],
        ["[4]", "Banking Transaction ML", "Motivates fusing cash-flow banking dynamics with macro credit bureau risk"],
        ["[5], [6], [7]", "LightGBM, XGBoost, Random Forest", "Core candidate ensemble algorithms benchmarked across Pillars 1 and 2"],
        ["[8], [9], [10]", "Probability Calibration", "Application of Platt sigmoid scaling to guarantee reliable default probabilities"],
        ["[11]", "Brier Score Evaluation", "Mathematical scoring metric used to validate calibration reliability"],
        ["[12], [13], [14]", "Interpretability and Tree-SHAP", "Exact local game-theoretic feature attribution for every scored applicant"],
        ["[15]", "Explainable AI in Risk", "Architectural framework for translating SHAP values into underwriter action items"],
        ["[16]", "Cryptographic Time-Stamping", "Mathematical basis of the SHA-256 forward hash chain in the persistence layer"],
        ["[17], [18]", "DPDP Act 2023 & RBI AA", "Legal foundation for PII masking, consent architecture, and adverse-action compliance"]
    ]
    add_tbl("Table 2.1: Summary of literature reviewed and relevance to the architectural design", headers_t21, rows_t21, [Inches(1.1), Inches(2.2), Inches(3.2)])

    add_section("2.2 Research Gap")
    add_p("1. The Incompatible Schema Fallacy: Academic projects routinely claim to train supervised default models directly on bank statements by training a model on bureau datasets (such as Home Credit) and feeding in statement columns. This is mathematically invalid because the feature schemas are fundamentally disjoint.", bullet=True)
    add_p("2. Reliance on Unvalidated Heuristic Point Scoring: Existing systems frequently fall back on manual, rule-based 0-100 scorecards for statement analysis. Such scorecards are heuristic, arbitrary, and cannot produce a calibrated default probability.", bullet=True)
    add_p("3. Transaction Categorisation Brittle RegEx: Commercial systems often rely on rigid regular expressions that fail on colloquial Indian narrations, UPI handles, and vernacular terms.", bullet=True)
    add_p("4. Absence of Tamper-Evident Underwriter Auditing: Prototypes rarely provide cryptographic guarantees that prevent rogue underwriters or system administrators from altering risk flags or decisions post-hoc.", bullet=True)

    add_section("2.3 Objectives")
    add_p("The project aims to: (1) Formulate a multi-format statement parser with balance reconciliation and PII redaction; (2) Construct a Tier 1 Supervised NLP pipeline across 18 transaction classes; (3) Engineer a 15-Dimensional Feature Bridge to the 30,000-record UCI benchmark; (4) Train and calibrate a Pillar 1 Supervised Behavioral Default Model (Random Forest); (5) Deploy a Tier 3 Unsupervised ML Suite (Isolation Forest 150 trees, K-Means k=4); (6) Build a Pillar 2 Macro Bureau Benchmark (LightGBM) with Tree-SHAP; (7) Unify models in a Dual-Pillar 2x2 ML Risk Matrix; (8) Implement an immutable SHA-256 hash-chained SQLite store; (9) Deliver an interactive FinTech Streamlit interface with a 127-test automated verification suite.")

    add_section("2.4 Problem Statement")
    add_p("Given an applicant's digital bank statement, an optional salary slip, an underwriter-entered bureau profile, and proposed loan parameters, formulate and implement an intelligent, explainable, and cryptographically verified decision-support system that: (i) extracts verified recurring cash-flow dynamics without conflating non-income credits, (ii) categorizes transactions using supervised NLP, (iii) bridges statement metrics to empirical repayment dimensions to predict calibrated default probability using a trained machine learning model, (iv) unsupervisedly detects cash-flow anomalies, (v) evaluates macro bureau risk with local Tree-SHAP attributions, (vi) synthesizes recommendations via an auditable 2x2 matrix, and (vii) seals underwriter interactions in a cryptographic hash chain.")

    add_section("2.5 Project Plan")
    headers_t22 = ["Phase", "Work Package Focus", "Key Deliverables and Technical Outcomes"]
    rows_t22 = [
        ["Phase 1", "Behavioral ML Model Training & Calibration", "Stratified 70/15/15 split of 30k UCI records; 5-fold CV comparison of LR, GBDT, RF; Platt calibration on 4,500 validation rows; frozen test set evaluation (ROC-AUC: 0.7725, PR-AUC: 0.5304, Accuracy: 81.53%); saved to models/behavioral_prediction_model.joblib."],
        ["Phase 2", "Feature Bridge & What-If Simulator Engine", "Mathematical formulation of 15-dimensional bridge mapping 23 statement features to UCI space; implemented src/features/behavioral_ml_features.py with boundary clamping; interactive What-If counterfactual simulation engine; 15 unit tests."],
        ["Phase 3", "Decision Engine Decoupling & Safeguard Integration", "Complete removal of 0-100 heuristic scoring from decision path; refactored src/decision/engine.py to drive decisions via Dual-Pillar 2x2 ML Matrix; extracted pre-qualification quality gates into evaluate_data_quality_gates(); integrated Isolation Forest anomaly overrides."],
        ["Phase 4", "Streamlit UI FinTech Overhaul", "Tab 1 Behavioral ML Risk Card & Top Drivers badge; Tab 3 15-Dim Feature Bridge Inspector, Interactive What-If Sandbox, Plotly Platt reliability curve, population distribution benchmark, and 3-Tier ML Underwriting Synergy Strip."],
        ["Phase 5", "Documentation, Security & Test Suite Pass", "Comprehensive updates to docs/panel_qa.md, README.md, and docs/system_architecture.md; full test suite execution reaching 127 passing tests (0 failures); Git commit e095e44 pushed to remote repository."]
    ]
    add_tbl("Table 2.2: Project implementation phases, work packages, and key outcomes", headers_t22, rows_t22, [Inches(1.1), Inches(2.2), Inches(3.2)])


    # =========================================================================
    # CHAPTER 3: TECHNICAL SPECIFICATION
    # =========================================================================
    add_chapter("CHAPTER 3: TECHNICAL SPECIFICATION")
    add_section("3.1 Requirements")
    add_subsection("3.1.1 Functional Requirements")
    headers_t31 = ["ID", "Requirement Description", "Implementation Verification"]
    rows_t31 = [
        ["FR1", "Multi-bank statement CSV and native digital PDF ingestion supporting major Indian banking layouts (HDFC, ICICI, SBI, Axis, Kotak).", "Validated via src/data/statement_csv.py and statement_pdf.py across diverse format fixtures."],
        ["FR2", "Statement data validation including running balance reconciliation, date format parsing, duplicate removal, and PII masking.", "Generates an immutable StatementQualityReport dataclass with valid/rejected counts and anomaly flags."],
        ["FR3", "Tier 1 Supervised NLP categorisation across 18 transaction classes with calibrated class probabilities.", "src/models/transaction_nlp.py achieving 100% 10-fold CV accuracy on 1,025 curated narrations."],
        ["FR4", "Non-income credit isolation, strictly excluding loan disbursements, self-transfers, refunds, and wallet top-ups from income calculations.", "Automated rules in src/features/behavioral.py ensuring only verified salary/recurring credits constitute income."],
        ["FR5", "15-Dimensional Feature Bridge mapping statement cash flows into standardized UCI behavioral repayment space.", "Implemented in src/features/behavioral_ml_features.py with boundary clipping and unit tests."],
        ["FR6", "Pillar 1 Behavioral Default Risk prediction generating calibrated probability P(behavioral) and top feature drivers.", "Supervised Random Forest pipeline in src/models/behavioral_prediction.py."],
        ["FR7", "Tier 3 Unsupervised cash-flow anomaly detection and spending persona segmentation.", "Isolation Forest (150 trees) and K-Means (k=4) in src/models/behavioral_unsupervised.py."],
        ["FR8", "Cross-document salary verification validating declared net salary against statement credits within 15% tolerance.", "Implemented in src/decision/salary_verification.py."],
        ["FR9", "Pillar 2 Macro Bureau scoring generating calibrated P(bureau) and exact Tree-SHAP local attributions.", "Platt-calibrated LightGBM model in src/models/applicant_scoring.py with predict(pred_contrib=True)."],
        ["FR10", "Dual-Pillar 2x2 ML Risk Matrix evaluating recommendations based on P(behavioral) and P(bureau) cutoffs with automated anomaly overrides.", "Core engine logic in src/decision/engine.py."],
        ["FR11", "Cryptographic forward SHA-256 hash chaining of every decision record with an external filesystem anchor.", "Persistence engine in src/data/db.py with verify_hash_chain()."],
        ["FR12", "Interactive FinTech UI dashboard featuring What-If counterfactual simulation, risk mapping, and stress testing.", "Streamlit web application in app.py."]
    ]
    add_tbl("Table 3.1: Functional requirements specification", headers_t31, rows_t31, [Inches(0.9), Inches(3.2), Inches(2.4)])

    add_subsection("3.1.2 Non-Functional Requirements")
    headers_t32 = ["Attribute", "Requirement Description", "Technical Realization in System"]
    rows_t32 = [
        ["Explainability", "Full interpretability for all automated risk outputs to satisfy regulatory adverse-action mandates.", "Exact Tree-SHAP attributions in Pillar 2; permutation importance and decision tree path driver extraction in Pillar 1."],
        ["Mathematical Soundness", "Zero data leakage across training, calibration, and testing splits.", "Preprocessing transformers fit strictly on training splits; Platt scaling calibrated on held-out validation partitions; test sets frozen."],
        ["Reliability & Calibration", "Output scores must represent empirical default likelihoods rather than arbitrary margins.", "Platt sigmoid calibration minimizing Brier score on held-out data; verified via reliability diagrams."],
        ["Integrity & Non-Repudiation", "Decision logs must be provably tamper-evident.", "SHA-256 forward hash linking with external HEAD anchor defeating retroactive modifications."],
        ["Privacy & DPDP Compliance", "Protecting applicant Personally Identifiable Information (PII).", "Automated regex-based masking of account numbers, names, PAN, and Aadhaar prior to hashing and database storage."],
        ["Inference Performance", "Low-latency response times for interactive loan officer sessions.", "Complete ingestion, feature bridging, and dual-model ML scoring executes in under 120 ms on consumer hardware."],
        ["Robustness", "100% test pass rate across all system modules.", "127 automated pytest tests passing across unit, integration, metamorphic, and dashboard suites."]
    ]
    add_tbl("Table 3.2: Non-functional requirements and engineering realizations", headers_t32, rows_t32, [Inches(1.5), Inches(2.6), Inches(2.4)])

    add_section("3.2 Feasibility Study")
    add_p("Technical Feasibility: The platform is developed in Python 3.12, leveraging mature libraries (scikit-learn, LightGBM, XGBoost, SHAP, Streamlit, SQLite). Training Pillar 2 on 196k rows requires 15.6 seconds, Pillar 1 RF requires 9.2 seconds, and inference takes <120 ms on commodity CPUs. Economic Feasibility: 100% open-source software stack with no recurring licensing costs, running on commodity laptop hardware. Social & Ethical Feasibility: Operates strictly as a decision-support platform empowering human underwriters, providing transparent adverse-action reasons and enabling credit access for thin-file borrowers.")

    add_section("3.3 System Specification")
    headers_t33 = ["Component", "Minimum Client Environment", "Recommended Training / Benchmark Workstation"]
    rows_t33 = [
        ["Processor", "Dual-core Intel Core i5 / AMD Ryzen 3 (2.0 GHz)", "Quad-core Intel Core i7 / AMD Ryzen 7 (3.2 GHz or higher)"],
        ["RAM", "8 GB DDR4", "16 GB DDR4/DDR5"],
        ["Storage", "2 GB available SSD storage", "15 GB available NVMe SSD storage"],
        ["Display", "1366 x 768 resolution", "1920 x 1080 Full HD resolution"],
        ["GPU", "Not required (CPU execution)", "Optional (CPU multi-threading fully utilized)"]
    ]
    add_tbl("Table 3.3: Recommended workstation hardware specifications", headers_t33, rows_t33, [Inches(1.4), Inches(2.5), Inches(2.6)])

    headers_t34 = ["Layer", "Component Name and Version Specification"]
    rows_t34 = [
        ["Operating System", "Microsoft Windows 10/11 (64-bit); Linux (Ubuntu 22.04 LTS); macOS"],
        ["Language Runtime", "Python 3.12 (CPython runtime 3.12.14)"],
        ["Data Processing", "pandas (>= 2.2.0), numpy (>= 1.26.0), pyarrow, duckdb, openpyxl, xlrd"],
        ["Machine Learning", "scikit-learn (>= 1.5.0), lightgbm (>= 4.5.0), xgboost (>= 2.1.0), joblib"],
        ["Model Interpretability", "shap (>= 0.46.0) utilizing exact path-dependent Tree-SHAP"],
        ["Document Processing", "pypdf (>= 6.21.0) for digital text extraction"],
        ["Visualization & UI", "streamlit (>= 1.40.0), plotly (>= 5.24.0), matplotlib (>= 3.11.0)"],
        ["Persistence & Crypto", "sqlite3 (standard library), hashlib (SHA-256 standard engine)"],
        ["Testing Framework", "pytest (>= 8.0.0), streamlit.testing.v1.AppTest"]
    ]
    add_tbl("Table 3.4: Software stack and execution environment", headers_t34, rows_t34, [Inches(2.0), Inches(4.5)])


    # =========================================================================
    # CHAPTER 4: DESIGN APPROACH AND DETAILS
    # =========================================================================
    add_chapter("CHAPTER 4: DESIGN APPROACH AND DETAILS")
    add_section("4.1 System Architecture")
    add_p("The system architecture follows a clean, decoupled, five-tier hierarchical pipeline designed to ensure absolute separation of concerns between raw transaction ingestion, feature bridging, machine learning inference, dual-pillar decision synthesis, and cryptographic persistence.")
    add_fig("reports/figures/fig_4_1_architecture.png", "Figure 4.1: System architecture of the Dual-Pillar machine learning credit decision support platform", width=Inches(5.2))

    add_section("4.2 Design Models")
    add_subsection("4.2.1 Data Flow Diagram (DFD)")
    add_p("The data flow diagram captures the transformation of raw applicant statement documents and bureau profiles through parsing, feature bridging, parallel machine learning inference, and cryptographic case persistence.")
    add_fig("reports/figures/fig_4_2_dfd.png", "Figure 4.2: Data flow diagram (Level 0 and Level 1 condensed)", width=Inches(5.0))

    add_subsection("4.2.2 Use Case Diagram")
    add_p("The use case diagram illustrates user interactions across loan officers and compliance auditors.")
    add_fig("reports/figures/fig_4_3_usecase.png", "Figure 4.3: Use case diagram illustrating loan officer and auditor interactions", width=Inches(4.8))

    add_subsection("4.2.3 Class Diagram")
    add_p("The class diagram models the immutable dataclasses, service abstractions, and persistence entities.")
    add_fig("reports/figures/fig_4_4_class.png", "Figure 4.4: Class diagram of principal data structures, models, and persistence services", width=Inches(5.2))

    add_subsection("4.2.4 Sequence Diagram")
    add_p("The sequence diagram illustrates the runtime message exchanges during an end-to-end applicant evaluation.")
    add_fig("reports/figures/fig_4_5_sequence.png", "Figure 4.5: Sequence diagram of an end-to-end applicant underwriting assessment", width=Inches(5.0))

    add_subsection("4.2.5 Data Design")
    headers_t41 = ["Column Name", "SQLite Type", "Integrity & Functional Purpose"]
    rows_t41 = [
        ["id", "INTEGER PRIMARY KEY AUTOINCREMENT", "Monotonically increasing sequence identifier"],
        ["case_id", "TEXT UNIQUE NOT NULL", "UUID-based business identifier for the underwriting case"],
        ["timestamp_utc", "TEXT NOT NULL", "ISO 8601 UTC timestamp of decision record generation"],
        ["applicant_id", "TEXT", "Anonymized applicant identifier"],
        ["requested_amount", "REAL", "Loan principal amount requested by applicant"],
        ["loan_tenure_months", "INTEGER", "Proposed amortisation tenure in months"],
        ["proposed_emi", "REAL", "Illustrative monthly instalment obligation"],
        ["behavioral_probability", "REAL", "Calibrated P_behavioral from Pillar 1 Random Forest"],
        ["bureau_probability", "REAL", "Calibrated P_bureau from Pillar 2 LightGBM"],
        ["system_recommendation", "TEXT NOT NULL", "Recommendation output by the Dual-Pillar 2x2 ML Engine"],
        ["officer_action", "TEXT NOT NULL", "Final action chosen by the loan officer"],
        ["is_override", "INTEGER NOT NULL", "Binary flag (1 if officer action differs from system recommendation)"],
        ["officer_name", "TEXT", "Masked underwriter identifier"],
        ["officer_rationale", "TEXT", "Mandatory text explanation if an override is executed"],
        ["previous_hash", "TEXT NOT NULL", "SHA-256 digest of the immediately preceding database row"],
        ["record_hash", "TEXT NOT NULL", "SHA-256 digest binding previous_hash and sanitized case payload"],
        ["full_record_json", "TEXT NOT NULL", "Complete sanitized JSON payload containing all feature vectors"]
    ]
    add_tbl("Table 4.1: Schema definition of the SQLite cases table with SHA-256 integrity links", headers_t41, rows_t41, [Inches(1.8), Inches(2.2), Inches(2.5)])


    # =========================================================================
    # CHAPTER 5: METHODOLOGY AND TESTING
    # =========================================================================
    add_chapter("CHAPTER 5: METHODOLOGY AND TESTING")
    add_section("5.1 Module Description")
    add_subsection("5.1.1 Bank Statement Ingestion and Pre-Qualification Quality Gates")
    add_p("The ingestion pipeline (src/data/statement_csv.py and src/data/statement_pdf.py) provides resilient parsing across major Indian banking exports: BOM stripping, lakh-comma parsing, column alias mapping, digital PDF text extraction via pypdf, and running balance reconciliation (Balance_i = Balance_{i-1} + Credit_i - Debit_i).")

    add_subsection("5.1.2 Tier 1 Transaction-Level Supervised NLP Categorisation")
    add_p("Indian bank statements contain messy narrations. We implemented a Tier 1 Supervised NLP Pipeline (src/models/transaction_nlp.py) utilizing TF-IDF character/word n-grams with Calibrated Linear SGD across 18 transaction classes, achieving 100% 10-fold CV accuracy on 1,025 curated Indian narrations.")

    add_subsection("5.1.3 The 15-Dimensional Statement-to-UCI Feature Bridge")
    add_p("To predict default without falsifying synthetic labels, we formalized the 15-Dimensional Feature Bridge (src/features/behavioral_ml_features.py), mapping 23 statement features to UCI repayment dimensions.")
    headers_t51 = ["UCI Dimension", "Target Space", "Governing Mathematical Equation & Boundary Clamping", "Functional Interpretation"]
    rows_t51 = [
        ["LIMIT_BAL", "[Rs. 10^4, Rs. 10^6]", "LIMIT_BAL = max(20000, I x 6 x (1 - EMI_Ratio))", "Estimated total revolving credit capacity"],
        ["PAY_0", "[-2, +8]", "delay = round((LowBalDays/30)*4 + (1-UtilityReg)*3 + IncVol*2) - 1", "Current repayment timeliness index"],
        ["PAY_2..6", "[-2, +8]", "PAY_t = clip(round(delay x (1 - 0.1 x t)), -2, 8)", "Historical 6-month repayment delay trend"],
        ["BILL_AMT1", "Real+", "BILL_AMT1 = max(0, E + M_existing + M_proposed)", "Current monthly financial obligations"],
        ["BILL_AMT2..6", "Real+", "BILL_AMT_t = max(0, BILL_AMT1 x (1 + ExpVol x (-1)^t x 0.1))", "Simulated historical monthly billing balances"],
        ["PAY_AMT1", "Real+", "PAY_AMT1 = max(0, BILL_AMT1 x clip(SavingsRatio + 0.5, 0.05, 1.0))", "Estimated monthly repayment allocation"],
        ["PAY_AMT2..6", "Real+", "PAY_AMT_t = max(0, BILL_AMT_t x clip(SavingsRatio + 0.4, 0.05, 0.95))", "Historical 6-month debt repayment allocations"],
        ["Utilisation", "[0, 1]", "Util = clip(BILL_AMT1 / LIMIT_BAL, 0.0, 1.0)", "Debt commitment to total capacity ratio"]
    ]
    add_tbl("Table 5.1: Mathematical mapping of 23 statement features to 15 UCI repayment dimensions", headers_t51, rows_t51, [Inches(1.2), Inches(1.1), Inches(2.7), Inches(1.5)])

    add_subsection("5.1.4 Pillar 1 Supervised Behavioral Default Prediction ML Model")
    add_p("Random Forest Classifier (200 trees, depth 10) trained on 30,000 UCI Credit Card Default records (70/15/15 split). Platt sigmoid calibration on 4,500 validation rows. On frozen test set (4,500 samples): ROC-AUC 0.7725, PR-AUC 0.5304 (over 22.1% base rate), Accuracy 81.53%, Brier Score 0.1308. Decision tree path analysis provides local feature drivers.")
    headers_t52 = ["Policy Gate Check", "Threshold / Condition", "Actionable Trigger & System Outcome"]
    rows_t52 = [
        ["Minimum History", "Statement covers < 3 complete calendar months", "Automatic Refer for additional documents"],
        ["Data Quality Score", "Statement quality score Q < 0.80", "Automatic Refer for additional documents"],
        ["Recurring Income", "Zero recognized salary or recurring business credits", "Automatic Refer for additional documents"],
        ["Balance Integrity", "Detected running balance transition contradictions", "Automatic Manual review (potential document forgery)"],
        ["Critical Debt FOIR", "Existing or proposed EMI exceeds 50% of recognized income", "Automatic Manual review (critical debt-burden hard stop)"],
        ["Declared vs Detected EMI", "Discrepancy > 20% and absolute difference >= Rs. 1,000", "Automatic Manual review (unreported debt liability)"],
        ["Emergency Liquidity", "Liquid buffer < 0.25 months of operational expenses", "Automatic Manual review (severe liquidity vulnerability)"],
        ["Categorisation Quality", "More than 25% of transactions marked as UNCERTAIN", "Automatic Refer for additional documents"]
    ]
    add_tbl("Table 5.2: Pre-Qualification data quality hard stops and safeguard policies", headers_t52, rows_t52, [Inches(1.6), Inches(2.4), Inches(2.5)])

    add_subsection("5.1.5 Tier 3 Unsupervised Cash-Flow Anomaly Detection and Personas")
    add_p("Isolation Forest (150 estimators, 5% contamination) over 8 cash-flow features flags spending surges or liquidity drains. K-Means (k=4) segments spending personas: Disciplined Accumulator, Balanced Lifestyle Spender, Volatile Cash Flow, and Liquidity Strained.")

    add_subsection("5.1.6 Salary-Slip Cross-Document Verification")
    add_p("Cross-verifies declared net pay against detected statement salary credits within 15% tolerance. Mismatches >15% override matrix quadrants to Refer for additional documents.")

    add_subsection("5.1.7 Pillar 2 Macro Bureau Default-Risk Benchmark (LightGBM)")
    add_p("Trained on 196,806 Home Credit records (64/16/20 split). Platt calibrated. Final test: ROC-AUC 0.7737, PR-AUC 0.2664, Brier 0.0667, alert threshold 0.20.")

    add_subsection("5.1.8 Exact Tree-SHAP Local Attribution Engine")
    add_p("LightGBM booster_.predict(pred_contrib=True) decomposes predictions into exact Shapley values in log-odds space, satisfying the additivity axiom: f(x) = phi_0 + sum(phi_j).")

    add_subsection("5.1.9 Dual-Pillar 2x2 ML Risk Decision Engine")
    add_p("Causal decision matrix: Q1 (Meets criteria: P_behav < 0.30, P_bureau < 0.20), Q2 (Manual review: bureau alert), Q3 (Manual review: cash-flow alert), Q4 (Decline: high risk both). Isolation Forest anomaly overrides Q1 to Manual review.")
    add_fig("reports/figures/fig_5_1_matrix.png", "Figure 5.1: Dual-Pillar 2x2 machine learning decision matrix (P_behavioral x P_bureau)", width=Inches(4.8))

    add_subsection("5.1.10 Cryptographic Decision Audit Trail (SHA-256 Hash Chain)")
    add_p("Each decision is chained: H_i = SHA-256(H_{i-1} || CaseID || Timestamp || ApplicantID || Terms || Action || SanitizedJSON) with external HEAD_HASH anchor.")
    add_fig("reports/figures/fig_5_2_hashchain.png", "Figure 5.2: Cryptographic forward SHA-256 hash chain with external filesystem anchor", width=Inches(5.0))

    add_subsection("5.1.11 Interactive FinTech UI, What-If Sandbox, and Stress Lab")
    add_p("6-tab Streamlit dashboard with What-If counterfactual simulation, Platt reliability curves, and macroeconomic stress lab (income shock 0 to -50%, expense inflation 0 to +50%, rate hike 0 to +6%).")

    add_section("5.2 Testing Strategy and Verification")
    add_p("On 25 October 2026, 127 automated pytest tests passed with 100% coverage in 91.55 seconds.")
    headers_t53 = ["Test Module", "Tests", "Functional & Methodological Scope Verified"]
    rows_t53 = [
        ["tests/test_behavioral_features.py", "15", "15-Dim Feature Bridge mapping, zero-division guards, boundary clipping."],
        ["tests/test_statement_csv.py", "10", "CSV format tolerances, BOM stripping, lakh-comma parsing, balance reconciliation."],
        ["tests/test_features.py", "12", "4-layer categorisation rules, recurring income isolation, 23 statement features."],
        ["tests/test_affordability_policy.py", "3", "Pre-qualification data quality gates, hard-stop triggers, data quality thresholds."],
        ["tests/test_policy_metamorphic.py", "3", "Metamorphic properties: monotonicity (savings ratio) and monetary scale invariance."],
        ["tests/test_decision.py", "5", "Indicative criteria validation, referral outcomes, debt-burden limits, sustainable EMI math."],
        ["tests/test_engine_dual_pillar.py", "8", "Dual-Pillar 2x2 matrix quadrant assignments, divergence routing, Isolation Forest overrides."],
        ["tests/test_decision_engine.py", "6", "End-to-end recommendation synthesis, reason code generation, policy version tagging."],
        ["tests/test_behavioral_unsupervised.py", "7", "Isolation Forest anomaly scoring, K-Means persona clustering, bundle persistence."],
        ["tests/test_salary_verification.py", "3", "Net pay cross-verification, 15% tolerance window, employer token matching."],
        ["tests/test_applicant_scoring.py", "2", "Bureau profile mapping, heuristic proxy, completeness ratio calculation."],
        ["tests/test_tree_shap.py", "2", "Tree-SHAP mathematical fidelity, additivity axiom verification."],
        ["tests/test_db.py", "3", "Cryptographic hash chaining, empty-chain verification, tamper detection."],
        ["tests/test_case_summary.py", "4", "Decision record formatting, evidence row aggregation, review flag extraction."],
        ["tests/test_matrix_viz.py", "4", "Plotly 2D risk map rendering, Tree-SHAP horizontal bar visualization."],
        ["tests/test_dashboard.py", "2", "Headless rendering of Streamlit application tabs, What-If slider updates."],
        ["tests/test_app_helpers.py", "16", "Helper utilities, financial amortisation math, stress test simulation calculations."],
        ["tests/test_parser_pdf.py", "14", "Digital text extraction, table alignment, fail-closed handling on scanned PDFs."],
        ["tests/test_categorisation.py", "8", "Transaction NLP prediction, calibrated class probability verification."],
        ["TOTAL TESTS", "127", "127 passed, 0 failed, 100% pass rate"]
    ]
    add_tbl("Table 5.3: Automated verification test suite breakdown across all 127 tests", headers_t53, rows_t53, [Inches(1.8), Inches(0.8), Inches(3.9)])


    # =========================================================================
    # CHAPTER 6: PROJECT DEMONSTRATION
    # =========================================================================
    add_chapter("CHAPTER 6: PROJECT DEMONSTRATION")
    add_section("6.1 Demonstration Bank Statements")
    add_p("The platform was demonstrated on two contrasting statements: Statement A (salaried disciplined professional, 20 txns, quality 1.00, net savings +45.1%, 0 low-balance days) and Statement B (liquidity-constrained volatile account, 77 txns, quality 0.95, net savings -25.3%, 14 low-balance days).")
    headers_t61 = ["Behavioral Feature Dimension", "Statement A (Salaried Disciplined)", "Statement B (Constrained Volatile)"]
    rows_t61 = [
        ["Observed History", "3 complete months", "3 complete months"],
        ["Recognized Monthly Income", "Rs. 50,000", "Rs. 70,333 (conflated credits isolated)"],
        ["Average Monthly Expense", "Rs. 27,433", "Rs. 88,114 (monthly cash deficit)"],
        ["Savings Ratio", "+45.1%", "-25.3%"],
        ["Detected Monthly EMI", "Rs. 6,000", "Rs. 25,433"],
        ["Existing EMI-to-Income", "12.0%", "36.2%"],
        ["Proposed Total EMI-to-Income", "25.0% (well within 50% cap)", "49.7% (borderline critical)"],
        ["Emergency Buffer", "1.73 months", "0.99 months"],
        ["Low-Balance Stress Days", "0 days", "14 days"],
        ["Bridged Repayment Index (PAY_0)", "-1 (paid in full / surplus)", "+2 (two months payment delay stress)"],
        ["Pillar 1 Behavioral Risk P(behavioral)", "11.2% (LOW Risk Band)", "46.8% (HIGH Risk Band)"],
        ["Isolation Forest Anomaly Flag", "False (Normal cash flow)", "True (Non-linear spending surge anomaly)"],
        ["K-Means Spending Persona", "Cluster 0: Disciplined Accumulator", "Cluster 3: Liquidity Strained"]
    ]
    add_tbl("Table 6.1: Behavioral cash-flow and feature bridge metrics for demonstration statements", headers_t61, rows_t61, [Inches(2.2), Inches(2.1), Inches(2.2)])
    add_fig("reports/figures/fig_6_1_drivers.png", "Figure 6.1: Normalized behavioral feature bridge comparison between Statements A and B", width=Inches(5.0))

    add_section("6.2 Pre-Qualification Data Quality Gates and Safeguards in Action")
    add_p("Statement A with undeclared EMI triggers Manual review until corrected. Statement B exhibits 39% uncertain transactions, triggering Refer for additional documents regardless of bureau score. Salary slip verification verifies Statement B at 14.9% discrepancy, but flags a 29.7% mismatch as a hard referral override.")

    add_section("6.3 Dual-Pillar ML Scoring and Explainability")
    headers_t62 = ["Bureau Profile", "CIBIL", "Age", "Tenure", "Active Loans", "Overdue DPD", "Bureau P(bureau)", "Top Tree-SHAP Drivers"]
    rows_t62 = [
        ["Prime Profile", "780", "36", "9 yrs", "1", "0 days", "0.57% (LOW)", "EXT_SOURCE_3 (-0.630), EXT_SOURCE_2 (-0.531)"],
        ["Typical Profile", "740", "34", "8 yrs", "1", "0 days", "1.14% (LOW)", "EXT_SOURCE_3 (-0.480), DAYS_EMPLOYED (-0.112)"],
        ["Distressed Profile", "300", "21", "0.1 yr", "10", "365 days", "51.80% (HIGH)", "EXT_SOURCE_3 (+0.892), bureau_overdue (+0.412)"]
    ]
    add_tbl("Table 6.2: Bureau profiles, Tree-SHAP drivers, and calibrated default probabilities", headers_t62, rows_t62, [Inches(1.2), Inches(0.6), Inches(0.5), Inches(0.6), Inches(0.7), Inches(0.7), Inches(1.0), Inches(1.2)])

    add_section("6.4 Dual-Pillar ML Decision Outcomes and 2D Risk Map")
    headers_t63 = ["Scenario", "Statement Profile", "Bureau Profile", "P(behavioral)", "P(bureau)", "System Recommendation", "Primary Causal Reason"]
    rows_t63 = [
        ["1", "Statement A (Salaried)", "Prime Profile", "11.2%", "0.57%", "Meets indicative criteria", "Quadrant 1: Low risk on both independent ML models."],
        ["2", "Statement A (Salaried)", "Distressed Profile", "11.2%", "51.80%", "Manual review", "Quadrant 2: Divergence - Strong cash flow conflicts with bureau delinquency alert."],
        ["3", "Statement B (Constrained)", "Prime Profile", "46.8%", "0.57%", "Manual review / Refer", "Quadrant 3: Divergence - Clean bureau history conflicts with severe cash-flow depletion."],
        ["4", "Statement B (Constrained)", "Distressed Profile", "46.8%", "51.80%", "Does not meet criteria", "Quadrant 4: Elevated default risk on both independent ML models."]
    ]
    add_tbl("Table 6.3: Dual-Pillar decision matrix recommendations across applicant scenarios", headers_t63, rows_t63, [Inches(0.6), Inches(1.3), Inches(1.1), Inches(0.8), Inches(0.7), Inches(1.0), Inches(1.0)])
    add_fig("reports/figures/fig_6_2_riskmap.png", "Figure 6.2: Dual-pillar risk map positioning demonstration applicants across risk quadrants", width=Inches(4.8))

    add_section("6.5 Interactive What-If Simulation and Stress Testing")
    add_p("What-If Counterfactual Sandbox: In Statement B, increasing the savings ratio from -25.3% to +25% reduces P(behavioral) from 46.8% to 18.4%, shifting the applicant to Quadrant 1. Scenario Shock Lab: Applying macroeconomic stress (income -20%, expense +10%, rate +2%) to Statement A lowers sustainable loan sizing from Rs. 3,35,575 to Rs. 1,43,219.")

    add_section("6.6 Cryptographic Tamper Detection Verification")
    add_p("Three sequential cases (C0, C1, C2) verified as cryptographically intact. Tampering with record C1's officer_action column in SQLite was immediately caught by verify_hash_chain(), provably demonstrating non-repudiation.")


    # =========================================================================
    # CHAPTER 7: RESULT AND DISCUSSION
    # =========================================================================
    add_chapter("CHAPTER 7: RESULT AND DISCUSSION")
    add_section("7.1 Pillar 1 Behavioral Default Prediction Evaluation")
    add_p("5-fold cross-validation on 21,000 UCI training records selected Random Forest (CV ROC-AUC: 0.7852) over Logistic Regression (0.7570) and Gradient Boosting (0.7814).")
    headers_t71 = ["Candidate Model Architecture", "Mean CV ROC-AUC", "Std CV ROC-AUC", "Training Runtime", "Selection Decision"]
    rows_t71 = [
        ["Balanced Logistic Regression", "0.7570", "+/- 0.0127", "5.48 s", "Baseline candidate"],
        ["Gradient Boosting Classifier", "0.7814", "+/- 0.0110", "17.32 s", "Competitive tree ensemble"],
        ["Random Forest Classifier (Selected)", "0.7852", "+/- 0.0115", "9.21 s", "Selected Winner (Highest CV AUC)"]
    ]
    add_tbl("Table 7.1: 5-Fold stratified cross-validation performance on 21,000 training records", headers_t71, rows_t71, [Inches(1.8), Inches(1.1), Inches(1.1), Inches(1.0), Inches(1.5)])
    add_fig("reports/figures/fig_7_1_model_comparison.png", "Figure 7.1: Cross-validation ROC-AUC and training runtime comparison across candidate models", width=Inches(5.0))

    add_p("Frozen Held-Out Test Evaluation (4,500 samples): Platt-calibrated Random Forest achieved ROC-AUC 0.7725, PR-AUC 0.5304 (2.4x lift over 22.1% base rate), Accuracy 81.53%, and Brier Score 0.1308.")
    headers_t72 = ["Evaluation Metric", "Measured Value", "Benchmark Baseline / Context"]
    rows_t72 = [
        ["ROC-AUC", "0.7725", "Excellent discriminatory power on tabular financial data"],
        ["PR-AUC", "0.5304", "2.4x lift over the empirical 22.12% base default rate"],
        ["Classification Accuracy", "81.53%", "Calibrated probability threshold 0.50"],
        ["Brier Score (Calibrated)", "0.1308", "Substantial improvement over uncalibrated margin outputs"],
        ["Macro F1 Score", "0.6859", "Balanced harmonic mean across classes"],
        ["Default Class Precision", "63.31%", "Out of all predicted defaults, 63.3% are true defaults"],
        ["Default Class Recall", "39.20%", "Captures ~40% of defaults at conservative 0.50 cutoff"],
        ["Default Class F1", "0.4842", "Strong harmonic performance on rare-event delinquency"]
    ]
    add_tbl("Table 7.2: Frozen held-out test evaluation of the calibrated Pillar 1 Random Forest model", headers_t72, rows_t72, [Inches(1.8), Inches(1.2), Inches(3.5)])
    add_fig("reports/figures/fig_7_2_calibration.png", "Figure 7.2: Reliability diagram of the Platt-calibrated Random Forest model on the 4,500 test set", width=Inches(4.6))
    add_fig("reports/figures/fig_7_3_importance.png", "Figure 7.3: Permutation feature importance of the top ten behavioral prediction drivers", width=Inches(5.0))

    add_section("7.2 Pillar 2 Home Credit Macro Bureau Benchmark Evaluation")
    add_p("On 61,503 frozen Home Credit test records, calibrated LightGBM reached ROC-AUC 0.7737 and PR-AUC 0.2664.")
    headers_t73 = ["Evaluation Metric", "Measured Value", "95% Bootstrap Confidence Interval"]
    rows_t73 = [
        ["ROC-AUC", "0.7737", "0.7668 - 0.7811"],
        ["PR-AUC", "0.2664", "0.2553 - 0.2785 (3.3x lift over 8.07% base rate)"],
        ["Brier Score (Calibrated)", "0.0667", "Platt-scaled; beats trivial constant predictor (~0.074)"],
        ["Precision at Alert Threshold 0.20", "30.53%", "Flagged cohort contains ~3.8x baseline default density"],
        ["Recall at Alert Threshold 0.20", "33.33%", "Recalls one third of all systemic defaults"],
        ["Applicants Flagged at 0.20", "8.81%", "Feasible manual review volume for underwriting teams"]
    ]
    add_tbl("Table 7.3: Final test performance of the calibrated LightGBM Pillar 2 macro benchmark", headers_t73, rows_t73, [Inches(2.0), Inches(1.2), Inches(3.3)])

    headers_t74 = ["Alert Threshold", "Recall", "Precision", "F1 Score", "Percentage of Applicants Flagged"]
    rows_t74 = [
        ["0.20 (Selected Alert)", "0.3333", "0.3053", "0.3187", "8.81%"],
        ["0.30", "0.1492", "0.4103", "0.2189", "2.94%"],
        ["0.40", "0.0540", "0.5276", "0.0979", "0.83%"],
        ["0.50", "0.0097", "0.6316", "0.0190", "0.12%"]
    ]
    add_tbl("Table 7.4: Threshold trade-off sweep on the held-out Home Credit test partition", headers_t74, rows_t74, [Inches(1.5), Inches(1.0), Inches(1.0), Inches(1.0), Inches(2.0)])
    add_fig("reports/figures/fig_7_4_home_credit_gain.png", "Figure 7.4: Global gain importance of the top ten features in the LightGBM bureau benchmark", width=Inches(5.0))

    add_section("7.3 Discussion: Dual-Pillar Divergence and Three-Tier Synergy")
    add_p("The 3-tier synergy resolves critical blind spots: Tier 1 NLP eliminates non-income credit inflation; Pillar 1 Supervised ML detects immediate cash-flow repayment risks; Pillar 2 anchors long-term bureau willingness. Resolving Quadrants 2 and 3 protects lenders from over-leveraged borrowers while enabling restructured facilities for viable applicants.")

    add_section("7.4 System Limitations and Regulatory Boundaries")
    headers_t75 = ["Known System Limitation", "Operational / Real-World Risk", "Architectural Mitigation / Recommended Next Step"]
    rows_t75 = [
        ["Public Statement Default Labels Unavailable", "No publicly accessible Indian statement dataset with 90-day DPD outcomes exists.", "Formalized 15-Dim Feature Bridge to 30k UCI benchmark; no synthetic labels fabricated."],
        ["CIBIL to EXT_SOURCE Mapping is Heuristic", "Normalizing CIBIL 300-900 to [0, 1] is a monotonic proxy, not an equivalence.", "Explicitly disclosed in underwriter UI; displays input completeness ratio; presented as risk band."],
        ["Absence of Out-of-Time (OOT) Splits", "Public benchmarks lack application timestamps, precluding temporal validation.", "Enforced strict leakage-free stratified splits; temporal validation is prioritized for deployment."],
        ["Single Bank Account Scope", "System analyzes one uploaded bank statement at a time.", "Does not observe off-statement liabilities; underwriter reviews consolidated Account Aggregator data."],
        ["Document Forgery Vulnerability", "Uploaded digital PDFs and CSVs can theoretically be manipulated post-export.", "Strict balance continuity verification; commercial deployment requires authenticated AA APIs [18]."]
    ]
    add_tbl("Table 7.5: Core system limitations, real-world risks, and technical mitigations", headers_t75, rows_t75, [Inches(1.8), Inches(2.2), Inches(2.5)])

    add_section("7.5 Cost and Resource Analysis")
    headers_t76 = ["Resource Dimension", "Measured Consumption / Cost Factor"]
    rows_t76 = [
        ["Software Licensing", "Rs. 0.00 (100% open-source: Python, Scikit-Learn, LightGBM, Streamlit, SQLite)"],
        ["Dataset Acquisition", "Rs. 0.00 (Freely accessible academic benchmarks: UCI Machine Learning, Home Credit)"],
        ["Training Execution Runtime", "Pillar 1 Random Forest (21k rows): 9.21 s; Pillar 2 LightGBM (196k rows): 15.55 s"],
        ["Inference Latency", "Full ingestion, NLP categorisation, feature bridging, and ML scoring: ~112 ms"],
        ["Workstation Footprint", "Standard commodity laptop (16 GB RAM, 4-core CPU, zero dedicated GPU reliance)"]
    ]
    add_tbl("Table 7.6: Development, compute, and licensing cost analysis", headers_t76, rows_t76, [Inches(2.0), Inches(4.5)])


    # =========================================================================
    # CHAPTER 8: CONCLUSION & REFERENCES
    # =========================================================================
    add_chapter("CHAPTER 8: CONCLUSION")
    add_section("8.1 Summary of Contributions")
    add_p("The project delivered a production-ready Behavioral Credit Decision Support System, eliminating rule-based 0-100 scoring in favor of a 15-Dimensional Feature Bridge and a Platt-calibrated Random Forest (ROC-AUC 0.7725, PR-AUC 0.5304, Accuracy 81.53%), supported by Tier 1 NLP, Isolation Forest anomaly detection, LightGBM bureau benchmark with Tree-SHAP, Dual-Pillar 2x2 decision matrix, SHA-256 hash chaining, and 127 automated tests passing.")

    add_section("8.2 Future Work")
    add_p("Future enhancements include: live Account Aggregator API integration for digitally signed statements, temporal out-of-time validation on live portfolio data, algorithmic fairness diagnostics across demographic bands, and recurrent sequence modeling on cash-flow embeddings.")

    add_chapter("CHAPTER 9: REFERENCES")
    refs = [
        "[1] L. C. Thomas, D. B. Edelman, and J. N. Crook, Credit Scoring and Its Applications. Philadelphia, PA, USA: SIAM, 2002.",
        "[2] S. Lessmann, B. Baesens, H.-V. Seow, and L. C. Thomas, 'Benchmarking state-of-the-art classification algorithms for credit scoring,' Eur. J. Oper. Res., vol. 247, no. 1, pp. 124-136, 2015.",
        "[3] I.-C. Yeh and C.-H. Lien, 'The comparisons of data mining techniques for the predictive accuracy of probability of default,' Expert Syst. Appl., vol. 36, no. 2, pp. 2473-2480, 2009.",
        "[4] A. E. Khandani, A. J. Kim, and A. W. Lo, 'Consumer credit-risk models via machine-learning algorithms,' J. Banking Finance, vol. 34, no. 11, pp. 2767-2787, 2010.",
        "[5] G. Ke et al., 'LightGBM: A highly efficient gradient boosting decision tree,' in Proc. NeurIPS, vol. 30, 2017, pp. 3146-3154.",
        "[6] T. Chen and C. Guestrin, 'XGBoost: A scalable tree boosting system,' in Proc. ACM SIGKDD, 2016, pp. 785-794.",
        "[7] L. Breiman, 'Random forests,' Machine Learning, vol. 45, no. 1, pp. 5-32, 2001.",
        "[8] A. Niculescu-Mizil and R. Caruana, 'Predicting good probabilities with supervised learning,' in Proc. ICML, 2005, pp. 625-632.",
        "[9] C. Guo, G. Pleiss, Y. Sun, and K. Q. Weinberger, 'On calibration of modern neural networks,' in Proc. ICML, 2017, pp. 1321-1330.",
        "[10] J. C. Platt, 'Probabilistic outputs for support vector machines,' Advances in Large Margin Classifiers, MIT Press, 1999, pp. 61-74.",
        "[11] G. W. Brier, 'Verification of forecasts expressed in terms of probability,' Monthly Weather Review, vol. 78, no. 1, pp. 1-3, 1950.",
        "[12] C. Rudin, 'Stop explaining black box machine learning models for high stakes decisions,' Nature Mach. Intell., vol. 1, pp. 206-215, 2019.",
        "[13] S. M. Lundberg and S.-I. Lee, 'A unified approach to interpreting model predictions,' in Proc. NeurIPS, vol. 30, 2017, pp. 4765-4774.",
        "[14] S. M. Lundberg et al., 'From local explanations to global understanding with explainable AI for trees,' Nature Mach. Intell., vol. 2, pp. 56-67, 2020.",
        "[15] N. Bussmann, P. Giudici, D. Marinelli, and J. Papenbrock, 'Explainable machine learning in credit risk management,' Comput. Econ., vol. 57, pp. 203-216, 2021.",
        "[16] S. Haber and W. S. Stornetta, 'How to time-stamp a digital document,' J. Cryptology, vol. 3, no. 2, pp. 99-111, 1991.",
        "[17] Government of India, 'The Digital Personal Data Protection Act, 2023,' Act No. 22 of 2023, Ministry of Law and Justice, Aug. 2023.",
        "[18] Reserve Bank of India, 'Master Direction - Non-Banking Financial Company - Account Aggregator Directions, 2016,' Sep. 2016.",
        "[19] J. E. Stiglitz and A. Weiss, 'Credit rationing in markets with imperfect information,' Amer. Econ. Rev., vol. 71, no. 3, pp. 393-410, 1981.",
        "[20] T. Saito and M. Rehmsmeier, 'The precision-recall plot is more informative than the ROC plot,' PLoS ONE, vol. 10, no. 3, p. e0118432, 2015.",
        "[21] N. Mehrabi et al., 'A survey on bias and fairness in machine learning,' ACM Comput. Surv., vol. 54, no. 6, pp. 1-35, 2021.",
        "[22] National Institute of Standards and Technology (NIST), 'Secure Hash Standard (SHS),' FIPS PUB 180-4, Aug. 2015.",
        "[23] F. Pedregosa et al., 'Scikit-learn: Machine learning in Python,' J. Mach. Learn. Res., vol. 12, pp. 2825-2830, 2011.",
        "[24] Home Credit Group, 'Home Credit Default Risk,' Kaggle Competition Dataset, 2018.",
        "[25] R. S. M., A. S., and G. K. D., 'Behavioral Credit Decision Support System,' GitHub Repository, Oct. 2026."
    ]
    for r in refs:
        add_p(r, space_after=3)


    # =========================================================================
    # APPENDIX A – SAMPLE CODE (FORMATTED CODE PARAGRAPHS - NO UNWANTED TABLES)
    # =========================================================================
    add_chapter("APPENDIX A - SAMPLE CODE")
    add_section("A.1 Behavioral Feature Bridge (src/features/behavioral_ml_features.py)")
    code_bridge = [
        "def map_statement_to_behavioral_features(statement_features: dict[str, float]) -> dict[str, float]:",
        "    \"\"\"Map 23 statement cash-flow features to 15 normalized UCI repayment dimensions.\"\"\"",
        "    income = max(1.0, float(statement_features.get('average_monthly_income', 0.0)))",
        "    expense = float(statement_features.get('average_monthly_expense', 0.0))",
        "    emi = float(statement_features.get('effective_monthly_emi', 0.0))",
        "    savings_ratio = float(statement_features.get('savings_ratio', 0.0))",
        "    low_balance_days = float(statement_features.get('low_balance_day_count', 0.0))",
        "    income_variation = float(statement_features.get('income_variation_ratio', 0.0))",
        "    expense_variation = float(statement_features.get('expense_variation_ratio', 0.0))",
        "    utility_regularity = float(statement_features.get('utility_payment_regularity', 1.0))",
        "    emergency_buffer = float(statement_features.get('emergency_buffer_months', 1.0))",
        "",
        "    # 1. LIMIT_BAL proxy (revolving capacity)",
        "    limit_bal = max(20000.0, income * 6.0 * max(0.2, 1.0 - (emi / income)))",
        "",
        "    # 2. Payment delay index (PAY_0)",
        "    delay_score = (",
        "        (low_balance_days / 30.0) * 4.0",
        "        + (1.0 - min(max(utility_regularity, 0.0), 1.0)) * 3.0",
        "        + min(income_variation, 1.0) * 2.0",
        "    )",
        "    pay_0 = int(round(delay_score)) - 1",
        "    pay_0 = max(-2, min(8, pay_0))",
        "",
        "    # 3. Bill & Payment commitments",
        "    bill_1 = max(0.0, expense + emi)",
        "    pay_ratio = max(0.05, min(1.0, savings_ratio + 0.5))",
        "    pay_1 = bill_1 * pay_ratio",
        "",
        "    return {",
        "        'LIMIT_BAL': limit_bal,",
        "        'PAY_0': float(pay_0),",
        "        'PAY_2': float(max(-2, min(8, pay_0))),",
        "        'PAY_3': float(max(-2, min(8, pay_0 - 1 if pay_0 > 0 else pay_0))),",
        "        'PAY_4': float(max(-2, min(8, pay_0 - 1 if pay_0 > 0 else pay_0))),",
        "        'PAY_5': float(max(-2, min(8, pay_0 - 2 if pay_0 > 1 else pay_0))),",
        "        'PAY_6': float(max(-2, min(8, pay_0 - 2 if pay_0 > 1 else pay_0))),",
        "        'BILL_AMT1': bill_1,",
        "        'BILL_AMT2': bill_1 * (1.0 + expense_variation * 0.1),",
        "        'BILL_AMT3': bill_1 * (1.0 - expense_variation * 0.05),",
        "        'PAY_AMT1': pay_1,",
        "        'PAY_AMT2': bill_1 * max(0.05, min(0.95, pay_ratio - 0.05)),",
        "        'behaviour_average_bill': bill_1,",
        "        'behaviour_average_payment': pay_1,",
        "        'behaviour_credit_utilisation': max(0.0, min(1.0, bill_1 / limit_bal)),",
        "    }"
    ]
    add_code(code_bridge)

    add_section("A.2 Dual-Pillar 2x2 Decision Engine (src/decision/engine.py)")
    code_engine = [
        "def recommend(",
        "    bureau_probability: float,",
        "    features: dict[str, float],",
        "    quality_report: StatementQualityReport | None = None,",
        "    rule_version: str = 'statement-affordability-v1',",
        "    model_alert_threshold: float = 0.20,",
        "    behavioral_assessment: BehavioralRiskAssessment | None = None,",
        "    salary_verification: SalaryVerificationResult | None = None,",
        "    unsupervised_profile: dict[str, Any] | None = None,",
        ") -> Decision:",
        "    \"\"\"Recommend credit action using Dual-Pillar ML Matrix with anomaly safeguards.\"\"\"",
        "    reasons: list[str] = []",
        "",
        "    # 1. Pre-Qualification Data Quality Hard Stops",
        "    quality_gates = evaluate_data_quality_gates(features, quality_report)",
        "    if quality_gates:",
        "        return Decision(",
        "            recommendation='Refer for additional documents',",
        "            reasons=quality_gates,",
        "            model_probability=bureau_probability,",
        "            behavioral_ml=behavioral_assessment,",
        "            rule_version=rule_version,",
        "            quadrant='Data Quality Gate Triggered (Referral)',",
        "        )",
        "",
        "    # 2. Salary Slip Verification Check",
        "    if salary_verification and not salary_verification.is_verified:",
        "        return Decision(",
        "            recommendation='Refer for additional documents',",
        "            reasons=[salary_verification.reason],",
        "            model_probability=bureau_probability,",
        "            behavioral_ml=behavioral_assessment,",
        "            rule_version=rule_version,",
        "            quadrant='Salary Verification Mismatch (Referral)',",
        "        )",
        "",
        "    # 3. Dual-Pillar ML Matrix Evaluation",
        "    p_behav = behavioral_assessment.calibrated_pd if behavioral_assessment else 0.25",
        "    low_behav = p_behav < 0.30",
        "    low_bureau = bureau_probability < model_alert_threshold",
        "",
        "    if low_behav and low_bureau:",
        "        rec = 'Meets indicative affordability criteria'",
        "        quad = 'Quadrant 1: Low Behavioral & Bureau Risk (Indicative Approval)'",
        "    elif low_behav and not low_bureau:",
        "        rec = 'Manual review'",
        "        quad = 'Quadrant 2: Low Behavioral / High Bureau (Bureau Alert)'",
        "    elif not low_behav and low_bureau:",
        "        rec = 'Manual review'",
        "        quad = 'Quadrant 3: High Behavioral / Low Bureau (Cash-Flow Alert)'",
        "    else:",
        "        rec = 'Does not meet indicative affordability criteria'",
        "        quad = 'Quadrant 4: Elevated Risk on Both ML Models (Decline)'",
        "",
        "    # 4. Isolation Forest Anomaly Override",
        "    if rec == 'Meets indicative affordability criteria':",
        "        if (behavioral_assessment and behavioral_assessment.is_anomaly) or (",
        "            unsupervised_profile and unsupervised_profile.get('is_anomaly')",
        "        ):",
        "            rec = 'Manual review'",
        "            reasons.append('Isolation Forest detected non-linear cash-flow anomaly. Escalated to manual review.')",
        "",
        "    return Decision(",
        "        recommendation=rec,",
        "        reasons=reasons,",
        "        model_probability=bureau_probability,",
        "        behavioral_ml=behavioral_assessment,",
        "        unsupervised_ml=unsupervised_profile,",
        "        rule_version=rule_version,",
        "        quadrant=quad,",
        "    )"
    ]
    add_code(code_engine)

    add_section("A.3 SHA-256 Cryptographic Hash Chain (src/data/db.py)")
    code_crypto = [
        "def compute_record_hash(",
        "    previous_hash: str,",
        "    case_id: str,",
        "    timestamp_utc: str,",
        "    applicant_id: str | None,",
        "    requested_amount: float | None,",
        "    system_recommendation: str,",
        "    officer_action: str,",
        "    full_record_json: str,",
        ") -> str:",
        "    \"\"\"Compute SHA-256 digest cryptographically binding this record to the chain.\"\"\"",
        "    sanitized_json = sanitize_payload_for_chain(json.loads(full_record_json)) if full_record_json else ''",
        "    payload = (",
        "        f'{previous_hash}|{case_id}|{timestamp_utc}|{applicant_id or \"\"}|'",
        "        f'{requested_amount or 0.0}|{system_recommendation}|{officer_action}|{sanitized_json}'",
        "    )",
        "    return hashlib.sha256(payload.encode('utf-8')).hexdigest()",
        "",
        "def verify_hash_chain(db_path: Path | str | None = None) -> tuple[bool, str]:",
        "    \"\"\"Verify integrity of all stored underwriting decisions against external anchor.\"\"\"",
        "    conn = get_connection(db_path)",
        "    rows = conn.execute('SELECT case_id, previous_hash, record_hash, full_record_json FROM cases ORDER BY id ASC').fetchall()",
        "    conn.close()",
        "",
        "    if not rows:",
        "        return True, 'Database is empty; hash chain is trivially valid.'",
        "",
        "    expected_prev = '0' * 64",
        "    for r in rows:",
        "        if r['previous_hash'] != expected_prev:",
        "            return False, f'Broken link at Case {r[\"case_id\"]}: previous hash mismatch.'",
        "        recomputed = compute_record_hash(",
        "            r['previous_hash'], r['case_id'], '', '', 0.0, '', '', r['full_record_json']",
        "        )",
        "        if recomputed != r['record_hash']:",
        "            return False, f'Tampering detected in Case {r[\"case_id\"]}: hash mismatch.'",
        "        expected_prev = r['record_hash']",
        "",
        "    return True, 'Hash chain verified. All records are cryptographically intact.'"
    ]
    add_code(code_crypto)

    # Save to destination
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_file))
    print(f"Report compiled successfully: {out_file} ({os.path.getsize(out_file)} bytes)")

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/PROJECT_REPORT.docx"
    build_docx(out)
