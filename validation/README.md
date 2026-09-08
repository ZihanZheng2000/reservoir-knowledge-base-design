# Validation Tooling And Studies

The canonical routine validation design is
[`docs/validation-framework.md`](../docs/validation-framework.md).

Per-run outputs are split by purpose:

- each numbered stage contains `automated_validation.json` and `human_review.json`;
- `runs/<run_id>/validation/` contains only run-level summaries and acceptance
  records (`run_validation_summary.*`, `validation_report.md`, and
  `run_contract_validation.json`).

This directory contains reusable tooling and optional research-study assets. It
does not redefine the routine six-stage workflow.

## Routine tooling

- `scripts/build_cross_stage_summary.py`: combines six stage validation outputs.
- `scripts/validate_stage_manifest.py`: checks the standardized stage delivery
  manifest and summary.
- `scripts/finalize_stage_artifacts.py`: safely removes allowlisted execution
  intermediates after a successful stage.
- `scripts/prepare_human_review.py`: generates populated review workpapers and
  source-navigation files from stage records.
- `scripts/validate_run_contract.py`: final acceptance check for all six stage
  deliverables.
- `schemas/`: contracts for standardized stage and cross-stage summaries.
- `templates/`: optional reviewer and benchmark instruments.
- `tests/`: deterministic tests for the summary builder.

## Optional studies

Method comparisons, detailed scoring instruments, runtime/token logging, and
transfer validation are optional research-design activities. Use dated,
immutable folders under `validation/studies/` when conducting one. These
assets must not change the routine automated indicators or the three human
review criteria defined for each stage in the canonical framework.

## Quick start

```powershell
python validation/scripts/build_cross_stage_summary.py `
  --run-dir runs/<run_id> `
  --out runs/<run_id>/validation/run_validation_summary.json `
  --out-md runs/<run_id>/validation/run_validation_summary.md

python validation/scripts/render_validation_report.py `
  --run-dir runs/<run_id> `
  --out-md runs/<run_id>/validation/validation_report.md

python validation/scripts/validate_run_contract.py `
  --run-dir runs/<run_id> `
  --out runs/<run_id>/validation/run_contract_validation.json

python -m unittest discover validation/tests -v
```
