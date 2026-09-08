---
name: indexing
description: Encode validated reservoir Evidence Units, Knowledge Cards, and Synthesis Cards into index-ready records while preserving evidence chains. Use when the knowledge base needs an embedding, keyword, hybrid-search, or other searchable index representation.
---

# Reservoir Knowledge-Base Indexing

## Overview

Use this skill after Synthesis validation. It is an offline encoding and index
preparation stage. It does not retrieve records, answer user questions, create
benchmark questions, or evaluate a retrieval system.

```text
validated EUs + KCs + Synthesis Cards -> encoded index records -> index manifest
```

## Workflow

1. Confirm validated EU, KC, and Synthesis Card JSONL files exist.
2. Create one index record per selected knowledge-base record; do not create
   new findings or analytical claims.
3. Build concise `index_text` from the record content and its material context.
4. Preserve record type, stable IDs, reservoir metadata, engineering dimension
   or analysis type, confidence, evidence depth, and evidence-chain IDs.
5. Encode the records with the selected index backend when one is configured.
6. Write the encoded record manifest and index metadata under `05_indexing/`.

Use `scripts/build_index_records.py` to produce the deterministic,
index-ready text records. A configured embedding or search backend may consume
those records afterward; that backend is not a retrieval or evaluation step.

## Validation

Follow `docs/validation-framework.md`. Validate index records before they are
released for search use and write `05_indexing/automated_validation.json`.
Assess schema conformance and traceability integrity back to validated EU, KC,
and Synthesis Card records.

When human review is requested, perform a retrieval evaluation after indexing
with a documented question set. Use recall, precision, and source adequacy;
write the query-level review in `05_indexing/human_review.json`.
Define simple,
plain-language benchmark questions that retrieve one directly documented fact,
not a cross-record reasoning task. Before running retrieval, prefill each row
with its required gold index-record IDs, optional supporting records, expected
answer points, and retrieval depth. After retrieval, record the retrieval
status, returned IDs, and answer. The run summary calculates recall and
precision from the returned IDs and the predefined relevance set. The human
reviewer fills only `source_adequacy_score` (0/1/2) plus optional notes and
required action.

## Index Record Requirements

Each record must include:

- `index_record_id`;
- `record_type`: `evidence_unit`, `knowledge_card`, or `synthesis_card`;
- `record_id` for the EU, KC, or Synthesis Card;
- reservoir ID and name;
- concise `index_text`;
- engineering dimension or primary synthesis pattern as applicable;
- source IDs, EU IDs, KC IDs, and source locators as applicable;
- confidence and evidence-depth fields when available;
- encoding model, index backend, and build timestamp in the manifest.

Use `schemas/index_record.schema.json` as the canonical record contract.

Do not index raw source chunks as primary knowledge-base records. They may be
kept as a separately labelled fallback corpus when needed, but never replace
the traceable EU/KC/Synthesis Card layers.

## Output Contract

The completed `05_indexing/` folder must also contain `stage_manifest.json`
and `stage_summary.md` as defined in `docs/run-artifact-contract.md`.
After successful validation, finalize the stage to remove explicitly labelled
temporary index work files while retaining canonical index records and manifest.

```text
05_indexing/encoded_knowledge_records.jsonl
05_indexing/index_manifest.json
```

```powershell
python skills/indexing/scripts/build_index_records.py `
  --evidence-units runs/<run_id>/02_evidence_extraction/evidence_units.jsonl `
  --knowledge-cards runs/<run_id>/03_knowledge_consolidation/knowledge_cards.jsonl `
  --synthesis-cards runs/<run_id>/04_synthesis/synthesis_cards.jsonl `
  --out runs/<run_id>/05_indexing/encoded_knowledge_records.jsonl `
  --manifest runs/<run_id>/05_indexing/index_manifest.json

python skills/indexing/scripts/validate_index_records.py `
  --index-records runs/<run_id>/05_indexing/encoded_knowledge_records.jsonl `
  --index-manifest runs/<run_id>/05_indexing/index_manifest.json `
  --evidence-units runs/<run_id>/02_evidence_extraction/evidence_units.jsonl `
  --knowledge-cards runs/<run_id>/03_knowledge_consolidation/knowledge_cards.jsonl `
  --synthesis-cards runs/<run_id>/04_synthesis/synthesis_cards.jsonl `
  --out runs/<run_id>/05_indexing/automated_validation.json
```
