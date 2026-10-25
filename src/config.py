"""Central project paths and decision-policy defaults."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
HOME_CREDIT_DIR = PROJECT_ROOT / "data" / "home_credit"
MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports"

MODEL_PATH = MODEL_DIR / "uci_logistic_regression.joblib"
METRICS_PATH = REPORT_DIR / "uci_metrics.json"
BEHAVIORAL_MODEL_PATH = MODEL_DIR / "behavioral_prediction_model.joblib"
BEHAVIORAL_METRICS_PATH = REPORT_DIR / "behavioral_prediction_metrics.json"
HOME_CREDIT_MODEL_PATH = MODEL_DIR / "home_credit_lightgbm.joblib"
HOME_CREDIT_METRICS_PATH = REPORT_DIR / "home_credit_metrics.json"
HOME_CREDIT_COMPARISON_PATH = REPORT_DIR / "home_credit_model_comparison.json"
HOME_CREDIT_THRESHOLD_PATH = REPORT_DIR / "home_credit_threshold_analysis.json"
HOME_CREDIT_CALIBRATION_PATH = REPORT_DIR / "home_credit_calibration.json"

LOW_RISK_THRESHOLD = 0.20
HIGH_RISK_THRESHOLD = 0.50
MAX_EMI_TO_INCOME = 0.50
MIN_EXTRACTION_CONFIDENCE = 0.80
