---
name: ku-extraction-prefilter
description: Extract source-grounded reservoir operation EUs after deterministic Python prefiltering of broad candidate passages. Use when comparing EU extraction methods, reducing LLM reading load, screening long source text for operational signals, or testing whether Python-assisted candidate passage selection improves EU extraction efficiency while preserving source evidence.
---

# Reservoir EU Extraction By Prefilter

## Overview

Use this skill when Python should first collect broad candidate passages from source text, and Codex should then convert those passages into document-level operational EUs.

This method is token-efficient compared with full source reading, but it can miss relevant material if the prefilter is too narrow. Use broad candidate extraction and treat recall as more important than precision.

Core boundary:

```text
source text -> broad Python candidate passages -> Codex EU extraction -> validation
```

## Required Context

Before extracting EUs, read:

- `skills/evidence-extraction/SKILL.md`
- `skills/evidence-extraction/references/extraction-protocol.md`
- `references/prefilter-protocol.md`

The base EU schema, dimensions, duplicate policy, and validation rules are inherited from `ku-extraction`.

## Workflow

1. Confirm the run has `01_source_acquisition/sources/source_inventory.jsonl` and extracted text files.
2. When running a method comparison, create one Codex Goal for the full
   prefilter method before preparing packets. Record the Goal objective and
   start time.
3. Create a method folder: `runs/<run_id>/02_evidence_extraction/method_prefilter/`.
4. Prepare the EU-ready source inventory with the base `ku-extraction` script.
5. Run `scripts/extract_candidate_passages.py` to create broad candidate passages.
6. Inspect candidate passage counts by source. If a source has zero candidates but is EU-ready, loosen keywords or increase window size before extraction.
7. Read candidate passages source by source.
8. Convert supported candidate passages into document-level EUs using the base EU extraction protocol.
9. Do not infer a EU from keywords alone; every EU must be supported by the candidate passage and evidence quote.
10. Write output to `runs/<run_id>/02_evidence_extraction/method_prefilter/evidence_units.jsonl`.
11. Set `extraction_method` to `ku-extraction-prefilter`.
12. Validate with the base validator.
13. Render a method-specific preview.
14. Mark the method Goal complete and record reported token usage when available.
15. Record method runtime/token metrics in
    `validation/ku_method_runtime_metrics.csv`.
16. Record major step timing in `validation/ku_method_step_metrics.csv`.

## Output Layout

Use this layout:

```text
runs/<run_id>/02_evidence_extraction/method_prefilter/
  source_inventory_eu_ready.jsonl
  candidate_passages.jsonl
  candidate_passages_summary.json
  evidence_units.jsonl
  evidence_units.md

runs/<run_id>/validation/
  evidence_extraction_validation_prefilter.json
```

## Candidate Passage Rules

Candidate passages are not EUs. They are source-reading shortcuts.

Keep the candidate filter broad enough to catch:

- operating rules, tiers, thresholds, releases, guide curves, schedules, triggers
- storage capacity, elevation targets, minimum pool, dead pool, low-water limits
- hydropower, flood operations, water delivery, recreation, ecology, compact compliance
- forecasts, observations, monitoring, datasets, time series, inflow, outflow
- models, alternatives, scenarios, uncertainty, risk, vulnerability
- agencies, agreements, governance, consultation, NEPA, records of decision
- infrastructure, outlets, penstocks, turbines, spillways, bypass, failure modes
- drought, flood, emergency, maintenance, real-time adjustments
- stakeholders, tribes, states, users, power customers, environmental groups

Prefer false positives over false negatives. Codex should reject irrelevant candidates during EU writing.

## Script Quick Reference

```powershell
python skills/evidence-extraction/scripts/prepare_ku_ready_inventory.py `
  --inventory runs/<run_id>/01_source_acquisition/sources/source_inventory.jsonl `
  --out runs/<run_id>/02_evidence_extraction/method_prefilter/source_inventory_eu_ready.jsonl

python skills/evidence-extraction-prefilter/scripts/extract_candidate_passages.py `
  --inventory runs/<run_id>/02_evidence_extraction/method_prefilter/source_inventory_eu_ready.jsonl `
  --out runs/<run_id>/02_evidence_extraction/method_prefilter/candidate_passages.jsonl `
  --summary-out runs/<run_id>/02_evidence_extraction/method_prefilter/candidate_passages_summary.json

python skills/evidence-extraction/scripts/validate_operational_kus.py `
  --evidence-units runs/<run_id>/02_evidence_extraction/method_prefilter/evidence_units.jsonl `
  --source-inventory runs/<run_id>/02_evidence_extraction/method_prefilter/source_inventory_eu_ready.jsonl `
  --out runs/<run_id>/02_evidence_extraction/method_prefilter/automated_validation.json

python skills/evidence-extraction/scripts/render_ku_preview.py `
  --evidence-units runs/<run_id>/02_evidence_extraction/method_prefilter/evidence_units.jsonl `
  --out-md runs/<run_id>/02_evidence_extraction/method_prefilter/evidence_units.md `
  --title "<Reservoir Name> EU Extraction Preview - Prefilter Method"

python validation/scripts/write_ku_method_metrics.py `
  --out runs/<run_id>/validation/ku_method_runtime_metrics.csv `
  --run-id <run_id> `
  --method-label method_prefilter `
  --method-type prefilter `
  --goal-objective "Run method_prefilter EU extraction for <run_id>" `
  --goal-status complete `
  --started-at <ISO_START_TIME> `
  --ended-at <ISO_END_TIME> `
  --source-inventory runs/<run_id>/02_evidence_extraction/method_prefilter/source_inventory_eu_ready.jsonl `
  --evidence-units runs/<run_id>/02_evidence_extraction/method_prefilter/evidence_units.jsonl `
  --candidate-passages runs/<run_id>/02_evidence_extraction/method_prefilter/candidate_passages.jsonl `
  --goal-reported-tokens <GOAL_TOKEN_USAGE_IF_AVAILABLE> `
  --token-source "codex-ui-manual"
```

## Method Notes

Use this method when the research question is whether deterministic candidate passage extraction reduces LLM reading cost while preserving EU usefulness and faithfulness.

The main risk is missed evidence. When using this method for comparison, keep the candidate passage summary and record the number of zero-candidate sources.

## Resources

- `scripts/extract_candidate_passages.py`: broad operational keyword and window-based candidate passage extractor.
- `references/prefilter-protocol.md`: candidate passage interpretation, recall checks, and comparison notes.
