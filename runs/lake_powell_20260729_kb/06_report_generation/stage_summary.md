# Stage Summary: Report Generation

## 1. Stage status

- Run ID: lake_powell_20260729_kb
- Stage: 06_report_generation
- Status: completed
- Workflow version: v0.2

## 2. Inputs used

| Artifact | Path | Record count / scope |
|---|---|---|
| Source inventory | `../01_source_acquisition/sources/source_inventory.jsonl` | 66 |
| Evidence Units (canonical) | `../02_evidence_extraction/evidence_units.jsonl` | 442 |
| Knowledge Cards (canonical) | `../03_knowledge_consolidation/knowledge_cards.jsonl` | 81 |
| Synthesis Cards (canonical) | `../04_synthesis/synthesis_cards.jsonl` | 15 |

## 3. Outputs produced

| Artifact | Path | Format | Record count | Required |
|---|---|---|---:|---|
| Case-study report | `lake_powell_case_study_report.md` | markdown | 10 sections | yes |
| Claim-evidence map | `claim_evidence_map.jsonl` | jsonl | 30 | yes |

The report is a case-study report covering the governing operating framework, the 2026 drought-response actions, infrastructure/reliability risk at low elevation, HFE/sediment/ecological flow tools, governance and the post-2026 transition, an explicit section on contested or unresolved figures, and a validation/traceability summary. All 30 claims in `claim_evidence_map.jsonl` cite at least one Evidence Unit, Knowledge Card, or Synthesis Card ID plus source IDs; support levels used are `knowledge_card_support` (12), `synthesis_card_support` (13), and `source_checked` (5).

## 4. Automated validation

| Indicator | Status | Issue count | Validation artifact |
|---|---|---:|---|
| Schema conformance | pass | 0 | `automated_validation.json` |
| Traceability integrity | pass | 0 | `automated_validation.json` |

## 5. Human review

- Status: not_requested
- Review artifact: `human_review.json` (prefilled with the report file link and claim-evidence-map link; faithfulness/readability/value scores left null)
- Applicable criteria: faithfulness, readability, value (deferred; not requested for this routine run)

## 6. Cleanup

- Status: completed
- Removed intermediate paths: none

## 7. Warnings and unresolved issues

- The report explicitly documents five contested or unresolved figures carried over from Knowledge consolidation (powerplant discharge capacity, 2021-2022 DROA release volumes, the Cool Mix Alternative's monitoring location, the 1991 interim-criteria establishment date, and CRSS's historic-record-only elevation-projection basis) rather than resolving them; these remain open items for any future refinement pass.
- One projected (not yet observed) outcome is flagged explicitly in the report (Section 4, the projected 2026-2027 Lake Powell elevation recovery) and should be rechecked once later 24-Month Studies are available.
- The claim-evidence map covers the report's substantive analytical and quantitative claims; it does not include a separate entry for the corpus-level EU/KC coverage statistic mentioned in Section 8 (229 of 442 EUs not cited by any Knowledge Card), since that figure is a direct restatement of Stage 3's own validated automated-validation and stage-summary output rather than a new claim requiring independent evidentiary support.

## 8. Downstream readiness and next action

- Readiness: ready
- Next action: run cross-stage validation (`validation/scripts/build_cross_stage_summary.py` and `validation/scripts/validate_run_contract.py`) to complete run handoff.
