# Stage Summary: Report Generation

## 1. Stage status

- Run ID: lake_powell_20261025_kb
- Stage: 06_report_generation
- Status: completed
- Workflow version: v0.2

## 2. Inputs used

| Artifact | Path | Record count / scope |
|---|---|---|
| Source inventory | `../01_source_acquisition/sources/source_inventory.jsonl` | 66 |
| Evidence Units (canonical) | `../02_evidence_extraction/evidence_units.jsonl` | 442 |
| Knowledge Cards (canonical) | `../03_knowledge_consolidation/knowledge_cards.jsonl` | 81 |
| Synthesis Cards (canonical) | `../04_synthesis/synthesis_cards.jsonl` | 19 |

## 3. Outputs produced

| Artifact | Path | Format | Record count | Required |
|---|---|---|---:|---|
| Case-study report | `lake_powell_case_study_report.md` | markdown | 1 | yes |
| Claim-evidence map | `claim_evidence_map.jsonl` | jsonl | 32 | yes |

The report has 10 sections. Sections 3-8 contain 32 numbered claims; each claim cites its Synthesis Card and Knowledge Card IDs inline, carries a `[CLM-xxx]` tag, and appears verbatim in `claim_evidence_map.jsonl` with its EU, KC, SC, and source IDs. All 19 Synthesis Cards are cited. All claims have support level `synthesis_card_support`; every cited card is `source_checked_with_direct_quote`.

## 4. Automated validation

| Indicator | Status | Issue count | Validation artifact |
|---|---|---:|---|
| Schema conformance | pass | 0 | `automated_validation.json` |
| Traceability integrity | pass | 0 | `automated_validation.json` |

## 5. Human review

- Status: not_requested
- Review artifact: `human_review.json` (prefilled by `validation/scripts/prepare_human_review.py`; scores left blank)
- Applicable criteria: faithfulness, readability, value

## 6. Cleanup

- Status: completed
- Removed intermediate paths: none

## 7. Warnings and unresolved issues

- No PDF rendering was produced; the Markdown report is the canonical output.
- Section 8 of the report states the open questions carried from the Synthesis Cards (conflicting 2021 DROA volumes, the 1991 date discrepancy, the DROA term question, and the untested Compact-shortfall claim).

## 8. Downstream readiness and next action

- Readiness: ready
- Next action: run the cross-stage validation summary, validation report, and run-contract check.
