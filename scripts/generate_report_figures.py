import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# Setup directories
FIG_DIR = Path("reports/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Publication styling
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['figure.dpi'] = 300

NAVY = "#1e3a8a"
SLATE = "#334155"
LIGHT_BLUE = "#60a5fa"
AMBER = "#d97706"
CRIMSON = "#dc2626"
GREEN = "#16a34a"
GRAY_BG = "#f8fafc"
BORDER_COLOR = "#94a3b8"

print("Generating Figure 4.1: System Architecture...")
fig, ax = plt.subplots(figsize=(10, 11))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Layer 1: Inputs
ax.add_patch(patches.Rectangle((2, 85), 96, 13, facecolor="#eff6ff", edgecolor=NAVY, lw=1.5, ls="--"))
ax.text(4, 95.5, "INPUT & INGESTION LAYER", fontsize=10, fontweight="bold", color=NAVY)
ax.add_patch(patches.Rectangle((5, 87), 20, 7, facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1))
ax.text(15, 90.5, "Bank Statement\n(CSV / PDF)", ha="center", va="center", fontsize=8.5)
ax.add_patch(patches.Rectangle((28, 87), 18, 7, facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1))
ax.text(37, 90.5, "Salary Slip\n(Net Pay / Employer)", ha="center", va="center", fontsize=8.5)
ax.add_patch(patches.Rectangle((49, 87), 22, 7, facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1))
ax.text(60, 90.5, "Bureau Profile\n(CIBIL, DPD, Loans)", ha="center", va="center", fontsize=8.5)
ax.add_patch(patches.Rectangle((74, 87), 22, 7, facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1))
ax.text(85, 90.5, "Benchmark Datasets\n(UCI 30k / Home Credit)", ha="center", va="center", fontsize=8.5)

# Layer 2: Dual Pillars
# Pillar 1 Box
ax.add_patch(patches.Rectangle((2, 38), 47, 44, facecolor="#f0fdf4", edgecolor=GREEN, lw=1.5))
ax.text(4, 79.5, "PILLAR 1: STATEMENT BEHAVIORAL ML ENGINE", fontsize=9, fontweight="bold", color=GREEN)
p1_steps = [
    ("Statement Parser & Quality Gate\n(Balance recon, PII mask, >=3mo check)", 71),
    ("Tier 1 Transaction Supervised NLP\n(TF-IDF + Calibrated Linear SGD, 18 classes)", 61),
    ("15-Dim Behavioral Feature Bridge\n(Maps 23 cash-flows -> UCI repayment space)", 51),
    ("Supervised Behavioral ML Default Model\n(Random Forest, Platt-Calibrated, P(default))", 41)
]
for title, y in p1_steps:
    ax.add_patch(patches.Rectangle((5, y), 41, 7.5, facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1))
    ax.text(25.5, y + 3.75, title, ha="center", va="center", fontsize=8)
    if y < 71:
        ax.annotate("", xy=(25.5, y + 7.5), xytext=(25.5, y + 10),
                    arrowprops=dict(arrowstyle="->", color=SLATE, lw=1))

# Pillar 2 Box
ax.add_patch(patches.Rectangle((51, 38), 47, 44, facecolor="#fffbeb", edgecolor=AMBER, lw=1.5))
ax.text(53, 79.5, "PILLAR 2: MACRO BUREAU ML BENCHMARK", fontsize=9, fontweight="bold", color=AMBER)
p2_steps = [
    ("Home Credit Benchmark Training Pipeline\n(64/16/20 split, 196k train rows, leakage-free)", 71),
    ("Calibrated LightGBM Model\n(Platt sigmoid scaling, Alert threshold 0.20)", 61),
    ("Bureau Feature Extraction & Proxy Mapping\n(CIBIL to EXT_SOURCE, Overdue mapping)", 51),
    ("Macro Default Risk & Local Explanations\n(Calibrated Bureau PD + Exact Tree-SHAP)", 41)
]
for title, y in p2_steps:
    ax.add_patch(patches.Rectangle((54, y), 41, 7.5, facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1))
    ax.text(74.5, y + 3.75, title, ha="center", va="center", fontsize=8)
    if y < 71:
        ax.annotate("", xy=(74.5, y + 7.5), xytext=(74.5, y + 10),
                    arrowprops=dict(arrowstyle="->", color=SLATE, lw=1))

# Unsupervised Anomaly Safeguard (spanning underneath)
ax.add_patch(patches.Rectangle((2, 28), 96, 7.5, facecolor="#f1f5f9", edgecolor=SLATE, lw=1.2))
ax.text(50, 31.75, "Tier 3 Unsupervised ML Suite: Isolation Forest (150 trees) Cash-Flow Anomaly Detection & K-Means (k=4) Personas",
        ha="center", va="center", fontsize=8.5, fontweight="bold", color=SLATE)

# Decision Engine Box
ax.add_patch(patches.Rectangle((10, 16), 80, 9.5, facecolor="#e0e7ff", edgecolor=NAVY, lw=1.5))
ax.text(50, 22.5, "DUAL-PILLAR 2x2 ML DECISION MATRIX & SAFEGUARD ENGINE", ha="center", va="center", fontsize=9.5, fontweight="bold", color=NAVY)
ax.text(50, 18.5, "Causal decision from P(behavioral) x P(bureau) | Isolation Forest Anomaly Override | Data Quality Hard Stops", ha="center", va="center", fontsize=8)

# Persistence & UI Layer
ax.add_patch(patches.Rectangle((5, 2), 42, 10, facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1.2))
ax.text(26, 7, "SQLite Cryptographic Store\n(SHA-256 Forward Hash Chain + External Anchor)", ha="center", va="center", fontsize=8)

ax.add_patch(patches.Rectangle((53, 2), 42, 10, facecolor="#ffffff", edgecolor=BORDER_COLOR, lw=1.2))
ax.text(74, 7, "Streamlit FinTech UI Dashboard (6 Tabs)\n(What-If Counterfactual Sandbox, Tree-SHAP, Risk Map)", ha="center", va="center", fontsize=8)

# Connectors
ax.annotate("", xy=(25.5, 38), xytext=(25.5, 35.5), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.2))
ax.annotate("", xy=(74.5, 38), xytext=(74.5, 35.5), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.2))
ax.annotate("", xy=(50, 28), xytext=(50, 25.5), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.5))
ax.annotate("", xy=(26, 16), xytext=(26, 12), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.2))
ax.annotate("", xy=(74, 16), xytext=(74, 12), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.2))

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_4_1_architecture.png", dpi=300)
plt.close()

print("Generating Figure 4.2: Data Flow Diagram...")
fig, ax = plt.subplots(figsize=(9, 6.5))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# External entities
ax.add_patch(patches.Rectangle((3, 70), 18, 12, facecolor="#eff6ff", edgecolor=NAVY, lw=1.2))
ax.text(12, 76, "Applicant\n(Documents)", ha="center", va="center", fontsize=9, fontweight="bold")

ax.add_patch(patches.Rectangle((3, 20), 18, 12, facecolor="#eff6ff", edgecolor=NAVY, lw=1.2))
ax.text(12, 26, "Loan Officer\n(Inputs & Review)", ha="center", va="center", fontsize=9, fontweight="bold")

# Processes (Circles)
procs = [
    (38, 76, "1.0 Parse &\nValidate"),
    (68, 76, "2.0 Feature\nBridge"),
    (68, 48, "3.0 Behavioral\nML Predict"),
    (38, 26, "4.0 Bureau ML\n& Tree-SHAP"),
    (68, 20, "5.0 Dual-Pillar\nDecision Matrix"),
    (90, 20, "6.0 Hash-Chain\nCase Store")
]
for x, y, label in procs:
    circle = patches.Circle((x, y), 8, facecolor="#f8fafc", edgecolor=NAVY, lw=1.2)
    ax.add_patch(circle)
    ax.text(x, y, label, ha="center", va="center", fontsize=7.5)

# Arrows
ax.annotate("Statement\nCSV/PDF", xy=(30, 76), xytext=(21, 76), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1), fontsize=7.5, ha="center")
ax.annotate("Clean txns", xy=(60, 76), xytext=(46, 76), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1), fontsize=7.5, ha="center")
ax.annotate("15-dim UCI\nfeatures", xy=(68, 56), xytext=(68, 68), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1), fontsize=7.5, ha="center")
ax.annotate("P(behavioral)", xy=(68, 28), xytext=(68, 40), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1), fontsize=7.5, ha="center")
ax.annotate("Bureau inputs", xy=(30, 26), xytext=(21, 26), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1), fontsize=7.5, ha="center")
ax.annotate("P(bureau) + SHAP", xy=(60, 23), xytext=(46, 25), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1), fontsize=7.5, ha="center")
ax.annotate("Recommendation", xy=(82, 20), xytext=(76, 20), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1), fontsize=7.5, ha="center")

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_4_2_dfd.png", dpi=300)
plt.close()

print("Generating Figure 4.3: Use Case Diagram...")
fig, ax = plt.subplots(figsize=(9, 6.5))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Boundary box
ax.add_patch(patches.Rectangle((25, 5), 70, 90, facecolor="#ffffff", edgecolor=SLATE, lw=1.5))
ax.text(60, 91, "Behavioral Credit Decision Support System", ha="center", fontsize=10, fontweight="bold", color=NAVY)

# Actor Officer
ax.text(10, 52, "Loan\nOfficer", ha="center", fontsize=9.5, fontweight="bold")
ax.plot([10, 10], [58, 66], color=SLATE, lw=1.5) # body
ax.plot([5, 15], [62, 62], color=SLATE, lw=1.5) # arms
ax.plot([10, 6], [58, 50], color=SLATE, lw=1.5) # legs
ax.plot([10, 14], [58, 50], color=SLATE, lw=1.5)
circle = patches.Circle((10, 69), 3, facecolor="#eff6ff", edgecolor=SLATE, lw=1.5)
ax.add_patch(circle)

# Use Cases (Ellipses)
use_cases = [
    (60, 80, "Upload & Validate Statement"),
    (60, 68, "Review Hybrid NLP Categories"),
    (60, 56, "Inspect 15-Dim Behavioral ML Profile"),
    (60, 44, "Run What-If Counterfactual Sandbox"),
    (60, 32, "Score Bureau Profile & View Tree-SHAP"),
    (60, 20, "Evaluate Dual-Pillar 2x2 Recommendation"),
    (60, 9, "Persist Sealed Hash-Chained Record")
]
for x, y, label in use_cases:
    ellipse = patches.Ellipse((x, y), 48, 8, facecolor="#f0fdf4", edgecolor=GREEN, lw=1.2)
    ax.add_patch(ellipse)
    ax.text(x, y, label, ha="center", va="center", fontsize=8)
    ax.plot([15, x - 24], [62, y], color=BORDER_COLOR, lw=0.9, ls="-")

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_4_3_usecase.png", dpi=300)
plt.close()

print("Generating Figure 4.4: Class Diagram...")
fig, ax = plt.subplots(figsize=(10, 7.5))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

classes = [
    ("StatementQualityReport", 5, 60, 26, 32, [
        "+ score: float",
        "+ valid_transactions: int",
        "+ rejected_rows: int",
        "+ observed_months: int",
        "+ balance_mismatch_rows: int",
        "+ is_valid_statement: bool"
    ]),
    ("BehavioralMLFeatures", 37, 60, 26, 32, [
        "+ pay_delay_history: list",
        "+ utilisation_ratios: list",
        "+ payment_to_bill_ratios: list",
        "+ emergency_buffer_months: float",
        "+ map_statement_to_uci(): dict"
    ]),
    ("BehavioralRiskAssessment", 69, 60, 26, 32, [
        "+ calibrated_pd: float",
        "+ risk_band: str",
        "+ feature_drivers: list",
        "+ is_anomaly: bool",
        "+ predict_behavioral_risk(): obj"
    ]),
    ("BureauScorer", 5, 10, 26, 35, [
        "+ model_bundle: joblib",
        "+ threshold: float = 0.20",
        "+ predict_applicant_risk(): float",
        "+ explain_local_factors(): dict",
        "+ tree_shap_values: ndarray"
    ]),
    ("DualPillarEngine", 37, 10, 26, 35, [
        "+ behavioral_assessment: obj",
        "+ bureau_probability: float",
        "+ data_quality_gates: list",
        "+ recommend(): Decision",
        "+ quadrant: str"
    ]),
    ("CaseStore (SQLite)", 69, 10, 26, 35, [
        "+ previous_hash: str",
        "+ record_hash: str",
        "+ save_case_record(): str",
        "+ verify_hash_chain(): bool",
        "+ update_external_anchor(): path"
    ])
]

for name, x, y, w, h, members in classes:
    ax.add_patch(patches.Rectangle((x, y), w, h, facecolor="#ffffff", edgecolor=NAVY, lw=1.2))
    ax.add_patch(patches.Rectangle((x, y + h - 7), w, 7, facecolor="#eff6ff", edgecolor=NAVY, lw=1.2))
    ax.text(x + w/2, y + h - 3.5, name, ha="center", va="center", fontsize=8.5, fontweight="bold", color=NAVY)
    for i, m in enumerate(members):
        ax.text(x + 1.5, y + h - 11 - (i * 3.8), m, fontsize=7.2, color=SLATE)

# Connectors
ax.annotate("", xy=(37, 75), xytext=(31, 75), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1))
ax.annotate("", xy=(69, 75), xytext=(63, 75), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1))
ax.annotate("", xy=(50, 45), xytext=(50, 60), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1))
ax.annotate("", xy=(37, 28), xytext=(31, 28), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1))
ax.annotate("", xy=(69, 28), xytext=(63, 28), arrowprops=dict(arrowstyle="->", color=SLATE, lw=1))

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_4_4_class.png", dpi=300)
plt.close()

print("Generating Figure 4.5: Sequence Diagram...")
fig, ax = plt.subplots(figsize=(9.5, 7))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

actors = [
    (10, "Officer"),
    (26, "Dashboard\n(app.py)"),
    (43, "FeatureBridge\n(features.py)"),
    (60, "BehavioralML\n(model.joblib)"),
    (77, "BureauScorer\n(LightGBM)"),
    (94, "DecisionEngine\n(engine.py)")
]

for x, label in actors:
    ax.add_patch(patches.Rectangle((x - 6, 88), 12, 9, facecolor="#eff6ff", edgecolor=NAVY, lw=1.2))
    ax.text(x, 92.5, label, ha="center", va="center", fontsize=7.5, fontweight="bold")
    ax.plot([x, x], [10, 88], color=BORDER_COLOR, lw=1, ls="--")

seq_msgs = [
    (10, 26, 80, "upload_statement(csv, terms)"),
    (26, 43, 71, "map_statement_to_features(txns)"),
    (43, 60, 62, "predict_behavioral_risk(uci_feats)"),
    (60, 26, 53, "calibrated_pd, drivers"),
    (10, 26, 44, "enter_bureau_profile()"),
    (26, 77, 35, "predict_bureau_risk()"),
    (77, 26, 27, "bureau_pd, tree_shap"),
    (26, 94, 19, "recommend(p_behav, p_bureau, anomalies)"),
    (94, 26, 12, "Decision(quadrant, reasons)")
]

for x1, x2, y, msg in seq_msgs:
    ax.annotate("", xy=(x2, y), xytext=(x1, y),
                arrowprops=dict(arrowstyle="->", color=NAVY if x2 > x1 else SLATE,
                                lw=1.2, ls="-" if x2 > x1 else "--"))
    ax.text((x1 + x2)/2, y + 1.8, msg, ha="center", fontsize=6.8, color=SLATE)

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_4_5_sequence.png", dpi=300)
plt.close()

print("Generating Figure 5.1: Dual-Pillar 2x2 Decision Matrix...")
fig, ax = plt.subplots(figsize=(7.5, 6.5))
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 1.0)

# Quadrant rectangles
ax.add_patch(patches.Rectangle((0, 0), 0.30, 0.20, facecolor="#dcfce7", edgecolor="none")) # Q1
ax.add_patch(patches.Rectangle((0, 0.20), 0.30, 0.80, facecolor="#fef9c3", edgecolor="none")) # Q2
ax.add_patch(patches.Rectangle((0.30, 0), 0.70, 0.20, facecolor="#fef3c7", edgecolor="none")) # Q3
ax.add_patch(patches.Rectangle((0.30, 0.20), 0.70, 0.80, facecolor="#fee2e2", edgecolor="none")) # Q4

# Boundary Lines
ax.axvline(0.30, color=SLATE, lw=2)
ax.axhline(0.20, color=SLATE, lw=2)

# Quadrant Texts
ax.text(0.15, 0.10, "QUADRANT 1\nMEETS INDICATIVE CRITERIA\n(Low Behavioral & Bureau Risk)", ha="center", va="center", fontsize=8.5, fontweight="bold", color=GREEN)
ax.text(0.15, 0.60, "QUADRANT 2\nMANUAL REVIEW: BUREAU ALERT\n(Low Behavioral Risk,\nElevated Bureau Risk)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#854d0e")
ax.text(0.65, 0.10, "QUADRANT 3\nMANUAL REVIEW / REFERRAL:\nCASH-FLOW ALERT\n(Elevated Behavioral Risk,\nLow Bureau Risk)", ha="center", va="center", fontsize=8.5, fontweight="bold", color="#b45309")
ax.text(0.65, 0.60, "QUADRANT 4\nDOES NOT MEET INDICATIVE CRITERIA\n(Elevated Risk on Both Models)", ha="center", va="center", fontsize=8.5, fontweight="bold", color=CRIMSON)

ax.set_xlabel("Pillar 1 Behavioral Default Risk $P_{behavioral}$ (Random Forest)", fontsize=10, fontweight="bold")
ax.set_ylabel("Pillar 2 Bureau Default Risk $P_{bureau}$ (LightGBM)", fontsize=10, fontweight="bold")
ax.set_title("Dual-Pillar 2×2 ML Risk Decision Matrix", fontsize=11, fontweight="bold", pad=12)

# Overrides note
ax.text(0.5, -0.15, "Note: Isolation Forest cash-flow anomalies or Salary-slip mismatches (>15%) automatically override Q1 into Manual Review / Refer.",
        ha="center", fontsize=8, style="italic", transform=ax.transAxes)

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_5_1_matrix.png", dpi=300)
plt.close()

print("Generating Figure 5.2: Hash Chain...")
fig, ax = plt.subplots(figsize=(9, 3.5))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

blocks = [
    (5, "Record 1 (Genesis)\n• Case ID: C0\n• PII-Stripped JSON\n• Prev Hash: 000...0\n• Hash: SHA256(...)"),
    (38, "Record 2\n• Case ID: C1\n• PII-Stripped JSON\n• Prev Hash: Hash(C0)\n• Hash: SHA256(...)"),
    (71, "Record 3 (Head)\n• Case ID: C2\n• PII-Stripped JSON\n• Prev Hash: Hash(C1)\n• Hash: SHA256(...)")
]

for x, text in blocks:
    ax.add_patch(patches.Rectangle((x, 15), 24, 70, facecolor="#eff6ff", edgecolor=NAVY, lw=1.5))
    ax.text(x + 12, 50, text, ha="center", va="center", fontsize=8, color=SLATE)

ax.annotate("", xy=(38, 50), xytext=(29, 50), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.8))
ax.annotate("", xy=(71, 50), xytext=(62, 50), arrowprops=dict(arrowstyle="->", color=NAVY, lw=1.8))

# Anchor Box
ax.add_patch(patches.Rectangle((73, 2), 20, 10, facecolor="#fef3c7", edgecolor=AMBER, lw=1.2))
ax.text(83, 7, "HEAD Anchor File\n(data/HEAD_HASH.sha256)", ha="center", va="center", fontsize=7.5, fontweight="bold", color=AMBER)
ax.annotate("", xy=(83, 15), xytext=(83, 12), arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.2))

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_5_2_hashchain.png", dpi=300)
plt.close()

print("Generating Figure 6.1: Feature Comparison / Drivers (Statements A & B)...")
fig, ax = plt.subplots(figsize=(8.5, 4.5))
categories = ["Savings Ratio", "Low-Balance Days (Norm)", "EMI-to-Income", "Emergency Buffer (Norm)", "Expense Volatility"]
stmt_a = [0.451, 0.0, 0.120, 0.58, 0.15]
stmt_b = [0.0, 0.70, 0.362, 0.33, 0.65]

x = np.arange(len(categories))
width = 0.35

ax.bar(x - width/2, stmt_a, width, label="Statement A (Salaried, Calibrated PD: 11.2%)", color=NAVY)
ax.bar(x + width/2, stmt_b, width, label="Statement B (Constrained, Calibrated PD: 46.8%)", color=AMBER)

ax.set_ylabel("Normalized Behavioral Metric", fontsize=9.5)
ax.set_title("Behavioral Cash-Flow Feature Bridge Comparison: Statements A vs B", fontsize=10.5, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(categories, fontsize=8.5)
ax.legend(frameon=True, fontsize=8.5)
ax.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_6_1_drivers.png", dpi=300)
plt.close()

print("Generating Figure 6.2: Demonstration Risk Map...")
fig, ax = plt.subplots(figsize=(7.5, 6))
ax.set_xlim(0, 1.0)
ax.set_ylim(0, 1.0)

ax.add_patch(patches.Rectangle((0, 0), 0.30, 0.20, facecolor="#dcfce7", alpha=0.8))
ax.add_patch(patches.Rectangle((0, 0.20), 0.30, 0.80, facecolor="#fef9c3", alpha=0.8))
ax.add_patch(patches.Rectangle((0.30, 0), 0.70, 0.20, facecolor="#fef3c7", alpha=0.8))
ax.add_patch(patches.Rectangle((0.30, 0.20), 0.70, 0.80, facecolor="#fee2e2", alpha=0.8))

ax.axvline(0.30, color=SLATE, lw=1.5, ls="--")
ax.axhline(0.20, color=SLATE, lw=1.5, ls="--")

# Scatter points
# 1. Statement A + Low Risk Profile
ax.scatter([0.112], [0.0057], color=NAVY, s=120, marker="o", label="Stmt A + Low Bureau (Q1: Approve)", zorder=5)
# 2. Statement A + High Risk Profile
ax.scatter([0.112], [0.518], color=CRIMSON, s=120, marker="s", label="Stmt A + High Bureau (Q2: Manual Review)", zorder=5)
# 3. Statement B + Low Risk Profile
ax.scatter([0.468], [0.0057], color=AMBER, s=120, marker="^", label="Stmt B + Low Bureau (Q3: Referral/Review)", zorder=5)
# 4. Statement B + High Risk Profile
ax.scatter([0.468], [0.518], color="#7f1d1d", s=120, marker="D", label="Stmt B + High Bureau (Q4: Decline)", zorder=5)

ax.set_xlabel("Pillar 1 Behavioral Default Risk $P_{behavioral}$", fontsize=10, fontweight="bold")
ax.set_ylabel("Pillar 2 Bureau Default Risk $P_{bureau}$", fontsize=10, fontweight="bold")
ax.set_title("Demonstration Applicants on Dual-Pillar Risk Map", fontsize=11, fontweight="bold")
ax.legend(loc="upper right", fontsize=8.5, frameon=True)
ax.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_6_2_riskmap.png", dpi=300)
plt.close()

print("Generating Figure 7.1: Candidate Model Comparison...")
with open("reports/behavioral_prediction_metrics.json", "r") as f:
    behav_data = json.load(f)

cv_results = behav_data["candidate_cv_results"]
models = list(cv_results.keys())
roc_means = [cv_results[m]["cv_roc_auc_mean"] for m in models]
times = [cv_results[m]["training_seconds"] for m in models]

fig, ax1 = plt.subplots(figsize=(8, 4.5))

x = np.arange(len(models))
width = 0.35

rects1 = ax1.bar(x - width/2, roc_means, width, label="5-Fold Stratified CV ROC-AUC", color=NAVY)
ax1.set_ylabel("Cross-Validation ROC-AUC", color=NAVY, fontsize=9.5, fontweight="bold")
ax1.set_ylim(0.70, 0.82)
ax1.set_xticks(x)
ax1.set_xticklabels(models, fontsize=9)

ax2 = ax1.twinx()
rects2 = ax2.bar(x + width/2, times, width, label="Training Time (seconds)", color=LIGHT_BLUE)
ax2.set_ylabel("Training Time (s)", color=SLATE, fontsize=9.5)
ax2.set_ylim(0, 22)

plt.title("Pillar 1 Candidate Comparison on 30k UCI Financial Dataset", fontsize=11, fontweight="bold")

# Add values above bars
for r in rects1:
    h = r.get_height()
    ax1.annotate(f"{h:.4f}", xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                 textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_7_1_model_comparison.png", dpi=300)
plt.close()

print("Generating Figure 7.2: Platt Calibration Reliability Diagram...")
cal_curve = behav_data["calibration_curve"]
frac_pos = cal_curve["fraction_of_positives"]
mean_pred = cal_curve["mean_predicted_value"]

fig, ax = plt.subplots(figsize=(6.5, 6))
ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration", lw=1.2)
ax.plot(mean_pred, frac_pos, "s-", color=NAVY, label="Platt-Calibrated RF (Brier: 0.1308)", lw=1.8, markersize=6)

ax.set_xlabel("Mean Predicted Default Probability", fontsize=10, fontweight="bold")
ax.set_ylabel("Fraction of Observed Delinquencies", fontsize=10, fontweight="bold")
ax.set_title("Reliability Diagram (Frozen 4,500 Test Partition)", fontsize=11, fontweight="bold")
ax.legend(loc="lower right", fontsize=9, frameon=True)
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_7_2_calibration.png", dpi=300)
plt.close()

print("Generating Figure 7.3: Permutation Feature Importance...")
perm = behav_data["permutation_feature_importance"]
sorted_perm = sorted(perm.items(), key=lambda item: item[1], reverse=True)[:10]
feat_names = [item[0] for item in sorted_perm][::-1]
importances = [item[1] for item in sorted_perm][::-1]

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(feat_names, importances, color=NAVY, height=0.6)
ax.set_xlabel("Permutation Importance (Mean ROC-AUC Decrease)", fontsize=9.5, fontweight="bold")
ax.set_title("Top 10 Behavioral Feature Drivers (Pillar 1 Random Forest)", fontsize=11, fontweight="bold")
ax.grid(axis="x", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_7_3_importance.png", dpi=300)
plt.close()

print("Generating Figure 7.4: Home Credit Top Gain Importance...")
with open("reports/home_credit_global_importance.json", "r") as f:
    hc_gain = json.load(f)

# Take top 10 from list of objects
sorted_hc = sorted(hc_gain, key=lambda item: item["gain_importance"], reverse=True)[:10]
hc_names = [item["feature"] for item in sorted_hc][::-1]
hc_vals = [item["gain_importance"] for item in sorted_hc][::-1]

fig, ax = plt.subplots(figsize=(8, 5))
ax.barh(hc_names, hc_vals, color="#1e40af", height=0.6)
ax.set_xlabel("LightGBM Split Gain Importance", fontsize=9.5, fontweight="bold")
ax.set_title("Top 10 Macro Bureau Features by Gain (Pillar 2)", fontsize=11, fontweight="bold")
ax.grid(axis="x", linestyle="--", alpha=0.5)

plt.tight_layout()
plt.savefig(FIG_DIR / "fig_7_4_home_credit_gain.png", dpi=300)
plt.close()

print("All 13 publication figures successfully generated in reports/figures!")
