"""Backward-compatible command for the Home Credit model benchmark and selection."""
from __future__ import annotations

import argparse
import json
from src.config import HOME_CREDIT_DIR
from src.models.benchmark_home_credit import train


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the Home Credit default-risk model.")
    parser.add_argument("--input", default=str(HOME_CREDIT_DIR), help="Directory containing Home Credit CSV files.")
    arguments = parser.parse_args()
    print(json.dumps(train(arguments.input), indent=2))
