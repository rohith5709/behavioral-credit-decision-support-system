"""Extract digital PDF bank statements and convert to standard tabular format."""
from __future__ import annotations

import io
import re
from typing import BinaryIO

import pandas as pd
import pypdf

from src.documents.statement_csv import (
    ALIASES,
    _normalise_name,
    parse_statement_csv,
    StatementQualityReport,
)


def extract_text_from_pdf(pdf_file: BinaryIO | bytes) -> str:
    """Extract plain text from a native digital PDF document."""
    if isinstance(pdf_file, bytes):
        stream = io.BytesIO(pdf_file)
    else:
        stream = pdf_file

    reader = pypdf.PdfReader(stream)
    text_parts = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text_parts.append(extracted)
    return "\n".join(text_parts)


def parse_statement_pdf(
    pdf_file: BinaryIO | bytes,
) -> tuple[pd.DataFrame, StatementQualityReport]:
    """Parse text from digital PDF bank statement into tabular transactions."""
    raw_text = extract_text_from_pdf(pdf_file)
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Could not extract any readable text from the uploaded PDF statement.")

    all_aliases = set().union(*ALIASES.values())
    header_idx = -1
    delimiter = None

    # Detect header line
    for idx, line in enumerate(lines[:35]):
        # Check comma, tab, or multiple spaces
        for sep in (",", "\t", r"\s{2,}"):
            tokens = [t.strip().strip('"').strip("'") for t in re.split(sep, line)]
            if sum(_normalise_name(t) in all_aliases for t in tokens if t) >= 2:
                header_idx = idx
                delimiter = sep
                break
        if header_idx != -1:
            break

    if header_idx == -1:
        # Fallback: create CSV directly from lines with comma or tab
        delimiter = ","
        csv_content = "\n".join(lines)
    else:
        if delimiter == r"\s{2,}":
            # Normalize whitespace delimiter to comma
            table_lines = []
            for line in lines[header_idx:]:
                parts = [p.strip() for p in re.split(r"\s{2,}", line)]
                table_lines.append(",".join(f'"{p}"' if "," in p else p for p in parts))
            csv_content = "\n".join(table_lines)
        else:
            csv_content = "\n".join(lines[header_idx:])

    return parse_statement_csv(io.StringIO(csv_content))
