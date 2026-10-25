"""NLP Machine Learning model training pipeline for bank statement transaction categorisation."""
from __future__ import annotations

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, f1_score

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data" / "evaluation"
REPORTS_DIR = PROJECT_ROOT / "reports"

TRAINING_DATA_PATH = DATA_DIR / "nlp_training_transactions.csv"
MODEL_OUTPUT_PATH = MODELS_DIR / "transaction_nlp_pipeline.joblib"
METRICS_OUTPUT_PATH = REPORTS_DIR / "transaction_nlp_metrics.json"

# Core synthetic training seed templates across all categories
BASE_EXAMPLES = [
    # Salary/income
    ("ACME TECH SALARY CREDIT", "Salary/income"),
    ("INFOSYS LTD PAYROLL CR", "Salary/income"),
    ("MONTHLY SAL CR FOR OCT", "Salary/income"),
    ("TATA CONSULTANCY WAGES", "Salary/income"),
    ("STIPEND FOR INTERNSHIP", "Salary/income"),
    ("GOVT PENSION CREDIT", "Salary/income"),
    ("DIRECT DEP SALARY CORP", "Salary/income"),
    ("SALARY DIRECT ADVANCE", "Salary/income"),
    ("VETAN BHUGTAN MAHINA", "Salary/income"),
    ("TANKHAH SALARY CREDIT", "Salary/income"),
    ("NET PAYROLL DISBURSAL", "Salary/income"),
    ("EMPLOYER SALARY NEFT", "Salary/income"),
    ("SAL CR BATCH 90214", "Salary/income"),
    ("WIPRO TECHNOLOGIES SALARY", "Salary/income"),
    ("COGNIZANT PAYROLL CREDIT", "Salary/income"),

    # Rent
    ("HOUSE RENT FOR FLAT 402", "Rent"),
    ("MONTHLY RENT TRANSFER LANDLORD", "Rent"),
    ("APARTMENT LEASE PAYMENT", "Rent"),
    ("PAYMENT FOR HOUSE RENT", "Rent"),
    ("PG RENT ACCOMMODATION", "Rent"),
    ("MAKAN KIRAYA PAYMENT", "Rent"),
    ("RENT FOR OFFICE PREMISES", "Rent"),
    ("LANDLORD RENTAL CREDIT", "Rent"),
    ("RENT DEPOSIT PARTIAL", "Rent"),
    ("SOCIETY MAINTENANCE RENT", "Rent"),

    # EMI/loan repayment
    ("HDFC BANK HOME LOAN EMI", "EMI/loan repayment"),
    ("BAJAJ FINANCE AUTO LOAN", "EMI/loan repayment"),
    ("KOTAK PERSONAL LOAN INSTALMENT", "EMI/loan repayment"),
    ("CAR LOAN MONTHLY EMI DEBIT", "EMI/loan repayment"),
    ("EDUCATION LOAN REPAYMENT", "EMI/loan repayment"),
    ("SBI LOAN KIST ACH", "EMI/loan repayment"),
    ("IDFC FIRST LOAN DEDUCTION", "EMI/loan repayment"),
    ("TATA CAPITAL FINANCE EMI", "EMI/loan repayment"),
    ("ACH DEBIT MAHINDRA FINANCE", "EMI/loan repayment"),
    ("NACH HDFC LOAN SERVICE", "EMI/loan repayment"),
    ("LOAN INSTALMENT BOI", "EMI/loan repayment"),
    ("MUTHOOT FINANCE EMI", "EMI/loan repayment"),

    # Groceries
    ("DMART SUPERMARKET RETAIL", "Groceries"),
    ("BIG BASKET ONLINE GROCERY", "Groceries"),
    ("BLINKIT INSTANT DELIVERY", "Groceries"),
    ("ZEPTO GROCERY STORE", "Groceries"),
    ("JIOMART HYPERMARKET", "Groceries"),
    ("LOCAL KIRANA STORE VEGETABLES", "Groceries"),
    ("MOTHER DAIRY MILK BOOTH", "Groceries"),
    ("NATURES BASKET GOURMET", "Groceries"),
    ("RATION STORE PURCHASE", "Groceries"),
    ("RELIANCE FRESH RETAIL", "Groceries"),
    ("SPENCERS RETAIL GROCERY", "Groceries"),
    ("VEGETABLE VENDOR MANDI", "Groceries"),
    ("PROVISION STORE RETAIL", "Groceries"),

    # Transport/fuel
    ("INDIAN OIL PETROL PUMP", "Transport/fuel"),
    ("BHARAT PETROLEUM FUEL", "Transport/fuel"),
    ("HINDUSTAN PETROLEUM DIESEL", "Transport/fuel"),
    ("UBER TRIP RIDE FARE", "Transport/fuel"),
    ("OLA CABS COMMUTE", "Transport/fuel"),
    ("RAPIDO BIKE TAXI", "Transport/fuel"),
    ("IRCTC RAILWAY TICKET", "Transport/fuel"),
    ("FASTAG TOLL RECHARGE", "Transport/fuel"),
    ("SHELL FUEL STATION", "Transport/fuel"),
    ("METRO RAIL SMART CARD", "Transport/fuel"),
    ("AUTO RICKSHAW RIDE UPI", "Transport/fuel"),

    # Utilities
    ("BESCOM ELECTRICITY BILL", "Utilities"),
    ("TNEB POWER DISCOM PAYMENT", "Utilities"),
    ("MSEB ELECTRICITY CHARGES", "Utilities"),
    ("BWSSB WATER SUPPLY BILL", "Utilities"),
    ("INDANE GAS CYLINDER REFILL", "Utilities"),
    ("BHARAT GAS BOOKING", "Utilities"),
    ("ACT FIBERNET BROADBAND", "Utilities"),
    ("AIRTEL BROADBAND BILL", "Utilities"),
    ("JIO PREPAID RECHARGE MOBILE", "Utilities"),
    ("VI VODAFONE POSTPAID", "Utilities"),
    ("BSNL LANDLINE BILL", "Utilities"),
    ("BIJLI BOARD PAYMENT", "Utilities"),
    ("TATA PLAY DTH RECHARGE", "Utilities"),

    # Healthcare
    ("APOLLO PHARMACY MEDICAL", "Healthcare"),
    ("MEDPLUS CHEMIST DRUGS", "Healthcare"),
    ("1MG HEALTHCARE PHARMA", "Healthcare"),
    ("FORTIS HOSPITAL OPD CONSULT", "Healthcare"),
    ("MAX HEALTHCARE CLINIC", "Healthcare"),
    ("PATHOLOGY LAB TEST CHARGES", "Healthcare"),
    ("DENTAL CARE CLINIC", "Healthcare"),
    ("DR LAL PATHLABS TEST", "Healthcare"),
    ("NETMEDS MEDICINE ORDER", "Healthcare"),
    ("DAWA DUKAN MEDICINES", "Healthcare"),

    # Shopping/discretionary
    ("AMAZON INDIA MARKETPLACE", "Shopping/discretionary"),
    ("FLIPKART INTERNET RETAIL", "Shopping/discretionary"),
    ("MYNTRA FASHION APPAREL", "Shopping/discretionary"),
    ("ZOMATO FOOD DELIVERY", "Shopping/discretionary"),
    ("SWIGGY RESTAURANT ORDER", "Shopping/discretionary"),
    ("PVR CINEMAS MOVIE TICKET", "Shopping/discretionary"),
    ("STARBUCKS COFFEE CAFE", "Shopping/discretionary"),
    ("CAFE COFFEE DAY BEVERAGES", "Shopping/discretionary"),
    ("ZARA CLOTHING STORE", "Shopping/discretionary"),
    ("H&M RETAIL SHOPPING", "Shopping/discretionary"),
    ("NYKAA BEAUTY COSMETICS", "Shopping/discretionary"),
    ("BOOKMYSHOW ENTERTAINMENT", "Shopping/discretionary"),

    # Education
    ("DELHI PUBLIC SCHOOL FEES", "Education"),
    ("ST XAVIERS COLLEGE TUITION", "Education"),
    ("UNIVERSITY TERM SEMESTER FEE", "Education"),
    ("UDEMY ONLINE COURSE", "Education"),
    ("COURSERA SUBSCRIPTION", "Education"),
    ("ALLEN CAREER INSTITUTE", "Education"),
    ("FIITJEE COACHING CLASSES", "Education"),
    ("SCHOOL BUS TRANSPORT CHARGES", "Education"),
    ("SHIKSHA VIDYALAYA FEES", "Education"),

    # Insurance
    ("LIC OF INDIA LIFE INSURANCE", "Insurance"),
    ("HDFC ERGO GENERAL INSURANCE", "Insurance"),
    ("ICICI PRUDENTIAL LIFE PREM", "Insurance"),
    ("MAX LIFE INSURANCE PAYMENT", "Insurance"),
    ("STAR HEALTH ALLIED INSURANCE", "Insurance"),
    ("POLICY BAZAAR PREMIUM", "Insurance"),
    ("BAJAJ ALLIANZ VEHICLE COVER", "Insurance"),
    ("BIMA KIST BHUGTAN", "Insurance"),

    # Card-bill payment
    ("HDFC BANK CREDIT CARD BILL", "Card-bill payment"),
    ("ICICI BANK CC PAYMENT", "Card-bill payment"),
    ("SBI CARD AUTOPAY DEBIT", "Card-bill payment"),
    ("AXIS BANK CREDIT CARD", "Card-bill payment"),
    ("AMEX CARD SETTLEMENT", "Card-bill payment"),
    ("CRED CREDIT CARD PAYMENT", "Card-bill payment"),
    ("RBL BANK CARD SETTLEMENT", "Card-bill payment"),

    # Cash withdrawal
    ("ATM CASH WITHDRAWAL SBI", "Cash withdrawal"),
    ("HDFC ATM WDL BRANCH", "Cash withdrawal"),
    ("CASH WDL AT KIOSK", "Cash withdrawal"),
    ("DOMESTIC ATM CASH WDL", "Cash withdrawal"),
    ("ICICI ATM CASH WITHDRAW", "Cash withdrawal"),

    # Cash deposit
    ("CASH DEPOSIT CDM MACHINE", "Cash deposit"),
    ("BRANCH CASH DEP COUNTER", "Cash deposit"),
    ("SELF CASH DEPOSIT MACHINE", "Cash deposit"),

    # Refund/reversal
    ("UPI REFUND FOR FAILED ORDER", "Refund/reversal"),
    ("MERCHANT REVERSAL CREDIT", "Refund/reversal"),
    ("AMAZON REFUND PROCESSED", "Refund/reversal"),
    ("CHARGEBACK DISPUTE SETTLED", "Refund/reversal"),
    ("IRCTC TICKET CANCEL REFUND", "Refund/reversal"),

    # Loan disbursement
    ("PERSONAL LOAN DISBURSAL CR", "Loan disbursement"),
    ("INSTANT LOAN DISB KREDITBEE", "Loan disbursement"),
    ("LOAN CREDIT PROCEEDS", "Loan disbursement"),
    ("HOME LOAN SANCTION TRANCHE", "Loan disbursement"),

    # Investment redemption
    ("MUTUAL FUND SIP REDEMPTION", "Investment redemption"),
    ("ZERODHA FUND PAYOUT CR", "Investment redemption"),
    ("GROWW INVESTMENT WITHDRAWAL", "Investment redemption"),
    ("DIVIDEND PAYOUT CREDIT", "Investment redemption"),

    # Transfer/other inflow
    ("UPI FUNDS TRANSFER FROM FRIEND", "Transfer/other inflow"),
    ("IMPS TRANSFER FROM PARENT", "Transfer/other inflow"),
    ("WALLET TOPUP PAYTM", "Transfer/other inflow"),
    ("SELF ACCOUNT NEFT TRF", "Transfer/other inflow"),
    ("GPAY PEER TRANSFER", "Transfer/other inflow"),

    # Other
    ("MISCELLANEOUS BANK CHARGES", "Other"),
    ("ANNUAL DEBIT CARD FEE", "Other"),
    ("SMS ALERT SERVICE FEE", "Other"),
    ("UNKNOWN VENDOR SETTLEMENT", "Other"),
    ("MUNICIPAL TAX STAMP DUTY", "Other"),
]


def generate_extended_dataset() -> pd.DataFrame:
    """Generate diverse variations of transaction descriptions with synthetic bank tokens."""
    np.random.seed(42)
    rows = []
    
    prefixes = [
        "", "UPI/", "IMPS-", "NEFT-", "POS-", "ACH/", "NACH/", "BIL/", "RTGS/", "E-TRF "
    ]
    suffixes = [
        "", " REF 91024", " /TXN7710", " BATCH41", " BANGALORE", " MUMBAI", " DELHI",
        " AUTH 4821", " ID 88392", " ONLINE", " STORE 102", " TERMINAL 4"
    ]

    for base_text, category in BASE_EXAMPLES:
        # Add the base exemplar
        rows.append({"description": base_text, "category": category})
        
        # Add 6 varied versions with banking artifacts
        for _ in range(6):
            pref = np.random.choice(prefixes)
            suff = np.random.choice(suffixes)
            var_text = f"{pref}{base_text}{suff}".strip()
            rows.append({"description": var_text, "category": category})

    df = pd.DataFrame(rows).drop_duplicates(subset=["description"]).reset_index(drop=True)
    return df


def train_and_evaluate_nlp_pipeline() -> dict[str, float]:
    """Train TF-IDF + Calibrated Linear Classifier and save bundle."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    df = generate_extended_dataset()
    df.to_csv(TRAINING_DATA_PATH, index=False)

    X = df["description"]
    y = df["category"]

    # NLP feature extractor: word n-grams capture both names and prefixes
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 3),
        analyzer="word",
        lowercase=True,
        sublinear_tf=True,
        min_df=1,
    )

    base_clf = SGDClassifier(
        loss="log_loss",
        penalty="l2",
        alpha=1e-4,
        max_iter=1000,
        random_state=42,
    )

    # Wrap in calibrated classifier for genuine posterior class probabilities
    pipeline = Pipeline([
        ("tfidf", vectorizer),
        ("clf", CalibratedClassifierCV(estimator=base_clf, method="sigmoid", cv=3)),
    ])

    # 5-fold cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    acc_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="accuracy")
    f1_scores = cross_val_score(pipeline, X, y, cv=cv, scoring="f1_macro")

    # Fit final pipeline on all training records
    pipeline.fit(X, y)

    # Save model bundle
    bundle = {
        "pipeline": pipeline,
        "classes": list(pipeline.classes_),
        "version": "transaction-nlp-v1",
        "training_samples": len(df),
        "mean_cv_accuracy": float(np.mean(acc_scores)),
        "mean_cv_f1": float(np.mean(f1_scores)),
    }
    joblib.dump(bundle, MODEL_OUTPUT_PATH)

    metrics = {
        "model_name": "Tfidf_Calibrated_Linear_NLP",
        "training_samples": len(df),
        "classes_count": len(bundle["classes"]),
        "cv_accuracy_mean": float(np.mean(acc_scores)),
        "cv_accuracy_std": float(np.std(acc_scores)),
        "cv_f1_macro_mean": float(np.mean(f1_scores)),
        "cv_f1_macro_std": float(np.std(f1_scores)),
        "artifact_path": str(MODEL_OUTPUT_PATH),
    }
    METRICS_OUTPUT_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    return metrics


if __name__ == "__main__":
    m = train_and_evaluate_nlp_pipeline()
    print("Training Complete. Metrics:")
    print(json.dumps(m, indent=2))
