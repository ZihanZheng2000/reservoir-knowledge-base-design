---
name: retrieval-indexing
description: Build and validate retrieval-ready records and semantic indexes from validated reservoir KUs and synthesis records. Use when the agent needs to prepare embedding records, metadata filters, benchmark questions, retrieval evaluation, or evidence-chain-preserving search outputs.
---

# Reservoir Retrieval Indexing

## Overview

Use this skill after KU extraction and synthesis validation. The goal is to convert validated KUs and synthesis records into retrieval-ready records while preserving evidence chains.

Core boundary:

```text
validated KUs + synthesis records -> retrieval-ready records + benchmark evaluation
```

Do not create new KUs or new synthesis claims in this skill. Retrieval records should reuse validated content.

## Workflow

1. Confirm validated KU and synthesis JSONL files exist.
2. Read `references/retrieval-indexing-protocol.md`.
3. Build embedding-ready records with normalized text and metadata.
4. Preserve links to source IDs, KU IDs, synthesis IDs, source locations, and evidence quotes.
5. Create or update benchmark retrieval questions.
6. Run top-k retrieval evaluation when a retrieval backend is available.
7. Write validation outputs under the run's `validation/` folder.

## Retrieval Record Requirements

Each retrieval-ready record should include:

- stable record ID;
- reservoir ID and name;
- record type: `source_ku`, `synthesis_record`, or `report_claim`;
- searchable text;
- engineering dimension or synthesis type;
- source tier metadata where available;
- supporting KU IDs;
- source IDs and source locators;
- confidence or evidence-depth fields when available.

## Output Contract

A completed retrieval/indexing stage should contain:

- `retrieval/retrieval_records.jsonl`
- `retrieval/benchmark_questions.jsonl`
- `validation/retrieval_validation.json`
- optional vector index files if a backend is used


