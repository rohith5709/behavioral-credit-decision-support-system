# Limitations and ethics

## Scope

This is a local educational prototype for human review. It is not a production lending system and must not make final lending decisions.

## Key limitations

- Statement categories use keywords and can misclassify ambiguous descriptions.
- A CSV statement does not verify identity, income authenticity, employment, or account ownership.
- The affordability score is a transparent heuristic; it is not a statistically validated probability of repayment.
- The Home Credit model was trained on a separate competition dataset. Its reported metrics do not establish performance for this prototype’s uploaded statements or for a particular institution or population.
- Probability calibration is evaluated on one held-out split, not an external validation population.
- Default labels and historical credit data can reflect structural bias. Metrics do not prove fairness across protected or vulnerable groups.

## Safeguards

- A human officer chooses the final action.
- Insufficient data, poor quality, missing salary, contradictory balances, and critical EMI burden trigger mandatory manual review.
- The application clearly separates rule-based statement affordability from model-validation evidence.
- Use only synthetic, anonymised, or consented data; minimise retention and do not expose records unnecessarily.

## Deferred work

PDF/image OCR, salary-slip and ITR parsing, deployment, authentication, database hosting, Docker, and SHAP/individual explainability remain deliberately out of scope.
