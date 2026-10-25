---
name: run-orchestration
description: Start, resume, or hand off a reservoir knowledge-base run using the project's six-stage artifact, validation, and review contract. Use whenever Codex is asked to create a new reservoir run, continue a paused run, or verify that a completed run is ready for delivery.
---

# Reservoir Run Orchestration

Use this as the entry point for every reservoir run. Read `AGENTS.md`,
`docs/run-artifact-contract.md`, and `docs/validation-framework.md` before
work. Do not replace a stage skill; invoke the matching stage skill in order.

## Start

1. Select a stable reservoir ID according to `AGENTS.md` and propose a unique
   `<reservoir_slug>_<YYYYMMDD>` run ID.
2. Run `scripts/bootstrap_run.py` to create the six numbered folders and a
   compliant run manifest. Never overwrite an existing run folder. If a run
   already exists for the same reservoir and date, pass `--run-id-suffix`
   (e.g. `--run-id-suffix smoke2`) instead of renaming the reservoir.
3. Record scope, intended use, and source plan in the manifest before source
   acquisition.

## Stage loop

For each stage in this fixed order, use the stage skill, write only its
canonical deliverables, run its validator, generate its actual review
workpaper, then complete `stage_manifest.json` and `stage_summary.md`:

1. `01_source_acquisition`
2. `02_evidence_extraction`
3. `03_knowledge_consolidation`
4. `04_synthesis`
5. `05_indexing`
6. `06_report_generation`

Run `scripts/prepare_human_review.py --run-dir runs/<run_id> --stage <stage>`
after the canonical records exist. For indexing, define the simple benchmark
questions before filling the review file; do not invent a benchmark by script.
Do not proceed after a failed automated result. Warnings require a recorded
limitation but do not automatically block the run.

## Finish

Run these commands before handoff:

```powershell
python skills/run-orchestration/scripts/build_cross_stage_summary.py --run-dir runs/<run_id> --out runs/<run_id>/validation/run_validation_summary.json --out-md runs/<run_id>/validation/run_validation_summary.md
python skills/run-orchestration/scripts/render_validation_report.py --run-dir runs/<run_id> --out-md runs/<run_id>/validation/validation_report.md
python skills/run-orchestration/scripts/validate_run_contract.py --run-dir runs/<run_id> --out runs/<run_id>/validation/run_contract_validation.json
```

A complete handoff gives paths, automated status, review completion, record
counts, supported conclusions, and unresolved limitations. Never treat legacy
KU/F2 files as the routine workflow.

## Validation tooling

The validation design is `docs/validation-framework.md`. Each numbered stage
holds its own `automated_validation.json` and `human_review.json`;
`runs/<run_id>/validation/` holds only run-level summaries.

- `scripts/bootstrap_run.py`: creates a new run folder and manifest.
- `scripts/validate_stage_manifest.py`: checks a stage's delivery manifest and
  summary; folded into that stage's schema-conformance result.
- `scripts/finalize_stage_artifacts.py`: removes allowlisted intermediates after
  a successful stage (dry run unless `--apply`).
- `scripts/prepare_human_review.py`: generates prefilled review workpapers and
  `source_navigation.md` from stage records.
- `scripts/run_lexical_retrieval_benchmark.py`: deterministic lexical baseline
  for the indexing-stage benchmark questions.
- `scripts/build_cross_stage_summary.py`, `scripts/render_validation_report.py`,
  `scripts/render_validation_score_figure.py`: run-level summary, report, and
  score figure.
- `scripts/validate_run_contract.py`: final acceptance check for all six stage
  deliverables.
- `tests/`: tests for the cross-stage summary builder
  (`python -m unittest discover -s skills/run-orchestration/tests`).
