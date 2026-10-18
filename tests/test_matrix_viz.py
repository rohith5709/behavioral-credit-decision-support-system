"""Tests for matrix visualization module."""
import plotly.graph_objects as go
from src.reporting.matrix_viz import build_decision_matrix_figure, build_shap_horizontal_bar_figure, build_gauge_figure


def test_build_decision_matrix_figure():
    fig = build_decision_matrix_figure(
        affordability_score=78.5,
        bureau_probability=0.12,
        applicant_id="APP-TEST",
    )
    assert isinstance(fig, go.Figure)
    assert len(fig.layout.shapes) >= 4  # 4 quadrants
    # Has applicant scatter trace
    assert len(fig.data) == 1
    assert fig.data[0].x[0] == 78.5
    assert fig.data[0].y[0] == 0.12


def test_build_decision_matrix_figure_none_values():
    fig = build_decision_matrix_figure(None, None)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 0  # No applicant point plotted


def test_build_shap_horizontal_bar_figure():
    dummy_shap = {
        "top_risk_increasing_factors": [
            {"feature": "Past Due Days", "shap_value": 0.25, "impact": "+0.25"},
        ],
        "top_risk_decreasing_factors": [
            {"feature": "CIBIL Score", "shap_value": -0.45, "impact": "-0.45"},
        ],
    }
    fig = build_shap_horizontal_bar_figure(dummy_shap)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert len(fig.data[0].x) == 2


def test_build_gauge_figure():
    fig = build_gauge_figure(value=82.0, title="Affordability Score", max_value=100.0)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].value == 82.0

