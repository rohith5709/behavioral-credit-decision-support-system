"""SQLite case storage with tamper-evident SHA-256 hash chaining for decision records."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any
import uuid

from src.config import PROJECT_ROOT

DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "decisions.db"
GENESIS_HASH = "GENESIS_" + "0" * 56


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a connection to the SQLite decision database."""
    path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | str | None = None) -> None:
    """Initialize the cases table schema if it does not already exist."""
    with get_connection(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE NOT NULL,
                timestamp_utc TEXT NOT NULL,
                applicant_id TEXT,
                requested_amount REAL,
                loan_tenure_months INTEGER,
                proposed_emi REAL,
                affordability_score INTEGER,
                bureau_probability REAL,
                system_recommendation TEXT NOT NULL,
                officer_action TEXT NOT NULL,
                is_override INTEGER NOT NULL DEFAULT 0,
                officer_name TEXT,
                officer_rationale TEXT,
                previous_hash TEXT NOT NULL,
                record_hash TEXT NOT NULL,
                full_record_json TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cases_case_id ON cases(case_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_cases_timestamp ON cases(timestamp_utc)")
        conn.commit()


def compute_record_hash(
    previous_hash: str,
    case_id: str,
    timestamp_utc: str,
    applicant_id: str | None,
    requested_amount: float | None,
    system_recommendation: str,
    officer_action: str,
    full_record_json: str,
) -> str:
    """Compute the SHA-256 cryptographic digest binding this record to the preceding record."""
    payload = f"{previous_hash}|{case_id}|{timestamp_utc}|{applicant_id or ''}|{requested_amount or 0.0}|{system_recommendation}|{officer_action}|{full_record_json}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def save_case_record(
    record_data: dict[str, Any],
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Persist a completed case decision record with tamper-evident hash chaining.

    Parameters
    ----------
    record_data : dict
        Full case record dictionary (e.g. from build_decision_record).
    db_path : Path | str | None
        Path to SQLite database. Defaults to data/decisions.db.

    Returns
    -------
    dict
        Metadata including assigned case_id, record_hash, and previous_hash.
    """
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT record_hash FROM cases ORDER BY id DESC LIMIT 1")
        last_row = cursor.fetchone()
        previous_hash = last_row["record_hash"] if last_row else GENESIS_HASH

        case_id = record_data.get("case_id") or f"CASE-{uuid.uuid4().hex[:8].upper()}"
        timestamp_utc = record_data.get("timestamp_utc", "")
        applicant_id = record_data.get("applicant_id")
        requested_amount = record_data.get("requested_amount")
        loan_tenure_months = record_data.get("loan_tenure_months")
        proposed_emi = record_data.get("estimated_proposed_emi")
        affordability_score = record_data.get("affordability_score")
        bureau_probability = record_data.get("model_probability")
        system_recommendation = record_data.get("system_recommendation", "")
        officer_action = record_data.get("officer_action", "")
        officer_name = record_data.get("officer")
        officer_rationale = record_data.get("officer_rationale", "")

        expected_action = {
            "Meets indicative affordability criteria": "Approve",
            "Manual review": "Refer for more documents",
            "Refer for additional documents": "Refer for more documents",
            "Does not meet indicative affordability criteria": "Decline",
        }.get(system_recommendation)
        is_override = 1 if (officer_action not in {"Pending review", expected_action}) else 0

        full_record_json = json.dumps(record_data, sort_keys=True)
        record_hash = compute_record_hash(
            previous_hash=previous_hash,
            case_id=case_id,
            timestamp_utc=timestamp_utc,
            applicant_id=applicant_id,
            requested_amount=requested_amount,
            system_recommendation=system_recommendation,
            officer_action=officer_action,
            full_record_json=full_record_json,
        )

        cursor.execute(
            """
            INSERT INTO cases (
                case_id, timestamp_utc, applicant_id, requested_amount,
                loan_tenure_months, proposed_emi, affordability_score,
                bureau_probability, system_recommendation, officer_action,
                is_override, officer_name, officer_rationale, previous_hash,
                record_hash, full_record_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case_id,
                timestamp_utc,
                applicant_id,
                requested_amount,
                loan_tenure_months,
                proposed_emi,
                affordability_score,
                bureau_probability,
                system_recommendation,
                officer_action,
                is_override,
                officer_name,
                officer_rationale,
                previous_hash,
                record_hash,
                full_record_json,
            ),
        )
        conn.commit()

        return {
            "case_id": case_id,
            "record_hash": record_hash,
            "previous_hash": previous_hash,
            "timestamp_utc": timestamp_utc,
        }


def get_case_records(
    db_path: Path | str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Retrieve saved decision records in reverse chronological order."""
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, case_id, timestamp_utc, applicant_id, requested_amount,
                   loan_tenure_months, proposed_emi, affordability_score,
                   bureau_probability, system_recommendation, officer_action,
                   is_override, officer_name, officer_rationale, previous_hash,
                   record_hash, full_record_json
            FROM cases
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def verify_hash_chain(db_path: Path | str | None = None) -> tuple[bool, str]:
    """Verify cryptographic integrity of the entire decision record hash chain.

    Returns
    -------
    tuple[bool, str]
        (True, message) if valid, (False, error_reason) if tampered.
    """
    init_db(db_path)
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cases ORDER BY id ASC")
        rows = cursor.fetchall()

        if not rows:
            return True, "Hash chain is empty (no records)."

        expected_prev = GENESIS_HASH
        for row in rows:
            if row["previous_hash"] != expected_prev:
                return (
                    False,
                    f"Hash chain broken at Case {row['case_id']} (ID {row['id']}): "
                    f"Expected previous hash {expected_prev[:12]}..., got {row['previous_hash'][:12]}...",
                )

            recomputed = compute_record_hash(
                previous_hash=row["previous_hash"],
                case_id=row["case_id"],
                timestamp_utc=row["timestamp_utc"],
                applicant_id=row["applicant_id"],
                requested_amount=row["requested_amount"],
                system_recommendation=row["system_recommendation"],
                officer_action=row["officer_action"],
                full_record_json=row["full_record_json"],
            )

            if recomputed != row["record_hash"]:
                return (
                    False,
                    f"Tamper detected in record content for Case {row['case_id']} (ID {row['id']}): "
                    f"Stored hash does not match recomputed SHA-256 digest.",
                )

            expected_prev = row["record_hash"]

        return True, f"Hash chain verified: {len(rows)} records are cryptographically intact."
