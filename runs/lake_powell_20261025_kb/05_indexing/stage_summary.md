# Stage Summary: Indexing

## 1. Stage status

- Run ID: lake_powell_20261025_kb
- Stage: 05_indexing
- Status: completed
- Workflow version: v0.2

## 2. Inputs used

| Artifact | Path | Record count / scope |
|---|---|---|
| Evidence Units (canonical) | `../02_evidence_extraction/evidence_units.jsonl` | 442 |
| Knowledge Cards (canonical) | `../03_knowledge_consolidation/knowledge_cards.jsonl` | 81 |
| Synthesis Cards (canonical) | `../04_synthesis/synthesis_cards.jsonl` | 19 |

## 3. Outputs produced

| Artifact | Path | Format | Record count | Required |
|---|---|---|---:|---|
| Encoded knowledge records | `encoded_knowledge_records.jsonl` | jsonl | 542 | yes |
| Index manifest | `index_manifest.json` | json | n/a | yes |

542 index records were built with `skills/indexing/scripts/build_index_records.py`: 442 evidence_unit, 81 knowledge_card, and 19 synthesis_card records, each preserving its source record ID, reservoir metadata, engineering dimension or primary pattern, confidence, evidence depth, and evidence-chain links. Encoding model is `structured_text_only`.

## 4. Automated validation

| Indicator | Status | Issue count | Validation artifact |
|---|---|---:|---|
| Schema conformance | pass | 0 | `automated_validation.json` |
| Traceability integrity | pass | 0 | `automated_validation.json` |

## 5. Human review

- Status: not_requested
- Review artifact: `human_review.json` (8 single-fact benchmark questions with gold index-record IDs, expected answer points, and retrieval depth fixed before retrieval; returned IDs filled by `skills/run-orchestration/scripts/run_lexical_retrieval_benchmark.py`; `source_adequacy_score` left null)
- Applicable criteria: recall, precision (computed from gold vs. returned IDs), source adequacy (not requested)

## 6. Cleanup

- Status: completed
- Removed intermediate paths: none

## 7. Warnings and unresolved issues

- No embedding or search backend was configured; records are deterministic structured text.
- The benchmark questions are reused unchanged from run `lake_powell_20260729_kb`. One gold Synthesis Card ID (IDX-QR-LP-007) was remapped from SC-LP-011 to SC-LP-014 because the cards were renumbered; the mapping is recorded in the item's `notes`.
- With the lexical token-overlap baseline at depth 10, mean recall is 0.667 and mean precision is 0.150, the same as in the earlier run. These figures characterize the baseline only.

## 8. Downstream readiness and next action

- Readiness: ready
- Next action: proceed to `06_report_generation` with 442 EUs, 81 KCs, 19 Synthesis Cards, and 542 index records.
