"""Streamlit interface for the decision-support prototype."""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.config import (
    HOME_CREDIT_COMPARISON_PATH,
    HOME_CREDIT_CALIBRATION_PATH,
    HOME_CREDIT_METRICS_PATH,
    HOME_CREDIT_MODEL_PATH,
    HOME_CREDIT_THRESHOLD_PATH,
    MODEL_PATH,
)
from src.decision.engine import recommend
from src.decision.affordability import POLICY, calculate_actionable_affordability_metrics
from src.documents.statement_csv import parse_statement_csv, read_statement_preview, safe_export_csv, suggest_column_mapping
from src.features.behavioral import (
    apply_bulk_category_override,
    build_repeated_merchant_groups,
    build_category_summary,
    build_monthly_statement_summary,
    build_statement_features,
    CATEGORY_OPTIONS,
    annotate_income_evidence,
    categorise_statement_transactions,
)
from src.reporting.case_summary import (
    build_case_summary_rows,
    build_decision_record,
    case_status,
    extract_review_flags,
)
from src.reporting.matrix_viz import build_decision_matrix_figure, build_shap_horizontal_bar_figure, build_gauge_figure
from src.models.applicant_scoring import predict_applicant_risk
from src.data.db import init_db, save_case_record, get_case_records, verify_hash_chain

# Initialize SQLite database for decision records
init_db()

st.set_page_config(page_title="Credit Decision Support | Sound Risk Intelligence", layout="wide")

# ── Production Spotify Dark Aesthetic — Full CSS overhaul ────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Core Canvas */
    .stApp { background-color: #0a0a0a !important; color: #FFFFFF !important; }
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0a0a0a; }
    ::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #1DB954; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d0d 0%, #111 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.05) !important;
    }
    [data-testid="stSidebar"] label {
        color: #888 !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #fff !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        border-left: 3px solid #1DB954 !important;
        padding-left: 10px !important;
        margin: 1.2rem 0 0.5rem !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #111;
        padding: 5px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 1.2rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 7px !important;
        color: #666 !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        padding: 7px 14px !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.18s ease !important;
    }
    .stTabs [aria-selected="true"] {
        background: #1DB954 !important;
        color: #000 !important;
        box-shadow: 0 2px 14px rgba(29,185,84,0.4) !important;
    }

    /* Badges */
    .badge-pill {
        display: inline-block;
        padding: 0.2rem 0.65rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.67rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .badge-pill-green  { background:rgba(29,185,84,0.14); color:#1DB954; border:1px solid rgba(29,185,84,0.4); }
    .badge-pill-amber  { background:rgba(255,160,0,0.14);  color:#FFA000; border:1px solid rgba(255,160,0,0.4); }
    .badge-pill-red    { background:rgba(233,20,41,0.14);   color:#E91429; border:1px solid rgba(233,20,41,0.4); }
    .badge-pill-blue   { background:rgba(46,119,208,0.14);  color:#5799EF; border:1px solid rgba(46,119,208,0.4); }

    /* Spotify Card */
    .spotify-card {
        background: #161616;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.22s cubic-bezier(0.4,0,0.2,1);
    }
    .spotify-card:hover {
        background: #1e1e1e;
        border-color: rgba(255,255,255,0.13);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.5);
    }
    .spotify-badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: rgba(29,185,84,0.12);
        border: 1px solid rgba(29,185,84,0.35);
        color: #1DB954;
        padding: 0.28rem 0.8rem;
        border-radius: 50px;
        font-size: 0.67rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* Decision Matrix Cards */
    .matrix-card {
        padding: 1rem 1.2rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
        background: #161616;
        border: 1px solid rgba(255,255,255,0.06);
        transition: all 0.22s ease;
    }
    .matrix-card-active {
        border: 2px solid #1DB954 !important;
        background: rgba(29,185,84,0.07) !important;
        box-shadow: 0 0 28px rgba(29,185,84,0.18);
    }

    /* Native Metrics */
    [data-testid="stMetric"] {
        background: #161616 !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    [data-testid="stMetricValue"] { color:#fff !important; font-weight:800 !important; }
    [data-testid="stMetricLabel"] { color:#666 !important; font-size:0.73rem !important; text-transform:uppercase; letter-spacing:0.04em; }

    /* Buttons */
    .stButton > button {
        background: #1DB954 !important;
        color: #000 !important;
        font-weight: 700 !important;
        border-radius: 50px !important;
        padding: 0.5rem 1.4rem !important;
        border: none !important;
        font-size: 0.84rem !important;
        transition: all 0.18s ease !important;
    }
    .stButton > button:hover {
        background: #1ED760 !important;
        transform: scale(1.03) !important;
        box-shadow: 0 6px 24px rgba(29,185,84,0.4) !important;
    }

    /* Inputs */
    [data-baseweb="input"] > div,
    [data-baseweb="select"] > div:first-child,
    [data-baseweb="textarea"] > div {
        background: #1a1a1a !important;
        border: 1px solid rgba(255,255,255,0.09) !important;
        border-radius: 8px !important;
        color: #fff !important;
    }

    /* DataFrames */
    [data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden; }

    /* Expanders */
    [data-testid="stExpander"] > div:first-child {
        background: #141414 !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
    }

    /* Alerts */
    [data-testid="stAlert"] { border-radius: 10px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Immersive Hero Header rendered as a standalone HTML component ─────────────
components.html(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800;900&display=swap');
      * { box-sizing: border-box; margin: 0; padding: 0; }
      body { background: transparent; font-family: 'Plus Jakarta Sans', sans-serif; overflow: hidden; }

      .hero {
        position: relative;
        background: #0a0a0a;
        border-radius: 20px;
        padding: 2.2rem 2.6rem 1.8rem;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,0.07);
      }
      .hero::before {
        content: '';
        position: absolute; top: -70px; left: -70px;
        width: 360px; height: 360px;
        background: radial-gradient(circle, rgba(29,185,84,0.20) 0%, transparent 70%);
        border-radius: 50%;
        animation: glow 4s ease-in-out infinite;
      }
      .hero::after {
        content: '';
        position: absolute; bottom: -90px; right: 3%;
        width: 280px; height: 280px;
        background: radial-gradient(circle, rgba(29,185,84,0.09) 0%, transparent 65%);
        border-radius: 50%;
        animation: glow 6.5s ease-in-out 1.2s infinite;
      }
      @keyframes glow {
        0%,100% { transform: scale(1);   opacity: 0.75; }
        50%      { transform: scale(1.18); opacity: 1; }
      }
      .inner { position: relative; z-index: 1; }

      .eyebrow {
        display: inline-flex; align-items: center; gap: 7px;
        background: rgba(29,185,84,0.10);
        border: 1px solid rgba(29,185,84,0.30);
        color: #1DB954;
        padding: 4px 14px;
        border-radius: 50px;
        font-size: 0.62rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.11em;
        margin-bottom: 1rem;
      }
      .dot {
        width: 6px; height: 6px;
        background: #1DB954;
        border-radius: 50%;
        animation: blink 1.5s ease-in-out infinite;
      }
      @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.15} }

      .title {
        font-size: 2.5rem;
        font-weight: 900;
        color: #fff;
        letter-spacing: -0.045em;
        line-height: 1.1;
        margin-bottom: 0.55rem;
      }
      .title .green { color: #1DB954; }

      .subtitle {
        font-size: 0.875rem;
        color: #606060;
        line-height: 1.55;
        max-width: 580px;
      }

      .pillars {
        display: flex; gap: 0.85rem; margin-top: 1.5rem; flex-wrap: wrap;
      }
      .chip {
        display: flex; align-items: center; gap: 9px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 0.5rem 0.9rem;
        font-size: 0.76rem;
        color: #aaa;
        font-weight: 500;
        transition: border-color 0.2s, background 0.2s;
      }
      .chip:hover { background: rgba(255,255,255,0.06); border-color: rgba(255,255,255,0.14); }
      .chip-ico {
        width: 26px; height: 26px;
        background: rgba(29,185,84,0.14);
        border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.72rem; color: #1DB954; font-weight: 900;
      }
      .chip-label { color: #fff; display: block; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; }
    </style>

    <div class="hero">
      <div class="inner">
        <div class="eyebrow">
          <div class="dot"></div>
          Sound Risk Intelligence &nbsp;&middot;&nbsp; DPDP Act 2023 &nbsp;&middot;&nbsp; SHA-256 Ledger
        </div>
        <div class="title">Credit Decision<br><span class="green">Support System</span></div>
        <div class="subtitle">
          Dual-Pillar Underwriting Engine — Deterministic Statement Cash Flow analysis combined with
          LightGBM Bureau Risk Benchmark for officer-assisted credit evaluation.
        </div>
        <div class="pillars">
          <div class="chip">
            <div class="chip-ico">P1</div>
            <div><span class="chip-label">Pillar 1</span>Statement Affordability</div>
          </div>
          <div class="chip">
            <div class="chip-ico">P2</div>
            <div><span class="chip-label">Pillar 2</span>Bureau Risk — LightGBM</div>
          </div>
          <div class="chip">
            <div class="chip-ico">2x2</div>
            <div><span class="chip-label">Matrix</span>Dual-Pillar Quadrant</div>
          </div>
        </div>
      </div>
    </div>
    """,
    height=272,
)


# Demo Personas Catalog for Instant Panel Evaluation
DEMO_PERSONAS = {
    "Custom / Manual Entry": None,
    "Persona 1: Prime Salaried Borrower (Q1 - Approve Target)": {
        "applicant_id": "APP-PRIME-01",
        "requested_amount": 300000.0,
        "loan_tenure_months": 24,
        "annual_interest_rate": 11.5,
        "declared_emi": 5000.0,
        "cibil_score": 780,
        "applicant_age": 32,
        "tenure_years": 4.5,
        "active_loans": 1,
        "overdue_days": 0,
    },
    "Persona 2: Over-Leveraged High Earner (Q2 - Bureau Risk Alert)": {
        "applicant_id": "APP-LEVERAGED-02",
        "requested_amount": 600000.0,
        "loan_tenure_months": 36,
        "annual_interest_rate": 14.0,
        "declared_emi": 28000.0,
        "cibil_score": 620,
        "applicant_age": 41,
        "tenure_years": 8.0,
        "active_loans": 5,
        "overdue_days": 42,
    },
    "Persona 3: Thin-Reserve / High-Spend (Q3 - Cashflow Alert)": {
        "applicant_id": "APP-THIN-03",
        "requested_amount": 200000.0,
        "loan_tenure_months": 18,
        "annual_interest_rate": 12.5,
        "declared_emi": 3000.0,
        "cibil_score": 750,
        "applicant_age": 25,
        "tenure_years": 1.5,
        "active_loans": 1,
        "overdue_days": 0,
    },
    "Persona 4: Discrepant / Elevated Default (Q4 - Decline Target)": {
        "applicant_id": "APP-DECLINE-04",
        "requested_amount": 500000.0,
        "loan_tenure_months": 24,
        "annual_interest_rate": 16.0,
        "declared_emi": 22000.0,
        "cibil_score": 540,
        "applicant_age": 36,
        "tenure_years": 0.5,
        "active_loans": 4,
        "overdue_days": 85,
    },
}

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1rem;">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:0.4rem;">
            <div style="width:8px;height:8px;background:#1DB954;border-radius:50%;box-shadow:0 0 8px rgba(29,185,84,0.7);flex-shrink:0;animation:pulse2 2s infinite"></div>
            <span style="font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#1DB954;">System Active</span>
          </div>
          <div style="font-size:1.05rem;font-weight:800;color:#fff;letter-spacing:-0.02em;">Underwriting Console</div>
          <div style="font-size:0.72rem;color:#444;margin-top:2px;">Dual-Pillar Credit Engine</div>
          <style>@keyframes pulse2{0%,100%{opacity:1}50%{opacity:0.3}}</style>
        </div>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin-bottom:0.8rem;">
        """,
        unsafe_allow_html=True,
    )
    st.header("Applicant & Request")

    selected_persona_name = st.selectbox(
        "Load Preset Demo Persona",
        options=list(DEMO_PERSONAS.keys()),
        index=0,
        help="Select a calibrated borrower persona to instantly evaluate dual-pillar matrix response.",
    )
    preset = DEMO_PERSONAS.get(selected_persona_name)

    default_app_id = preset["applicant_id"] if preset else "APP-001"
    default_req_amt = preset["requested_amount"] if preset else 100000.0
    default_tenure = preset["loan_tenure_months"] if preset else 24
    default_rate = preset["annual_interest_rate"] if preset else 12.0
    default_decl_emi = preset["declared_emi"] if preset else 0.0

    applicant_id = st.text_input("Applicant ID", value=default_app_id)
    requested_amount = st.number_input("Requested loan amount (INR)", min_value=0.0, value=default_req_amt, step=10_000.0)
    loan_tenure_months = st.number_input("Requested loan tenure (months)", min_value=1, value=default_tenure, step=1)
    annual_interest_rate = st.number_input("Indicative annual interest rate (%)", min_value=0.0, value=default_rate, step=0.5)
    declared_emi = st.number_input("Declared monthly EMI (INR)", min_value=0.0, value=default_decl_emi, step=1_000.0)
    officer_name = st.text_input("Reviewing officer", placeholder="Loan officer name")
    consent = st.checkbox("Applicant consent for prototype analysis confirmed", value=True)
    monthly_rate = annual_interest_rate / 1200
    proposed_emi = (
        requested_amount / loan_tenure_months
        if monthly_rate == 0 else requested_amount * monthly_rate * (1 + monthly_rate) ** loan_tenure_months / ((1 + monthly_rate) ** loan_tenure_months - 1)
    ) if requested_amount else 0.0
    st.caption(f"Estimated new EMI: INR {proposed_emi:,.0f}/month")

    with st.expander("Applicant Bureau Profile (Pillar 2)", expanded=True):
        enable_bureau = st.checkbox("Enable bureau risk scoring", value=True)
        default_cibil = preset["cibil_score"] if preset else 740
        default_age = preset["applicant_age"] if preset else 32
        default_emp = preset["tenure_years"] if preset else 4.0
        default_active = preset["active_loans"] if preset else 1
        default_overdue = preset["overdue_days"] if preset else 0

        cibil_score = st.number_input("CIBIL / Credit Score", min_value=300, max_value=900, value=default_cibil, step=10)
        applicant_age = st.number_input("Applicant Age (years)", min_value=18, max_value=85, value=default_age, step=1)
        tenure_years = st.number_input("Employment tenure (years)", min_value=0.0, max_value=45.0, value=default_emp, step=0.5)
        active_loans = st.number_input("Active loans count", min_value=0, max_value=30, value=default_active, step=1)
        overdue_days = st.number_input("Past overdue days", min_value=0, max_value=365, value=default_overdue, step=1)

        bureau_profile = {
            "cibil_score": cibil_score,
            "age_years": applicant_age,
            "years_employed": tenure_years,
            "active_loans_count": active_loans,
            "overdue_days": overdue_days,
            "requested_amount": requested_amount,
            "monthly_emi": proposed_emi or declared_emi,
        }
        if enable_bureau and Path(HOME_CREDIT_MODEL_PATH).exists():
            try:
                bureau_result = predict_applicant_risk(bureau_profile)
                st.session_state.bureau_result = bureau_result
                st.caption(f"Bureau Default Risk: **{bureau_result['model_probability']:.1%}** ({bureau_result['risk_band']})")
            except Exception as e:
                st.session_state.bureau_result = None
                st.caption(f"Bureau model note: {e}")
        else:
            st.session_state.bureau_result = None

SYNTHETIC_FEATURES_PATH = Path("data/synthetic/simulator_behaviour_features.csv")


@st.cache_data(ttl="15m")
def load_synthetic_portfolio(path: Path, modified_at_ns: int) -> pd.DataFrame:
    """Load the derived synthetic portfolio only when it has been imported."""
    return pd.read_csv(path)


@st.cache_data(ttl="15m")
def load_metrics(path: Path, modified_at_ns: int) -> dict[str, float]:
    """Load saved evaluation metrics without recalculating the model."""
    return json.loads(path.read_text(encoding="utf-8"))


tab_summary, tab_upload, tab_profile, tab_portfolio, tab_validation, tab_decision = st.tabs([
    "1. Case summary", "2. Upload statement", "3. Behaviour profile", "4. Illustrative synthetic data", "5. ML benchmark (separate)", "6. Officer decision"
])

if "statement" not in st.session_state:
    st.session_state.statement = None
    st.session_state.quality_report = None
    st.session_state.features = None
    st.session_state.monthly_summary = None
    st.session_state.category_summary = None
    st.session_state.column_mapping = None
    st.session_state.salary_verification = None
    st.session_state.bureau_result = None


def apply_statement(statement: pd.DataFrame, quality_report) -> None:
    """Refresh all derived state whenever mapping or officer category edits change."""
    statement = categorise_statement_transactions(statement) if "category" not in statement else statement
    statement = annotate_income_evidence(statement)
    st.session_state.statement = statement
    st.session_state.quality_report = quality_report
    st.session_state.features = build_statement_features(statement, monthly_emi=declared_emi, requested_amount=requested_amount, proposed_emi=proposed_emi)
    st.session_state.monthly_summary = build_monthly_statement_summary(statement)
    st.session_state.category_summary = build_category_summary(statement)


def category_override_records(statement: pd.DataFrame | None) -> list[dict[str, object]]:
    """Return a JSON-safe list of officer category changes for this prototype case."""
    required = {"category_review_status", "category_reviewer", "category_override_rationale"}
    if statement is None or not required.issubset(statement.columns):
        return []
    fields = [
        "date", "description", "original_category", "category", "category_confidence",
        "category_reviewer", "category_override_rationale", "category_override_timestamp_utc",
    ]
    return statement.loc[
        statement["category_review_status"].astype(str).str.startswith("Officer"), fields
    ].to_dict(orient="records")


def format_percent(value: object, signed: bool = False) -> str:
    """Show unavailable evidence explicitly instead of formatting it as zero."""
    if value is None or pd.isna(value):
        return "Not available"
    return f"{float(value):{'+.1%' if signed else '.1%'}}"


with tab_summary:
    st.subheader("Case summary")
    if st.session_state.features is None:
        st.info("Upload and analyse a statement to create a case summary.")
    else:
        decision = recommend(None, st.session_state.features, quality_report=st.session_state.quality_report)
        quality = st.session_state.quality_report
        visual_status, status_message = case_status(decision.recommendation)

        # Futuristic Gauge Cluster (Spotify Green theme)
        gauge_col1, gauge_col2, gauge_col3 = st.columns([1, 1, 1.2])
        with gauge_col1:
            fig_aff = build_gauge_figure(
                value=float(decision.affordability_score or 0.0),
                title="Affordability Score",
                max_value=100.0,
                threshold_low=45.0,
                threshold_high=70.0,
                suffix=" / 100",
            )
            st.plotly_chart(fig_aff, use_container_width=True)
        with gauge_col2:
            fig_q = build_gauge_figure(
                value=float((quality.score or 0.0) * 100.0),
                title="Data Quality Integrity",
                max_value=100.0,
                threshold_low=60.0,
                threshold_high=80.0,
                suffix="%",
            )
            st.plotly_chart(fig_q, use_container_width=True)
        with gauge_col3:
            rec_badge_class = (
                "badge-pill-green" if "Meets" in decision.recommendation
                else "badge-pill-amber" if "Review" in decision.recommendation or "Refer" in decision.recommendation
                else "badge-pill-red"
            )
            st.markdown(
                f"""
                <div class="spotify-card" style="height: 190px; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.06em; color:#B3B3B3; margin-bottom:6px;">
                        System Recommendation
                    </div>
                    <div>
                        <span class="badge-pill {rec_badge_class}" style="font-size:0.9rem; padding: 0.4rem 0.9rem;">
                            {decision.recommendation}
                        </span>
                    </div>
                    <div style="font-size:0.83rem; color:#B3B3B3; margin-top:10px; line-height:1.4;">
                        {status_message}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Custom animated stat card row ────────────────────────────────────────
        surplus_before = st.session_state.features['monthly_surplus']
        surplus_after  = st.session_state.features['post_loan_monthly_surplus']
        surplus_delta  = surplus_after - surplus_before
        surplus_after_color  = "#1DB954" if surplus_after >= 0 else "#E91429"
        surplus_delta_color  = "#1DB954" if surplus_delta >= 0 else "#E91429"
        _stat_cards_html = f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800;900&display=swap');
          * {{ box-sizing: border-box; margin: 0; padding: 0; }}
          body {{ background: transparent; font-family: 'Plus Jakarta Sans', sans-serif; overflow: hidden; }}
          .stat-row {{ display: flex; gap: 14px; }}
          .stat-card {{
            flex: 1;
            background: #161616;
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 14px;
            padding: 1.1rem 1.3rem 1rem;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, border-color 0.2s;
          }}
          .stat-card:hover {{ transform: translateY(-3px); border-color: rgba(255,255,255,0.15); }}
          .stat-card::after {{
            content: '';
            position: absolute;
            bottom: 0; left: 0; right: 0;
            height: 3px;
            border-radius: 0 0 14px 14px;
          }}
          .card-green::after  {{ background: #1DB954; box-shadow: 0 0 12px rgba(29,185,84,0.5); }}
          .card-red::after    {{ background: #E91429; box-shadow: 0 0 12px rgba(233,20,41,0.4); }}
          .card-neutral::after {{ background: #5799EF; box-shadow: 0 0 12px rgba(87,153,239,0.4); }}
          .card-label {{
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: #555;
            margin-bottom: 0.55rem;
          }}
          .card-value {{
            font-size: 1.75rem;
            font-weight: 900;
            color: #fff;
            letter-spacing: -0.03em;
            line-height: 1;
          }}
          .card-sub {{
            font-size: 0.72rem;
            color: #555;
            margin-top: 0.35rem;
          }}
          .card-delta {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 50px;
            margin-top: 0.4rem;
          }}
        </style>
        <div class="stat-row">
          <div class="stat-card card-green">
            <div class="card-label">Before New Loan — Monthly Surplus</div>
            <div class="card-value">INR {surplus_before:,.0f}</div>
            <div class="card-sub">Current net cash position after expenses</div>
          </div>
          <div class="stat-card card-neutral">
            <div class="card-label">Estimated New EMI</div>
            <div class="card-value">INR {proposed_emi:,.0f}</div>
            <div class="card-sub">Calculated at {annual_interest_rate:.1f}% p.a. over {loan_tenure_months} months</div>
          </div>
          <div class="stat-card {'card-green' if surplus_after >= 0 else 'card-red'}">
            <div class="card-label">After New Loan — Monthly Surplus</div>
            <div class="card-value" style="color:{surplus_after_color};">INR {surplus_after:,.0f}</div>
            <div class="card-delta" style="background:{'rgba(29,185,84,0.12)' if surplus_delta >= 0 else 'rgba(233,20,41,0.12)'}; color:{surplus_delta_color};">
              {'▲' if surplus_delta >= 0 else '▼'} INR {abs(surplus_delta):,.0f} vs before
            </div>
          </div>
        </div>
        """
        components.html(_stat_cards_html, height=130)

        review_flags = extract_review_flags(decision.reasons)
        # ── Styled Review Checklist ───────────────────────────────────────────
        if review_flags:
            flag_items_html = "".join(
                f"""<div class="flag-item">
                      <div class="flag-dot"></div>
                      <div class="flag-text">{flag}</div>
                    </div>"""
                for flag in review_flags
            )
            checklist_status = "action-required"
            checklist_header = "Review Flags — Action Required"
            checklist_border = "#E91429"
            checklist_bg = "rgba(233,20,41,0.05)"
        else:
            flag_items_html = """<div class="flag-item clear">
                                   <div class="flag-dot clear-dot"></div>
                                   <div class="flag-text">No mandatory evidence safeguard triggered. Officer review remains required per policy.</div>
                                 </div>"""
            checklist_header = "Review Checklist — No Critical Flags"
            checklist_border = "#1DB954"
            checklist_bg = "rgba(29,185,84,0.05)"

        _checklist_html = f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
          * {{ box-sizing: border-box; margin: 0; padding: 0; }}
          body {{ background: transparent; font-family: 'Plus Jakarta Sans', sans-serif; overflow: hidden; }}
          .checklist {{
            background: {checklist_bg};
            border: 1px solid rgba(255,255,255,0.07);
            border-left: 4px solid {checklist_border};
            border-radius: 12px;
            padding: 1rem 1.3rem;
          }}
          .checklist-header {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {checklist_border};
            margin-bottom: 0.8rem;
          }}
          .flag-item {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 0.45rem 0;
            border-bottom: 1px solid rgba(255,255,255,0.04);
          }}
          .flag-item:last-child {{ border-bottom: none; }}
          .flag-dot {{
            width: 7px; height: 7px;
            background: #E91429;
            border-radius: 50%;
            margin-top: 5px;
            flex-shrink: 0;
          }}
          .clear-dot {{ background: #1DB954; }}
          .flag-text {{ font-size: 0.82rem; color: #ccc; line-height: 1.45; }}
        </style>
        <div class="checklist">
          <div class="checklist-header">{checklist_header}</div>
          {flag_items_html}
        </div>
        """
        components.html(_checklist_html, height=max(80, 50 + len(review_flags) * 52) if review_flags else 100)

        with st.expander("Case-summary evidence table", expanded=True):
            case_summary = build_case_summary_rows(
                st.session_state.features, quality, decision, requested_amount, proposed_emi, applicant_id
            )
            st.dataframe(case_summary, hide_index=True)
            st.download_button(
                "Download case summary CSV", safe_export_csv(case_summary),
                "case_summary.csv", "text/csv",
            )
        with st.expander("All system reasons"):
            for reason in decision.reasons:
                st.write(f"- {reason}")
        st.warning(
            "Evidence boundary: this is a transparent statement-based affordability assessment, not an automated lending decision. "
            "It assesses one uploaded account only and cannot verify document authenticity, employment, household costs, or finances held elsewhere."
        )

with tab_upload:
    st.subheader("Bank statement upload (CSV or Digital PDF)")
    st.write("Required: date, description, and either debit/credit or one signed amount column. Optional: closing balance.")
    uploaded = st.file_uploader("Upload bank statement", type=["csv", "pdf"])
    mapping: dict[str, str | None] | None = None
    opening_balance = None
    if uploaded:
        is_pdf = uploaded.name.lower().endswith(".pdf")
        try:
            if is_pdf:
                from src.documents.statement_pdf import extract_text_from_pdf
                pdf_text = extract_text_from_pdf(BytesIO(uploaded.getvalue()))
                st.info(f"Digital PDF statement detected. Extracted {len(pdf_text.splitlines())} text lines.")
            else:
                preview = read_statement_preview(BytesIO(uploaded.getvalue()))
                suggested_mapping = suggest_column_mapping(list(preview.columns))
                with st.expander("Review or map CSV columns", expanded=not (suggested_mapping["date"] and suggested_mapping["description"])):
                    st.caption("Use the automatic mapping where correct. For a signed amount export, leave Debit and Credit as Not supplied and select Amount.")
                    choices = ["Not supplied", *preview.columns.tolist()]
                    mapping = {}
                    for field, label in [("date", "Date"), ("description", "Description"), ("debit", "Debit"), ("credit", "Credit"), ("amount", "Signed amount"), ("balance", "Closing balance")]:
                        suggested = suggested_mapping.get(field)
                        mapping[field] = st.selectbox(label, choices, index=choices.index(suggested) if suggested in choices else 0, key=f"mapping_{field}")
                        if mapping[field] == "Not supplied":
                            mapping[field] = None
                    opening_balance = st.number_input("Opening balance (optional)", value=0.0, step=1_000.0, help="Used only to validate the first balance transition when supplied.")
                    st.dataframe(preview.head(10), hide_index=True)
        except (ValueError, pd.errors.ParserError) as error:
            st.error(str(error))

    st.subheader("Optional: Salary slip cross-verification")
    slip_col1, slip_col2 = st.columns(2)
    slip_salary = slip_col1.number_input("Salary slip net pay (₹)", min_value=0.0, step=5_000.0)
    slip_employer = slip_col2.text_input("Declared employer name", placeholder="e.g. Infosys, TCS, ACME")

    if uploaded and st.button("Analyse statement", type="primary"):
        try:
            if uploaded.name.lower().endswith(".pdf"):
                from src.documents.statement_pdf import parse_statement_pdf
                statement, quality_report = parse_statement_pdf(BytesIO(uploaded.getvalue()))
            else:
                statement, quality_report = parse_statement_csv(BytesIO(uploaded.getvalue()), column_mapping=mapping, opening_balance=opening_balance if opening_balance else None)
            statement = annotate_income_evidence(statement)
            apply_statement(statement, quality_report)
            st.success(f"Parsed {len(statement)} transactions. Data-quality score: {quality_report.score:.0%}")

            if slip_salary > 0:
                from src.documents.salary_verification import verify_salary_slip_cross_document
                verification = verify_salary_slip_cross_document(statement, slip_salary, slip_employer)
                st.session_state.salary_verification = verification
                if verification.is_verified:
                    st.success(f"Salary slip verification: {verification.status}")
                else:
                    st.warning(f"Salary slip verification: {verification.status}")
                for r in verification.reasons:
                    st.caption(f"- {r}")
            else:
                st.session_state.salary_verification = None
        except (ValueError, pd.errors.ParserError) as error:
            st.error(str(error))
    if st.session_state.statement is not None:
        quality_report = st.session_state.quality_report
        with st.container(border=True):
            st.subheader("Statement data quality")
            quality_columns = st.columns(4)
            quality_columns[0].metric("Quality score", f"{quality_report.score:.0%}")
            quality_columns[1].metric("Observed months", quality_report.observed_months)
            quality_columns[2].metric("Valid / rejected", f"{quality_report.valid_transactions} / {quality_report.rejected_rows}")
            quality_columns[3].metric("Duplicate rows removed", quality_report.duplicate_rows_removed)
            st.caption(f"Date range: {quality_report.date_range_start or 'Not available'} to {quality_report.date_range_end or 'Not available'}")
            for warning in quality_report.warnings:
                st.warning(warning)
        st.subheader("Categorised transactions")
        st.caption("Review uncertain categories before using the summary. An override preserves the initial category, reviewer, rationale, and UTC timestamp in this prototype case record.")
        editable = st.session_state.statement.copy()
        editable["officer_category"] = editable["category"]
        if "category_override_rationale" not in editable:
            editable["category_override_rationale"] = ""
        editable["category_reviewer"] = officer_name or "Not supplied"
        edited = st.data_editor(editable, key="category_review", hide_index=True, disabled=[column for column in editable.columns if column not in {"officer_category", "category_override_rationale"}], column_config={"officer_category": st.column_config.SelectboxColumn("Officer category", options=list(CATEGORY_OPTIONS))})
        if st.button("Apply category overrides"):
            if "original_category" not in edited:
                edited["original_category"] = edited["category"]
            else:
                edited["original_category"] = edited["original_category"].fillna(edited["category"])
            changed = edited["officer_category"] != edited["category"]
            edited.loc[changed, "category"] = edited.loc[changed, "officer_category"]
            edited.loc[changed, "category_review_status"] = "Officer override"
            edited.loc[changed, "category_confidence"] = 1.0
            edited.loc[changed, "category_reviewer"] = officer_name or "Not supplied"
            edited.loc[changed, "category_override_timestamp_utc"] = datetime.now(timezone.utc).isoformat()
            apply_statement(edited.drop(columns=["officer_category"]), st.session_state.quality_report)
            st.success("Category overrides applied and behavioural indicators refreshed.")
        with st.expander("Bulk recategorise a repeated merchant"):
            st.caption(
                "This applies one officer-reviewed category to every transaction with the same normalised narration. "
                "Review the example and transaction count before applying it."
            )
            merchant_groups = build_repeated_merchant_groups(st.session_state.statement)
            if merchant_groups.empty:
                st.info("No repeated merchant narrations are available for bulk review.")
            else:
                merchant_options = merchant_groups["merchant_key"].tolist()
                selected_merchant = st.selectbox(
                    "Repeated merchant narration", merchant_options, key="bulk_merchant_key",
                    format_func=lambda key: (
                        f"{merchant_groups.loc[merchant_groups['merchant_key'].eq(key), 'example_description'].iloc[0]} "
                        f"({merchant_groups.loc[merchant_groups['merchant_key'].eq(key), 'transactions'].iloc[0]} transactions)"
                    ),
                )
                selected_group = merchant_groups.loc[merchant_groups["merchant_key"].eq(selected_merchant)].iloc[0]
                st.caption(f"Current categories: {selected_group['current_categories']}")
                bulk_category = st.selectbox("Bulk officer category", list(CATEGORY_OPTIONS), key="bulk_category")
                bulk_rationale = st.text_input(
                    "Bulk override rationale", key="bulk_category_rationale",
                    placeholder="Why should all matching narrations use this category?",
                )
                if st.button("Apply bulk category override"):
                    try:
                        bulk_updated, changed_count = apply_bulk_category_override(
                            st.session_state.statement,
                            selected_merchant,
                            bulk_category,
                            officer_name or "Not supplied",
                            bulk_rationale,
                            datetime.now(timezone.utc).isoformat(),
                        )
                        apply_statement(bulk_updated, st.session_state.quality_report)
                        st.success(f"Applied the reviewed category to {changed_count} transaction(s).")
                    except ValueError as error:
                        st.error(str(error))
        export_columns = st.columns(4)
        export_columns[0].download_button("Download cleaned transactions CSV", safe_export_csv(st.session_state.statement), "cleaned_transactions.csv", "text/csv")
        export_columns[1].download_button("Download categorised transactions CSV", safe_export_csv(st.session_state.statement), "categorised_transactions.csv", "text/csv")
        export_columns[2].download_button("Download behavioural features CSV", safe_export_csv(pd.DataFrame([st.session_state.features])), "behavioural_features.csv", "text/csv")
        export_decision = recommend(None, st.session_state.features, quality_report=st.session_state.quality_report)
        export_columns[3].download_button(
            "Download affordability breakdown CSV",
            safe_export_csv(pd.DataFrame([{"component": label, "points": points} for label, points in (export_decision.affordability_components or {}).items()])),
            "affordability_score_breakdown.csv",
            "text/csv",
        )
        category_evaluation_path = Path("reports/category_rule_evaluation.json")
        if category_evaluation_path.exists():
            category_evaluation = json.loads(category_evaluation_path.read_text(encoding="utf-8"))
            with st.expander("Category-rule regression fixture (not production validation)"):
                st.caption(
                    f"{category_evaluation['note']} The displayed metrics are regression-fixture results, "
                    "not a claim of real-world categorisation accuracy."
                )
                metrics = st.columns(3)
                metrics[0].metric("Macro precision", f"{category_evaluation['macro_precision']:.1%}")
                metrics[1].metric("Macro recall", f"{category_evaluation['macro_recall']:.1%}")
                metrics[2].metric("Macro F1", f"{category_evaluation['macro_f1']:.1%}")
                st.dataframe(pd.DataFrame(category_evaluation["per_category"]), hide_index=True)
                st.dataframe(pd.DataFrame(category_evaluation["confusion_matrix"]).T)
        category_coverage_path = Path("reports/heldout_category_rule_evaluation.json")
        if category_coverage_path.exists():
            category_coverage = json.loads(category_coverage_path.read_text(encoding="utf-8"))
            with st.expander("Category-rule coverage fixture (not production validation)"):
                st.warning(
                    "This small curated sample checks rule coverage only. Its metrics are not real-statement "
                    "or production-performance validation."
                )
                metrics = st.columns(3)
                metrics[0].metric("Macro precision", f"{category_coverage['macro_precision']:.1%}")
                metrics[1].metric("Macro recall", f"{category_coverage['macro_recall']:.1%}")
                metrics[2].metric("Macro F1", f"{category_coverage['macro_f1']:.1%}")
                st.dataframe(pd.DataFrame(category_coverage["per_category"]), hide_index=True)

with tab_profile:
    st.subheader("Behavioural and affordability indicators")
    if st.session_state.features is None:
        st.info("Upload and analyse a CSV statement first.")
    else:
        features = st.session_state.features
        with st.container(horizontal=True):
            st.metric("Average monthly income", f"₹{features['average_monthly_income']:,.0f}", border=True)
            st.metric("Other statement credits", f"₹{features['other_statement_credits']:,.0f}", help="Credits excluded from recurring-income affordability calculations.", border=True)
            st.metric("Average monthly expense", f"₹{features['average_monthly_expense']:,.0f}", border=True)
            st.metric("Monthly surplus", f"₹{features['monthly_surplus']:,.0f}", help="Based on recognised recurring income, not every statement credit.", border=True)
        with st.container(horizontal=True):
            st.metric("Savings ratio", f"{features['savings_ratio']:.1%}", border=True)
            st.metric("EMI-to-income ratio", f"{features['emi_to_income_ratio']:.1%}", border=True)
            st.metric("Income variation", f"{features['income_variation_ratio']:.1%}", border=True)
        with st.container(horizontal=True):
            st.metric("Income trend", format_percent(features['income_trend_ratio'], signed=True), help="Shown only with at least three months and no partial boundary month.", border=True)
            st.metric("Savings trend", format_percent(features['savings_trend_ratio'], signed=True), help="Shown only with at least three months and no partial boundary month.", border=True)
            st.metric("Expense variation", f"{features['expense_variation_ratio']:.1%}", border=True)
        with st.container(horizontal=True):
            st.metric("Salary frequency", str(features["salary_frequency"]).title(), help="Detected frequency of rule-labelled salary credits.", border=True)
            emergency_buffer = f"{features['emergency_buffer_months']:.1f} months" if features["has_balance_history"] else "Not available"
            emi_after_loan = f"{features['proposed_emi_to_income_ratio']:.1%}" if features["average_monthly_income"] else "Not available"
            st.metric("Emergency buffer", emergency_buffer, help="Average closing balance divided by average monthly expense. Not available without balance history.", border=True)
            st.metric("After new loan EMI burden", emi_after_loan, help="Existing detected/declared EMI plus estimated new EMI divided by income.", border=True)
            st.metric("EMI evidence", "Check required" if features["emi_difference_amount"] >= 1_000 and features["emi_discrepancy_ratio"] > 0.20 else "No material mismatch", help="Compares declared EMI with detected EMI-payment occurrence; it cannot verify payment timeliness.", border=True)
        if features["partial_boundary_month"]:
            st.warning("The first or last statement month appears partial. Trend metrics are withheld to avoid over-interpreting incomplete months.")
        st.caption("Income uses recognised recurring income evidence. Other credits are displayed separately and are not assumed to be income.")

        monthly_summary = st.session_state.monthly_summary
        category_summary = st.session_state.category_summary
        filter_columns = st.columns(2)
        selected_months = filter_columns[0].multiselect("Months to display", monthly_summary["month"].tolist(), default=monthly_summary["month"].tolist())
        selected_categories = filter_columns[1].multiselect("Categories to display", category_summary["Category"].tolist(), default=category_summary["Category"].tolist())
        transaction_search = st.text_input("Search transactions", placeholder="Search a merchant, payment, or description")
        filtered_monthly = monthly_summary[monthly_summary["month"].isin(selected_months)]
        filtered_categories = category_summary[category_summary["Category"].isin(selected_categories)]
        with st.container(border=True):
            st.subheader("Monthly cash flow")
            cash_flow_chart = filtered_monthly[["month", "income", "expense", "surplus"]].rename(columns={
                "income": "Income", "expense": "Expense", "surplus": "Surplus",
            })
            st.line_chart(cash_flow_chart, x="month", y=["Income", "Expense", "Surplus"])
            st.dataframe(filtered_monthly[["month", "income", "expense", "surplus", "closing_balance"]], hide_index=True)

        chart_left, chart_right = st.columns(2)
        with chart_left:
            with st.container(border=True):
                st.subheader("Expense categories")
                st.bar_chart(filtered_categories, x="Category", y="Expense")
        with chart_right:
            with st.container(border=True):
                st.subheader("Behavioural indicators")
                indicators = pd.DataFrame({
                    "Indicator": [
                        "Salary-income share",
                        "Essential-expense ratio",
                        "Discretionary-expense ratio",
                        "Utility-payment regularity",
                        "Cash withdrawals per month",
                        "Low-balance days",
                        "Large-spending transactions",
                        "Missed salary months",
                        "Uncertain transaction share",
                        "Post-loan monthly surplus",
                    ],
                    "Value": [
                        format_percent(features['salary_income_share']),
                        f"{features['essential_expense_ratio']:.1%}",
                        f"{features['discretionary_expense_ratio']:.1%}",
                        f"{features['utility_payment_regularity']:.1%}",
                        f"{features['cash_withdrawals_per_month']:.1f}",
                        f"{features['low_balance_day_count']:.0f}",
                        f"{features['large_spending_count']:.0f}",
                        f"{features['missed_salary_months']:.0f}",
                        f"{features['uncertain_transaction_share']:.1%}",
                        f"₹{features['post_loan_monthly_surplus']:,.0f}",
                    ],
                })
                st.dataframe(indicators, hide_index=True)

        if filtered_monthly["closing_balance"].notna().any():
            with st.container(border=True):
                st.subheader("Month-end balance trend")
                st.line_chart(filtered_monthly, x="month", y="closing_balance", y_label="Closing balance (₹)")
        searched_transactions = st.session_state.statement.copy()
        if transaction_search.strip():
            searched_transactions = searched_transactions[
                searched_transactions["description"].astype(str).str.contains(transaction_search, case=False, na=False)
            ]
        with st.expander("Searchable transaction view"):
            st.dataframe(searched_transactions, hide_index=True)
        st.caption("These are descriptive affordability signals. They support review and do not determine a lending outcome.")

with tab_portfolio:
    st.subheader("Synthetic behavioural portfolio")
    if not SYNTHETIC_FEATURES_PATH.exists():
        st.info(
            "Import Bank Data Simulator output to view the synthetic portfolio here. "
            "See docs/bank_data_simulator.md for the command."
        )
    else:
        portfolio = load_synthetic_portfolio(SYNTHETIC_FEATURES_PATH, SYNTHETIC_FEATURES_PATH.stat().st_mtime_ns)
        metric_columns = st.columns(3, border=True)
        metric_columns[0].metric("Synthetic profiles", f"{len(portfolio):,}")
        metric_columns[1].metric("Behavioural fields", len(portfolio.columns) - 2)
        metric_columns[2].metric("Latest snapshot", str(portfolio.iloc[-1, 1]) if portfolio.shape[1] > 1 else "Available")
        behavioural_columns = [
            column for column in portfolio.select_dtypes(include="number").columns if column != "customer_id"
        ]
        st.bar_chart(portfolio[behavioural_columns].mean().rename("Average").reset_index(), x="index", y="Average")
        st.dataframe(portfolio.head(100), hide_index=True)

with tab_validation:
    st.subheader("Home Credit default-risk model")
    if not HOME_CREDIT_METRICS_PATH.exists() or not HOME_CREDIT_MODEL_PATH.exists():
        st.info("Train the Home Credit model to display its held-out evaluation metrics.")
    else:
        metrics = load_metrics(HOME_CREDIT_METRICS_PATH, HOME_CREDIT_METRICS_PATH.stat().st_mtime_ns)
        final_test = metrics.get("final_test_metrics", metrics)
        protocol = metrics.get("evaluation_protocol", {})
        display_recall = final_test.get("recall", final_test.get("recall_at_0_50", 0.0))
        display_precision = final_test.get("precision", final_test.get("precision_at_0_50", 0.0))
        metric_columns = st.columns(3, border=True)
        metric_columns[0].metric("Final-test ROC-AUC", f"{final_test['roc_auc']:.3f}")
        metric_columns[1].metric("Final-test PR-AUC", f"{final_test['pr_auc']:.3f}")
        metric_columns[2].metric("Features", f"{metrics['feature_count']}")
        metric_columns = st.columns(2, border=True)
        metric_columns[0].metric(f"Default recall at {final_test.get('threshold', 0.50):.2f}", f"{display_recall:.1%}")
        metric_columns[1].metric(f"Default precision at {final_test.get('threshold', 0.50):.2f}", f"{display_precision:.1%}")
        st.caption(
            f"Selected model: {metrics['model_name']}. Final-test Brier score: {final_test['brier_score']:.3f} "
            "(lower indicates better probability accuracy)."
        )
        st.caption(
            "This model uses Home Credit repayment and credit-history features; it is not applied directly to raw uploaded statements. "
            f"Final test set: {protocol.get('test_rows', final_test.get('test_rows', 'Not available')):,} held-out applicants. "
            "Model, calibration, and threshold were selected on separate training/validation data."
        )
        if HOME_CREDIT_COMPARISON_PATH.exists():
            comparison = load_metrics(
                HOME_CREDIT_COMPARISON_PATH, HOME_CREDIT_COMPARISON_PATH.stat().st_mtime_ns
            )
            benchmark = pd.DataFrame(comparison["models"])
            with st.container(border=True):
                st.subheader("Candidate model benchmark")
                st.caption(
                    "All candidates used the same validation applicants. Selection order: "
                    f"{comparison['selection_metric']}."
                )
                st.bar_chart(benchmark, x="model", y=["roc_auc", "pr_auc"])
                st.dataframe(benchmark, hide_index=True)
        if HOME_CREDIT_THRESHOLD_PATH.exists():
            threshold_report = load_metrics(
                HOME_CREDIT_THRESHOLD_PATH, HOME_CREDIT_THRESHOLD_PATH.stat().st_mtime_ns
            )
            thresholds = pd.DataFrame(threshold_report.get("final_test_rows", threshold_report.get("rows", [])))
            with st.container(border=True):
                st.subheader("Selected-model threshold analysis")
                st.caption(
                    f"Threshold was selected on validation data using this policy: {threshold_report.get('risk_policy', 'Not available')} "
                    "Final-test values are descriptive only and do not create an automatic lending rule."
                )
                st.line_chart(thresholds, x="threshold", y=["recall", "precision", "flagged_applicant_rate"])
                st.dataframe(thresholds, hide_index=True)
        if HOME_CREDIT_CALIBRATION_PATH.exists():
            calibration = load_metrics(
                HOME_CREDIT_CALIBRATION_PATH, HOME_CREDIT_CALIBRATION_PATH.stat().st_mtime_ns
            )
            final_calibration = calibration.get("final_test", calibration)
            reliability = pd.DataFrame(final_calibration["reliability"])
            with st.container(border=True):
                st.subheader("Probability calibration")
                st.caption(
                    f"Selected calibration: {calibration.get('selected_method', calibration.get('method', 'Not available'))}. "
                    f"Final-test Brier score: {final_calibration.get('brier_score', calibration.get('calibrated_brier_score')):.3f}. "
                    "Calibration method was selected on validation data."
                )
                st.line_chart(reliability, x="mean_predicted_risk", y="observed_default_rate")
                st.dataframe(reliability, hide_index=True)
        importance_path = Path("reports/home_credit_global_importance.json")
        if importance_path.exists():
            importance = pd.DataFrame(json.loads(importance_path.read_text(encoding="utf-8")))
            st.subheader("Global feature importance (Tree gain)")
            st.bar_chart(importance, x="feature", y="gain_importance")
            st.caption("Gain importance shows which credit-history and repayment features contributed most across the model. It is a global explanation, not an individual lending decision explanation.")

            from src.models.explain_home_credit import explain_local_factors
            st.subheader("Explainable risk factor attribution (Exact Tree-SHAP)")
            st.caption("Path-dependent Shapley values computed via LightGBM booster. Features with positive SHAP push predicted risk higher, while negative values act as protective buffers.")
            
            # Reuse pre-computed Tree-SHAP attributions from the active applicant bureau scoring if available
            if st.session_state.get("bureau_result") and "local_explanations" in st.session_state.bureau_result:
                local_exp = st.session_state.bureau_result["local_explanations"]
                st.info(f"Displaying Tree-SHAP attributions for the active applicant profile (CIBIL: {cibil_score}, Age: {applicant_age}).")
            else:
                mock_applicant = {
                    "EXT_SOURCE_3": 0.28,
                    "EXT_SOURCE_2": 0.42,
                    "DAYS_EMPLOYED": -650,
                    "installment_days_late": 4.0,
                }
                local_exp = explain_local_factors(mock_applicant)
                st.caption("Displaying Tree-SHAP attributions for reference applicant persona.")

            fig_shap = build_shap_horizontal_bar_figure(local_exp)
            st.plotly_chart(fig_shap, use_container_width=True)

            c_risk, c_prot = st.columns(2)
            with c_risk:
                st.markdown("**Top risk-increasing drivers (Positive SHAP):**")
                for r in local_exp["top_risk_increasing_factors"]:
                    st.write(f"- :red[{r['feature']}]: {r['impact']}")
            with c_prot:
                st.markdown("**Top protective factors (Negative SHAP):**")
                for p in local_exp["top_risk_decreasing_factors"]:
                    st.write(f"- :green[{p['feature']}]: {p['impact']}")

with tab_decision:
    st.subheader("Indicative assessment and officer review")
    if not consent:
        st.warning("Confirm applicant consent before recording a prototype recommendation.")
    bureau_prob = (
        st.session_state.bureau_result["model_probability"]
        if st.session_state.get("bureau_result") is not None
        else None
    )
    completeness_pct = (
        st.session_state.bureau_result.get("input_completeness_percent", "N/A")
        if st.session_state.get("bureau_result") is not None
        else "N/A"
    )
    decision = recommend(
        model_probability=bureau_prob,
        statement_features=st.session_state.features,
        extraction_confidence=(st.session_state.quality_report.score if st.session_state.quality_report else None),
        quality_report=st.session_state.quality_report,
        salary_verification=st.session_state.get("salary_verification"),
    )
    if decision.affordability_score is None:
        st.info("Upload and analyse a statement to generate an affordability assessment.")
    else:
        if decision.pillar_summary and decision.pillar_summary.get("mode", "").startswith("Dual-Pillar"):
            with st.container(border=True):
                st.subheader("Unified Dual-Pillar Credit Evaluation Matrix")
                col_p1, col_p2, col_q = st.columns(3)
                col_p1.metric(
                    "Pillar 1: Statement Affordability",
                    f"{decision.affordability_score}/100",
                    decision.pillar_summary.get("affordability_band", ""),
                )
                col_p2.metric(
                    "Pillar 2: Bureau Default Risk",
                    f"{bureau_prob:.1%}",
                    f"{decision.pillar_summary.get('bureau_risk_band', '')} (Input Completeness: {completeness_pct})",
                    delta_color="inverse",
                )
                col_q.metric(
                    "Matrix Quadrant",
                    decision.recommendation,
                    decision.pillar_summary.get("quadrant", ""),
                )

                # Visual 2x2 Decision Matrix Map
                fig_matrix = build_decision_matrix_figure(
                    affordability_score=decision.affordability_score,
                    bureau_probability=bureau_prob,
                    applicant_id=applicant_id or "Current Applicant",
                )
                st.plotly_chart(fig_matrix, use_container_width=True)

                # Visual 4-Quadrant Policy Cards Grid
                active_quad = decision.pillar_summary.get("quadrant", "")
                q_row1_col1, q_row1_col2 = st.columns(2)
                with q_row1_col1:
                    is_active = active_quad == "Quadrant 1"
                    card_border = "matrix-card-active" if is_active else ""
                    st.markdown(
                        f"""
                        <div class="matrix-card {card_border}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#34D399;">Q1: Meets Indicative Criteria</b>
                                <span class="badge-pill badge-pill-green">{'ACTIVE' if is_active else 'Score ≥ 70 & PD < 20%'}</span>
                            </div>
                            <div style="font-size:0.83rem; color:#94A3B8; margin-top:4px;">
                                Robust statement cash-flow surplus accompanied by acceptable external credit bureau default risk.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with q_row1_col2:
                    is_active = active_quad == "Quadrant 2"
                    card_border = "matrix-card-active" if is_active else ""
                    st.markdown(
                        f"""
                        <div class="matrix-card {card_border}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#FBBF24;">Q2: Manual Review (Bureau Risk)</b>
                                <span class="badge-pill badge-pill-amber">{'ACTIVE' if is_active else 'Score ≥ 70 & PD ≥ 20%'}</span>
                            </div>
                            <div style="font-size:0.83rem; color:#94A3B8; margin-top:4px;">
                                Statement surplus appears viable, but external trade lines or delinquency history signal elevated default risk.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                q_row2_col1, q_row2_col2 = st.columns(2)
                with q_row2_col1:
                    is_active = active_quad == "Quadrant 3"
                    card_border = "matrix-card-active" if is_active else ""
                    st.markdown(
                        f"""
                        <div class="matrix-card {card_border}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#FBBF24;">Q3: Manual Review (Cashflow Alert)</b>
                                <span class="badge-pill badge-pill-amber">{'ACTIVE' if is_active else 'Score < 70 & PD < 20%'}</span>
                            </div>
                            <div style="font-size:0.83rem; color:#94A3B8; margin-top:4px;">
                                Clean bureau history, but statement indicates thin cash reserves, volatile income, or heavy expense burden.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with q_row2_col2:
                    is_active = active_quad == "Quadrant 4"
                    card_border = "matrix-card-active" if is_active else ""
                    st.markdown(
                        f"""
                        <div class="matrix-card {card_border}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#F87171;">Q4: Decline (Dual Risk Elevation)</b>
                                <span class="badge-pill badge-pill-red">{'ACTIVE' if is_active else 'Score < 70 & PD ≥ 20%'}</span>
                            </div>
                            <div style="font-size:0.83rem; color:#94A3B8; margin-top:4px;">
                                Depleted cash flow and high debt obligations compounded by elevated external credit default risk.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            decision_columns = st.columns(2, border=True)
            decision_columns[0].metric("Behavioural affordability score", f"{decision.affordability_score}/100")
            decision_columns[1].metric("System recommendation", decision.recommendation)

        if st.session_state.get("salary_verification"):
            sv = st.session_state.salary_verification
            if sv.is_verified:
                st.success(f"Cross-document salary verification: {sv.status}")
            else:
                st.warning(f"Cross-document salary safeguard: {sv.status} (Declared: ₹{sv.slip_net_salary:,.0f} vs Statement: ₹{sv.detected_statement_salary:,.0f})")

        st.caption(f"Rule version: {decision.rule_version}. Policy safeguards override numerical scores when evidence is contradictory or incomplete.")

        # ── Animated score breakdown bars (replaces st.dataframe) ────────────
        affordability_components = decision.affordability_components or {}
        if affordability_components:
            max_points_total = max(abs(v) for v in affordability_components.values()) if affordability_components else 1
            bar_items_html = ""
            for comp_name, comp_pts in affordability_components.items():
                pct = min(100.0, abs(comp_pts) / max(1, max_points_total) * 100)
                bar_color = "#1DB954" if comp_pts >= 0 else "#E91429"
                bar_bg    = "rgba(29,185,84,0.10)" if comp_pts >= 0 else "rgba(233,20,41,0.10)"
                pts_label = f"+{comp_pts:.1f}" if comp_pts >= 0 else f"{comp_pts:.1f}"
                label_clean = comp_name.replace("_", " ").title()
                bar_items_html += f"""
                <div class="bar-row">
                  <div class="bar-label">{label_clean}</div>
                  <div class="bar-track">
                    <div class="bar-fill" style="width:{pct:.1f}%; background:{bar_color}; box-shadow: 0 0 8px {bar_color}44;"></div>
                  </div>
                  <div class="bar-pts" style="color:{bar_color};">{pts_label}</div>
                </div>
                """
            total_pts = sum(affordability_components.values())
            total_color = "#1DB954" if total_pts >= 0 else "#E91429"
            n_bars = len(affordability_components)
            bar_height = 50 + n_bars * 46
            _score_bars_html = f"""
            <style>
              @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
              * {{ box-sizing: border-box; margin: 0; padding: 0; }}
              body {{ background: transparent; font-family: 'Plus Jakarta Sans', sans-serif; overflow: hidden; }}
              .score-container {{
                background: #141414;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 14px;
                padding: 1.2rem 1.5rem;
              }}
              .score-header {{
                display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 1rem;
                padding-bottom: 0.7rem;
                border-bottom: 1px solid rgba(255,255,255,0.06);
              }}
              .score-title {{
                font-size: 0.68rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #555;
              }}
              .score-total {{
                font-size: 1.3rem;
                font-weight: 900;
                color: {total_color};
                letter-spacing: -0.03em;
              }}
              .bar-row {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-bottom: 0.55rem;
              }}
              .bar-label {{
                font-size: 0.76rem;
                color: #aaa;
                font-weight: 500;
                width: 220px;
                flex-shrink: 0;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
              }}
              .bar-track {{
                flex: 1;
                height: 6px;
                background: rgba(255,255,255,0.06);
                border-radius: 3px;
                overflow: hidden;
              }}
              .bar-fill {{
                height: 100%;
                border-radius: 3px;
                width: 0%;
                transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
              }}
              .bar-pts {{
                font-size: 0.77rem;
                font-weight: 700;
                width: 46px;
                text-align: right;
                flex-shrink: 0;
              }}
            </style>
            <div class="score-container">
              <div class="score-header">
                <div class="score-title">Affordability Score Breakdown</div>
                <div class="score-total">{decision.affordability_score} / 100</div>
              </div>
              {bar_items_html}
            </div>
            <script>
              // Trigger bar animations after render
              setTimeout(function() {{
                document.querySelectorAll('.bar-fill').forEach(function(el) {{
                  el.style.width = el.style.width; // reflow
                }});
              }}, 80);
            </script>
            """
            components.html(_score_bars_html, height=bar_height)
        else:
            st.caption("No affordability score components available.")

        with st.expander("Active policy and safeguards"):
            st.caption(POLICY["evidence_status"])
            st.dataframe(
                pd.DataFrame([
                    {"Component": label.replace("_", " ").title(), "Rationale": rationale}
                    for label, rationale in POLICY["component_rationale"].items()
                ]),
                hide_index=True,
            )
            st.caption(
                "Safeguards override the numerical score when evidence is incomplete or contradictory. "
                "See docs/affordability_policy.md for the complete policy definition."
            )
        if st.session_state.features:
            metrics_actionable = calculate_actionable_affordability_metrics(
                st.session_state.features,
                loan_tenure_months=int(loan_tenure_months),
                annual_interest_rate=float(annual_interest_rate),
            )
            with st.expander("Actionable loan metrics, stress scenarios & counterfactuals", expanded=True):
                col_a, col_b = st.columns(2)
                col_a.metric("Max sustainable EMI", f"₹{metrics_actionable['max_sustainable_monthly_emi']:,.0f}")
                col_b.metric("Max indicative loan", f"₹{metrics_actionable['max_indicative_loan_amount']:,.0f}")
                st.caption(f"Stress test (Income -20%, Expense +10%, Rate +2%): Stressed max loan = ₹{metrics_actionable['stressed_max_indicative_loan']:,.0f}")
                
                # Interactive Scenario Stress Testing Lab
                st.markdown("---")
                st.subheader("Scenario Shock and Stress Testing Lab")
                st.caption("Interactively test applicant loan capacity and risk stability under adverse economic shocks.")
                
                col_s1, col_s2, col_s3 = st.columns(3)
                shock_inc = col_s1.slider("Income Shock", min_value=-50, max_value=0, value=-20, step=5, format="%d%%", key="slider_shock_inc")
                shock_exp = col_s2.slider("Expense Inflation", min_value=0, max_value=50, value=10, step=5, format="+%d%%", key="slider_shock_exp")
                shock_rate = col_s3.slider("Interest Rate Hike", min_value=0.0, max_value=6.0, value=2.0, step=0.5, format="+%.1f%%", key="slider_shock_rate")

                # Dynamic calculations under shock
                feat = st.session_state.features
                st_inc = max(0.0, float(feat["average_monthly_income"]) * (1.0 + shock_inc / 100.0))
                st_exp = float(feat["average_monthly_expense"]) * (1.0 + shock_exp / 100.0)
                st_surplus = max(0.0, st_inc - st_exp)
                st_max_emi = max(0.0, st_surplus * 0.50)
                st_annual_rate = float(annual_interest_rate) + shock_rate
                st_m_rate = st_annual_rate / 1200.0
                st_months = int(loan_tenure_months)
                if st_m_rate > 0 and st_max_emi > 0:
                    st_max_loan = st_max_emi * ((1.0 + st_m_rate) ** st_months - 1.0) / (st_m_rate * (1.0 + st_m_rate) ** st_months)
                else:
                    st_max_loan = st_max_emi * st_months

                col_res1, col_res2, col_res3 = st.columns(3)
                col_res1.metric(
                    "Stressed Monthly Surplus",
                    f"₹{st_surplus:,.0f}",
                    delta=f"{st_surplus - feat['monthly_surplus']:,.0f}",
                )
                col_res2.metric(
                    "Stressed Max Sustainable EMI",
                    f"₹{st_max_emi:,.0f}",
                    delta=f"{st_max_emi - metrics_actionable['max_sustainable_monthly_emi']:,.0f}",
                )
                base_loan = metrics_actionable['max_indicative_loan_amount']
                retention_pct = (st_max_loan / base_loan) if base_loan > 0 else 0.0
                col_res3.metric(
                    "Stressed Loan Capacity",
                    f"₹{st_max_loan:,.0f}",
                    delta=f"{retention_pct:.0%} retention",
                )

                st.subheader("Counterfactual guidance")
                for item in metrics_actionable["counterfactual_guidance"]:
                    st.write(f"- {item}")
    for reason in decision.reasons:
        st.write(f"- {reason}")

    st.subheader("Officer final action")
    override = st.selectbox("Officer final action", ["Pending review", "Approve", "Refer for more documents", "Decline"])
    rationale = st.text_area("Officer rationale", placeholder="Record the final decision and supporting evidence.")
    expected_action = {
        "Meets indicative affordability criteria": "Approve",
        "Manual review": "Refer for more documents",
        "Refer for additional documents": "Refer for more documents",
        "Does not meet indicative affordability criteria": "Decline",
    }.get(decision.recommendation)
    is_override = override not in {"Pending review", expected_action}
    if is_override and not rationale.strip():
        st.warning("A rationale is required when the officer overrides the system recommendation.")

    quality_score = st.session_state.quality_report.score if st.session_state.quality_report else None
    model_version = "Not available"
    if HOME_CREDIT_METRICS_PATH.exists():
        model_version = str(load_metrics(HOME_CREDIT_METRICS_PATH, HOME_CREDIT_METRICS_PATH.stat().st_mtime_ns).get("model_name", "Home Credit benchmark"))
    with st.container(border=True):
        st.subheader("Decision summary")
        st.table({
            "Applicant ID": applicant_id or "Not supplied",
            "Requested amount": f"₹{requested_amount:,.0f}",
            "Statement-quality score": f"{quality_score:.0%}" if quality_score is not None else "Not available",
            "Affordability score": f"{decision.affordability_score}/100" if decision.affordability_score is not None else "Not available",
            "Bureau default risk": f"{bureau_prob:.1%}" if bureau_prob is not None else "Not evaluated",
            "System recommendation": decision.recommendation,
            "Officer action": override,
            "Rule version": decision.rule_version or "Not available",
            "Home Credit model": model_version,
        })
        if decision.affordability_score is not None:
            summary_rows = build_case_summary_rows(
                st.session_state.features or {}, st.session_state.quality_report, decision,
                requested_amount, proposed_emi, applicant_id,
            )
            st.download_button(
                "Download decision summary CSV", safe_export_csv(summary_rows),
                "decision_summary.csv", "text/csv",
            )
    can_create_record = consent and override != "Pending review" and (not is_override or bool(rationale.strip()))
    if not consent:
        st.info("Confirm applicant consent and choose an officer action to create a decision record.")
    if st.button("Create decision record", disabled=not can_create_record):
        base_record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "applicant_id": applicant_id or None,
            "requested_amount": requested_amount,
            "loan_tenure_months": loan_tenure_months,
            "indicative_annual_interest_rate": annual_interest_rate,
            "estimated_proposed_emi": proposed_emi,
            "statement_quality_score": quality_score,
            "officer": officer_name or None,
            "consent_confirmed": consent,
            "system_recommendation": decision.recommendation,
            "officer_action": override,
            "officer_rationale": rationale,
            "statement_features": st.session_state.features,
            "affordability_score": decision.affordability_score,
            "affordability_components": decision.affordability_components,
            "model_probability": bureau_prob,
            "pillar_summary": decision.pillar_summary,
            "system_reasons": decision.reasons,
            "category_overrides": category_override_records(st.session_state.statement),
            "rule_version": decision.rule_version,
            "home_credit_model_version": model_version,
            "model_available": Path(MODEL_PATH).exists(),
        }
        record = build_decision_record(base_record, decision, st.session_state.quality_report)
        saved_meta = save_case_record(record)
        st.markdown(
            f"""
            <div class="spotify-card" style="border-left: 4px solid #1DB954; margin-top: 1rem;">
                <div style="display:flex; align-items:center; gap: 0.5rem; margin-bottom: 4px;">
                    <span class="badge-pill badge-pill-green">Cryptographically Sealed</span>
                    <span style="font-weight:700; color:#FFFFFF;">Case ID: {saved_meta['case_id']}</span>
                </div>
                <div style="font-family: monospace; font-size: 0.8rem; color: #B3B3B3;">
                    SHA-256 Digest: {saved_meta['record_hash'][:24]}... (Anchored to HEAD_HASH)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.download_button("Download decision record", data=pd.Series(record).to_json(indent=2), file_name="decision_record.json", mime="application/json")

    with st.expander("Database Audit Trail & Tamper Verification (SQLite)", expanded=False):
        col_btn, col_res = st.columns([1, 3])
        if col_btn.button("Verify Hash Chain"):
            valid, msg = verify_hash_chain()
            if valid:
                col_res.markdown(f'<span class="badge-pill badge-pill-green">Chain Verified</span> {msg}', unsafe_allow_html=True)
            else:
                col_res.markdown(f'<span class="badge-pill badge-pill-red">Tamper Detected</span> {msg}', unsafe_allow_html=True)
        recent_cases = get_case_records(limit=10)
        if recent_cases:
            st.caption("Recent sealed case records in SQLite database:")
            st.dataframe(
                pd.DataFrame([
                    {
                        "Case ID": r["case_id"],
                        "Timestamp": r["timestamp_utc"][:19] if r["timestamp_utc"] else "-",
                        "Applicant": r["applicant_id"] or "N/A",
                        "Requested": f"INR {r['requested_amount']:,.0f}" if r["requested_amount"] else "-",
                        "Score": f"{r['affordability_score']}/100" if r["affordability_score"] is not None else "-",
                        "Bureau PD": f"{r['bureau_probability']:.1%}" if r["bureau_probability"] is not None else "-",
                        "Recommendation": r["system_recommendation"],
                        "Officer Action": r["officer_action"],
                        "Record Hash": r["record_hash"][:12] + "...",
                    }
                    for r in recent_cases
                ]),
                hide_index=True,
            )
        else:
            st.info("No cases sealed in SQLite database yet.")
