# Lake Powell Demo Dataset

Preliminary, validated demo dataset for the Lake Powell / Glen Canyon Dam
knowledge base. This is a direct, unmodified copy of the canonical outputs
from run [`runs/lake_powell_20260729_kb`](../../runs/lake_powell_20260729_kb/)
(run date 2026-07-29), packaged here so the AI-ready records are easy to find
without navigating the full run directory.

This is the featured demo dataset for the reservoir-operation knowledge-base
component of the NSF proposal. See the [repository README](../../README.md)
for the full demo story, the definitions of Evidence Unit / Knowledge Card /
Synthesis Card, and the evidence-chain example.

## Files

| File | Record count | Content |
|---|---:|---|
| `evidence_units.jsonl` | 442 | Source-grounded atomic Evidence Units (EUs) — one operational fact, rule, constraint, observation, or relationship per record, each tied to one source document and quote. |
| `knowledge_cards.jsonl` | 81 | Knowledge Cards (KCs) that consolidate related EUs answering the same operational question, preserving conditions, disagreements, and every supporting EU ID. |
| `synthesis_cards.jsonl` | 15 | Synthesis Cards (SCs) — cross-source analytical findings (operational tradeoffs, regime changes, discrepancies, evidence gaps) that cite supporting EU and KC IDs. |
| `encoded_knowledge_records.jsonl` | 538 | Index-ready encoding of all EUs, KCs, and SCs (442 + 81 + 15 = 538) as structured text records, each preserving its source record's ID, reservoir metadata, engineering dimension, confidence, and evidence-chain links. |
| `claim_evidence_map.jsonl` | 30 | Every claim in the case-study report, mapped to its supporting EU/KC/SC IDs, source IDs, and support level. |

These counts come directly from
[`run_manifest.json`](../../runs/lake_powell_20260729_kb/run_manifest.json)
and each stage's own `stage_manifest.json`.

## Provenance and traceability

Every record in every file traces back to a specific source document:

- Each Evidence Unit cites one `source_id`, a source title/URL, a source
  location (section/table), and a short verbatim `evidence_quote`.
- Each Knowledge Card lists the `based_on_eu_ids` it consolidates.
- Each Synthesis Card lists the `based_on_eu_ids` and, where useful,
  `based_on_knowledge_card_ids` behind its cross-source claim.
- Each report claim in `claim_evidence_map.jsonl` cites the EU/KC/SC and
  source IDs behind it.

The underlying source inventory (66 selected sources, screened from 201
candidates) is in
[`runs/lake_powell_20260729_kb/01_source_acquisition/sources/source_inventory.jsonl`](../../runs/lake_powell_20260729_kb/01_source_acquisition/sources/source_inventory.jsonl),
with each source's original URL. The raw preserved PDFs and extracted text
that inventory points to are kept locally on disk under that same
`01_source_acquisition/sources/raw|text/` but are excluded from this public
repository (`.gitignore`) for size — they are not shipped here or in the run
directory on GitHub; each Evidence Unit's `source_url` and `evidence_quote`
are the citable substitute. Automated validation results (schema conformance and traceability
integrity, both passing for all five files above) are in
[`runs/lake_powell_20260729_kb/validation/`](../../runs/lake_powell_20260729_kb/validation/).

## Intended AI use

This dataset is intended as an AI-ready alternative to raw-document retrieval
for reservoir-operation question answering and synthesis: each record carries
explicit operational meaning, provenance, and confidence, rather than being an
arbitrary text chunk. See the "AI Use and Evaluation" section of the
[repository README](../../README.md#ai-use-and-evaluation) for the planned
comparison against an LLM-only baseline and raw-document RAG, and
[`validation/nsf_demo_benchmark.md`](../../validation/nsf_demo_benchmark.md)
for the 8 preliminary retrieval-benchmark questions defined against this
dataset.

No benchmark results comparing these conditions exist yet; this dataset is
being released ahead of that evaluation.
