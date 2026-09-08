---
name: synthesis
description: Build source-grounded reservoir Synthesis Cards from validated Evidence Units and Knowledge Cards. Use when the agent needs to analyze decision processes, constraint structures, operational tradeoffs, operating-regime changes, historical operation failures, or operational consequences.
---

# Reservoir Synthesis

## Overview

Use this skill after Knowledge consolidation. It creates an analytical layer on
top of traceable Evidence Units (EUs) and Knowledge Cards (KCs). It does not
create new source evidence, reorganize EUs into KCs, or write unsupported
causal, legal, numerical, or historical claims.

```text
validated EUs + validated KCs
  -> candidate operational relationship
  -> original-source rereading when needed
  -> source-grounded Synthesis Card
```

EU and KC IDs are evidence locators, not substitutes for source reading. Use
them to return to the relevant original passages whenever a synthesis claim
depends on source context, formal authority, thresholds, dates, causal
language, historical events, implementation status, or an apparent conflict.

## Six Primary Synthesis Patterns

Each card has exactly one `primary_pattern`:

- `decision_process`: how information, rules, authority, judgment, and system
  conditions are translated into an operating decision or implementation.
- `constraint_structure`: how jointly relevant physical, operational, legal,
  ecological, infrastructural, or institutional constraints define the feasible
  operating space.
- `operational_tradeoff`: how competing objectives, risks, or stakeholder
  outcomes are connected through the same operation or constrained resource.
- `operating_regime_change`: how and why rules, objectives, constraints,
  capabilities, or decision environments change across time or operating
  regimes.
- `historical_operation_failure`: a documented historical episode in which an
  operational function, requirement, or target was not achieved, with cautious
  treatment of documented causes and consequences.
- `operational_consequence`: an observed, modeled, or projected consequence of
  an identified operation, rule, decision, or operating regime.

Use `secondary_lenses` only when they add a supported, subordinate perspective
to the primary pattern. Do not force every pattern to appear in a reservoir run.

## Workflow

1. Confirm validated EU and KC JSONL files exist.
2. Read `references/synthesis-protocol.md`.
3. Use KCs to identify related operational questions and the EUs that support
   them. Do not treat a KC as a replacement for the cited original sources.
4. Draft an operational relationship that is more than a restatement of one EU
   or KC.
5. Reread original source passages when the claim is important, technical,
   quantitative, causal, legal, historical, contested, or sensitive to date,
   scenario, status, version, or decision context.
6. Write one Synthesis Card with one primary pattern, an explicit scope, a
   supported analysis chain, EU/KC evidence links, and uncertainty or exceptions.
7. Record `evidence_depth`. For source-checked cards, include both a concise
   locator summary and a note explaining what rereading confirmed, narrowed,
   complicated, or rejected.
8. Validate with `scripts/validate_synthesis_cards.py` before indexing or
   report generation.
9. Render `synthesis_cards.md` with `scripts/render_synthesis_cards.py` as
   the required reading view of the validated JSONL.

## Validation

Follow `docs/validation-framework.md`. Before Indexing or Report generation,
write `04_synthesis/automated_validation.json` and assess:

1. schema conformance of Synthesis Cards;
2. traceability integrity from each cited EU/KC through to source evidence.

When human review is requested, use faithfulness, reasoning soundness, and
value on a documented Synthesis Card sample. Write the review in
`04_synthesis/human_review.json`.
Run `validation/scripts/prepare_human_review.py --run-dir runs/<run_id> --stage synthesis`. It prefills every
sampled card row with its primary pattern, full claim, scope and conditions,
analysis chain, uncertainty or exception, operational implication, and compact
EU/KC evidence summaries with locators and relative PDF/text links. Create
`source_navigation.md` beside the review JSON with directly clickable relative
Markdown links to the underlying sources and reading views.

## Common Card Requirements

Every Synthesis Card must include:

- one answerable `operational_question`;
- one evidence-constrained `synthesis_claim`;
- `scope_and_conditions` that preserves relevant dates, scenarios, statuses,
  locations, decision contexts, and exceptions;
- an `analysis_chain` that makes the supported relationship explicit;
- non-empty `based_on_eu_ids` and relevant `based_on_knowledge_card_ids`;
- an `evidence_role_map` showing how cited EUs support the analysis;
- `uncertainty_or_exception` and `operational_implication`;
- evidence-depth and original-source verification fields where applicable.

Do not use synthesis to store source discrepancy, corpus evidence gaps, or
generic source coverage observations. Those belong to validation, source review,
or research notes rather than the operational Synthesis Card layer.

## Required Output Shape

The completed `04_synthesis/` folder must also contain `stage_manifest.json`
and `stage_summary.md` as defined in `docs/run-artifact-contract.md`.
After successful validation, finalize the stage to remove synthesis work files
while retaining `synthesis_cards.jsonl` and its required human-readable view,
`synthesis_cards.md`.

Use `schemas/synthesis_card.schema.json` as the canonical record contract.

```json
{
  "synthesis_card_id": "SC-LP-001",
  "knowledge_layer": "synthesis_analysis",
  "reservoir_id": "597",
  "reservoir_name": "<reservoir name>",
  "primary_pattern": "decision_process",
  "secondary_lenses": [],
  "title": "How forecast information enters annual release decisions",
  "operational_question": "How do inflow forecasts affect annual-release decisions?",
  "synthesis_claim": "...",
  "scope_and_conditions": "...",
  "analysis_chain": [
    {"stage": "forecast signal", "statement": "...", "based_on_eu_ids": ["EU-LP-001"]},
    {"stage": "applicable rule", "statement": "...", "based_on_eu_ids": ["EU-LP-002"]}
  ],
  "based_on_eu_ids": ["EU-LP-001", "EU-LP-002"],
  "based_on_knowledge_card_ids": ["KC-LP-001"],
  "evidence_role_map": [
    {"role": "forecast input", "eu_ids": ["EU-LP-001"]},
    {"role": "formal rule", "eu_ids": ["EU-LP-002"]}
  ],
  "uncertainty_or_exception": "...",
  "operational_implication": "...",
  "confidence": "high",
  "next_step": "...",
  "evidence_depth": "source_checked",
  "source_locator_summary": "...",
  "source_verification_note": "...",
  "notes": "..."
}
```

`historical_operation_failure` may additionally include a `failure_episode`
object. `operational_consequence` must include `consequence_basis` with one of
`observed_consequence`, `modeled_consequence`, or `projected_consequence`.

## Output Contract

```text
04_synthesis/synthesis_cards.jsonl
04_synthesis/synthesis_cards.md
04_synthesis/automated_validation.json
04_synthesis/human_review.json
```

## Resources

- `references/synthesis-protocol.md`
- `scripts/validate_synthesis_cards.py`
- `scripts/render_synthesis_cards.py`
- `schemas/synthesis_card.schema.json`

## Script Quick Reference

```powershell
python skills/synthesis/scripts/render_synthesis_cards.py `
  --synthesis-cards runs/<run_id>/04_synthesis/synthesis_cards.jsonl `
  --out-md runs/<run_id>/04_synthesis/synthesis_cards.md `
  --title "<Reservoir Name> Synthesis Cards"
```
