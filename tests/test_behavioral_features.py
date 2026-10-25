"""Tests for the Statement-to-UCI Behavioral ML Feature Bridge.

Covers:
1. Exact output contract (columns, shape, non-null numeric floats).
2. Domain bounds enforcement (clipping of extreme negative/positive ratios).
3. Defensive handling of missing, None, and corrupted data types.
4. Monotonicity and directional validity across key financial stress signals.
5. Verification of the examiner-facing feature mapping metadata dictionary.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.features.behavioral_ml_features import (
    BEHAVIORAL_FEATURES,
    FEATURE_MAPPING_SPECS,
    get_feature_mapping_documentation,
    map_statement_to_behavioral_features,
)


@pytest.fixture
def baseline_statement_features() -> dict[str, object]:
    """Typical healthy salaried applicant feature dictionary."""
    return {
        "savings_ratio": 0.32,
        "emi_to_income_ratio": 0.18,
        "average_monthly_income": 85000.0,
        "average_monthly_expense": 58000.0,
        "income_variation_ratio": 0.05,
        "salary_consistency_ratio": 0.02,
        "utility_payment_regularity": 1.0,
        "low_balance_day_count": 0.0,
        "emergency_buffer_months": 3.5,
        "missed_salary_months": 0.0,
        "monthly_surplus": 27000.0,
        "minimum_monthly_surplus": 22000.0,
        "expense_variation_ratio": 0.09,
        "savings_trend_ratio": 0.04,
    }


class TestFeatureBridgeContract:
    def test_output_is_dataframe_with_single_row(self, baseline_statement_features):
        df = map_statement_to_behavioral_features(baseline_statement_features)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1

    def test_output_columns_match_behavioral_features_exactly(self, baseline_statement_features):
        df = map_statement_to_behavioral_features(baseline_statement_features)
        assert list(df.columns) == BEHAVIORAL_FEATURES

    def test_output_contains_zero_nans_or_infs(self, baseline_statement_features):
        df = map_statement_to_behavioral_features(baseline_statement_features)
        assert not df.isna().any().any(), "Found NaN in feature bridge output"
        assert not np.isinf(df.values).any(), "Found Inf in feature bridge output"

    def test_all_output_values_are_floats(self, baseline_statement_features):
        df = map_statement_to_behavioral_features(baseline_statement_features)
        for col in BEHAVIORAL_FEATURES:
            val = df[col].iloc[0]
            assert isinstance(val, (float, np.floating)), f"Column {col} is not float: {type(val)}"


class TestBoundaryAndClampingRules:
    def test_savings_ratio_clipped_to_bounds(self, baseline_statement_features):
        # Test negative clipping at -1.0
        neg_feats = baseline_statement_features.copy()
        neg_feats["savings_ratio"] = -3.5
        df_neg = map_statement_to_behavioral_features(neg_feats)
        assert df_neg["behaviour_payment_to_bill_ratio"].iloc[0] == -1.0

        # Test upper clipping at +2.0
        high_feats = baseline_statement_features.copy()
        high_feats["savings_ratio"] = 5.0
        df_high = map_statement_to_behavioral_features(high_feats)
        assert df_high["behaviour_payment_to_bill_ratio"].iloc[0] == 2.0

    def test_credit_utilisation_clipped_to_bounds(self, baseline_statement_features):
        feats = baseline_statement_features.copy()
        feats["emi_to_income_ratio"] = 4.2
        df = map_statement_to_behavioral_features(feats)
        assert df["behaviour_credit_utilisation"].iloc[0] == 2.0

        feats["emi_to_income_ratio"] = -0.5
        df2 = map_statement_to_behavioral_features(feats)
        assert df2["behaviour_credit_utilisation"].iloc[0] == 0.0

    def test_late_month_count_clamped_at_six(self, baseline_statement_features):
        feats = baseline_statement_features.copy()
        feats["low_balance_day_count"] = 280.0  # > 6 months of days
        df = map_statement_to_behavioral_features(feats)
        assert df["behaviour_late_month_count"].iloc[0] == 6.0

    def test_pay_delays_clamped_correctly(self, baseline_statement_features):
        feats = baseline_statement_features.copy()
        feats["salary_consistency_ratio"] = 10.0  # huge variation
        df = map_statement_to_behavioral_features(feats)
        assert df["PAY_0"].iloc[0] == 8.0  # Max bound

        feats["missed_salary_months"] = 12.0
        df2 = map_statement_to_behavioral_features(feats)
        assert df2["PAY_3"].iloc[0] == 6.0


class TestDefensiveRobustness:
    def test_completely_empty_dictionary_returns_clean_row(self):
        df = map_statement_to_behavioral_features({})
        assert len(df) == 1
        assert list(df.columns) == BEHAVIORAL_FEATURES
        assert not df.isna().any().any()
        assert not np.isinf(df.values).any()

    def test_corrupted_or_non_numeric_types_do_not_crash(self):
        corrupted = {
            "savings_ratio": "not_a_number",
            "emi_to_income_ratio": None,
            "average_monthly_income": [1, 2, 3],
            "low_balance_day_count": object(),
        }
        df = map_statement_to_behavioral_features(corrupted)
        assert len(df) == 1
        assert not df.isna().any().any()

    def test_zero_income_and_expense_do_not_divide_by_zero(self):
        zero_feats = {
            "average_monthly_income": 0.0,
            "average_monthly_expense": 0.0,
            "savings_ratio": 0.0,
            "emi_to_income_ratio": 0.0,
        }
        df = map_statement_to_behavioral_features(zero_feats)
        assert df["LIMIT_BAL"].iloc[0] == 0.0
        assert df["behaviour_average_bill"].iloc[0] == 0.0
        assert df["behaviour_average_payment"].iloc[0] == 0.0


class TestMonotonicDirectionality:
    def test_higher_salary_interruption_increases_pay_3(self, baseline_statement_features):
        f0 = baseline_statement_features.copy()
        f0["missed_salary_months"] = 0.0
        f2 = baseline_statement_features.copy()
        f2["missed_salary_months"] = 3.0

        d0 = map_statement_to_behavioral_features(f0)
        d2 = map_statement_to_behavioral_features(f2)
        assert d2["PAY_3"].iloc[0] > d0["PAY_3"].iloc[0]

    def test_utility_disruption_increases_pay_2(self, baseline_statement_features):
        f_clean = baseline_statement_features.copy()
        f_clean["utility_payment_regularity"] = 1.0
        f_poor = baseline_statement_features.copy()
        f_poor["utility_payment_regularity"] = 0.0

        d_clean = map_statement_to_behavioral_features(f_clean)
        d_poor = map_statement_to_behavioral_features(f_poor)
        assert d_poor["PAY_2"].iloc[0] > d_clean["PAY_2"].iloc[0]


class TestFeatureDocumentationMetadata:
    def test_metadata_covers_all_fifteen_features(self):
        specs = get_feature_mapping_documentation()
        assert set(specs.keys()) == set(BEHAVIORAL_FEATURES)

    def test_metadata_has_required_keys(self):
        specs = get_feature_mapping_documentation()
        for feat, info in specs.items():
            assert "statement_source" in info
            assert "description" in info
            assert "rationale" in info
            assert "bounds" in info
