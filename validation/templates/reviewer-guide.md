# Reviewer Guide

Review the assigned item against its cited evidence, not against writing style or
method identity. Use only integer scores 0-5. Mark `not_reviewable=true` when the
source or locator cannot be accessed; explain why instead of assigning zero.

## Scoring anchors

| Score | Anchor |
|---:|---|
| 5 | Correct, specific, well supported, and directly usable |
| 4 | Correct with a minor wording, scope, or locator issue |
| 3 | Substantively usable after revision |
| 2 | Partially supported or useful, with a clear material problem |
| 1 | Marginal relevance or very weak support |
| 0 | Unsupported, incorrect, irrelevant, or contradicts accessible evidence |

## Issue codes

- `UNSUPPORTED`: evidence does not support the claim.
- `OVERSTATED`: claim is stronger or broader than the evidence.
- `MISCLASSIFIED`: wrong engineering dimension or analysis type.
- `OVERMERGED`: distinct claims or contexts were combined.
- `FRAGMENTED`: one finding was split without operational reason.
- `DUPLICATE`: semantically duplicates another item.
- `WEAK_LOCATOR`: cited location is insufficient for verification.
- `MISSED_CONTEXT`: condition, date, scenario, status, or limitation was omitted.
- `NON_OPERATIONAL`: background content without operational value.
- `BROKEN_LINK`: KU/source/synthesis reference does not resolve.
- `NOT_REVIEWABLE`: evidence is inaccessible or corrupted.

Reviewers may assign multiple codes separated by semicolons. Comments should
identify the smallest correction needed. Do not discuss scores with another
reviewer before independent scoring is frozen.

