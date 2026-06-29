---
name: ku-extraction
description: Extract source-grounded operational knowledge units from reservoir operation documents. Use when the agent needs to turn reservoir source text, official reports, webpages, PDFs, technical memos, operating plans, data documentation, or research pages into concise operational KUs with evidence quotes, engineering dimensions, and JSONL validation.
---

# Reservoir KU Extraction

## Overview

Use this skill to extract document-level operational knowledge units from reservoir operation sources. The output is the KU layer only; do not write cross-document synthesis as KUs.

Core boundary:

```text
source text -> operational KUs
operational KUs -> synthesis analysis later
```

Preferred extraction pipeline:

```text
document -> page/section-aware chunks -> candidate KUs -> dedupe/consolidate -> validated KUs
```

KU role:

```text
KU = concise operational summary + locator back to source evidence
```

A KU should help the researcher quickly understand an operational point and quickly return to the original source location for review.

KUs are not intended to replace the source document. They are a structured index layer that reduces information fragmentation and makes later research easier, including synthesis, retrieval, engineering review, document comparison, and text-plus-time-series analysis.

## Workflow

1. Confirm the source inventory and extracted text files exist.
2. Generate full-coverage extraction packets with `scripts/make_extraction_packet.py`.
3. Read `references/extraction-protocol.md`.
4. Split long documents into page/section-aware chunks before extraction. Do not rely on first-N-character truncation.
5. Draft candidate KUs from each section or chunk.
6. Dedupe and consolidate candidates within the source before writing final KUs.
7. Write one JSON object per validated KU to `operational_kus.jsonl`.
8. Validate against `schemas/operational_ku.schema.json` or the run-specific KU validator.
9. If validation fails, repair the KU file; do not loosen the schema to pass.
10. Record whether the KU set has only automated validation or has also received human/domain research validation.

## KU Rules

Each KU must:

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

- `Operation Purpose`
- `Operation Rules`
- `Infrastructure`
- `Real-Time / Emergency Operations`
- `Coordination / Governance`
- `Operational Data`
- `Research / Modeling / Analysis`
- `Evidence Gap / Uncertainty`

## Extraction Standard

There is no fixed KU count limit per source. The number of KUs should be determined by how many distinct, source-grounded, operationally useful findings the document contains.

For short webpages, this may produce only a few KUs. For engineering manuals, operating manuals, operating plans, operation guides, environmental impact statements, technical appendices, or data documentation, this may produce many KUs. Extract zero KUs when a source is only navigation, duplicate metadata, or not operationally useful.

Official operating manuals, operation guides, reservoir operation plans, water control manuals, and similar authoritative rule documents are high-density priority sources. Do not summarize these documents only at a high level. Mine them for distinct operating purposes, rules, thresholds, release schedules, seasonal criteria, drought or emergency triggers, infrastructure limits, required data inputs, responsible agencies, and documentation requirements.

Prefer complete coverage of valid operational findings over an artificial count target. Still keep quality strict: do not split one operational finding into tiny fragments unless the fragments support different operational decisions, and consolidate repeated claims before finalizing.

## Required Output Fields

Use the project `operational_ku.schema.json` shape:

```json
{
  "ku_id": "KU-LP-OFFICIAL-001",
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
  "affected_operation_purposes": ["water_delivery"],
  "condition_or_trigger": "...",
  "evidence_quote": "...",
  "source_location": "extracted text; section or page if known",
  "confidence": "high",
  "extraction_method": "ku-extraction-skill",
  "notes": "..."
}
```

## Resources

- `references/extraction-protocol.md`: detailed extraction protocol, anti-patterns, and validation strategy.
- `scripts/make_extraction_packet.py`: create compact source packets from an inventory and extracted text files.

