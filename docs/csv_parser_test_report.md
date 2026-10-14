# CSV parser test report

Command run: `python -m pytest -q`

This report is a historical parser-coverage summary. The current full suite is run with `python -m pytest -q`; see `CLAIMS.md` for the boundary between software correctness tests and real-world validation.

## Parser coverage

| Scenario | Expected behaviour | Automated coverage |
|---|---|---|
| Required schema missing | Reject when date/description or both financial amount columns are absent | Yes |
| Empty CSV | Clear error rather than analysis | Yes |
| Invalid date | Drop invalid transaction and reduce quality score | Yes |
| Indian currency | Parse values such as `₹50,000` and `15,000` | Yes |
| Invalid amount text | Convert to zero, warn, and reduce quality score | Yes |
| Negative debit/credit | Reject source data | Yes |
| Duplicate transaction | Remove exact duplicate and add warning | Yes |
| Signed amount column | Positive values become credits and negative values become debits | Yes |
| Both debit and credit | Exclude contradictory row and report it | Yes |
| Zero-value transaction | Exclude row and report it | Yes |
| Ambiguous category | Mark multi-match descriptions as uncertain / needs review | Yes |
| Fewer than three months | Add quality warning and enforce manual review | Yes |
| Missing salary | Add quality warning and refer for additional documents | Yes |
| Zero income / negative savings | Feature calculation remains safe and rule policy responds | Yes |
| High EMI burden | Affordability policy enforces review safeguard above 50% | Yes |
| Policy outcomes | Approve, manual-review, and decline paths | Yes |

The optional pytest cache warning on Windows is unrelated to test outcomes; it only prevents pytest from storing its local cache.
