import io
import pandas as pd
import pytest

from src.documents.salary_verification import verify_salary_slip_cross_document
from src.features.behavioral import categorise_statement_transactions


def test_salary_slip_cross_document_verification_aligned():
    transactions = pd.DataFrame({
        "date": ["2026-01-01", "2026-02-01", "2026-03-01"],
        "description": ["INFOSYS LTD SALARY CREDIT", "INFOSYS LTD SALARY CREDIT", "INFOSYS LTD SALARY CREDIT"],
        "debit": [0.0, 0.0, 0.0],
        "credit": [50_000.0, 50_000.0, 50_000.0],
    })
    categorised = categorise_statement_transactions(transactions)
    result = verify_salary_slip_cross_document(categorised, slip_net_salary=50_000.0, employer_name="Infosys")

    assert result.is_verified is True
    assert result.discrepancy_amount == 0.0
    assert result.employer_matched_in_statement is True
    assert "VERIFIED" in result.status


def test_salary_slip_cross_document_verification_discrepancy():
    transactions = pd.DataFrame({
        "date": ["2026-01-01", "2026-02-01", "2026-03-01"],
        "description": ["SALARY CREDIT ACME", "SALARY CREDIT ACME", "SALARY CREDIT ACME"],
        "debit": [0.0, 0.0, 0.0],
        "credit": [30_000.0, 30_000.0, 30_000.0],
    })
    categorised = categorise_statement_transactions(transactions)
    # Declared 50,000 but actual statement salary is 30,000 (40% discrepancy)
    result = verify_salary_slip_cross_document(categorised, slip_net_salary=50_000.0, employer_name="TCS")

    assert result.is_verified is False
    assert result.discrepancy_amount == 20_000.0
    assert result.employer_matched_in_statement is False
    assert "DISCREPANCY" in result.status


def test_salary_slip_cross_document_no_statement_salary():
    transactions = pd.DataFrame({
        "date": ["2026-01-01"],
        "description": ["CASH DEPOSIT"],
        "debit": [0.0],
        "credit": [10_000.0],
    })
    categorised = categorise_statement_transactions(transactions)
    result = verify_salary_slip_cross_document(categorised, slip_net_salary=50_000.0)

    assert result.is_verified is False
    assert result.detected_statement_salary == 0.0
    assert "CRITICAL" in result.status
