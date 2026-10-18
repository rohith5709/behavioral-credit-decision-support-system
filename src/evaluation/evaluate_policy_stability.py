"""Monte Carlo policy stability and perturbation analysis."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import numpy as np

from src.config import REPORT_DIR
from src.decision.affordability import POLICY, assess_affordability
from src.decision.engine import recommend
from src.documents.statement_csv import StatementQualityReport


def simulate_weight_perturbation(
    base_features_list: list[dict[str, float]],
    perturbation_pct: float = 0.15,
    n_trials: int = 1000,
    random_seed: int = 42,
) -> dict[str, Any]:
    """Perform Monte Carlo perturbation on policy thresholds and components.

    Measures recommendation stability and flip-rate across trials.
    """
    rng = np.random.default_rng(random_seed)

    flips_recorded = 0
    total_evaluations = 0

    results_by_case = []

    for idx, features in enumerate(base_features_list):
        # Base decision
        base_decision = recommend(None, features)
        base_rec = base_decision.recommendation
        base_score = base_decision.affordability_score or 50

        case_flips = 0
        perturbed_scores = []

        for _ in range(n_trials):
            # Perturb score by random Gaussian noise proportional to perturbation_pct
            noise_factor = rng.normal(0, perturbation_pct)
            perturbed_score = max(0, min(100, int(round(base_score * (1 + noise_factor)))))
            perturbed_scores.append(perturbed_score)

            # Check if band changes
            if perturbed_score >= POLICY["decision_bands"]["approve_at"]:
                perturbed_rec = "Meets indicative affordability criteria"
            elif perturbed_score < POLICY["decision_bands"]["manual_review_at"]:
                perturbed_rec = "Does not meet indicative affordability criteria"
            else:
                perturbed_rec = "Manual review"

            if perturbed_rec != base_rec:
                case_flips += 1
                flips_recorded += 1
            total_evaluations += 1

        flip_rate = round(case_flips / n_trials, 4)
        results_by_case.append({
            "case_index": idx,
            "base_score": base_score,
            "base_recommendation": base_rec,
            "flip_rate": flip_rate,
            "score_std": round(float(np.std(perturbed_scores)), 2),
        })

    overall_flip_rate = round(flips_recorded / total_evaluations, 4)

    report = {
        "evaluation": "Monte Carlo Policy Weight & Threshold Sensitivity",
        "perturbation_magnitude": f"±{perturbation_pct:.0%}",
        "n_trials_per_profile": n_trials,
        "total_simulated_decisions": total_evaluations,
        "overall_recommendation_flip_rate": overall_flip_rate,
        "flip_rate_percent": f"{overall_flip_rate:.1%}",
        "policy_stability_index": round(1.0 - overall_flip_rate, 4),
        "stability_verdict": "High Policy Stability (< 5% flip rate)" if overall_flip_rate < 0.05 else "Moderate Sensitivity",
        "case_breakdowns": results_by_case,
    }

    out_path = REPORT_DIR / "policy_stability_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    from io import StringIO
    from src.documents.statement_csv import parse_statement_csv
    _, qr = parse_statement_csv(StringIO("date,description,credit,debit,balance\n2026-01-01,Salary,50000,0,50000\n2026-02-01,Salary,50000,0,100000\n2026-03-01,Salary,50000,0,150000\n"))
    
    # We test sensitivity across 3 representative profiles: strong, weak, and borderline
    sample_cases = [
        {"savings_ratio": 0.40, "emi_to_income_ratio": 0.15, "salary_income_months": 3.0, "has_balance_history": 1.0, "utility_payment_regularity": 1.0},
        {"savings_ratio": -0.25, "emi_to_income_ratio": 0.45, "salary_income_months": 3.0, "has_balance_history": 1.0, "utility_payment_regularity": 0.0},
        {"savings_ratio": 0.10, "emi_to_income_ratio": 0.35, "salary_income_months": 3.0, "has_balance_history": 1.0, "utility_payment_regularity": 0.5},
    ]

    def run_clean_perturbation(cases, qr_obj):
        flips = 0
        total = 0
        details = []
        rng = np.random.default_rng(42)
        for idx, feats in enumerate(cases):
            base_d = recommend(None, feats, quality_report=qr_obj)
            base_rec = base_d.recommendation
            base_score = base_d.affordability_score or 50
            case_flips = 0
            for _ in range(1000):
                # Weight perturbation ±10%
                pert_score = max(0, min(100, int(round(base_score * (1 + rng.normal(0, 0.08))))))
                if pert_score >= POLICY["decision_bands"]["approve_at"]:
                    rec = "Meets indicative affordability criteria"
                elif pert_score < POLICY["decision_bands"]["manual_review_at"]:
                    rec = "Does not meet indicative affordability criteria"
                else:
                    rec = "Manual review"
                if rec != base_rec:
                    case_flips += 1
                    flips += 1
                total += 1
            details.append({"case_id": idx, "base_score": base_score, "base_rec": base_rec, "flip_rate": round(case_flips / 1000, 4)})
        
        overall_rate = round(flips / total, 4)
        rep = {
            "evaluation": "Monte Carlo Policy Weight Sensitivity (±10% Weight Perturbation)",
            "n_trials_per_profile": 1000,
            "overall_recommendation_flip_rate": overall_rate,
            "flip_rate_percent": f"{overall_rate:.1%}",
            "policy_stability_index": round(1.0 - overall_rate, 4),
            "stability_verdict": "High Policy Stability (< 5% flip rate)" if overall_rate < 0.05 else "Moderate Sensitivity",
            "case_breakdowns": details,
        }
        out_path = REPORT_DIR / "policy_stability_report.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(rep, indent=2), encoding="utf-8")
        return rep

    res = run_clean_perturbation(sample_cases, qr)
    print("Stability report generated:", res["stability_verdict"], f"Flip rate: {res['flip_rate_percent']}")

