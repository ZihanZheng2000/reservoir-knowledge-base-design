# Run Artifact Contract

## Purpose

This contract defines how every new run and every stage folder is presented.
It complements the record schemas in `schemas/`: record schemas define JSONL
rows; this contract defines the folder-level deliverable.

Do not rewrite historical runs to satisfy this contract.

## Retention policy

The run directory is a clean delivery space, not a permanent scratch space.
After a stage has passed automated validation and its `stage_summary.md` is
written, remove reproducible execution intermediates. Do not remove canonical
deliverables or the preserved source evidence required for traceability.

| Retain | Remove after successful stage finalization |
|---|---|
| run/stage manifests and stage summaries | candidate-search dumps and screening workbooks |
| source manifest, final candidate inventory, acquired-source inventory, raw source files, extracted source text | Docling parse cache and parse manifests |
| validated EU, KC, Synthesis Card, index, report, and claim-evidence-map records | extraction packets, EU previews, temporary summaries, and draft notes |
| standard automated validation outputs and stage human-review records | `work/` directories and explicitly labelled temporary backend/debug files |

The finalizer is intentionally allowlisted and runs in dry-run mode unless
`--apply` is supplied. It refuses to clean a stage whose manifest is not
completed or whose automated validation contains a failure.

## Universal stage deliverable

Every numbered stage folder must contain exactly these four standard delivery
files in addition to its stage-specific data artifacts:

```text
stage_manifest.json
stage_summary.md
automated_validation.json
human_review.json
```

### `stage_manifest.json`

This is the machine-readable delivery record. It must conform to
`schemas/stage_manifest.schema.json` and state:

- the run ID, stage ID, workflow version, and completion status;
- input and output artifact paths, formats, schemas, and record counts where
  applicable;
- the two automated-validation results and their artifact path;
- human-review status and the stage-local review artifact path;
- cleanup status and removed intermediate paths;
- warnings, unresolved issues, and downstream readiness.

Artifact paths are relative to the run directory. Do not put raw records,
claims, or prose findings inside the manifest.

### `stage_summary.md`

This is the fixed, human-readable handoff. It must use the project template
and contain these sections in this order:

1. Stage status;
2. inputs used;
3. outputs produced;
4. automated validation;
5. human review;
6. cleanup;
7. warnings and unresolved issues;
8. downstream readiness and next action.

It reports counts, paths, statuses, and concise limitations. It does not add
new evidence claims or analysis not present in the stage artifacts.

### `automated_validation.json`

This is the one machine-validation record for the stage. It records the two
automated indicators and their detailed errors or warnings. The delivery
contract check is folded into its **schema conformance** indicator, rather
than written as a separate third validation result.

### `human_review.json`

This is the one human-review record for the stage. Its `review_status` field
uses `not_requested`, `not_reviewed`, `in_progress`, or `completed`; the file
then records the required three review criteria, item-level judgments, and
follow-up. Keep this file even when review has not been requested so the
review location is always obvious.

Start from the matching JSON template in `templates/human_review/`, then prefill
the rows with the stage's actual source, EU, KC, Synthesis Card, query, or
report-claim records. Preserve Codex's recommendation and provide a separate
column for the human disposition. Use 0/1/2 for human-scored criteria. A
status-only placeholder is not a valid review workpaper.

Validate the stage manifest after the stage-specific automated validator has
written its output:

```powershell
python validation/scripts/validate_stage_manifest.py `
  --manifest runs/<run_id>/<stage_folder>/stage_manifest.json `
  --run-dir runs/<run_id> `
  --automated-result runs/<run_id>/<stage_folder>/automated_validation.json `
  --out runs/<run_id>/<stage_folder>/automated_validation.json
```

This check is part of the stage's **schema conformance** indicator; it is not a
third automated indicator.

After validation, clean only the approved intermediate paths:

```powershell
python validation/scripts/finalize_stage_artifacts.py `
  --run-dir runs/<run_id> `
  --stage <stage_id> `
  --apply
```

The finalizer records removed paths in `stage_manifest.json` and never removes
raw source evidence, canonical records, final reports, or validation results.

## Stage-specific artifacts

| Stage folder | Required primary artifacts | Optional/supporting artifacts |
|---|---|---|
| `01_source_acquisition/` | `source_manifest.json`; `sources/candidate_inventory.jsonl`; `sources/source_inventory.jsonl`; `sources/raw/`; `sources/text/` | source-discovery and parsing intermediates |
| `02_evidence_extraction/` | `evidence_units.jsonl`; `evidence_units.md`; `source_navigation.md` | extraction packets and temporary summaries |
| `03_knowledge_consolidation/` | `knowledge_cards.jsonl`; `knowledge_cards.md`; `source_navigation.md` | consolidation work files |
| `04_synthesis/` | `synthesis_cards.jsonl`; `synthesis_cards.md`; `source_navigation.md` | synthesis work files and drafts |
| `05_indexing/` | `encoded_knowledge_records.jsonl`; `index_manifest.json` | temporary backend/debug files |
| `06_report_generation/` | `<report_name>.md`; `claim_evidence_map.jsonl` | report drafts and temporary renderings |

## Validation artifacts

Run-level validation contains summaries only:

```text
validation/
```

The standard filenames are:

```text
run_validation_summary.json
run_validation_summary.md
run_contract_validation.json
```

Each stage's `human_review.json` is optional in substance, but required as a
location. When no review is required, mark the file `not_requested` and retain
the applicable criteria for later use.

## Naming and formatting rules

- Use the canonical filenames above; do not create alternate names such as
  `final`, `new`, `latest`, `result2`, or `output_final`.
- Write machine records as UTF-8 JSON or JSONL; one JSON object per line in
  JSONL files.
- Write summaries as UTF-8 Markdown.
- Use relative forward-slash paths in manifests, for example
  `02_evidence_extraction/evidence_units.jsonl`.
- The Markdown views in stages 2–4 are required reading views derived only from
  their corresponding canonical JSONL records. They make the final delivery
  easy to inspect; JSONL remains the machine-readable source of record.
- Keep experimental, temporary, or method-comparison material in clearly named
  subfolders; do not mix it with canonical primary artifacts.
- If a required artifact cannot be created, list it as missing in the manifest,
  give the reason, and set downstream readiness to `blocked` or `conditional`.
