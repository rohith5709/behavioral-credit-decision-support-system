"""Streamlit interface for the decision-support prototype."""
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

st.set_page_config(page_title="Credit Decision Support", page_icon="💳", layout="wide")
st.title("Behavioral Credit Decision Support System")
st.caption("A prototype for human loan-officer review. It does not make final lending decisions.")

with st.sidebar:
    st.header("Applicant and request")
    applicant_id = st.text_input("Applicant ID", placeholder="APP-001")
    requested_amount = st.number_input("Requested loan amount", min_value=0.0, step=10_000.0)
    loan_tenure_months = st.number_input("Requested loan tenure (months)", min_value=1, value=24, step=1)
    annual_interest_rate = st.number_input("Indicative annual interest rate (%)", min_value=0.0, value=12.0, step=0.5)
    declared_emi = st.number_input("Declared monthly EMI", min_value=0.0, step=1_000.0)
    officer_name = st.text_input("Reviewing officer", placeholder="Officer name")
    consent = st.checkbox("Applicant consent for prototype analysis confirmed")
    monthly_rate = annual_interest_rate / 1200
    proposed_emi = (
        requested_amount / loan_tenure_months
        if monthly_rate == 0 else requested_amount * monthly_rate * (1 + monthly_rate) ** loan_tenure_months / ((1 + monthly_rate) ** loan_tenure_months - 1)
    ) if requested_amount else 0.0
    st.caption(f"Estimated new EMI: ₹{proposed_emi:,.0f}")

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
        with st.container(horizontal=True):
            st.metric("Data quality", f"{quality.score:.0%}", help="Completeness and consistency of the uploaded statement.", border=True)
            st.metric("Affordability score", f"{decision.affordability_score}/100", help="Transparent rule-based statement assessment.", border=True)
            st.metric("Recommendation", decision.recommendation, help="Officer-support recommendation, never a final lending decision.", border=True)
        with st.container(horizontal=True):
            st.metric("Before new loan surplus", f"₹{st.session_state.features['monthly_surplus']:,.0f}", border=True)
            st.metric("Estimated new EMI", f"₹{proposed_emi:,.0f}", border=True)
            st.metric("After new loan surplus", f"₹{st.session_state.features['post_loan_monthly_surplus']:,.0f}", border=True)
        st.subheader(f"{visual_status} status: {decision.recommendation}")
        st.caption(status_message)
        review_flags = extract_review_flags(decision.reasons)
        with st.container(border=True):
            st.subheader("Officer review checklist")
            if review_flags:
                for flag in review_flags:
                    st.write(f"- {flag}")
            else:
                st.write("- No mandatory evidence safeguard is currently triggered. Officer review remains required.")
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
    st.subheader("CSV bank statement")
    st.write("Required: date, description, and either debit/credit or one signed amount column. Optional: closing balance.")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    mapping: dict[str, str | None] | None = None
    opening_balance = None
    if uploaded:
        try:
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
    if uploaded and st.button("Analyse statement", type="primary"):
        try:
            statement, quality_report = parse_statement_csv(BytesIO(uploaded.getvalue()), column_mapping=mapping, opening_balance=opening_balance if opening_balance else None)
            statement = annotate_income_evidence(statement)
            apply_statement(statement, quality_report)
            st.success(f"Parsed {len(statement)} transactions. Data-quality score: {quality_report.score:.0%}")
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
            "This model uses Home Credit repayment and credit-history features; it is not applied directly to raw uploaded statements."
            f"Final test set: {protocol.get('test_rows', final_test.get('test_rows', 'Not available')):,} held-out applicants. "
            "Model, calibration, and threshold were selected on separate training/validation data. "
            "This model uses Home Credit repayment and credit-history features; it is not applied directly to raw uploaded statements."
            "This model uses Home Credit repayment and credit-history features; it is not applied directly to raw uploaded statements."
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
            st.subheader("Explainable risk factor attribution (Local drivers)")
            st.caption("Example attribution demonstrating top risk-increasing and protective factors translated into accessible business terms.")
            mock_applicant = {
                "EXT_SOURCE_3": 0.28,
                "EXT_SOURCE_2": 0.42,
                "DAYS_EMPLOYED": -650,
                "installment_days_late": 4.0,
            }
            local_exp = explain_local_factors(mock_applicant)
            c_risk, c_prot = st.columns(2)
            with c_risk:
                st.markdown("**Top risk-increasing factors:**")
                for r in local_exp["top_risk_increasing_factors"]:
                    st.write(f"- :red[{r['feature']}]: {r['impact']}")
            with c_prot:
                st.markdown("**Top protective factors:**")
                for p in local_exp["top_risk_decreasing_factors"]:
                    st.write(f"- :green[{p['feature']}]: {p['impact']}")

with tab_decision:
    st.subheader("Indicative assessment and officer review")
    if not consent:
        st.warning("Confirm applicant consent before recording a prototype recommendation.")
    decision = recommend(
        model_probability=None,
        statement_features=st.session_state.features,
        extraction_confidence=(st.session_state.quality_report.score if st.session_state.quality_report else None),
        quality_report=st.session_state.quality_report,
    )
    if decision.affordability_score is None:
        st.info("Upload and analyse a statement to generate an affordability assessment.")
    else:
        decision_columns = st.columns(2, border=True)
        decision_columns[0].metric("Behavioural affordability score", f"{decision.affordability_score}/100")
        decision_columns[1].metric("System recommendation", decision.recommendation)
        st.caption(f"Rule version: {decision.rule_version}. This is a transparent statement-based assessment, not the Home Credit risk model.")
        st.subheader("Score components")
        component_table = pd.DataFrame([
            {"Component": component, "Points": f"{points:.1f}"}
            for component, points in (decision.affordability_components or {}).items()
        ])
        st.dataframe(component_table, hide_index=True)
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
                st.subheader("Counterfactual guidance")
                for item in metrics_actionable["counterfactual_guidance"]:
                    st.write(f"- {item}")
    for reason in decision.reasons:
        st.write(f"- {reason}")
    st.info(
        "The Home Credit model is a separate benchmark evaluated on another dataset. "
        "It is not applied to raw uploaded statements with incompatible fields."
    )

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
            "system_reasons": decision.reasons,
            "category_overrides": category_override_records(st.session_state.statement),
            "rule_version": decision.rule_version,
            "home_credit_model_version": model_version,
            "model_available": Path(MODEL_PATH).exists(),
        }
        record = build_decision_record(base_record, decision, st.session_state.quality_report)
        st.download_button("Download decision record", data=pd.Series(record).to_json(indent=2), file_name="decision_record.json", mime="application/json")
