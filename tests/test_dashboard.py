"""Headless interaction checks for the officer-facing Streamlit workflow."""
from io import StringIO
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from src.documents.statement_csv import parse_statement_csv
from src.features.behavioral import (
    build_category_summary,
    build_monthly_statement_summary,
    build_statement_features,
    categorise_statement_transactions,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _prepared_case():
    statement, report = parse_statement_csv(StringIO("""date,description,credit,debit,balance
2026-01-01,Salary credit,50000,0,50000
2026-01-03,Rent payment,0,15000,35000
2026-02-01,Salary credit,50000,0,85000
2026-02-03,Rent payment,0,15000,70000
2026-03-01,Salary credit,50000,0,120000
2026-03-03,Rent payment,0,15000,105000
"""))
    statement = categorise_statement_transactions(statement)
    return (
        statement,
        report,
        build_statement_features(statement, requested_amount=100_000, proposed_emi=5_000),
        build_monthly_statement_summary(statement),
        build_category_summary(statement),
    )


def test_dashboard_renders_case_summary_with_seeded_case():
    statement, report, features, monthly_summary, category_summary = _prepared_case()
    app = AppTest.from_file(PROJECT_ROOT / "app.py", default_timeout=30)
    app.session_state["statement"] = statement
    app.session_state["quality_report"] = report
    app.session_state["features"] = features
    app.session_state["monthly_summary"] = monthly_summary
    app.session_state["category_summary"] = category_summary
    app.session_state["bureau_result"] = None   # disable bureau scoring during headless test
    app.session_state["salary_verification"] = None
    app.run(timeout=30)

    assert not app.exception
    summary_frames = [frame.value for frame in app.dataframe if "Policy version" in frame.value.get("Metric", pd.Series(dtype=str)).tolist()]
    assert summary_frames
    assert "Emergency buffer" in summary_frames[0]["Metric"].tolist()


def test_dashboard_officer_action_interaction_does_not_crash():
    app = AppTest.from_file(PROJECT_ROOT / "app.py", default_timeout=20).run(timeout=20)
    assert not app.exception
    officer_action = next(widget for widget in app.selectbox if widget.label == "Officer final action")
    officer_action.select("Approve").run(timeout=20)
    assert not app.exception
