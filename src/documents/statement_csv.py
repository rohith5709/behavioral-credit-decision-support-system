"""Validate and normalise CSV bank statements into a reliable transaction schema."""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO, StringIO
import io
from typing import BinaryIO
import re

import pandas as pd

CANONICAL_COLUMNS = ("date", "description", "debit", "credit", "balance")
ALIASES = {
    "date": {"date", "transaction_date", "txn_date", "value_date"},
    "description": {"description", "narration", "particulars", "remarks", "details", "transaction_remarks", "txn_remarks"},
    "debit": {"debit", "withdrawal", "debit_amount", "withdrawal_amount", "withdrawal_amt", "dr"},
    "credit": {"credit", "deposit", "credit_amount", "deposit_amount", "deposit_amt", "cr"},
    "balance": {"balance", "closing_balance", "running_balance"},
    "amount": {"amount", "transaction_amount", "txn_amount"},
}


@dataclass(frozen=True)
class StatementQualityReport:
    """Data-quality outcomes for a parsed statement, not an authenticity verdict."""

    score: float
    valid_transactions: int
    rejected_rows: int
    observed_months: int
    date_range_start: str | None
    date_range_end: str | None
    duplicate_rows_removed: int
    invalid_date_rows: int
    ambiguous_date_rows: int
    invalid_amount_cells: int
    both_debit_credit_rows: int
    zero_value_rows: int
    balance_mismatch_rows: int
    salary_income_detected: bool
    warnings: tuple[str, ...]


def _normalise_name(name: object) -> str:
    cleaned = str(name).strip().lower().replace(".", "").replace("-", "_").replace(" ", "_")
    return re.sub(r"_+", "_", cleaned)


def _find_column(columns: list[str], canonical: str) -> str | None:
    return next((column for column in columns if _normalise_name(column) in ALIASES[canonical]), None)


def _read_csv_with_bank_tolerances(uploaded_file: BinaryIO | BytesIO | str) -> pd.DataFrame:
    """Read common bank-export encodings and skip a short non-tabular preamble."""
    payload = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else None
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    attempts = ("utf-8-sig", "utf-16", "cp1252")
    last_error: Exception | None = None
    all_aliases = set().union(*ALIASES.values())

    for encoding in attempts:
        try:
            if payload is not None:
                lines = payload.decode(encoding).splitlines()
            elif hasattr(uploaded_file, "seek") and hasattr(uploaded_file, "read"):
                uploaded_file.seek(0)
                raw_bytes = uploaded_file.read()
                if isinstance(raw_bytes, str):
                    lines = raw_bytes.splitlines()
                else:
                    lines = raw_bytes.decode(encoding).splitlines()
            else:
                lines = []

            if not lines or all(not line.strip() for line in lines):
                raise pd.errors.EmptyDataError("The uploaded CSV is empty.")

            header_row = 0
            for idx, line in enumerate(lines[:25]):
                tokens = [t.strip().strip('"').strip("'") for t in re.split(r",|\t", line)]
                if sum(_normalise_name(t) in all_aliases for t in tokens if t) >= 2:
                    header_row = idx
                    break

            source = io.StringIO("\n".join(lines[header_row:]))
            return pd.read_csv(source)
        except (UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as error:
            last_error = error
            if payload is None and hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)

    if isinstance(last_error, pd.errors.EmptyDataError):
        raise ValueError("The uploaded CSV is empty.") from last_error
    raise ValueError("The CSV could not be decoded as UTF-8, UTF-16, or Windows-1252.") from last_error


def read_statement_preview(uploaded_file: BinaryIO | BytesIO | str) -> pd.DataFrame:
    """Read unmodified CSV data so an officer can review/map columns before parsing."""
    return _read_csv_with_bank_tolerances(uploaded_file)


def suggest_column_mapping(columns: list[str]) -> dict[str, str | None]:
    """Suggest source columns for canonical transaction fields using aliases."""
    return {field: _find_column(columns, field) for field in (*CANONICAL_COLUMNS, "amount")}


def _parse_amount(values: pd.Series) -> tuple[pd.Series, int]:
    """Support common Indian currency formats and record malformed cells."""
    cleaned = (
        values.fillna("").astype(str).str.strip()
        .str.replace("₹", "", regex=False).str.replace(",", "", regex=False)
        .str.replace(r"^\((.*)\)$", r"-\1", regex=True)
    )
    debit_marker = cleaned.str.contains(r"\bdr\b|\bdebit\b", case=False, regex=True, na=False)
    credit_marker = cleaned.str.contains(r"\bcr\b|\bcredit\b", case=False, regex=True, na=False)
    cleaned = cleaned.str.replace(r"\s*(dr|cr|debit|credit)\s*$", "", case=False, regex=True)
    empty = cleaned.eq("") | cleaned.str.lower().isin({"nan", "none", "null", "-"})
    parsed = pd.to_numeric(cleaned.mask(empty), errors="coerce")
    parsed = parsed.where(~debit_marker, -parsed.abs()).where(~credit_marker, parsed.abs())
    return parsed.fillna(0.0), int((parsed.isna() & ~empty).sum())


def safe_export_csv(frame: pd.DataFrame, mask_pii: bool = True) -> str:
    """Return a spreadsheet-safe CSV and mask obvious PII-like text in exports.

    This is a display/export safeguard, not a guarantee of anonymisation.
    """
    exported = frame.copy()
    for column in exported.select_dtypes(include="object").columns:
        values = exported[column].fillna("").astype(str)
        if mask_pii:
            values = values.str.replace(r"(?<!\d)\d{8,}(?!\d)", "[masked-number]", regex=True)
            values = values.str.replace(r"\b[\w.+-]+@[\w.-]+\b", "[masked-upi-or-email]", regex=True)
            values = values.str.replace(r"(?<!\d)\d{10}(?!\d)", "[masked-phone]", regex=True)
        exported[column] = values.map(lambda value: f"'{value}" if value.startswith(("=", "+", "-", "@")) else value)
    return exported.to_csv(index=False)


def _quality_score(
    schema_score: float, raw_rows: int, valid_rows: int, duplicates: int,
    invalid_dates: int, invalid_amounts: int, balance_mismatches: int, observed_months: int,
    salary_income_detected: bool,
    both_debit_credit_rows: int = 0, zero_value_rows: int = 0, ambiguous_dates: int = 0,
) -> tuple[float, tuple[str, ...]]:
    warnings: list[str] = []
    score = schema_score * min(valid_rows / max(raw_rows, 1), 1.0)
    if duplicates:
        warnings.append(f"Removed {duplicates} duplicate transaction row(s).")
        score -= min(duplicates / max(raw_rows, 1), 0.10)
    if invalid_dates:
        warnings.append(f"Ignored {invalid_dates} row(s) with invalid dates.")
        score -= min(invalid_dates / max(raw_rows, 1), 0.20)
    if ambiguous_dates:
        warnings.append(
            f"{ambiguous_dates} numeric date value(s) were interpreted as day-first; officer verification is recommended."
        )
    if invalid_amounts:
        warnings.append(f"Converted {invalid_amounts} invalid amount cell(s) to zero; verify the source statement.")
        score -= min(invalid_amounts / max(raw_rows * 2, 1), 0.20)
    if both_debit_credit_rows:
        warnings.append(f"Ignored {both_debit_credit_rows} row(s) with both debit and credit values.")
        score -= min(both_debit_credit_rows / max(raw_rows, 1), 0.15)
    if zero_value_rows:
        warnings.append(f"Ignored {zero_value_rows} zero-value transaction row(s).")
        score -= min(zero_value_rows / max(raw_rows, 1), 0.10)
    if balance_mismatches:
        warnings.append(f"{balance_mismatches} balance transition(s) do not match debit/credit values; officer verification is required.")
        score -= min(balance_mismatches / max(valid_rows, 1), 0.25)
    if observed_months < 3:
        warnings.append("Fewer than three months of transactions are available; affordability analysis is limited.")
        score -= 0.15
    if not salary_income_detected:
        warnings.append("No salary/income credit was detected; officer verification is required.")
    return round(max(0.0, min(score, 1.0)), 2), tuple(warnings)


def parse_statement_csv(
    uploaded_file: BinaryIO | BytesIO | str,
    column_mapping: dict[str, str | None] | None = None,
    opening_balance: float | None = None,
) -> tuple[pd.DataFrame, StatementQualityReport]:
    """Read a statement CSV and return clean transactions plus quality evidence."""
    raw = read_statement_preview(uploaded_file)
    if raw.empty:
        raise ValueError("The uploaded CSV has no transaction rows.")

    mapping = column_mapping or suggest_column_mapping(list(raw.columns))
    missing = [field for field in ("date", "description") if mapping[field] is None]
    if missing:
        raise ValueError(f"Statement CSV needs columns for: {', '.join(missing)}")
    if mapping.get("debit") is None and mapping.get("credit") is None and mapping.get("amount") is None:
        raise ValueError("Statement CSV needs at least a debit or credit column, or one signed amount column.")
    if any(column is not None and column not in raw.columns for column in mapping.values()):
        raise ValueError("A selected mapping column was not found in the uploaded CSV.")

    result = pd.DataFrame({field: raw[mapping[field]] if mapping.get(field) else 0.0 for field in CANONICAL_COLUMNS})
    raw_date_text = result["date"].fillna("").astype(str).str.strip()
    numeric_dates = raw_date_text.str.extract(r"^(\d{1,2})[/-](\d{1,2})[/-]\d{2,4}$")
    ambiguous_dates = int(
        ((pd.to_numeric(numeric_dates[0], errors="coerce") <= 12)
         & (pd.to_numeric(numeric_dates[1], errors="coerce") <= 12)).sum()
    )
    result["date"] = pd.to_datetime(result["date"], errors="coerce", dayfirst=True, format="mixed")
    invalid_dates = int(result["date"].isna().sum())
    invalid_amounts = 0
    if mapping.get("amount") and not mapping.get("debit") and not mapping.get("credit"):
        signed_amount, invalid_cells = _parse_amount(raw[mapping["amount"]])
        result["credit"] = signed_amount.clip(lower=0)
        result["debit"] = (-signed_amount).clip(lower=0)
        invalid_amounts += invalid_cells
    for field in ("debit", "credit", "balance"):
        if mapping.get("amount") and field in {"debit", "credit"} and not mapping.get(field):
            continue
        result[field], invalid_cells = _parse_amount(result[field])
        invalid_amounts += invalid_cells
    if (result[["debit", "credit"]] < 0).any().any():
        raise ValueError("Debit and credit amounts must be zero or positive. Correct negative values in the source CSV.")
    result["description"] = result["description"].fillna("").astype(str).str.strip()
    both_debit_credit_rows = int(((result["debit"] > 0) & (result["credit"] > 0)).sum())
    zero_value_rows = int(((result["debit"] == 0) & (result["credit"] == 0)).sum())
    result = result.dropna(subset=["date"])
    result = result.loc[~((result["debit"] > 0) & (result["credit"] > 0))]
    result = result.loc[~((result["debit"] == 0) & (result["credit"] == 0))]
    before_deduplication = len(result)
    result["_description_key"] = result["description"].str.lower().str.replace(r"\s+", " ", regex=True)
    result["_amount_key"] = (result["credit"] - result["debit"]).round(2)
    result = result.drop_duplicates(subset=["date", "_description_key", "_amount_key"]).sort_values("date").reset_index(drop=True)
    duplicates = before_deduplication - len(result)
    if result.empty:
        raise ValueError("No valid dated transactions were found in the CSV.")

    balance_mismatches = 0
    if mapping["balance"] is not None and len(result) > 1:
        expected_delta = result["credit"] - result["debit"]
        actual_delta = result["balance"].diff()
        balance_mismatches = int(((actual_delta - expected_delta).abs() > 1.0).iloc[1:].sum())
        if opening_balance is not None:
            balance_mismatches += int(abs(result.loc[0, "balance"] - float(opening_balance) - expected_delta.iloc[0]) > 1.0)
    observed_months = int(result["date"].dt.to_period("M").nunique())
    salary_income_detected = bool(
        ((result["credit"] > 0) & result["description"].str.contains(
            r"salary|payroll|wages|income|stipend|pension", case=False, regex=True, na=False
        )).any()
    )
    schema_score = sum(mapping[field] is not None for field in CANONICAL_COLUMNS) / len(CANONICAL_COLUMNS)
    score, warnings = _quality_score(
        schema_score, len(raw), len(result), duplicates, invalid_dates, invalid_amounts,
        balance_mismatches, observed_months,
        salary_income_detected, both_debit_credit_rows, zero_value_rows, ambiguous_dates,
    )
    result = result.drop(columns=["_description_key", "_amount_key"])
    return result, StatementQualityReport(
        score=score, valid_transactions=len(result), rejected_rows=len(raw) - len(result), observed_months=observed_months,
        date_range_start=result["date"].min().date().isoformat(), date_range_end=result["date"].max().date().isoformat(),
        duplicate_rows_removed=duplicates, invalid_date_rows=invalid_dates,
        ambiguous_date_rows=ambiguous_dates,
        invalid_amount_cells=invalid_amounts, both_debit_credit_rows=both_debit_credit_rows, zero_value_rows=zero_value_rows, balance_mismatch_rows=balance_mismatches,
        salary_income_detected=salary_income_detected,
        warnings=warnings,
    )
