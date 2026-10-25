import sys
from pathlib import Path
import docx

def inspect_docx(docx_path="docs/PROJECT_REPORT.docx"):
    p = Path(docx_path)
    if not p.exists():
        print(f"Error: {docx_path} does not exist!")
        return 1

    doc = docx.Document(str(p))
    print("=" * 60)
    print(f"INSPECTING REPORT QUALITY: {docx_path}")
    print("=" * 60)

    issues = []

    # 1. Check Paragraphs
    total_paragraphs = len(doc.paragraphs)
    empty_paragraphs = []
    large_space_before = []
    large_space_after = []

    for idx, para in enumerate(doc.paragraphs):
        txt = para.text.strip()
        # Has image drawing?
        has_drawing = bool(para._p.xpath('.//w:drawing'))
        
        if not txt and not has_drawing:
            empty_paragraphs.append(idx)

        sb = para.paragraph_format.space_before.pt if para.paragraph_format.space_before else 0
        sa = para.paragraph_format.space_after.pt if para.paragraph_format.space_after else 0

        if sb > 16:
            large_space_before.append((idx, sb, txt[:30]))
        if sa > 20:
            large_space_after.append((idx, sa, txt[:30]))

    print(f"Total Paragraphs: {total_paragraphs}")
    print(f"Empty Paragraphs: {len(empty_paragraphs)}")
    if empty_paragraphs:
        issues.append(f"Found {len(empty_paragraphs)} empty paragraphs at indices: {empty_paragraphs[:10]}")

    print(f"Large Space Before (>16pt): {len(large_space_before)}")
    print(f"Large Space After (>20pt): {len(large_space_after)}")

    # 2. Check Tables
    total_tables = len(doc.tables)
    print(f"Total Tables: {total_tables}")
    
    # Check for unwanted 1x1 tables (code blocks) or 1-row signature tables
    code_tables = []
    for t_idx, tbl in enumerate(doc.tables):
        rows = len(tbl.rows)
        cols = len(tbl.columns)
        first_cell_txt = tbl.rows[0].cells[0].text.strip() if rows > 0 and cols > 0 else ""
        if rows == 1 and cols == 1:
            code_tables.append((t_idx, first_cell_txt[:40]))
        if "Register Number" in first_cell_txt and rows <= 4:
            issues.append(f"Table {t_idx} appears to be candidate details table on cover page! Should be text.")
        if "................" in first_cell_txt:
            issues.append(f"Table {t_idx} appears to be signature line table! Should be typographic blocks.")

    if code_tables:
        issues.append(f"Found {len(code_tables)} 1x1 single-cell tables (code placed in table cells!): {code_tables}")

    # Check that key tables exist
    table_captions_found = []
    for para in doc.paragraphs:
        txt = para.text.strip()
        if txt.startswith("Table ") or txt in ["Table of Contents", "List of Figures", "List of Tables", "List of Abbreviations", "Symbols and Notations"]:
            table_captions_found.append(txt[:40])

    print(f"Tables with Captions Found: {len(table_captions_found)}")

    # 3. Check Images / Figures
    figures_found = []
    for para in doc.paragraphs:
        txt = para.text.strip()
        if txt.startswith("Figure "):
            figures_found.append(txt[:40])

    print(f"Figure Captions Found: {len(figures_found)}")
    expected_figs = ["Figure 4.1", "Figure 4.2", "Figure 4.3", "Figure 4.4", "Figure 4.5", "Figure 5.1", "Figure 5.2", "Figure 6.1", "Figure 6.2", "Figure 7.1", "Figure 7.2", "Figure 7.3", "Figure 7.4"]
    for ef in expected_figs:
        if not any(ef in f for f in figures_found):
            issues.append(f"Missing Figure: {ef}")

    # 4. Check Chapters
    expected_chapters = [
        "CHAPTER 1: INTRODUCTION",
        "CHAPTER 2: PROJECT DESCRIPTION AND GOALS",
        "CHAPTER 3: TECHNICAL SPECIFICATION",
        "CHAPTER 4: DESIGN APPROACH AND DETAILS",
        "CHAPTER 5: METHODOLOGY AND TESTING",
        "CHAPTER 6: PROJECT DEMONSTRATION",
        "CHAPTER 7: RESULT AND DISCUSSION",
        "CHAPTER 8: CONCLUSION",
        "CHAPTER 9: REFERENCES",
        "APPENDIX A - SAMPLE CODE"
    ]
    all_text = "\n".join(para.text.strip() for para in doc.paragraphs)
    for ec in expected_chapters:
        if ec not in all_text:
            issues.append(f"Missing Chapter: {ec}")

    print("=" * 60)
    if issues:
        print(f"QUALITY CHECK FAILED: {len(issues)} issue(s) detected:")
        for iss in issues:
            print(f"  [X] {iss}")
        return 1
    else:
        print("QUALITY CHECK PASSED! Document is clean, professional, and compliant with all criteria.")
        return 0

if __name__ == "__main__":
    docx_file = sys.argv[1] if len(sys.argv) > 1 else "docs/PROJECT_REPORT.docx"
    sys.exit(inspect_docx(docx_file))
