"""Export global feature importance for the trained Home Credit model."""
from __future__ import annotations

import json

import joblib
import pandas as pd

from src.config import HOME_CREDIT_MODEL_PATH, REPORT_DIR


def export_global_importance(top_n: int = 15) -> pd.DataFrame:
    """Save LightGBM gain importance for the model-validation dashboard/report."""
    model_bundle = joblib.load(HOME_CREDIT_MODEL_PATH)
    values = model_bundle["classifier"].booster_.feature_importance(importance_type="gain")
    report = (
        pd.DataFrame({"feature": model_bundle["features"], "gain_importance": values})
        .sort_values("gain_importance", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    destination = REPORT_DIR / "home_credit_global_importance.json"
    destination.write_text(json.dumps(report.to_dict(orient="records"), indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    print(export_global_importance().to_string(index=False))
