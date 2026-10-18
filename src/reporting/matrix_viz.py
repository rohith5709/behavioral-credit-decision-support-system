"""Interactive visualization components for Dual-Pillar Decision Matrix and Model Explainability."""
from __future__ import annotations

from typing import Any
import pandas as pd
import plotly.graph_objects as go


def build_decision_matrix_figure(
    affordability_score: float | None,
    bureau_probability: float | None,
    affordability_cutoff: float = 70.0,
    bureau_cutoff: float = 0.20,
    applicant_id: str | None = None,
) -> go.Figure:
    """Generate an interactive 2x2 Dual-Pillar Decision Matrix map in Plotly.

    Parameters
    ----------
    affordability_score : float | None
        Pillar 1 statement affordability score (0 to 100).
    bureau_probability : float | None
        Pillar 2 calibrated default probability (0.0 to 1.0).
    affordability_cutoff : float
        Policy threshold separating acceptable from low cash flow affordability (default: 70).
    bureau_cutoff : float
        Policy alert threshold separating acceptable from elevated bureau risk (default: 0.20).
    applicant_id : str | None
        Optional applicant label for chart annotation.
    """
    fig = go.Figure()

    # Define plotting limits
    x_min, x_max = 0.0, 100.0
    y_min, y_max = 0.0, 0.40

    # Quadrant 1: High Affordability, Low Risk (Top-Right in coordinate terms, or Q1)
    # X: [cutoff, 100], Y: [0, cutoff] -> Meets Indicative Criteria (Green)
    fig.add_shape(
        type="rect",
        x0=affordability_cutoff, y0=0.0, x1=x_max, y1=bureau_cutoff,
        fillcolor="rgba(16, 185, 129, 0.14)",
        line=dict(color="rgba(16, 185, 129, 0.4)", width=1, dash="dot"),
        layer="below",
    )

    # Quadrant 2: High Affordability, High Risk
    # X: [cutoff, 100], Y: [cutoff, 0.40] -> Manual Review: Bureau Risk Alert (Amber)
    fig.add_shape(
        type="rect",
        x0=affordability_cutoff, y0=bureau_cutoff, x1=x_max, y1=y_max,
        fillcolor="rgba(245, 158, 11, 0.12)",
        line=dict(color="rgba(245, 158, 11, 0.4)", width=1, dash="dot"),
        layer="below",
    )

    # Quadrant 3: Low Affordability, Low Risk
    # X: [0, cutoff], Y: [0, cutoff] -> Manual Review: Cashflow Alert (Amber)
    fig.add_shape(
        type="rect",
        x0=x_min, y0=0.0, x1=affordability_cutoff, y1=bureau_cutoff,
        fillcolor="rgba(245, 158, 11, 0.12)",
        line=dict(color="rgba(245, 158, 11, 0.4)", width=1, dash="dot"),
        layer="below",
    )

    # Quadrant 4: Low Affordability, High Risk
    # X: [0, cutoff], Y: [cutoff, 0.40] -> Decline: Dual Risk Elevation (Red)
    fig.add_shape(
        type="rect",
        x0=x_min, y0=bureau_cutoff, x1=affordability_cutoff, y1=y_max,
        fillcolor="rgba(239, 68, 68, 0.14)",
        line=dict(color="rgba(239, 68, 68, 0.4)", width=1, dash="dot"),
        layer="below",
    )

    # Threshold guidelines
    fig.add_vline(
        x=affordability_cutoff, line_width=2, line_dash="dash", line_color="#94A3B8",
        annotation_text=f"Affordability Cutoff ({affordability_cutoff:.0f})",
        annotation_position="top left",
        annotation_font=dict(color="#94A3B8", size=10),
    )
    fig.add_hline(
        y=bureau_cutoff, line_width=2, line_dash="dash", line_color="#94A3B8",
        annotation_text=f"Bureau Alert Threshold ({bureau_cutoff:.0%})",
        annotation_position="bottom right",
        annotation_font=dict(color="#94A3B8", size=10),
    )

    # Quadrant Labels
    fig.add_annotation(
        x=85, y=0.05, text="<b>Q1: Meets Criteria</b><br><span style='font-size:10px; color:#34D399'>High Cashflow & Low Bureau Risk</span>",
        showarrow=False, font=dict(color="#34D399", size=12), bgcolor="rgba(15, 23, 42, 0.6)",
    )
    fig.add_annotation(
        x=85, y=0.32, text="<b>Q2: Manual Review</b><br><span style='font-size:10px; color:#FBBF24'>Bureau Risk Alert</span>",
        showarrow=False, font=dict(color="#FBBF24", size=12), bgcolor="rgba(15, 23, 42, 0.6)",
    )
    fig.add_annotation(
        x=35, y=0.05, text="<b>Q3: Manual Review</b><br><span style='font-size:10px; color:#FBBF24'>Cashflow Margin Alert</span>",
        showarrow=False, font=dict(color="#FBBF24", size=12), bgcolor="rgba(15, 23, 42, 0.6)",
    )
    fig.add_annotation(
        x=35, y=0.32, text="<b>Q4: Decline</b><br><span style='font-size:10px; color:#F87171'>Dual Risk Elevation</span>",
        showarrow=False, font=dict(color="#F87171", size=12), bgcolor="rgba(15, 23, 42, 0.6)",
    )

    # Plot applicant marker if both pillars are evaluated
    if affordability_score is not None and bureau_probability is not None:
        clamped_y = min(bureau_probability, y_max)
        app_label = f"Applicant {applicant_id or ''}".strip()
        fig.add_trace(go.Scatter(
            x=[affordability_score],
            y=[clamped_y],
            mode="markers+text",
            name="Current Applicant",
            text=[f"<b>{app_label}</b>"],
            textposition="top center",
            textfont=dict(color="#38BDF8", size=12),
            marker=dict(
                size=18,
                color="#0284C7",
                symbol="diamond",
                line=dict(color="#E0F2FE", width=3),
            ),
            hovertemplate=(
                f"<b>{app_label}</b><br>"
                "Pillar 1 Affordability Score: %{x:.1f}/100<br>"
                f"Pillar 2 Bureau Default Risk: {bureau_probability:.1%}<br>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(
            text="<b>Dual-Pillar Credit Evaluation Matrix</b> (Interactive 2D Risk Map)",
            font=dict(size=14, color="#E2E8F0"),
        ),
        xaxis=dict(
            title="Pillar 1: Statement Affordability Score (0 – 100)",
            range=[0, 100],
            gridcolor="rgba(148, 163, 184, 0.1)",
            zeroline=False,
            color="#94A3B8",
        ),
        yaxis=dict(
            title="Pillar 2: Calibrated Bureau Default Probability (0% – 40%)",
            range=[0, 0.40],
            tickformat=".0%",
            gridcolor="rgba(148, 163, 184, 0.1)",
            zeroline=False,
            color="#94A3B8",
        ),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        margin=dict(l=40, r=40, t=50, b=40),
        height=380,
        showlegend=False,
    )

    return fig


def build_shap_horizontal_bar_figure(local_explanations: dict[str, Any]) -> go.Figure:
    """Generate a horizontal bar chart visualizing Tree-SHAP local attributions."""
    risk_factors = local_explanations.get("top_risk_increasing_factors", [])
    protective_factors = local_explanations.get("top_risk_decreasing_factors", [])

    items = []
    for r in risk_factors:
        items.append({
            "name": r["feature"],
            "val": r["shap_value"],
            "type": "Risk-Increasing (+)",
            "color": "#EF4444",
        })
    for p in protective_factors:
        items.append({
            "name": p["feature"],
            "val": p["shap_value"],
            "type": "Protective Buffer (-)",
            "color": "#10B981",
        })

    if not items:
        fig = go.Figure()
        fig.update_layout(
            title="No significant feature deviations detected.",
            paper_bgcolor="#0F172A",
            plot_bgcolor="#0F172A",
            font=dict(color="#94A3B8"),
            height=260,
        )
        return fig

    df = pd.DataFrame(items).sort_values("val", ascending=True)

    fig = go.Figure(go.Bar(
        x=df["val"],
        y=df["name"],
        orientation="h",
        marker=dict(color=df["color"].tolist(), line=dict(color="rgba(255,255,255,0.2)", width=1)),
        hovertemplate="<b>%{y}</b><br>Tree-SHAP Impact: %{x:+.4f} default log-odds<extra></extra>",
    ))

    fig.add_vline(x=0, line_width=1.5, line_color="#94A3B8")

    fig.update_layout(
        title=dict(
            text="<b>Tree-SHAP Feature Attributions</b> (Log-Odds Impact on Benchmark Default Risk)",
            font=dict(size=13, color="#E2E8F0"),
        ),
        xaxis=dict(
            title="Shapley Value (Log-Odds Contribution)",
            gridcolor="rgba(148, 163, 184, 0.15)",
            color="#94A3B8",
            zeroline=False,
        ),
        yaxis=dict(
            color="#CBD5E1",
        ),
        plot_bgcolor="#0F172A",
        paper_bgcolor="#0F172A",
        margin=dict(l=20, r=20, t=40, b=30),
        height=300,
    )

    return fig
