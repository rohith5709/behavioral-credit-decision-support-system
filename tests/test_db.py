import tempfile
from pathlib import Path
import pytest
import sqlite3

from src.data.db import init_db, save_case_record, get_case_records, verify_hash_chain, GENESIS_HASH


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_decisions.db"
    init_db(db_file)
    return db_file


def test_db_init_and_empty_verification(temp_db):
    valid, message = verify_hash_chain(temp_db)
    assert valid is True
    assert "empty" in message


def test_db_save_and_retrieve_record(temp_db):
    record = {
        "timestamp_utc": "2026-10-18T12:00:00Z",
        "applicant_id": "APP-TEST-001",
        "requested_amount": 500_000.0,
        "loan_tenure_months": 36,
        "estimated_proposed_emi": 16_500.0,
        "affordability_score": 82,
        "model_probability": 0.065,
        "system_recommendation": "Meets indicative affordability criteria",
        "officer_action": "Approve",
        "officer": "Officer Sharma",
        "officer_rationale": "Strong verified salary and pristine credit history.",
    }
    saved_meta = save_case_record(record, temp_db)
    assert saved_meta["case_id"].startswith("CASE-")
    assert saved_meta["previous_hash"] == GENESIS_HASH
    assert len(saved_meta["record_hash"]) == 64

    # Save a second record to test chaining
    record2 = {
        "timestamp_utc": "2026-10-18T12:30:00Z",
        "applicant_id": "APP-TEST-002",
        "requested_amount": 100_000.0,
        "loan_tenure_months": 12,
        "estimated_proposed_emi": 9_000.0,
        "affordability_score": 40,
        "model_probability": 0.32,
        "system_recommendation": "Does not meet indicative affordability criteria",
        "officer_action": "Decline",
        "officer": "Officer Sharma",
        "officer_rationale": "High existing debt and frequent late payments.",
    }
    saved_meta2 = save_case_record(record2, temp_db)
    assert saved_meta2["previous_hash"] == saved_meta["record_hash"]

    # Verify chain
    valid, message = verify_hash_chain(temp_db)
    assert valid is True
    assert "2 records are cryptographically intact" in message

    # Retrieve rows
    records = get_case_records(temp_db)
    assert len(records) == 2
    assert records[0]["case_id"] == saved_meta2["case_id"]  # reverse chronological
    assert records[1]["case_id"] == saved_meta["case_id"]


def test_db_tamper_detection(temp_db):
    record = {
        "timestamp_utc": "2026-10-18T12:00:00Z",
        "applicant_id": "APP-TAMPER-001",
        "requested_amount": 300_000.0,
        "system_recommendation": "Meets indicative affordability criteria",
        "officer_action": "Approve",
    }
    saved = save_case_record(record, temp_db)

    # Legitimate state is valid
    valid, _ = verify_hash_chain(temp_db)
    assert valid is True

    # Maliciously mutate the saved record directly in SQLite
    conn = sqlite3.connect(str(temp_db))
    conn.execute("UPDATE cases SET requested_amount = 9999999.0 WHERE case_id = ?", (saved["case_id"],))
    conn.commit()
    conn.close()

    # Integrity verification must catch the tampering
    tamper_valid, tamper_msg = verify_hash_chain(temp_db)
    assert tamper_valid is False
    assert "Tamper detected" in tamper_msg
