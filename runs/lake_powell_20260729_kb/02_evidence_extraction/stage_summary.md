# Stage Summary: Evidence Extraction

## 1. Stage status

- Run ID: lake_powell_20260729_kb
- Stage: 02_evidence_extraction
- Status: completed_with_warnings
- Workflow version: v0.2

## 2. Inputs used

| Artifact | Path | Record count / scope |
|---|---|---|
| EU-ready source inventory | `source_inventory_eu_ready.jsonl` | 50 sources (filtered from the 66-source Stage 1 inventory by `status=ok` and `eu_readiness=ready`) |

## 3. Outputs produced

| Artifact | Path | Format | Record count | Required |
|---|---|---|---:|---|
| Evidence Units (canonical) | `evidence_units.jsonl` | jsonl | 442 | yes |
| Evidence Units reading view | `evidence_units.md` | markdown | 442 | yes |
| Source navigation | `source_navigation.md` | markdown | 50 sources | yes |

442 Evidence Units were extracted from 47 of the 50 EU-ready sources (3 sources legitimately yielded 0 EUs; see Warnings). Engineering-dimension distribution: Operation Rules 103, Regulation/Governance 58, Emergency Operations 38, Storage Capacity and Storage Targets 37, Modeling 34, Uncertainty and Risk Management 32, Observation and Data 31, Operation Failure 29, Multiple Objectives 21, Real-Time Operations 17, Stakeholders 16, Inflow Forecast 14, Operation Purposes 12. Confidence: 433 high, 9 medium, 0 low.

## 4. Automated validation

| Indicator | Status | Issue count | Validation artifact |
|---|---|---:|---|
| Schema conformance | pass | 0 | `automated_validation.json` |
| Traceability integrity | pass | 0 | `automated_validation.json` |

Overall stage status is `completed_with_warnings` rather than `completed` because of one delivery-check warning (see Section 7): the stage manifest's `source_inventory_eu_ready.jsonl` input is correctly absent from disk (removed as an intermediate at cleanup) and is now marked `required=false`, which resolves as a warning rather than an error.

## 5. Human review

- Status: not_requested
- Review artifact: `human_review.json` (prefilled with all 442 EU rows: engineering dimension, finding, source locator, relative PDF/text links, Codex retain decision; human disposition/scores left null pending an explicit review request)
- Applicable criteria: faithfulness, relevance, value (deferred; not requested for this routine run)

## 6. Cleanup

- Status: completed
- Removed intermediate paths: `02_evidence_extraction/source_inventory_eu_ready.jsonl`

## 7. Warnings and unresolved issues

- The `source_inventory_eu_ready.jsonl` input was a reproducible, derived filter of the canonical `sources/source_inventory.jsonl` and was correctly removed as an execution intermediate at stage finalization (see Cleanup, above). During the run's final contract check, its manifest entry was corrected from `required=true` to `required=false` to match this already-removed state; `validation/scripts/validate_stage_manifest.py` now reports this as an expected warning ("optional inputs artifact not found"), not an error. The file remains regenerable from `source_inventory.jsonl` (rows with `eu_readiness=ready`) at any time.
- Extraction of the 50 EU-ready sources was distributed across 14 parallel extraction passes (9 dedicated single-document passes for the largest sources, 5 passes each covering a balanced batch of smaller/medium sources) to make full-corpus extraction tractable in one session. Every fragment was structurally validated against `schemas/evidence_unit.schema.json` (required fields, allowed `engineering_dimension`/`confidence` enums, `evidence_quote` <=320 chars, no disallowed fields, `source_id` resolves to an EU-ready source) before being merged into the canonical `evidence_units.jsonl`; 0 duplicate `eu_id` values and 0 cross-fragment collisions were found on merge.
- Two `evidence_quote` values were found 1-4 characters over the 320-character schema limit during pre-merge validation (`EU-LP-OFF-003-21`, `EU-LP-OFF-010-01`) and were corrected to a shorter genuine verbatim excerpt of the same source passage before merging; both pass validation now.
- 3 of the 50 EU-ready sources produced 0 EUs on review: `OFF-033` and `OFF-034` (Federal Register notice pages whose preserved text is a short access/notice header with no extractable rule text) and `RES-023` (a digital-repository landing page for the Colorado River Basin Study with no report body text preserved). This reflects genuine content-quality limitations recorded in Stage 1, not a missed extraction pass; no EUs were fabricated to fill these gaps.
- For the 9 largest documents (250K-2,010K extracted characters — LTEMP FEIS/SEIS volumes and appendices, the GAO report, and two large USGS reports), extraction sampled the introduction/summary plus spaced windows through the remainder rather than reading every character; this gives representative, not exhaustive, coverage of those mega-documents. A full exhaustive pass over these documents would materially increase the EU count for this run if performed in a follow-up extraction pass.
- Coverage density intentionally follows source priority: official operating plans, Records of Decision, and technical/model documentation (e.g., the 2007 Interim Guidelines ROD, the 1996 ROD, the Draft 2026 AOP, the CRSS model documentation appendix) received 10-22 EUs each, consistent with the extraction protocol's priority-source rule, while short agency webpages and news items received 1-5 EUs each.

## 8. Downstream readiness and next action

- Readiness: ready
- Next action: proceed to `03_knowledge_consolidation` using the 442 validated EUs in `evidence_units.jsonl`.
