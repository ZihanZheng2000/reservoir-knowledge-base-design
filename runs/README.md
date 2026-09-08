# Runs

Create one folder per reservoir workflow run.

Suggested name:

```text
<reservoir_slug>_<YYYYMMDD>
```

Examples:

```text
lake_powell_20260625
shasta_lake_20260702
```

Do not overwrite prior runs. If a workflow version changes, create a new run folder or add a clear version suffix.

Each run uses numbered stage folders in workflow order:

```text
01_source_acquisition/
02_evidence_extraction/
03_knowledge_consolidation/
04_synthesis/
05_indexing/
06_report_generation/
validation/
```

`validation/` contains automated stage results, the cross-stage summary, and,
when requested, `human_review/` records. Follow
`docs/validation-framework.md` for the two automated and three human-review
indicators per stage.

Each numbered stage folder also contains `stage_manifest.json` and
`stage_summary.md`. See `docs/run-artifact-contract.md` for the required
folder-level delivery format.
