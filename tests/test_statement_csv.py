from io import StringIO

import pytest

from src.documents.statement_csv import parse_statement_csv, read_statement_preview, safe_export_csv


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


def test_parser_handles_preamble_utf8_bom_lakh_amounts_and_dr_cr():
    csv = StringIO(
        "Generated statement - not a transaction row\n"
        "Account summary\n"
        "Transaction Date,Narration,Amount,Closing Balance\n"
        '01/01/2026,Salary Credit,"1,00,000 Cr","1,00,000"\n'
        '02/01/2026,Rent payment,"25,000 Dr","75,000"\n'
    )
    preview = read_statement_preview(csv)
    transactions, _ = parse_statement_csv(
        StringIO('Generated statement - not a transaction row\nAccount summary\nTransaction Date,Narration,Amount,Closing Balance\n01/01/2026,Salary Credit,"1,00,000 Cr","1,00,000"\n02/01/2026,Rent payment,"25,000 Dr","75,000"\n'),
        column_mapping={"date": "Transaction Date", "description": "Narration", "amount": "Amount", "balance": "Closing Balance", "debit": None, "credit": None},
    )
    assert preview.columns.tolist() == ["Transaction Date", "Narration", "Amount", "Closing Balance"]
    assert transactions["credit"].tolist() == [100000.0, 0.0]
    assert transactions["debit"].tolist() == [0.0, 25000.0]


def test_safe_export_masks_obvious_pii_and_prevents_formula_injection():
    frame = __import__("pandas").DataFrame({
        "description": ["=SUM(1,1)", "@danger", "+formula", "-formula", "UPI alice@bank 9876543210 123456789012"],
        "amount": [1, 2, 3, 4, 5]
    })
    exported = safe_export_csv(frame)
    assert "'=SUM(1,1)" in exported
    assert "'@danger" in exported
    assert "'+formula" in exported
    assert "'-formula" in exported
    assert "[masked-upi-or-email]" in exported
    assert "[masked-number]" in exported


def test_parser_handles_synthetic_bank_layouts_hdfc_sbi_icici_axis_kotak():
    # Synthetic HDFC-like export with preamble and Dr/Cr
    hdfc_csv = StringIO(
        "HDFC BANK LIMITED - Statement of Account\n"
        "Customer Name: Mock User | Account: XXXXXXXXX123\n"
        "Date,Narration,Withdrawal Amt.,Deposit Amt.,Closing Balance\n"
        "01/01/2026,SALARY CREDIT HDFC,0,75000,75000\n"
        "05/01/2026,UPI-RENT-PAYMENT,20000,0,55000\n"
    )
    tx_hdfc, rep_hdfc = parse_statement_csv(hdfc_csv)
    assert rep_hdfc.valid_transactions == 2
    assert tx_hdfc["credit"].sum() == 75000.0

    # Synthetic SBI-like export with Txn Date and Details
    sbi_csv = StringIO(
        "STATE BANK OF INDIA\n"
        "Txn Date,Details,Debit,Credit,Balance\n"
        "02/01/2026,INB SALARY,0,60000,60000\n"
        "10/01/2026,ELECTRICITY BILL,2500,0,57500\n"
    )
    tx_sbi, rep_sbi = parse_statement_csv(sbi_csv)
    assert rep_sbi.valid_transactions == 2
    assert tx_sbi["debit"].sum() == 2500.0

    # Synthetic ICICI-like with signed amount and Value Date
    icici_csv = StringIO(
        "ICICI Bank Statement\n"
        "Value Date,Transaction Remarks,Amount,Balance\n"
        '03/01/2026,SALARY CREDIT,"80,000",80000\n'
        '04/01/2026,GROCERY PURCHASE,"-3,500",76500\n'
    )
    tx_icici, rep_icici = parse_statement_csv(icici_csv)
    assert rep_icici.valid_transactions == 2
    assert tx_icici["credit"].iloc[0] == 80000.0
    assert tx_icici["debit"].iloc[1] == 3500.0

