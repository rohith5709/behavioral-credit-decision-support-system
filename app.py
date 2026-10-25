"""Modern Fintech Risk Intelligence UI - Streamlit frontend."""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
import json
from pathlib import Path

import pandas as pd
import streamlit as st

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
from src.models.behavioral_unsupervised import score_behavioral_profile
from src.data.db import init_db, save_case_record, get_case_records, verify_hash_chain

# Initialize SQLite database for decision records
init_db()

st.set_page_config(
    page_title="Credit Decision Support | Sound Risk Intelligence",
    page_icon="SOUND",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Clean, Futuristic Dark Fintech Styling ──────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    code, kbd, samp, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Core Canvas */
    .stApp {
        background-color: #0B0E14 !important;
        color: #E2E8F0 !important;
    }
    .main .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 3rem !important;
        max-width: 1440px !important;
    }

    /* Header Bar */
    .top-nav-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #111726;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 0.9rem 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    .top-nav-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .top-nav-logo {
        width: 32px;
        height: 32px;
        background: linear-gradient(135deg, #10B981, #047857);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        font-weight: 800;
        font-size: 0.85rem;
        letter-spacing: -0.05em;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
    }
    .top-nav-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.2;
    }
    .top-nav-sub {
        font-size: 0.75rem;
        color: #64748B;
        margin: 0;
    }
    .top-nav-badges {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Status Pills */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        font-family: 'JetBrains Mono', monospace;
    }
    .status-pill-green {
        background: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-pill-blue {
        background: rgba(59, 130, 246, 0.12);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }
    .status-pill-amber {
        background: rgba(245, 158, 11, 0.12);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .status-pill-red {
        background: rgba(239, 68, 68, 0.12);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0E131F !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #F8FAFC !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stSidebar"] label {
        color: #94A3B8 !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #111726;
        padding: 5px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px !important;
        color: #94A3B8 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        padding: 8px 14px !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.15s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #34D399 !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: #111726 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 0.9rem 1.1rem !important;
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        border-color: rgba(16, 185, 129, 0.35) !important;
        transform: translateY(-1px);
    }
    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetricValue"] {
        color: #F8FAFC !important;
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }

    /* Form Controls & Inputs */
    [data-baseweb="input"] > div,
    [data-baseweb="select"] > div:first-child,
    [data-baseweb="textarea"] > div {
        background-color: #141B2D !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #F8FAFC !important;
    }
    [data-baseweb="input"] > div:focus-within,
    [data-baseweb="select"] > div:first-child:focus-within {
        border-color: #10B981 !important;
        box-shadow: 0 0 0 1px #10B981 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #10B981, #059669) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        border: none !important;
        font-size: 0.82rem !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #059669, #047857) !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4) !important;
        transform: translateY(-1px);
    }

    /* Decision Matrix Policy Cards */
    .policy-quadrant-card {
        background: #111726;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease;
    }
    .policy-quadrant-card-active {
        border: 2px solid #10B981 !important;
        background: rgba(16, 185, 129, 0.08) !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.2) !important;
    }

    /* Container Borders */
    [data-testid="stExpander"] {
        background: #111726 !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 10px !important;
    }

    /* Tables & Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Clean Production Navigation Bar ─────────────────────────────────────────────
st.markdown(
    """
    <div class="top-nav-bar">
        <div class="top-nav-brand">
            <div class="top-nav-logo">CD</div>
            <div>
                <div class="top-nav-title">Behavioral Credit Decision Support System</div>
                <div class="top-nav-sub">Dual-Pillar Risk Intelligence &middot; Cash Flow Engine + LightGBM Benchmark</div>
            </div>
        </div>
        <div class="top-nav-badges">
            <span class="status-pill status-pill-green">ENGINE ONLINE</span>
            <span class="status-pill status-pill-blue">DPDP ACT 2023</span>
            <span class="status-pill status-pill-blue">SHA-256 LEDGER</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
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
    st.markdown("### Underwriting Console")
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

    st.markdown("### Loan Request")
    applicant_id = st.text_input("Applicant ID", value=default_app_id)
    requested_amount = st.number_input("Requested loan amount (INR)", min_value=0.0, value=default_req_amt, step=10_000.0)
    loan_tenure_months = st.number_input("Requested loan tenure (months)", min_value=1, value=default_tenure, step=1)
    annual_interest_rate = st.number_input("Indicative annual interest rate (%)", min_value=0.0, value=default_rate, step=0.5)
    declared_emi = st.number_input("Declared monthly EMI (INR)", min_value=0.0, value=default_decl_emi, step=1_000.0)
    officer_name = st.text_input("Reviewing officer", placeholder="Loan officer name")
    consent = st.checkbox("Applicant consent for analysis confirmed", value=True)

    monthly_rate = annual_interest_rate / 1200
    proposed_emi = (
        requested_amount / loan_tenure_months
        if monthly_rate == 0 else requested_amount * monthly_rate * (1 + monthly_rate) ** loan_tenure_months / ((1 + monthly_rate) ** loan_tenure_months - 1)
    ) if requested_amount else 0.0
    st.caption(f"Estimated proposed EMI: **INR {proposed_emi:,.0f} / month**")

    with st.expander("Bureau Profile (Pillar 2)", expanded=True):
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
    "1. Case summary",
    "2. Upload statement",
    "3. Behaviour profile",
    "4. Illustrative synthetic data",
    "5. ML benchmark (separate)",
    "6. Officer decision",
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

        # Primary Gauge & Status Summary
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
            rec_pill_class = (
                "status-pill-green" if "Meets" in decision.recommendation
                else "status-pill-amber" if "Review" in decision.recommendation or "Refer" in decision.recommendation
                else "status-pill-red"
            )
            st.markdown(
                f"""
                <div style="background:#111726; border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:1.25rem 1.4rem; height:190px; display:flex; flex-direction:column; justify-content:center;">
                    <div style="font-size:0.72rem; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8; margin-bottom:8px;">
                        System Recommendation
                    </div>
                    <div>
                        <span class="status-pill {rec_pill_class}" style="font-size:0.85rem; padding: 5px 12px;">
                            {decision.recommendation}
                        </span>
                    </div>
                    <div style="font-size:0.82rem; color:#94A3B8; margin-top:12px; line-height:1.45;">
                        {status_message}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Core Financial Position Metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        surplus_before = st.session_state.features['monthly_surplus']
        surplus_after = st.session_state.features['post_loan_monthly_surplus']
        surplus_delta = surplus_after - surplus_before

        col_m1.metric("Monthly surplus (before loan)", f"INR {surplus_before:,.0f}")
        col_m2.metric("Estimated proposed EMI", f"INR {proposed_emi:,.0f}")
        col_m3.metric(
            "Monthly surplus (after loan)",
            f"INR {surplus_after:,.0f}",
            delta=f"INR {surplus_delta:,.0f}",
            delta_color="normal",
        )

        review_flags = extract_review_flags(decision.reasons)
        with st.container(border=True):
            st.markdown("#### Officer Review Checklist")
            if review_flags:
                for flag in review_flags:
                    st.markdown(f"- <span style='color:#F87171;'>[ACTION REQUIRED]</span> {flag}", unsafe_allow_html=True)
            else:
                st.markdown("<span style='color:#34D399;'>[OK]</span> No mandatory evidence safeguard is currently triggered. Officer review remains required per policy.", unsafe_allow_html=True)

        with st.expander("Case-summary evidence table", expanded=True):
            case_summary = build_case_summary_rows(
                st.session_state.features, quality, decision, requested_amount, proposed_emi, applicant_id
            )
            st.dataframe(case_summary, hide_index=True, use_container_width=True)
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
    st.caption("Required: date, description, and either debit/credit or one signed amount column. Optional: closing balance.")
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
                    st.dataframe(preview.head(10), hide_index=True, use_container_width=True)
        except (ValueError, pd.errors.ParserError) as error:
            st.error(str(error))

    st.markdown("#### Optional: Salary slip cross-verification")
    slip_col1, slip_col2 = st.columns(2)
    slip_salary = slip_col1.number_input("Salary slip net pay (INR)", min_value=0.0, step=5_000.0)
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
            st.markdown("#### Statement data quality")
            quality_columns = st.columns(4)
            quality_columns[0].metric("Quality score", f"{quality_report.score:.0%}")
            quality_columns[1].metric("Observed months", quality_report.observed_months)
            quality_columns[2].metric("Valid / rejected", f"{quality_report.valid_transactions} / {quality_report.rejected_rows}")
            quality_columns[3].metric("Duplicate rows removed", quality_report.duplicate_rows_removed)
            st.caption(f"Date range: {quality_report.date_range_start or 'Not available'} to {quality_report.date_range_end or 'Not available'}")
            for warning in quality_report.warnings:
                st.warning(warning)

        st.markdown("#### Categorised transactions")
        st.caption("Review uncertain categories before using the summary. An override preserves the initial category, reviewer, rationale, and UTC timestamp in this prototype case record.")
        editable = st.session_state.statement.copy()
        editable["officer_category"] = editable["category"]
        if "category_override_rationale" not in editable:
            editable["category_override_rationale"] = ""
        editable["category_reviewer"] = officer_name or "Not supplied"
        edited = st.data_editor(
            editable,
            key="category_review",
            hide_index=True,
            use_container_width=True,
            disabled=[column for column in editable.columns if column not in {"officer_category", "category_override_rationale"}],
            column_config={"officer_category": st.column_config.SelectboxColumn("Officer category", options=list(CATEGORY_OPTIONS))},
        )
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
        export_columns[0].download_button("Download cleaned CSV", safe_export_csv(st.session_state.statement), "cleaned_transactions.csv", "text/csv")
        export_columns[1].download_button("Download categorised CSV", safe_export_csv(st.session_state.statement), "categorised_transactions.csv", "text/csv")
        export_columns[2].download_button("Download features CSV", safe_export_csv(pd.DataFrame([st.session_state.features])), "behavioural_features.csv", "text/csv")
        export_decision = recommend(None, st.session_state.features, quality_report=st.session_state.quality_report)
        export_columns[3].download_button(
            "Download score breakdown CSV",
            safe_export_csv(pd.DataFrame([{"component": label, "points": points} for label, points in (export_decision.affordability_components or {}).items()])),
            "affordability_score_breakdown.csv",
            "text/csv",
        )

with tab_profile:
    st.subheader("Behavioural and affordability indicators")
    if st.session_state.features is None:
        st.info("Upload and analyse a bank statement first.")
    else:
        features = st.session_state.features

        # Unsupervised Machine Learning Behavioral Persona & Anomaly Intelligence
        behavioral_ml = score_behavioral_profile(features)
        if behavioral_ml.get("status") == "scored":
            persona = behavioral_ml["behavioral_persona"]
            anomaly = behavioral_ml["anomaly_detection"]
            with st.container(border=True):
                st.markdown("#### Unsupervised Behavioral ML Intelligence (K-Means & Isolation Forest)")
                ml_col1, ml_col2 = st.columns([1.5, 1])
                with ml_col1:
                    st.markdown(
                        f"""
                        <div style="background:#111726; border-left:4px solid {persona['color']}; border-radius:8px; padding:1rem 1.2rem; margin-bottom:0.5rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8;">Behavioral Spending Persona</span>
                                <span class="status-pill" style="background:{persona['color']}22; color:{persona['color']}; border:1px solid {persona['color']}55;">
                                    {persona['risk_profile']} &middot; {persona['fit_confidence']:.0%} Fit
                                </span>
                            </div>
                            <div style="font-size:1.15rem; font-weight:800; color:#F8FAFC; margin-top:4px;">
                                {persona['name']}
                            </div>
                            <div style="font-size:0.8rem; color:#94A3B8; margin-top:4px; line-height:1.4;">
                                {persona['archetype']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with ml_col2:
                    anom_color = "#EF4444" if anomaly["is_anomaly"] else "#10B981"
                    st.markdown(
                        f"""
                        <div style="background:#111726; border-left:4px solid {anom_color}; border-radius:8px; padding:1rem 1.2rem; margin-bottom:0.5rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.06em; color:#94A3B8;">Isolation Forest Anomaly Check</span>
                                <span class="status-pill" style="background:{anom_color}22; color:{anom_color}; border:1px solid {anom_color}55;">
                                    Score: {anomaly['anomaly_score']:.2f}
                                </span>
                            </div>
                            <div style="font-size:1.05rem; font-weight:800; color:#F8FAFC; margin-top:4px;">
                                {anomaly['verdict']}
                            </div>
                            <div style="font-size:0.8rem; color:#94A3B8; margin-top:4px; line-height:1.4;">
                                {'Elevated non-linear deviation detected in spending or withdrawal pattern.' if anomaly['is_anomaly'] else 'Transaction distribution is consistent with typical peer cohorts.'}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with st.container(border=True):
            st.markdown("#### Primary Monthly Cash Flow Indicators")
            r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
            r1_c1.metric("Average monthly income", f"INR {features['average_monthly_income']:,.0f}")
            r1_c2.metric("Other statement credits", f"INR {features['other_statement_credits']:,.0f}")
            r1_c3.metric("Average monthly expense", f"INR {features['average_monthly_expense']:,.0f}")
            r1_c4.metric("Monthly surplus", f"INR {features['monthly_surplus']:,.0f}")

        with st.container(border=True):
            st.markdown("#### Financial Health Ratios & Volatility")
            r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
            r2_c1.metric("Savings ratio", f"{features['savings_ratio']:.1%}")
            r2_c2.metric("EMI-to-income ratio", f"{features['emi_to_income_ratio']:.1%}")
            r2_c3.metric("Income variation", f"{features['income_variation_ratio']:.1%}")
            r2_c4.metric("Expense variation", f"{features['expense_variation_ratio']:.1%}")

        with st.container(border=True):
            st.markdown("#### Debt Capacity & Buffer Indicators")
            r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
            r3_c1.metric("Salary frequency", str(features["salary_frequency"]).title())
            emergency_buffer = f"{features['emergency_buffer_months']:.1f} months" if features["has_balance_history"] else "Not available"
            emi_after_loan = f"{features['proposed_emi_to_income_ratio']:.1%}" if features["average_monthly_income"] else "Not available"
            r3_c2.metric("Emergency buffer", emergency_buffer)
            r3_c3.metric("Post-loan EMI burden", emi_after_loan)
            r3_c4.metric("EMI evidence", "Check required" if features["emi_difference_amount"] >= 1_000 and features["emi_discrepancy_ratio"] > 0.20 else "Consistent")

        if features["partial_boundary_month"]:
            st.warning("The first or last statement month appears partial. Trend metrics are withheld to avoid over-interpreting incomplete months.")

        monthly_summary = st.session_state.monthly_summary
        category_summary = st.session_state.category_summary
        filter_columns = st.columns(2)
        selected_months = filter_columns[0].multiselect("Months to display", monthly_summary["month"].tolist(), default=monthly_summary["month"].tolist())
        selected_categories = filter_columns[1].multiselect("Categories to display", category_summary["Category"].tolist(), default=category_summary["Category"].tolist())
        transaction_search = st.text_input("Search transactions", placeholder="Search a merchant, payment, or description")
        filtered_monthly = monthly_summary[monthly_summary["month"].isin(selected_months)]
        filtered_categories = category_summary[category_summary["Category"].isin(selected_categories)]

        with st.container(border=True):
            st.markdown("#### Monthly Cash Flow Trajectory")
            cash_flow_chart = filtered_monthly[["month", "income", "expense", "surplus"]].rename(columns={
                "income": "Income", "expense": "Expense", "surplus": "Surplus",
            })
            st.line_chart(cash_flow_chart, x="month", y=["Income", "Expense", "Surplus"])
            st.dataframe(filtered_monthly[["month", "income", "expense", "surplus", "closing_balance"]], hide_index=True, use_container_width=True)

        chart_left, chart_right = st.columns(2)
        with chart_left:
            with st.container(border=True):
                st.markdown("#### Spending by Category")
                st.bar_chart(filtered_categories, x="Category", y="Expense")
        with chart_right:
            with st.container(border=True):
                st.markdown("#### Behavioral Risk Signals")
                indicators = pd.DataFrame({
                    "Signal": [
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
                    "Observed Value": [
                        format_percent(features['salary_income_share']),
                        f"{features['essential_expense_ratio']:.1%}",
                        f"{features['discretionary_expense_ratio']:.1%}",
                        f"{features['utility_payment_regularity']:.1%}",
                        f"{features['cash_withdrawals_per_month']:.1f}",
                        f"{features['low_balance_day_count']:.0f}",
                        f"{features['large_spending_count']:.0f}",
                        f"{features['missed_salary_months']:.0f}",
                        f"{features['uncertain_transaction_share']:.1%}",
                        f"INR {features['post_loan_monthly_surplus']:,.0f}",
                    ],
                })
                st.dataframe(indicators, hide_index=True, use_container_width=True)

        searched_transactions = st.session_state.statement.copy()
        if transaction_search.strip():
            searched_transactions = searched_transactions[
                searched_transactions["description"].astype(str).str.contains(transaction_search, case=False, na=False)
            ]
        with st.expander("Searchable transaction ledger"):
            st.dataframe(searched_transactions, hide_index=True, use_container_width=True)

with tab_portfolio:
    st.subheader("Synthetic behavioural portfolio")
    if not SYNTHETIC_FEATURES_PATH.exists():
        st.info("Import Bank Data Simulator output to view the synthetic portfolio here.")
    else:
        portfolio = load_synthetic_portfolio(SYNTHETIC_FEATURES_PATH, SYNTHETIC_FEATURES_PATH.stat().st_mtime_ns)
        metric_columns = st.columns(3)
        metric_columns[0].metric("Synthetic profiles", f"{len(portfolio):,}")
        metric_columns[1].metric("Behavioural fields", len(portfolio.columns) - 2)
        metric_columns[2].metric("Latest snapshot", str(portfolio.iloc[-1, 1]) if portfolio.shape[1] > 1 else "Available")
        behavioural_columns = [
            column for column in portfolio.select_dtypes(include="number").columns if column != "customer_id"
        ]
        st.bar_chart(portfolio[behavioural_columns].mean().rename("Average").reset_index(), x="index", y="Average")
        st.dataframe(portfolio.head(100), hide_index=True, use_container_width=True)

with tab_validation:
    st.subheader("Home Credit default-risk model (Pillar 2 Benchmark)")
    if not HOME_CREDIT_METRICS_PATH.exists() or not HOME_CREDIT_MODEL_PATH.exists():
        st.info("Train the Home Credit model to display held-out evaluation metrics.")
    else:
        metrics = load_metrics(HOME_CREDIT_METRICS_PATH, HOME_CREDIT_METRICS_PATH.stat().st_mtime_ns)
        final_test = metrics.get("final_test_metrics", metrics)
        protocol = metrics.get("evaluation_protocol", {})
        display_recall = final_test.get("recall", final_test.get("recall_at_0_50", 0.0))
        display_precision = final_test.get("precision", final_test.get("precision_at_0_50", 0.0))

        metric_columns = st.columns(4)
        metric_columns[0].metric("Final-test ROC-AUC", f"{final_test['roc_auc']:.3f}")
        metric_columns[1].metric("Final-test PR-AUC", f"{final_test['pr_auc']:.3f}")
        metric_columns[2].metric(f"Recall ({final_test.get('threshold', 0.50):.2f})", f"{display_recall:.1%}")
        metric_columns[3].metric(f"Precision ({final_test.get('threshold', 0.50):.2f})", f"{display_precision:.1%}")

        st.caption(
            f"Selected model: **{metrics['model_name']}** ({metrics['feature_count']} features). "
            f"Brier score: {final_test['brier_score']:.3f}. Evaluated on {protocol.get('test_rows', final_test.get('test_rows', 'Not available')):,} held-out test applicants."
        )

        importance_path = Path("reports/home_credit_global_importance.json")
        if importance_path.exists():
            from src.models.explain_home_credit import explain_local_factors
            st.markdown("#### Explainable Risk Factor Attribution (Exact Tree-SHAP)")
            st.caption("Path-dependent Shapley values computed via LightGBM booster. Features with positive SHAP push predicted risk higher, while negative values act as protective buffers.")

            if st.session_state.get("bureau_result") and "local_explanations" in st.session_state.bureau_result:
                local_exp = st.session_state.bureau_result["local_explanations"]
                st.info(f"Displaying Tree-SHAP attributions for active applicant profile (CIBIL: {cibil_score}, Age: {applicant_age}).")
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
                    st.write(f"- <span style='color:#F87171;'>{r['feature']}</span>: {r['impact']}", unsafe_allow_html=True)
            with c_prot:
                st.markdown("**Top protective factors (Negative SHAP):**")
                for p in local_exp["top_risk_decreasing_factors"]:
                    st.write(f"- <span style='color:#34D399;'>{p['feature']}</span>: {p['impact']}", unsafe_allow_html=True)

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
        st.info("Upload and analyse a bank statement to generate an affordability assessment.")
    else:
        if decision.pillar_summary and decision.pillar_summary.get("mode", "").startswith("Dual-Pillar"):
            with st.container(border=True):
                st.markdown("#### Unified Dual-Pillar Credit Evaluation Matrix")
                col_p1, col_p2, col_q = st.columns(3)
                col_p1.metric(
                    "Pillar 1: Statement Affordability",
                    f"{decision.affordability_score} / 100",
                    decision.pillar_summary.get("affordability_band", ""),
                )
                col_p2.metric(
                    "Pillar 2: Bureau Default Risk",
                    f"{bureau_prob:.1%}",
                    f"{decision.pillar_summary.get('bureau_risk_band', '')} (Completeness: {completeness_pct})",
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
                    card_border = "policy-quadrant-card-active" if is_active else ""
                    st.markdown(
                        f"""
                        <div class="policy-quadrant-card {card_border}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#34D399;">Q1: Meets Indicative Criteria</b>
                                <span class="status-pill status-pill-green">{'ACTIVE PLACEMENT' if is_active else 'Score ≥ 70 & PD < 20%'}</span>
                            </div>
                            <div style="font-size:0.8rem; color:#94A3B8; margin-top:6px;">
                                Robust statement cash-flow surplus accompanied by acceptable external credit bureau default risk.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with q_row1_col2:
                    is_active = active_quad == "Quadrant 2"
                    card_border = "policy-quadrant-card-active" if is_active else ""
                    st.markdown(
                        f"""
                        <div class="policy-quadrant-card {card_border}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#FBBF24;">Q2: Manual Review (Bureau Risk)</b>
                                <span class="status-pill status-pill-amber">{'ACTIVE PLACEMENT' if is_active else 'Score ≥ 70 & PD ≥ 20%'}</span>
                            </div>
                            <div style="font-size:0.8rem; color:#94A3B8; margin-top:6px;">
                                Statement surplus appears viable, but external trade lines or delinquency history signal elevated default risk.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                q_row2_col1, q_row2_col2 = st.columns(2)
                with q_row2_col1:
                    is_active = active_quad == "Quadrant 3"
                    card_border = "policy-quadrant-card-active" if is_active else ""
                    st.markdown(
                        f"""
                        <div class="policy-quadrant-card {card_border}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#FBBF24;">Q3: Manual Review (Cashflow Alert)</b>
                                <span class="status-pill status-pill-amber">{'ACTIVE PLACEMENT' if is_active else 'Score < 70 & PD < 20%'}</span>
                            </div>
                            <div style="font-size:0.8rem; color:#94A3B8; margin-top:6px;">
                                Clean bureau history, but statement indicates thin cash reserves, volatile income, or heavy expense burden.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with q_row2_col2:
                    is_active = active_quad == "Quadrant 4"
                    card_border = "policy-quadrant-card-active" if is_active else ""
                    st.markdown(
                        f"""
                        <div class="policy-quadrant-card {card_border}">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <b style="color:#F87171;">Q4: Decline (Dual Risk Elevation)</b>
                                <span class="status-pill status-pill-red">{'ACTIVE PLACEMENT' if is_active else 'Score < 70 & PD ≥ 20%'}</span>
                            </div>
                            <div style="font-size:0.8rem; color:#94A3B8; margin-top:6px;">
                                Depleted cash flow and high debt obligations compounded by elevated external credit default risk.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            decision_columns = st.columns(2)
            decision_columns[0].metric("Behavioural affordability score", f"{decision.affordability_score} / 100")
            decision_columns[1].metric("System recommendation", decision.recommendation)

        if st.session_state.get("salary_verification"):
            sv = st.session_state.salary_verification
            if sv.is_verified:
                st.success(f"Cross-document salary verification: {sv.status}")
            else:
                st.warning(f"Cross-document salary safeguard: {sv.status} (Declared: INR {sv.slip_net_salary:,.0f} vs Statement: INR {sv.detected_statement_salary:,.0f})")

        st.caption(f"Rule version: {decision.rule_version}. Policy safeguards override numerical scores when evidence is contradictory or incomplete.")

        with st.container(border=True):
            st.markdown("#### Affordability Score Component Breakdown")
            comp_cols = st.columns(2)
            comps = list((decision.affordability_components or {}).items())
            mid = len(comps) // 2
            with comp_cols[0]:
                for comp, pts in comps[:mid]:
                    pts_color = "#34D399" if pts >= 0 else "#F87171"
                    sign = "+" if pts >= 0 else ""
                    st.markdown(
                        f"<div style='display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.04);'>"
                        f"<span style='color:#94A3B8; font-size:0.82rem;'>{comp.replace('_', ' ').title()}</span>"
                        f"<span style='color:{pts_color}; font-weight:700; font-family:monospace;'>{sign}{pts:.1f} pts</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
            with comp_cols[1]:
                for comp, pts in comps[mid:]:
                    pts_color = "#34D399" if pts >= 0 else "#F87171"
                    sign = "+" if pts >= 0 else ""
                    st.markdown(
                        f"<div style='display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.04);'>"
                        f"<span style='color:#94A3B8; font-size:0.82rem;'>{comp.replace('_', ' ').title()}</span>"
                        f"<span style='color:{pts_color}; font-weight:700; font-family:monospace;'>{sign}{pts:.1f} pts</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        if st.session_state.features:
            metrics_actionable = calculate_actionable_affordability_metrics(
                st.session_state.features,
                loan_tenure_months=int(loan_tenure_months),
                annual_interest_rate=float(annual_interest_rate),
            )
            with st.expander("Actionable loan metrics, stress scenarios & counterfactuals", expanded=True):
                col_a, col_b = st.columns(2)
                col_a.metric("Max sustainable EMI", f"INR {metrics_actionable['max_sustainable_monthly_emi']:,.0f}")
                col_b.metric("Max indicative loan", f"INR {metrics_actionable['max_indicative_loan_amount']:,.0f}")
                st.caption(f"Stress baseline (Income -20%, Expense +10%, Rate +2%): Stressed max loan = INR {metrics_actionable['stressed_max_indicative_loan']:,.0f}")

                st.markdown("#### Scenario Shock & Stress Testing Lab")
                col_s1, col_s2, col_s3 = st.columns(3)
                shock_inc = col_s1.slider("Income Shock", min_value=-50, max_value=0, value=-20, step=5, format="%d%%", key="slider_shock_inc")
                shock_exp = col_s2.slider("Expense Inflation", min_value=0, max_value=50, value=10, step=5, format="+%d%%", key="slider_shock_exp")
                shock_rate = col_s3.slider("Interest Rate Hike", min_value=0.0, max_value=6.0, value=2.0, step=0.5, format="+%.1f%%", key="slider_shock_rate")

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
                    f"INR {st_surplus:,.0f}",
                    delta=f"{st_surplus - feat['monthly_surplus']:,.0f}",
                )
                col_res2.metric(
                    "Stressed Max Sustainable EMI",
                    f"INR {st_max_emi:,.0f}",
                    delta=f"{st_max_emi - metrics_actionable['max_sustainable_monthly_emi']:,.0f}",
                )
                base_loan = metrics_actionable['max_indicative_loan_amount']
                retention_pct = (st_max_loan / base_loan) if base_loan > 0 else 0.0
                col_res3.metric(
                    "Stressed Loan Capacity",
                    f"INR {st_max_loan:,.0f}",
                    delta=f"{retention_pct:.0%} retention",
                )

                st.markdown("#### Counterfactual guidance")
                for item in metrics_actionable["counterfactual_guidance"]:
                    st.write(f"- {item}")

    st.markdown("#### Officer Final Action")
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
        st.markdown("#### Decision Summary")
        st.table({
            "Applicant ID": applicant_id or "Not supplied",
            "Requested amount": f"INR {requested_amount:,.0f}",
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
            <div style="background:#111726; border-left:4px solid #10B981; border-radius:8px; padding:1rem 1.2rem; margin-top:1rem;">
                <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                    <span class="status-pill status-pill-green">SEALED</span>
                    <span style="font-weight:700; color:#F8FAFC;">Case ID: {saved_meta['case_id']}</span>
                </div>
                <div style="font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#94A3B8;">
                    SHA-256 Digest: {saved_meta['record_hash'][:32]}... (Anchored to HEAD_HASH)
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
                col_res.markdown(f'<span class="status-pill status-pill-green">Chain Verified</span> {msg}', unsafe_allow_html=True)
            else:
                col_res.markdown(f'<span class="status-pill status-pill-red">Tamper Detected</span> {msg}', unsafe_allow_html=True)
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
                use_container_width=True,
            )
        else:
            st.info("No cases sealed in SQLite database yet.")
