---
name: synthesis-analysis
description: Synthesize reservoir operational KUs into source-grounded analysis cards. Use when the agent needs to analyze a reservoir KU JSONL file for recurring findings, complementary evidence, source discrepancies, operational tradeoffs, evidence gaps, or outstanding operational issues; create synthesis reports; or validate synthesis cards that cite KU IDs.
---

# Reservoir Synthesis Analysis

## Overview

Use this skill to build the synthesis layer on top of document-level reservoir KUs. The output is analysis, not new source evidence.

Core boundary:

```text
validated KUs -> consolidated knowledge points -> synthesis analysis cards
synthesis cards -> report / next research decisions
```

Do not write synthesis findings back into the KU layer.

The synthesis stage has two distinct parts:

1. **KU consolidation:** reorganize and restate the important source-grounded knowledge already extracted in the KU layer. This should preserve the KU taxonomy, such as Operation Purpose, Operation Rules, Infrastructure, Real-Time / Emergency Operations, Coordination / Governance, Operational Data, Research / Modeling / Analysis, and Evidence Gap / Uncertainty.
2. **Cross-KU analysis:** answer higher-level synthesis questions using the consolidated KU evidence, including recurring findings, complementary evidence, true source discrepancies, operational tradeoffs, evidence gaps in the source corpus, and outstanding operational issues.

Do not force every category or analysis type to appear. If the KU set does not contain meaningful evidence for a category or analysis type, omit it and record that it was not supported.

For v3/deep synthesis, do not rely only on KU summaries. Use KUs as the entry point, then retrieve and reread the relevant original source sections before making stronger cross-document claims.

V3 synthesis role:

```text
validated KUs -> KU consolidation -> candidate synthesis -> source locator rereading -> source-verified synthesis cards
```

## Workflow

1. Confirm the input KU JSONL exists and contains `knowledge_layer = document_finding`.
2. Read `references/synthesis-protocol.md`.
3. First produce KU consolidation outputs by grouping KUs under the approved KU dimensions and merging repeated or overlapping source-level findings.
4. For each KU dimension, write consolidated knowledge points only when the KU set contains meaningful evidence. Do not invent a category summary.
5. Then draft cross-KU synthesis observations across multiple consolidated points or KUs.
6. For v3/deep synthesis, return to the source chunks/sections indicated by the relevant KUs and verify the claim against original evidence.
7. Assign exactly one `analysis_type`.
8. Cite all supporting KU IDs in `based_on_ku_ids`.
9. Write one JSON object per synthesis card.
10. Keep `next_step` as an action field; do not use it as an analysis type.
11. Validate with `scripts/validate_synthesis_cards.py`.
12. Generate a readable report only after the cards validate.

## Analysis Types

Use only these types:

- `recurring_finding`
- `complementary_evidence`
- `source_discrepancy`
- `operational_tradeoff`
- `evidence_gap`
- `outstanding_operational_issue`

Use these analysis types only when the evidence supports them. In particular:

- `source_discrepancy` requires a real inconsistency about the same object, definition, time, status, or decision context. Different values from different scenarios, rule layers, forecast dates, or decision stages should usually be treated as complementary evidence with status/provenance metadata, not as a discrepancy.
- `evidence_gap` means the collected source corpus lacks enough evidence to answer an operational question. It does not mean the workflow failed to parse a table, figure, or time series. Method limitations belong in run notes or workflow limitations, not in synthesis cards.

## Required Output Fields

Use the project `synthesis.schema.json` shape:

```json
{
  "synthesis_id": "SYN-LP-V3-001",
  "knowledge_layer": "synthesis_analysis",
  "reservoir_id": "597",
  "reservoir_name": "<reservoir name>",
  "analysis_type": "recurring_finding",
  "title": "...",
  "summary": "...",
  "based_on_ku_ids": ["KU-LP-V2-001"],
  "interpretation": "...",
  "confidence": "high",
  "next_step": "...",
  "notes": "..."
}
```

## Quality Rules

Each synthesis card must:

- cite at least one KU ID, preferably multiple KUs for cross-document synthesis
- use KU IDs as locators back to original evidence for deep or high-confidence claims
- state whether evidence depth is `ku_only`, `source_checked`, or `source_checked_with_direct_quote`
- explain what source context was checked when a card is source-verified
- distinguish document discrepancy from operational tradeoff
- distinguish missing evidence from unresolved operational decisions
- distinguish true source discrepancy from scenario/date/status/version differences
- distinguish source-corpus evidence gaps from workflow extraction limitations
- avoid unsupported claims that cannot be traced back to cited KUs
- avoid becoming a generic literature-review paragraph
- omit unsupported analysis types instead of filling every category by default
- keep next-step recommendations in `next_step`, not in `analysis_type`

## V3 Optional Output Fields

Use these fields for source-verified synthesis cards:

- `evidence_depth`: `ku_only`, `source_checked`, or `source_checked_with_direct_quote`
- `source_locator_summary`: concise list of source locations reread for the synthesis claim
- `source_verification_note`: what the reread source context confirmed or changed
- `research_relevance`: `supports_story`, `needs_more_evidence`, or `background_only`

## Resources

- `references/synthesis-protocol.md`: detailed taxonomy, workflow, and anti-patterns.
- `scripts/validate_synthesis_cards.py`: validate synthesis JSONL against a KU JSONL file.

