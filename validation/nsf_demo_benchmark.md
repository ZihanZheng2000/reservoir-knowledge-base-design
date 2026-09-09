# NSF Demo Benchmark: Lake Powell Retrieval Questions

Source of truth:
[`runs/lake_powell_20260729_kb/05_indexing/human_review.json`](../runs/lake_powell_20260729_kb/05_indexing/human_review.json).
This file summarizes that record for readers who do not want to open the raw
JSON. If the two ever disagree, the run's `human_review.json` is authoritative.

## What this is

During the July 29, 2026 Lake Powell run, the indexing stage defined **8
manually written, single-fact retrieval questions** against the validated
knowledge base (442 Evidence Units, 81 Knowledge Cards, 15 Synthesis Cards;
538 encoded index records). Each question was written *before* retrieval was
run, together with:

- **gold index-record IDs** — the specific EU/KC/SC index records that
  contain the answer;
- **expected answer points** — the specific facts a correct answer must
  contain;
- a fixed **retrieval depth** (top 10).

This gives a small, hand-curated, ground-truth benchmark: it exists to check
whether the knowledge base's records actually contain and surface the facts
they are supposed to, not to demonstrate a finished retrieval system.

## What this is not

The retrieval run against these 8 questions used
[`validation/scripts/run_lexical_retrieval_benchmark.py`](scripts/run_lexical_retrieval_benchmark.py),
a **deterministic lexical token-overlap baseline** (no embeddings, no
learned ranking, no LLM). It is a mechanical sanity check on the index
records, not a production RAG or embedding-based retrieval system, and its
recall/precision numbers characterize that baseline only — they should not be
read as a statement about how well structured retrieval could perform with a
real retriever.

## The 8 questions

| ID | Question | Gold records |
|---|---|---|
| IDX-QR-LP-001 | What is Glen Canyon Dam's minimum power pool elevation? | `IDX-KC-LP-STG-01`, `IDX-EU-LP-OFF-025-03` |
| IDX-QR-LP-002 | What is Lake Powell's current total storage capacity per the 2018 USGS resurvey? | `IDX-KC-LP-STG-04`, `IDX-EU-LP-RES-013-01` |
| IDX-QR-LP-003 | What is the minimum objective annual release volume from Lake Powell under the Long-Range Operating Criteria? | `IDX-KC-LP-OPR-08`, `IDX-EU-LP-OFF-015-01` |
| IDX-QR-LP-004 | What are the minimum and maximum release limits under Modified Low Fluctuating Flow at Glen Canyon Dam? | `IDX-KC-LP-OPR-01`, `IDX-EU-LP-OFF-008-04` |
| IDX-QR-LP-005 | What situations allow Glen Canyon Dam to deviate from normal operations under the Emergency Exception Criteria? | `IDX-KC-LP-EMR-03`, `IDX-EU-LP-OFF-008-06` |
| IDX-QR-LP-006 | How much was the Lake Powell annual release reduced under Section 6.E for water year 2026? | `IDX-KC-LP-OPR-13`, `IDX-EU-LP-OFF-023-02`, `IDX-SC-LP-001` |
| IDX-QR-LP-007 | What caused the September 2005 dissolved oxygen violation at Glen Canyon Dam? | `IDX-KC-LP-UNC-10`, `IDX-EU-LP-RES-020-07`, `IDX-SC-LP-011` |
| IDX-QR-LP-008 | What is the combined discharge capacity of Glen Canyon Dam's river outlet works? | `IDX-KC-LP-EMR-13`, `IDX-EU-LP-MED-002-02` |

(Question IDX-QR-LP-004 is traced end-to-end as the worked example in the
main [README](../README.md#example-from-source-document-to-ai-usable-knowledge).)

## Current lexical-baseline result

From [`runs/lake_powell_20260729_kb/validation/run_validation_summary.json`](../runs/lake_powell_20260729_kb/validation/run_validation_summary.json),
computed at top-10 depth over all 8 questions:

| Metric | Value |
|---|---|
| Mean recall (gold IDs returned in top 10) | 66.7% |
| Mean precision (returned IDs that are gold, top 10) | 15.0% |

Low precision at this depth is expected for a lexical baseline returning a
fixed top-10 list against short, specific gold sets (typically 2-3 records
per question) — it is not evidence about how a production retriever would
perform. `source_adequacy_score` (a human-judgment metric) is left `null`
because human review was not requested for this routine run.

## Status and next steps

- `status: draft_needs_domain_adjudication` equivalents from earlier drafts of
  this benchmark have been superseded by this manually curated 8-question set
  with fixed gold IDs; treat this file, not
  [`retrieval-benchmark-lake-powell-draft-v1.jsonl`](retrieval-benchmark-lake-powell-draft-v1.jsonl)
  (an earlier, larger draft built against a prior, now-superseded run), as the
  current NSF-demo benchmark asset.
- This benchmark is a **preliminary evaluation asset**, sized for a demo, not
  a statistically powered evaluation. Scaling it up, adding held-out
  multi-hop and synthesis-level questions, and running it against an actual
  embedding-based retriever and an LLM-only / raw-document-RAG baseline is
  the next step described in the README's "AI Use and Evaluation" section.
