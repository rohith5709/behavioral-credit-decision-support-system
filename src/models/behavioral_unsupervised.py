"""Account-level Unsupervised Machine Learning: Behavioral Anomaly Detection & Spending Clustering."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
SYNTHETIC_DATA_PATH = PROJECT_ROOT / "data" / "synthetic" / "simulator_behaviour_features.csv"

BEHAVIORAL_MODEL_OUTPUT_PATH = MODELS_DIR / "behavioral_unsupervised_bundle.joblib"
BEHAVIORAL_METRICS_PATH = REPORTS_DIR / "behavioral_unsupervised_metrics.json"

# Core account-level behavioral features mapped to unsupervised analysis
CORE_BEHAVIORAL_FEATURES = [
    "savings_ratio",
    "income_variation_ratio",
    "expense_variation_ratio",
    "effective_monthly_emi",
    "cash_withdrawal_share",
    "low_balance_day_count",
    "emergency_buffer_months",
    "uncertain_transaction_share",
]

PERSONA_ARCHETYPES = {
    0: {
        "name": "Disciplined Accumulator",
        "archetype": "High surplus retention, low expense volatility, healthy emergency cash buffer.",
        "risk_profile": "Low Risk",
        "color": "#10B981",
    },
    1: {
        "name": "Balanced Lifestyle Spender",
        "archetype": "Consistent earnings, moderate discretionary spending, predictable cash flow.",
        "risk_profile": "Moderate Risk",
        "color": "#3B82F6",
    },
    2: {
        "name": "Volatile Cash Flow / Gig Earner",
        "archetype": "Fluctuating income intervals, uneven monthly savings margins.",
        "risk_profile": "Elevated Monitoring",
        "color": "#F59E0B",
    },
    3: {
        "name": "Liquidity Strained / High Buffer Drag",
        "archetype": "High debt-to-income or heavy cash depletion, frequent low-balance days.",
        "risk_profile": "High Caution",
        "color": "#EF4444",
    },
}


def generate_representative_cohort(n_samples: int = 1500) -> pd.DataFrame:
    """Generate representative account-level behavioral distributions for clustering & anomaly baseline."""
    np.random.seed(42)
    
    # Cluster 0: Disciplined Accumulator (~35%)
    n0 = int(n_samples * 0.35)
    c0 = pd.DataFrame({
        "savings_ratio": np.clip(np.random.normal(0.40, 0.08, n0), 0.15, 0.85),
        "income_variation_ratio": np.clip(np.random.normal(0.08, 0.04, n0), 0.0, 0.25),
        "expense_variation_ratio": np.clip(np.random.normal(0.12, 0.05, n0), 0.02, 0.30),
        "effective_monthly_emi": np.clip(np.random.normal(5000, 2000, n0), 0, 15000),
        "cash_withdrawal_share": np.clip(np.random.normal(0.05, 0.03, n0), 0.0, 0.15),
        "low_balance_day_count": np.clip(np.random.poisson(0.5, n0), 0, 3),
        "emergency_buffer_months": np.clip(np.random.normal(5.5, 1.5, n0), 2.0, 15.0),
        "uncertain_transaction_share": np.clip(np.random.normal(0.02, 0.01, n0), 0.0, 0.08),
    })

    # Cluster 1: Balanced Spender (~30%)
    n1 = int(n_samples * 0.30)
    c1 = pd.DataFrame({
        "savings_ratio": np.clip(np.random.normal(0.20, 0.06, n1), 0.05, 0.35),
        "income_variation_ratio": np.clip(np.random.normal(0.12, 0.05, n1), 0.02, 0.30),
        "expense_variation_ratio": np.clip(np.random.normal(0.18, 0.06, n1), 0.05, 0.40),
        "effective_monthly_emi": np.clip(np.random.normal(12000, 4000, n1), 1000, 25000),
        "cash_withdrawal_share": np.clip(np.random.normal(0.12, 0.05, n1), 0.02, 0.25),
        "low_balance_day_count": np.clip(np.random.poisson(2.0, n1), 0, 7),
        "emergency_buffer_months": np.clip(np.random.normal(2.5, 0.8, n1), 1.0, 5.0),
        "uncertain_transaction_share": np.clip(np.random.normal(0.04, 0.02, n1), 0.0, 0.12),
    })

    # Cluster 2: Volatile Earner (~20%)
    n2 = int(n_samples * 0.20)
    c2 = pd.DataFrame({
        "savings_ratio": np.clip(np.random.normal(0.15, 0.12, n2), -0.10, 0.45),
        "income_variation_ratio": np.clip(np.random.normal(0.42, 0.12, n2), 0.20, 0.85),
        "expense_variation_ratio": np.clip(np.random.normal(0.35, 0.10, n2), 0.15, 0.70),
        "effective_monthly_emi": np.clip(np.random.normal(8000, 5000, n2), 0, 22000),
        "cash_withdrawal_share": np.clip(np.random.normal(0.18, 0.08, n2), 0.05, 0.40),
        "low_balance_day_count": np.clip(np.random.poisson(4.0, n2), 0, 12),
        "emergency_buffer_months": np.clip(np.random.normal(1.8, 0.9, n2), 0.5, 4.5),
        "uncertain_transaction_share": np.clip(np.random.normal(0.06, 0.03, n2), 0.01, 0.18),
    })

    # Cluster 3: Liquidity Strained / High Buffer Drag (~15%)
    n3 = n_samples - (n0 + n1 + n2)
    c3 = pd.DataFrame({
        "savings_ratio": np.clip(np.random.normal(-0.05, 0.08, n3), -0.35, 0.08),
        "income_variation_ratio": np.clip(np.random.normal(0.25, 0.10, n3), 0.08, 0.55),
        "expense_variation_ratio": np.clip(np.random.normal(0.40, 0.12, n3), 0.18, 0.80),
        "effective_monthly_emi": np.clip(np.random.normal(26000, 7000, n3), 8000, 50000),
        "cash_withdrawal_share": np.clip(np.random.normal(0.35, 0.12, n3), 0.12, 0.70),
        "low_balance_day_count": np.clip(np.random.poisson(9.0, n3), 2, 25),
        "emergency_buffer_months": np.clip(np.random.normal(0.4, 0.3, n3), 0.0, 1.2),
        "uncertain_transaction_share": np.clip(np.random.normal(0.10, 0.04, n3), 0.02, 0.25),
    })

    cohort = pd.concat([c0, c1, c2, c3], ignore_index=True)
    return cohort


def train_behavioral_unsupervised_models() -> dict[str, Any]:
    """Train Isolation Forest and K-Means models and save bundled artifacts."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    data = generate_representative_cohort(n_samples=2000)
    features = data[CORE_BEHAVIORAL_FEATURES]

    # Preprocessing scaler for distance-based clustering
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    # 1. K-Means Persona Clustering
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(scaled_features)

    # Automatically identify cluster identities based on cluster center characteristics:
    # - Disciplined Accumulator: highest savings_ratio & emergency_buffer
    # - Liquidity Strained: lowest savings_ratio & highest low_balance_day_count
    # - Volatile Gig Earner: highest income_variation_ratio
    # - Balanced Spender: remaining cluster
    centers = kmeans.cluster_centers_
    savings_idx = CORE_BEHAVIORAL_FEATURES.index("savings_ratio")
    inc_var_idx = CORE_BEHAVIORAL_FEATURES.index("income_variation_ratio")
    low_bal_idx = CORE_BEHAVIORAL_FEATURES.index("low_balance_day_count")

    disciplined_cluster = int(np.argmax(centers[:, savings_idx]))
    strained_cluster = int(np.argmax(centers[:, low_bal_idx]))
    
    remaining = [i for i in range(4) if i not in (disciplined_cluster, strained_cluster)]
    if centers[remaining[0], inc_var_idx] > centers[remaining[1], inc_var_idx]:
        volatile_cluster = remaining[0]
        balanced_cluster = remaining[1]
    else:
        volatile_cluster = remaining[1]
        balanced_cluster = remaining[0]

    cluster_personas = {
        disciplined_cluster: {
            "name": "Disciplined Accumulator",
            "archetype": "High surplus retention, low expense volatility, healthy emergency cash buffer.",
            "risk_profile": "Low Risk",
            "color": "#10B981",
        },
        balanced_cluster: {
            "name": "Balanced Lifestyle Spender",
            "archetype": "Consistent earnings, moderate discretionary spending, predictable cash flow.",
            "risk_profile": "Moderate Risk",
            "color": "#3B82F6",
        },
        volatile_cluster: {
            "name": "Volatile Cash Flow / Gig Earner",
            "archetype": "Fluctuating income intervals, uneven monthly savings margins.",
            "risk_profile": "Elevated Monitoring",
            "color": "#F59E0B",
        },
        strained_cluster: {
            "name": "Liquidity Strained / High Buffer Drag",
            "archetype": "High debt-to-income or heavy cash depletion, frequent low-balance days.",
            "risk_profile": "High Caution",
            "color": "#EF4444",
        },
    }

    # 2. Isolation Forest Anomaly Detection
    # Contamination set to 5% for calibrated outlier detection
    iso_forest = IsolationForest(
        n_estimators=150,
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    iso_forest.fit(features)

    bundle = {
        "features": CORE_BEHAVIORAL_FEATURES,
        "scaler": scaler,
        "kmeans": kmeans,
        "isolation_forest": iso_forest,
        "personas": cluster_personas,
        "cluster_centers": kmeans.cluster_centers_.tolist(),
        "version": "behavioral-ml-v1",
    }
    joblib.dump(bundle, BEHAVIORAL_MODEL_OUTPUT_PATH)

    metrics = {
        "model_name": "Behavioral_Unsupervised_ML_Suite",
        "clustering_algorithm": "KMeans(k=4)",
        "anomaly_algorithm": "IsolationForest(n_estimators=150, contamination=0.05)",
        "training_samples": len(data),
        "features": CORE_BEHAVIORAL_FEATURES,
        "clusters_distribution": {
            str(k): int((cluster_labels == k).sum()) for k in range(4)
        },
        "artifact_path": str(BEHAVIORAL_MODEL_OUTPUT_PATH),
    }
    BEHAVIORAL_METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


_cached_bundle = None


def load_behavioral_bundle() -> dict[str, Any] | None:
    """Load cached behavioral unsupervised bundle."""
    global _cached_bundle
    if _cached_bundle is not None:
        return _cached_bundle
    if BEHAVIORAL_MODEL_OUTPUT_PATH.exists():
        try:
            _cached_bundle = joblib.load(BEHAVIORAL_MODEL_OUTPUT_PATH)
        except Exception:
            _cached_bundle = None
    return _cached_bundle


def score_behavioral_profile(statement_features: dict[str, Any]) -> dict[str, Any]:
    """Score an applicant's statement features with Isolation Forest and K-Means clustering."""
    bundle = load_behavioral_bundle()
    if bundle is None:
        return {
            "status": "unavailable",
            "reason": "Unsupervised model bundle not initialized",
        }

    features_list = bundle["features"]
    scaler: StandardScaler = bundle["scaler"]
    kmeans: KMeans = bundle["kmeans"]
    iso_forest: IsolationForest = bundle["isolation_forest"]
    personas: dict[int, dict[str, str]] = bundle["personas"]

    # Extract features with conservative defaults
    values = []
    for f in features_list:
        val = statement_features.get(f)
        if val is None or pd.isna(val):
            val = 0.0
        values.append(float(val))

    X_raw = np.array([values])
    X_scaled = scaler.transform(X_raw)

    # 1. Anomaly Scoring
    # score_samples returns opposite of anomaly score; lower = more abnormal
    raw_anomaly_score = iso_forest.score_samples(X_raw)[0]
    # Normalize anomaly score roughly to [0, 1] where >0.65 indicates anomaly
    # Typical score_samples range is [-0.8, -0.4]
    normalized_anomaly_score = float(np.clip(( -raw_anomaly_score - 0.40) / 0.40, 0.0, 1.0))
    is_anomaly = bool(iso_forest.predict(X_raw)[0] == -1)

    # 2. Cluster / Persona Assignment
    cluster_idx = int(kmeans.predict(X_scaled)[0])
    # Compute distances to cluster centers to compute fit confidence
    distances = np.linalg.norm(X_scaled - kmeans.cluster_centers_, axis=1)
    closest_dist = float(distances[cluster_idx])
    fit_confidence = float(np.clip(1.0 / (1.0 + closest_dist), 0.50, 0.99))

    persona = personas.get(cluster_idx, {
        "name": f"Cluster {cluster_idx}",
        "archetype": "Custom behavioral cluster",
        "risk_profile": "Standard",
        "color": "#94A3B8",
    })

    return {
        "status": "scored",
        "anomaly_detection": {
            "is_anomaly": is_anomaly,
            "anomaly_score": round(normalized_anomaly_score, 3),
            "verdict": "Elevated Cash Flow Outlier Detected" if is_anomaly else "Normal Cash Flow Profile",
        },
        "behavioral_persona": {
            "cluster_id": cluster_idx,
            "name": persona["name"],
            "archetype": persona["archetype"],
            "risk_profile": persona["risk_profile"],
            "color": persona["color"],
            "fit_confidence": round(fit_confidence, 2),
        },
    }


if __name__ == "__main__":
    m = train_behavioral_unsupervised_models()
    print("Behavioral Unsupervised Suite Trained Successfully:")
    print(json.dumps(m, indent=2))
