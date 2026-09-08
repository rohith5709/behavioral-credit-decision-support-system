"""Load and validate the UCI Default of Credit Card Clients dataset."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

TARGET_COLUMN = "default_payment_next_month"
REQUIRED_COLUMNS = {
    "LIMIT_BAL", "SEX", "EDUCATION", "MARRIAGE", "AGE",
    *[f"PAY_{month}" for month in (0, 2, 3, 4, 5, 6)],
    *[f"BILL_AMT{month}" for month in range(1, 7)],
    *[f"PAY_AMT{month}" for month in range(1, 7)],
}


def load_uci_credit_default(path: str | Path) -> pd.DataFrame:
    """Load the official UCI Excel file and standardise its column names.

    The official file stores labels in the first row, so this function tries
    the standard Excel header first and falls back to the second row.
    """
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"UCI dataset was not found: {source}")

    frame = pd.read_excel(source)
    if "LIMIT_BAL" not in frame.columns:
        frame = pd.read_excel(source, header=1)

    frame = frame.rename(columns={
        "default payment next month": TARGET_COLUMN,
        "PAY_0": "PAY_0",
    })
    frame.columns = [str(column).strip().replace(" ", "_") for column in frame.columns]
    if "default_payment_next_month" not in frame.columns:
        matching = [column for column in frame.columns if "default" in column.lower()]
        if matching:
            frame = frame.rename(columns={matching[0]: TARGET_COLUMN})

    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"UCI dataset is missing expected columns: {sorted(missing)}")
    if TARGET_COLUMN not in frame.columns:
        raise ValueError("UCI dataset does not include the default target column.")

    return frame.drop(columns=["ID"], errors="ignore").copy()
