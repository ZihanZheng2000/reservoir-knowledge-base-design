---
name: knowledge-consolidation
description: Consolidate validated reservoir Evidence Units into traceable Knowledge Cards. Use when the agent needs to organize repeated or complementary document-level evidence around the same operational question without making cross-document analytical claims.
---

# Reservoir Knowledge Consolidation

## Overview

Use this skill after Evidence extraction and before Synthesis. It creates the
knowledge-consolidation layer; it does not create new source evidence or
cross-document analysis.

```text
validated Evidence Units -> Knowledge Cards -> Synthesis later
```

An Evidence Unit (EU) is a finding from one source. A Knowledge Card (KC)
conservatively organizes one or more EUs that answer the same operational
question. A KC must preserve the evidence chain and all material conditions.

## Workflow

1. Confirm that the validated EU JSONL exists and every record has
   `knowledge_layer = document_finding`.
2. Read `references/knowledge-consolidation-protocol.md`.
3. Group EUs first by approved engineering dimension and then by the
   `operational_question` they answer. Do not merge records merely because
   they share a broad topic.
4. Create one Knowledge Card only for repeated facts, complementary facts, or
   a meaningfully contested or unresolved point.
5. Preserve separate rules, thresholds, facilities, dates, scenarios, statuses,
   and decision contexts when they answer different operational questions.
6. Cite every supporting EU ID in `based_on_eu_ids`.
7. Validate the Knowledge Card JSONL with
   `scripts/validate_knowledge_cards.py` before passing it to Synthesis.
8. Render `knowledge_cards.md` with `scripts/render_knowledge_cards.py` as
   the required reading view of the validated JSONL.

## Validation

Follow `docs/validation-framework.md`. Before Synthesis, write
`03_knowledge_consolidation/automated_validation.json` and assess:

1. schema conformance of Knowledge Cards;
2. traceability integrity from each cited EU through to source evidence.

When human review is requested, use faithfulness, consolidation
appropriateness, and value on a documented KC sample. Write the review in
`03_knowledge_consolidation/human_review.json`.
Run `validation/scripts/prepare_human_review.py --run-dir runs/<run_id> --stage knowledge_consolidation`.
It prefills every sampled KC row with its approved engineering-dimension topic,
title, full consolidated finding, consolidation type, coverage limitation, and
a compact supporting-EU table containing each EU finding, locator, and
relative PDF/text links. Create `source_navigation.md` beside the review JSON
with directly clickable relative Markdown links to the source files.

## Knowledge Card Rules

Each Knowledge Card must:

- state one operational question;
- use one `consolidation_type`: `repeated_fact`, `complementary_facts`, or
  `contested_or_unresolved`;
- preserve source-defined names, values, dates, units, thresholds, statuses,
  and rule contexts;
- cite every supporting EU ID;
- remain an evidence organization record, not an inferred relationship,
  recommendation, or conclusion.

Do not create a card for a dimension without meaningful evidence. Do not
resolve an apparent disagreement unless the supporting source context directly
explains it; preserve the disagreement for Synthesis and source rereading.

## Required Output Fields

Use `schemas/knowledge_card.schema.json` as the canonical record contract.

```json
{
  "knowledge_card_id": "KC-LP-001",
  "knowledge_layer": "knowledge_consolidation",
  "reservoir_id": "597",
  "reservoir_name": "<reservoir name>",
  "engineering_dimension": "Operation Rules",
  "operational_question": "What annual release rule applies under the stated conditions?",
  "title": "Annual release rule evidence",
  "consolidated_finding": "...",
  "based_on_eu_ids": ["EU-LP-001", "EU-LP-002"],
  "consolidation_type": "complementary_facts",
  "source_coverage_note": "...",
  "confidence": "high",
  "notes": "..."
}
```

## Output Contract

The completed `03_knowledge_consolidation/` folder must also contain
`stage_manifest.json` and `stage_summary.md` as defined in
`docs/run-artifact-contract.md`.
After successful validation, finalize the stage to remove its `work/`
intermediates while retaining `knowledge_cards.jsonl` and its required
human-readable view, `knowledge_cards.md`.

```text
03_knowledge_consolidation/knowledge_cards.jsonl
03_knowledge_consolidation/knowledge_cards.md
03_knowledge_consolidation/automated_validation.json
03_knowledge_consolidation/human_review.json
```

## Resources

- `references/knowledge-consolidation-protocol.md`
- `scripts/validate_knowledge_cards.py`
- `scripts/render_knowledge_cards.py`
- `schemas/knowledge_card.schema.json`

## Script Quick Reference

```powershell
python skills/knowledge-consolidation/scripts/render_knowledge_cards.py `
  --knowledge-cards runs/<run_id>/03_knowledge_consolidation/knowledge_cards.jsonl `
  --out-md runs/<run_id>/03_knowledge_consolidation/knowledge_cards.md `
  --title "<Reservoir Name> Knowledge Cards"
```
