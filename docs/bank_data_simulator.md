# Bank Data Simulator integration

## Purpose

The simulator supplies synthetic, transaction-level behavioural data for the dashboard demonstration: salary consistency, credit utilisation, EMI burden, balances, and transaction patterns.

It is **not** the default-risk training source. Its documented prediction labels are churn-oriented, so default-risk evaluation remains on Home Credit Default Risk.

## Generate source data

Download or clone the upstream MIT-licensed project: <https://github.com/kannanjayachandran/bank-data-simulator>.

From its own project directory, follow its documented quick validation run. A sensible first run is 2,000 customers, 12 months, and one job on a typical student laptop:

```powershell
uv venv
uv pip install -e .
$env:PYTHONPATH = "."
uv run python main.py --n-customers 2000 --sim-months 12 --jobs 1 --output-dir "C:\path\to\simulator-output"
```

The expected source table is `churn_feature_snapshot` in Parquet form. The adapter uses the documented fields when they are present:

- `salary_credit_consistency`
- `credit_utilization`
- `emi_to_income_ratio`
- `balance_change_3m`
- `txn_count_change_3m`
- `tenure_months`
- `products_count`
- `dormant_days`

## Import into this project

From this project's root, run:

```powershell
python -m src.data.simulator_adapter --input "C:\path\to\simulator-output" --output data/synthetic/simulator_behaviour_features.csv
```

The adapter keeps the simulator's three-month snapshot horizon by default, avoiding duplicate customer-month rows from its multi-horizon output. The generated CSV is intentionally ignored by Git because it is derived data. It can be used to explore the synthetic portfolio and test the behavioural dashboard flow.
