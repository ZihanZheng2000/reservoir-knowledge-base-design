# Run `lake_powell_20260729_kb`

Complete six-stage run for Lake Powell / Glen Canyon Dam (run date
2026-07-29). This is the run behind the repository README and the packaged
dataset in [`datasets/lake_powell_demo/`](../../datasets/lake_powell_demo/).

| Folder | Main output | Records |
|---|---|---:|
| `01_source_acquisition/` | `sources/source_inventory.jsonl` (selected), `sources/candidate_inventory.jsonl` (screened) | 66 / 201 |
| `02_evidence_extraction/` | `evidence_units.jsonl` | 442 |
| `03_knowledge_consolidation/` | `knowledge_cards.jsonl` | 81 |
| `04_synthesis/` | `synthesis_cards.jsonl` | 15 |
| `05_indexing/` | `encoded_knowledge_records.jsonl` | 538 |
| `06_report_generation/` | `lake_powell_case_study_report.md` / `.pdf`, `claim_evidence_map.jsonl` | 30 claims |
| `validation/` | Run-level validation summary and report | — |

Each stage folder also holds `stage_manifest.json`, `stage_summary.md`, and
`automated_validation.json`. The `.md` files next to the JSONL outputs are
human-readable renderings of the same records.

## Validation status

- **Automated validation is complete** for all six stages: 0 errors; source
  acquisition carries 42 documented, non-blocking acquisition issues. See
  [`validation/validation_report.md`](validation/validation_report.md).
- **Human review has not been performed.** Each stage's `human_review.json`
  is a review form pre-filled with every review unit and the agent's own
  decisions, with all human score and decision fields left blank
  (`review_status: not_requested`). The only filled metrics are the indexing
  stage's automated 8-question lexical retrieval benchmark (see
  [`validation/nsf_demo_benchmark.md`](../../validation/nsf_demo_benchmark.md)).

## Not included

Preserved source PDFs and extracted text (`01_source_acquisition/sources/raw/`
and `text/`) are kept locally and excluded from the public repository for
size and third-party copyright. Each source's original `source_url` is listed
in `source_inventory.jsonl`.
