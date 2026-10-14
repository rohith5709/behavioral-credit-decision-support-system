# Independent transaction-category validation

The category rules are transparent keyword rules. The included regression and
coverage fixtures protect known behaviour during code changes; they are **not**
evidence of real-world categorisation accuracy.

## Data collection protocol

1. Obtain consented, anonymised transaction exports from multiple bank formats.
2. Remove account numbers, names, UPI identifiers, reference IDs, addresses,
   and any free text that can identify a customer. Retain only the minimum
   transaction description needed to label a category.
3. Use `data/evaluation/independent_category_labels_template.csv` to record
   each example. Do not commit real customer data to this repository.
4. Use at least two reviewers for a sample of records. Resolve disagreements
   before assigning `expected_category`.
5. Partition cases—not random individual transactions—into `development` and
   `heldout` sets so descriptions from the same account or merchant family do
   not leak between them.
6. Freeze the held-out set before changing keyword rules. Tune only with the
   development set.
7. Run `python -m src.evaluation.evaluate_categories` separately for each
   dataset and report the held-out precision, recall, F1-score, support, and
   confusion matrix by category.

## Reporting rule

Do not report the fixture's 100% F1-score as production accuracy. The project
may report real category performance only after a frozen, independently
labelled held-out dataset exists.
