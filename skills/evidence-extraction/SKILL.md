---
name: evidence-extraction
description: Extract source-grounded operational evidence units from reservoir operation documents. Use when the agent needs to turn reservoir source text, official reports, webpages, PDFs, technical memos, operating plans, data documentation, or research pages into concise operational EUs with evidence quotes, engineering dimensions, and JSONL validation.
---

# Reservoir Evidence Extraction

## Overview

Use this skill to extract document-level operational evidence units from reservoir operation sources. The output is the EU layer only; do not write cross-document synthesis as EUs.

Core boundary:

```text
source text -> operational EUs
operational EUs -> synthesis analysis later
```

Preferred extraction pipeline:

```text
document -> page/section-aware chunks -> candidate EUs -> validated EUs
```

EU role:

```text
EU = concise operational summary + locator back to source evidence
```

A EU should help the researcher quickly understand an operational point and quickly return to the original source location for review.

EUs are not intended to replace the source document. They are a structured index layer that reduces information fragmentation and makes later research easier, including synthesis, retrieval, engineering review, document comparison, and text-plus-time-series analysis.

## Workflow

1. Confirm the source inventory and extracted text files exist.
2. When running a method comparison, create one Codex Goal for this direct
   method before reading source text. Record the Goal objective and start time.
3. Create `02_evidence_extraction/source_inventory_eu_ready.jsonl` with `scripts/prepare_ku_ready_inventory.py`.
4. Generate full-coverage extraction packets at `02_evidence_extraction/extraction_packets.jsonl` with `scripts/make_extraction_packet.py`.
5. Read `references/extraction-protocol.md`.
6. Split long documents into page/section-aware chunks before extraction. Do not rely on first-N-character truncation.
7. Use LLM reasoning to draft candidate EUs from each section or chunk.
8. Remove exact or semantic duplicates that state the same operational fact.
   Keep different operational facts as separate EUs even when they share the
   same engineering dimension or broader topic.
9. Write one JSON object per validated EU to `evidence_units.jsonl`.
10. Validate with `scripts/validate_operational_kus.py`.
11. If validation fails, repair the EU file; do not loosen the schema to pass.
12. Render `evidence_units.md` with `scripts/render_ku_preview.py` as the
    required reading view of the validated JSONL.
13. Mark the method Goal complete and record reported token usage when available.
14. Record method runtime/token metrics in
    `validation/evidence_method_runtime_metrics.csv` when this extraction is part of
    a method comparison.
15. Record major step timing in `validation/evidence_method_step_metrics.csv`.
16. Record whether the EU set has only automated validation or has also received human/domain research validation.

## Validation

Follow `docs/validation-framework.md`. Before Knowledge consolidation, write
`02_evidence_extraction/automated_validation.json` and assess:

1. schema conformance of extraction packets and EUs;
2. traceability integrity from every EU through its source inventory record to
   preserved source material.

When human review is requested, use faithfulness, relevance, and value on a
documented EU sample. Write the review in `02_evidence_extraction/human_review.json`.
Run `validation/scripts/prepare_human_review.py --run-dir runs/<run_id> --stage evidence_extraction`
to prefill every sampled EU row with its Codex retain decision, approved
`engineering_dimension` topic, source locator, and relative links to the
preserved PDF and extracted text. Create `source_navigation.md` beside the
review JSON so the reviewer has directly clickable source links.

## EU Rules

Each EU must:

- be a document-level finding, not a cross-document conclusion
- be concise and self-contained
- function as both a summary and a source locator
- have one main engineering dimension
- explain why it matters for reservoir operation
- include a short evidence quote from the source
- cite `source_id`, `source_title`, `source_url`, and `source_location`
- preserve enough locator detail for later source rereading during deep synthesis
- avoid generic summaries, background boilerplate, and navigation text

Engineering dimensions:

- `Operation Purposes`
- `Multiple Objectives`
- `Storage Capacity and Storage Targets`
- `Operation Rules`
- `Emergency Operations`
- `Real-Time Operations`
- `Regulation / Governance`
- `Uncertainty and Risk Management`
- `Observation and Data`
- `Inflow Forecast`
- `Modeling`
- `Stakeholders`
- `Operation Failure`

For EUs about `Operation Purposes`, describe the supported purpose directly
using the terminology in the source. Do not add a separate
`affected_operation_purposes` field.

## Dimension Decision Rules

Assign the most specific supported dimension:

- Forecast values, forecast horizons, and probable/minimum/maximum inflow scenarios belong in `Inflow Forecast`.
- Observed records, data portals, variables, coverage, and monitoring products belong in `Observation and Data`.
- Models, simulation systems, scenario methods, decision frameworks, and modeling assumptions belong in `Modeling`.
- Laws, agreements, agency authority, NEPA/consultation processes, decision responsibility, and documentation requirements belong in `Regulation / Governance`.
- Rules, thresholds, release schedules, operating tiers, guide curves, if/then criteria, and formal triggers belong in `Operation Rules`.
- Storage capacity, elevation targets, minimum pool, dead pool, storage protection, and storage-related operating limits belong in `Storage Capacity and Storage Targets`.
- Emergency, drought, flood, infrastructure, or safety actions that change normal operation belong in `Emergency Operations`.
- Near-term operational adjustments, monitoring-based actions, maintenance operations, and special-event implementation belong in `Real-Time Operations`.

Do not put a EU in `Storage Capacity and Storage Targets` merely because it mentions storage or elevation. If the main point is a forecast, model, law, data record, or governance process, use that more specific dimension.

## Extraction Standard

There is no fixed EU count limit per source. The number of EUs should be determined by how many distinct, source-grounded, operationally useful findings the document contains.

For short webpages, this may produce only a few EUs. For engineering manuals, operating manuals, operating plans, operation guides, environmental impact statements, technical appendices, or data documentation, this may produce many EUs. Extract zero EUs when a source is only navigation, duplicate metadata, or not operationally useful.

Official operating manuals, operation guides, reservoir operation plans, water control manuals, and similar authoritative rule documents are high-density priority sources. Do not summarize these documents only at a high level. Mine them for distinct operating purposes, rules, thresholds, release schedules, seasonal criteria, drought or emergency triggers, infrastructure limits, required data inputs, responsible agencies, and documentation requirements.

Prefer complete coverage of valid operational findings over an artificial count
target. If multiple candidates state the same operational fact, retain one EU
with the clearest evidence and locator. Do not merge different facts merely
because they belong to the same engineering dimension, section, or broader
topic. Cross-document consolidation remains part of synthesis.

## Required Output Fields

Use the project `schemas/evidence_unit.schema.json` shape:

```json
{
  "eu_id": "EU-LP-OFFICIAL-001",
  "knowledge_layer": "document_finding",
  "reservoir_id": "597",
  "reservoir_name": "<reservoir name>",
  "source_id": "LP-OFFICIAL-001",
  "source_title": "...",
  "source_url": "...",
  "document_type": "agency_webpage",
  "engineering_dimension": "Operation Rules",
  "finding": "...",
  "why_it_matters": "...",
  "evidence_quote": "...",
  "source_location": "extracted text; section or page if known",
  "confidence": "high",
  "extraction_method": "evidence-extraction-skill",
  "notes": "..."
}
```

## Resources

The completed `02_evidence_extraction/` folder must also contain
`stage_manifest.json` and `stage_summary.md` as defined in
`docs/run-artifact-contract.md`.
After successful validation, finalize the stage to remove extraction packets
and other reproducible intermediates; retain `evidence_units.jsonl` and its
required `evidence_units.md` reading view.

- `references/extraction-protocol.md`: detailed extraction protocol, anti-patterns, and validation strategy.
- `scripts/prepare_ku_ready_inventory.py`: deterministic filter from source inventory to EU-ready inventory.
- `scripts/make_extraction_packet.py`: create compact source packets from an inventory and extracted text files.
- `scripts/validate_operational_kus.py`: backward-compatible structural validator for `evidence_units.jsonl`.
- `scripts/render_ku_preview.py`: render EU JSONL to the required Markdown reading view and optional summary JSON.

## Script Quick Reference

```powershell
python skills/evidence-extraction/scripts/prepare_ku_ready_inventory.py `
  --inventory runs/<run_id>/01_source_acquisition/sources/source_inventory.jsonl `
  --out runs/<run_id>/02_evidence_extraction/source_inventory_eu_ready.jsonl

python skills/evidence-extraction/scripts/make_extraction_packet.py `
  --inventory runs/<run_id>/02_evidence_extraction/source_inventory_eu_ready.jsonl `
  --out runs/<run_id>/02_evidence_extraction/extraction_packets.jsonl `
  --parse-manifest runs/<run_id>/01_source_acquisition/sources/docling_parse_manifest.jsonl

# After LLM/Codex writes runs/<run_id>/02_evidence_extraction/evidence_units.jsonl:
python skills/evidence-extraction/scripts/validate_operational_kus.py `
  --evidence-units runs/<run_id>/02_evidence_extraction/evidence_units.jsonl `
  --source-inventory runs/<run_id>/02_evidence_extraction/source_inventory_eu_ready.jsonl `
  --out runs/<run_id>/02_evidence_extraction/automated_validation.json

python skills/evidence-extraction/scripts/render_ku_preview.py `
  --evidence-units runs/<run_id>/02_evidence_extraction/evidence_units.jsonl `
  --out-md runs/<run_id>/02_evidence_extraction/evidence_units.md `
  --title "<Reservoir Name> Evidence Units"

```
