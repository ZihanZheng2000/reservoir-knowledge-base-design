# Stage Summary: Knowledge Consolidation

## 1. Stage status

- Run ID: lake_powell_20260729_kb
- Stage: 03_knowledge_consolidation
- Status: completed
- Workflow version: v0.2

## 2. Inputs used

| Artifact | Path | Record count / scope |
|---|---|---|
| Evidence Units (canonical) | `../02_evidence_extraction/evidence_units.jsonl` | 442 |

## 3. Outputs produced

| Artifact | Path | Format | Record count | Required |
|---|---|---|---:|---|
| Knowledge Cards (canonical) | `knowledge_cards.jsonl` | jsonl | 81 | yes |
| Knowledge Cards reading view | `knowledge_cards.md` | markdown | 81 | yes |
| Source navigation | `source_navigation.md` | markdown | 50 sources | yes |

81 Knowledge Cards were created, covering 213 of 442 EUs (48%). Consolidation type: complementary_facts 54, repeated_fact 23, contested_or_unresolved 4. Engineering-dimension distribution of the cards: Operation Rules 20, Emergency Operations 11, Regulation/Governance 10, Storage Capacity and Storage Targets 8, Operation Failure 6, Uncertainty and Risk Management 6, Modeling 5, Observation and Data 4, Operation Purposes 4, Real-Time Operations 3, Inflow Forecast 2, Stakeholders 2.

Representative cards include: the Modified Low Fluctuating Flow baseline operating limits (min/max release, ramp rates, daily-fluctuation tiers) confirmed across 11 EUs from 8 sources spanning 1996-2018+; the 3,490 ft minimum power pool elevation confirmed across 8 EUs from 7 independent sources including 2024/2026 operational updates; the CRSS/RiverWare modeling framework used across planning studies; and several drought-response/low-reservoir-level trigger cards synthesizing the 2007 Interim Guidelines, 2019 DCP, 2024 SEIS, and 2024 Technical Decision Memorandum.

## 4. Automated validation

| Indicator | Status | Issue count | Validation artifact |
|---|---|---:|---|
| Schema conformance | pass | 0 | `automated_validation.json` |
| Traceability integrity | pass | 0 | `automated_validation.json` |

## 5. Human review

- Status: not_requested
- Review artifact: `human_review.json` (prefilled with all 81 KC rows: operational question, consolidated finding, consolidation type, supporting-EU table with locators and relative PDF/text links, Codex retain decision; human disposition/scores left null)
- Applicable criteria: faithfulness, consolidation appropriateness, value (deferred; not requested for this routine run)

## 6. Cleanup

- Status: completed
- Removed intermediate paths: none

## 7. Warnings and unresolved issues

- Consolidation was distributed across 6 parallel review passes, one per engineering-dimension group (Operation Rules; Regulation/Governance + Operation Purposes; Emergency/Real-Time/Stakeholders; Storage/Inflow Forecast/Multiple Objectives; Modeling/Observation and Data; Uncertainty/Operation Failure), so that all 442 EUs could be reviewed for consolidation within one session. Each pass only clustered EUs answering the same narrow operational question within its own dimension group; an EU whose closest conceptual match sits in a different dimension group was left unclustered rather than force-merged across groups. This is a scope limitation worth noting for any future refinement pass, not a defect in the cards produced.
- 213 of 442 EUs (48%) are cited by at least one Knowledge Card. The remaining 229 EUs are treated as single, non-duplicated findings with no identified repeat or complement in this pass and are not represented in any KC. This follows the protocol's conservative grouping rule (only consolidate genuine same-question repeats/complements/contested pairs) rather than reflecting missing coverage.
- All 6 fragment outputs were structurally validated (required fields; `consolidation_type`/`confidence` enum membership; `based_on_eu_ids` resolving to real records in `evidence_units.jsonl` with `minItems=2`) before merging into the canonical `knowledge_cards.jsonl`; 0 duplicate `knowledge_card_id` values were found across the 6 fragments.
- 4 Knowledge Cards are marked `consolidation_type=contested_or_unresolved`, meaning EUs from different sources appear numerically or categorically inconsistent about the same operational question even after preserving date/status/version context. These are intentionally preserved as unresolved (both readings retained in `consolidated_finding`) rather than force-resolved; they are flagged here as a limitation to note if Synthesis or a future human review needs to reread the original sources to adjudicate them.

## 8. Downstream readiness and next action

- Readiness: ready
- Next action: proceed to `04_synthesis` using the 442 validated EUs and 81 validated Knowledge Cards.
