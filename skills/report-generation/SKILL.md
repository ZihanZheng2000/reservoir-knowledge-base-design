---
name: report-generation
description: Generate evidence-grounded reservoir operation reports from validated Evidence Units, Knowledge Cards, Synthesis Cards, and source metadata. Use when the agent needs to create human-readable reports, claim-evidence maps, report validation samples, or presentation-ready case-study summaries.
---

# Reservoir Report Generation

## Overview

Use this skill after Evidence extraction, Knowledge consolidation, and Synthesis. The goal is to turn validated structured knowledge into readable reports without losing evidence traceability.

Core boundary:

```text
validated EUs + Knowledge Cards + Synthesis Cards + source metadata -> human-readable report + claim evidence map
```

Do not introduce unsupported claims. Report claims must cite EUs, Knowledge Cards, Synthesis Cards, or source IDs.

## Workflow

1. Confirm validated EUs, Knowledge Cards, Synthesis Cards, and source inventory exist.
2. Read `references/report-generation-protocol.md`.
3. Select report type: technical report, short briefing, case-study summary, or validation report.
4. Build a report outline from validated EUs, Knowledge Cards, and Synthesis Cards.
5. Draft report sections with citation links to EU IDs, KC IDs, Synthesis Card IDs, or source IDs.
6. Create a claim-evidence map for substantive claims.
7. Sample report claims for traceability and faithfulness review.
8. Write final report outputs under the run's `06_report_generation/` folder.

## Validation

Follow `docs/validation-framework.md`. Validate the claim-evidence map and
report artifacts, writing `06_report_generation/automated_validation.json`.
Assess schema conformance and traceability integrity from every material claim
through validated records to source evidence.

When human review is requested, use faithfulness, readability, and value for
the report as a whole. Record one report-level review in
`06_report_generation/human_review.json`.
Run `validation/scripts/prepare_human_review.py --run-dir runs/<run_id> --stage report_generation`
to prefill the report and claim-evidence-map links. The claim-evidence map remains
the automated traceability artifact; do not require per-claim human scoring.

## Report Rules

Reports should:

- separate source-grounded findings from interpretation;
- explicitly mark uncertainty, evidence gaps, and unresolved issues;
- preserve citations to EUs, Knowledge Cards, Synthesis Cards, or source IDs;
- avoid claims that cannot be traced to validated evidence;
- use reservoir-domain language and avoid generic AI summaries.

## Output Contract

The completed `06_report_generation/` folder must also contain
`stage_manifest.json` and `stage_summary.md` as defined in
`docs/run-artifact-contract.md`.
After successful validation, finalize the stage to remove report work files
while retaining the final report and claim-evidence map.

A completed report-generation stage should contain:

- `06_report_generation/<report_name>.md`
- `06_report_generation/claim_evidence_map.jsonl`
- `06_report_generation/automated_validation.json`
- `06_report_generation/human_review.json`
- optional PDF, Word, or slide outputs when requested

```powershell
python skills/report-generation/scripts/validate_claim_evidence_map.py `
  --claim-evidence-map runs/<run_id>/06_report_generation/claim_evidence_map.jsonl `
  --source-inventory runs/<run_id>/01_source_acquisition/sources/source_inventory.jsonl `
  --evidence-units runs/<run_id>/02_evidence_extraction/evidence_units.jsonl `
  --knowledge-cards runs/<run_id>/03_knowledge_consolidation/knowledge_cards.jsonl `
  --synthesis-cards runs/<run_id>/04_synthesis/synthesis_cards.jsonl `
  --report runs/<run_id>/06_report_generation/<report_name>.md `
  --out runs/<run_id>/06_report_generation/automated_validation.json
```
