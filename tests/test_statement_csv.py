from io import StringIO

import pytest

from src.documents.statement_csv import parse_statement_csv


def test_parser_handles_indian_amounts_and_removes_duplicates():
    csv = StringIO(
        "date,description,debit,credit,balance\n"
        "2026-01-01,Salary,0,\"₹50,000\",50000\n"
        "2026-01-02,Rent,\"15,000\",0,35000\n"
        "2026-01-02,Rent,\"15,000\",0,35000\n"
        "2026-02-01,Salary,0,50000,85000\n"
        "2026-03-01,Salary,0,50000,135000\n"
    )
    transactions, report = parse_statement_csv(csv)
    assert len(transactions) == 4
    assert report.duplicate_rows_removed == 1
    assert report.observed_months == 3
    assert transactions.loc[0, "credit"] == 50_000


def test_parser_reports_invalid_dates_and_amounts():
    csv = StringIO(
        "date,description,debit,credit\n"
        "not-a-date,Shop,abc,0\n"
        "2026-01-01,Salary,0,10000\n"
    )
    transactions, report = parse_statement_csv(csv)
    assert len(transactions) == 1
    assert report.invalid_date_rows == 1
    assert report.invalid_amount_cells == 1
    assert report.score < 1


def test_parser_rejects_negative_debits_or_credits():
    csv = StringIO("date,description,debit,credit\n2026-01-01,Adjustment,-10,0\n")
    with pytest.raises(ValueError, match="zero or positive"):
        parse_statement_csv(csv)


def test_parser_requires_financial_amount_column():
    csv = StringIO("date,description\n2026-01-01,Salary\n")
    with pytest.raises(ValueError, match="debit or credit"):
        parse_statement_csv(csv)


def test_parser_supports_a_signed_amount_column_and_flags_invalid_rows():
    csv = StringIO(
        "Transaction Date,Narration,Amount,Closing Balance\n"
        "01/01/2026,Salary,50000,50000\n"
        "02/01/2026,Rent,-15000,35000\n"
        "03/01/2026,Zero,0,35000\n"
    )
    transactions, report = parse_statement_csv(
        csv,
        column_mapping={"date": "Transaction Date", "description": "Narration", "amount": "Amount", "balance": "Closing Balance", "debit": None, "credit": None},
    )
    assert transactions["credit"].tolist() == [50_000.0, 0.0]
    assert transactions["debit"].tolist() == [0.0, 15_000.0]
    assert report.zero_value_rows == 1


def test_parser_rejects_rows_with_both_debit_and_credit():
    csv = StringIO("date,description,debit,credit\n2026-01-01,Salary,0,10000\n2026-01-02,Adjustment,10,10\n")
    transactions, report = parse_statement_csv(csv)
    assert len(transactions) == 1
    assert report.both_debit_credit_rows == 1


def test_parser_warns_when_numeric_dates_are_ambiguous():
    csv = StringIO("date,description,debit,credit\n03/04/2026,Salary,0,10000\n")
    _, report = parse_statement_csv(csv)
    assert report.ambiguous_date_rows == 1
    assert any("day-first" in warning for warning in report.warnings)
