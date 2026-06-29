---
name: report-generation
description: Generate evidence-grounded reservoir operation reports from validated KUs, synthesis records, retrieval outputs, and source metadata. Use when the agent needs to create human-readable reports, claim-evidence maps, report validation samples, or presentation-ready case-study summaries.
---

# Reservoir Report Generation

## Overview

Use this skill after KU extraction, synthesis, and optional retrieval preparation. The goal is to turn validated structured knowledge into readable reports without losing evidence traceability.

Core boundary:

```text
validated KUs + synthesis records + source metadata -> human-readable report + claim evidence map
```

Do not introduce unsupported claims. Report claims must cite KUs, synthesis records, or source IDs.

## Workflow

1. Confirm validated KUs, synthesis records, and source inventory exist.
2. Read `references/report-generation-protocol.md`.
3. Select report type: technical report, short briefing, case-study summary, or validation report.
4. Build a report outline from validated KUs and synthesis records.
5. Draft report sections with citation links to KU IDs, synthesis IDs, or source IDs.
6. Create a claim-evidence map for substantive claims.
7. Sample report claims for traceability and faithfulness review.
8. Write final report outputs under the run's `reports/` folder.

## Report Rules

Reports should:

- separate source-grounded findings from interpretation;
- explicitly mark uncertainty, evidence gaps, and unresolved issues;
- preserve citations to KUs, synthesis records, or source IDs;
- avoid claims that cannot be traced to validated evidence;
- use reservoir-domain language and avoid generic AI summaries.

## Output Contract

A completed report-generation stage should contain:

- `reports/<report_name>.md`
- `reports/claim_evidence_map.jsonl`
- `validation/report_validation_sample.md`
- optional PDF, Word, or slide outputs when requested


