# Run `lake_powell_20261025_kb`

Lake Powell / Glen Canyon Dam knowledge base. Stages 1-3 are carried over
unchanged from run `lake_powell_20260729_kb` (work performed 2026-07-29);
Stages 4-6 (synthesis, indexing, report) were redone on 2026-10-25. Records
are released under CC BY 4.0 (see [`LICENSE-DATA.md`](../../LICENSE-DATA.md)).

| Folder | Main output | Records |
|---|---|---:|
| `01_source_acquisition/` | `sources/source_inventory.jsonl` (selected), `sources/candidate_inventory.jsonl` (screened) | 66 / 201 |
| `02_evidence_extraction/` | `evidence_units.jsonl` | 442 |
| `03_knowledge_consolidation/` | `knowledge_cards.jsonl` | 81 |
| `04_synthesis/` | `synthesis_cards.jsonl`, `candidate_screening.jsonl` | 19 / 30 candidates |
| `05_indexing/` | `encoded_knowledge_records.jsonl` | 542 |
| `06_report_generation/` | `lake_powell_case_study_report.md`, `claim_evidence_map.jsonl` | 32 claims |
| `validation/` | Run-level validation summary and report | — |

Each stage folder also holds `stage_manifest.json`, `stage_summary.md`, and
`automated_validation.json`. The `.md` files next to the JSONL outputs are
human-readable renderings of the same records.

## What changed in Stages 4-6

- **Synthesis** screened all 442 EUs, not only the EUs grouped into Knowledge
  Cards. Every candidate relationship and the reason it was kept, merged, or
  rejected is in `04_synthesis/candidate_screening.jsonl`. All 19 cards were
  written after rereading the cited source passages
  (`evidence_depth: source_checked_with_direct_quote`); each card's
  `source_verification_note` says what the reread confirmed or changed.
- **Indexing** rebuilt the index (542 records) and reran the same 8 benchmark
  questions, with one gold Synthesis Card ID remapped because cards were
  renumbered.
- **Report** claims appear verbatim in the report with inline `[CLM-xxx]`
  tags that match `claim_evidence_map.jsonl`.

## Validation status

- **Automated validation is complete** for all six stages: 0 errors; source
  acquisition carries 42 documented, non-blocking acquisition issues. See
  [`validation/validation_report.md`](validation/validation_report.md).
- **Human review has not been performed.** Each stage's `human_review.json`
  is a review form pre-filled with every review unit and the agent's own
  decisions, with all human score and decision fields left blank
  (`review_status: not_requested`). The only filled metrics are the indexing
  stage's automated 8-question lexical retrieval benchmark.

## Known limitations not addressed in this run

- 9 of the largest source documents were extracted by sampling rather than
  in full (see `02_evidence_extraction/stage_summary.md`).
- 3 sources marked usable (OFF-033, OFF-034, RES-023) are access-blocked or
  landing pages and produced no Evidence Units.
- Two Evidence Unit quotes do not match their sources verbatim
  (EU-LP-OFF-006-12, EU-LP-OFF-023-06); the Synthesis Cards that use them
  rely on the source wording.

## Not included

Preserved source PDFs and extracted text (`01_source_acquisition/sources/raw/`
and `text/`) are kept locally and excluded from the public repository for
size and third-party copyright. Each source's original `url` is listed in
`source_inventory.jsonl`.
