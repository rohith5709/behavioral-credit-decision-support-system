"""Tests for the transaction NLP classification model and hybrid categorization."""
from pathlib import Path
import joblib
import pandas as pd
import pytest

from src.features.behavioral import categorise_statement_transactions, load_nlp_pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NLP_MODEL_PATH = PROJECT_ROOT / "models" / "transaction_nlp_pipeline.joblib"


def test_nlp_model_bundle_exists_and_loads():
    """Verify the trained NLP model artifact is present and loads cleanly."""
    assert NLP_MODEL_PATH.exists(), "NLP model artifact missing"
    bundle = joblib.load(NLP_MODEL_PATH)
    assert "pipeline" in bundle
    assert "classes" in bundle
    assert len(bundle["classes"]) >= 15
    pipeline = load_nlp_pipeline()
    assert pipeline is not None


def test_nlp_model_predicts_with_confidence():
    """Verify the pipeline outputs valid predictions and probability distributions."""
    pipeline = load_nlp_pipeline()
    sample_texts = [
        "ACME TECH PAYROLL SALARY CREDIT",
        "DMART SUPERMARKET RETAIL STORE",
        "HDFC HOME LOAN EMI DEDUCTION",
        "UBER COMMUTE TRIP",
        "APOLLO PHARMACY DRUGS MEDICINE",
    ]
    preds = pipeline.predict(sample_texts)
    probs = pipeline.predict_proba(sample_texts)

    assert len(preds) == len(sample_texts)
    assert preds[0] == "Salary/income"
    assert preds[1] == "Groceries"
    assert preds[2] == "EMI/loan repayment"
    assert preds[3] == "Transport/fuel"
    assert preds[4] == "Healthcare"

    # Verify probabilistic calibration: max probability should be between 0 and 1
    for prob_row in probs:
        max_p = max(prob_row)
        assert 0.0 < max_p <= 1.0


def test_hybrid_categorisation_handles_nlp_generalisation():
    """Verify that unlabelled descriptions are categorised with confidence tracking."""
    df = pd.DataFrame({
        "description": [
            "SALARY CREDIT OCT",
            "POS-4912 CAFE COFFEE BLR",
            "INDIAN OIL PETROL PUMP",
        ],
        "debit": [0, 450, 1500],
        "credit": [50000, 0, 0],
    })
    res = categorise_statement_transactions(df)
    assert res.loc[0, "category"] == "Salary/income"
    assert res.loc[1, "category"] in ["Shopping/discretionary", "Other"]
    assert res.loc[2, "category"] == "Transport/fuel"
    assert "category_confidence" in res.columns
    assert "category_review_status" in res.columns
    assert (res["category_confidence"] > 0).all()
