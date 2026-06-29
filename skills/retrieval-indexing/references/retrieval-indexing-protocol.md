# Retrieval Indexing Protocol

## Purpose

Retrieval indexing makes the reservoir knowledge base searchable while preserving the evidence chain needed for review.

## Indexing Units

Use validated structured records as retrieval units:

- source-level operational KUs;
- cross-document synthesis records;
- report claims only when they cite KUs or synthesis records.

Do not index raw source chunks as the primary knowledge-base units unless they are clearly marked as source text. Raw chunks can support fallback search, but the main retrieval objects should remain curated KUs and synthesis records.

## Record Text

The searchable text should be concise and meaningful:

- KU records: use finding, why-it-matters, engineering dimension, condition/trigger, and evidence cue.
- Synthesis records: use summary, interpretation, synthesis type, implication, and uncertainty.
- Report-claim records: use the claim and citation chain.

## Metadata

Include metadata that supports filtered search:

- reservoir ID and name;
- engineering dimension;
- synthesis type;
- source tier;
- source document type;
- confidence;
- evidence depth;
- validation status.

## Evaluation

Create benchmark questions covering:

- operation purpose;
- operation rules;
- infrastructure constraints;
- data/models;
- real-time or emergency operations;
- coordination/governance;
- evidence gaps or uncertainty;
- cross-document synthesis questions.

Evaluate top-k retrieval with precision, recall, F2, and traceability rate on sampled benchmark questions.

