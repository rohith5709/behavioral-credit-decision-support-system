# System architecture

```mermaid
flowchart TD
    A[CSV bank statement] --> B[Parser and data-quality checks]
    B --> C[Normalised transactions]
    C --> D[Transparent category rules]
    D --> E[Behavioural features and monthly summaries]
    E --> F[0–100 affordability score]
    B --> F
    F --> G[Dynamic statement recommendation and reasons]

    H[Home Credit CSV data] --> I[Feature aggregation]
    I --> J[Candidate benchmark]
    J --> K[Selected calibrated LightGBM]
    K --> L[Validation metrics, thresholds, calibration]

    G --> M[Officer review]
    L --> M
    M --> N[Decision summary and downloadable record]
```

The statement path and the Home Credit model path remain intentionally separate. The system does not apply a model trained on Home Credit fields to raw uploaded bank-statement transactions.
