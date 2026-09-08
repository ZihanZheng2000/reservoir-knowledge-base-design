---
name: ku-extraction-subagent
description: Extract source-grounded reservoir operation EUs by assigning sources to tier-specific subagents. Use when comparing EU extraction methods, reducing main-agent context contamination, or having separate agents read Tier A, Tier B, and Tier C source documents before merging and validating document-level operational EUs.
---

# Reservoir EU Extraction By Subagent

## Overview

Use this skill when EU extraction should be done by tier-specific subagents instead of the main Codex instance reading all source text directly.

This method is designed for method comparison and context isolation. It does not reduce total token use; it reduces the amount of source text and intermediate reasoning retained in the main agent's active context.

Core boundary:

```text
source text -> tier subagents -> document-level EUs -> main-agent merge and validation
```

## Required Context

Before starting extraction, read:

- `skills/evidence-extraction/SKILL.md`
- `skills/evidence-extraction/references/extraction-protocol.md`
- `references/subagent-protocol.md`

The base EU schema, dimensions, duplicate policy, and validation rules are inherited from `ku-extraction`.

## Workflow

1. Confirm the run has `01_source_acquisition/sources/source_inventory.jsonl` and source text files.
2. When running a method comparison, create one Codex Goal for the full
   subagent method before preparing packets. Record the Goal objective and
   start time.
3. Create a method folder: `runs/<run_id>/02_evidence_extraction/method_subagent/`.
4. Prepare the EU-ready source inventory with the base `ku-extraction` script.
5. Generate extraction packets with the base `ku-extraction` script.
6. Partition the EU-ready inventory by `source_tier`:
   - Tier A -> one subagent
   - Tier B -> one subagent
   - Tier C -> one subagent
7. Spawn only the tier subagents needed by the selected sources.
8. Give each subagent only its assigned tier, the run path, the base EU protocol, and the required output path.
9. Require each subagent to write valid JSONL to:
   - `02_evidence_extraction/method_subagent/tier_a_evidence_units.jsonl`
   - `02_evidence_extraction/method_subagent/tier_b_evidence_units.jsonl`
   - `02_evidence_extraction/method_subagent/tier_c_evidence_units.jsonl`
10. The main agent merges the tier files into:
   - `02_evidence_extraction/method_subagent/evidence_units.jsonl`
11. Renumber EU IDs only if needed for uniqueness. Preserve source IDs, evidence quotes, and locators.
12. Validate with the base validator.
13. Render a method-specific preview.
14. Mark the method Goal complete and record reported token usage when available.
15. Record method runtime/token metrics in
    `validation/ku_method_runtime_metrics.csv`.
16. Record major step timing in `validation/ku_method_step_metrics.csv`.
17. Record that the extraction method is `ku-extraction-subagent`.

## Subagent Contract

Each subagent must:

- extract document-level EUs only from assigned sources
- not synthesize across sources
- not inspect other tiers
- preserve source wording, technical terms, names, values, units, dates, and thresholds
- remove only exact or semantic duplicates that state the same operational fact within the same source
- keep different operational facts separate, even if they share a dimension or topic
- write JSONL records that pass `skills/evidence-extraction/scripts/validate_operational_kus.py`
- set `extraction_method` to `ku-extraction-subagent`

The main agent must not ask the subagent to produce broad notes, article summaries, or hidden reasoning. Ask for artifact output and a short completion report only.

## Output Layout

Use this layout:

```text
runs/<run_id>/02_evidence_extraction/method_subagent/
  source_inventory_eu_ready.jsonl
  extraction_packets.jsonl
  tier_a_evidence_units.jsonl
  tier_b_evidence_units.jsonl
  tier_c_evidence_units.jsonl
  evidence_units.jsonl
  evidence_units.md

runs/<run_id>/validation/
  evidence_extraction_validation_subagent.json
```

## Script Quick Reference

```powershell
python skills/evidence-extraction/scripts/prepare_ku_ready_inventory.py `
  --inventory runs/<run_id>/01_source_acquisition/sources/source_inventory.jsonl `
  --out runs/<run_id>/02_evidence_extraction/method_subagent/source_inventory_eu_ready.jsonl

python skills/evidence-extraction/scripts/make_extraction_packet.py `
  --inventory runs/<run_id>/02_evidence_extraction/method_subagent/source_inventory_eu_ready.jsonl `
  --out runs/<run_id>/02_evidence_extraction/method_subagent/extraction_packets.jsonl `
  --parse-manifest runs/<run_id>/01_source_acquisition/sources/docling_parse_manifest.jsonl

python skills/evidence-extraction/scripts/validate_operational_kus.py `
  --evidence-units runs/<run_id>/02_evidence_extraction/method_subagent/evidence_units.jsonl `
  --source-inventory runs/<run_id>/02_evidence_extraction/method_subagent/source_inventory_eu_ready.jsonl `
  --out runs/<run_id>/02_evidence_extraction/method_subagent/automated_validation.json

python skills/evidence-extraction/scripts/render_ku_preview.py `
  --evidence-units runs/<run_id>/02_evidence_extraction/method_subagent/evidence_units.jsonl `
  --out-md runs/<run_id>/02_evidence_extraction/method_subagent/evidence_units.md `
  --title "<Reservoir Name> EU Extraction Preview - Subagent Method"

python validation/scripts/write_ku_method_metrics.py `
  --out runs/<run_id>/validation/ku_method_runtime_metrics.csv `
  --run-id <run_id> `
  --method-label method_subagent `
  --method-type subagent `
  --goal-objective "Run method_subagent EU extraction for <run_id>" `
  --goal-status complete `
  --started-at <ISO_START_TIME> `
  --ended-at <ISO_END_TIME> `
  --source-inventory runs/<run_id>/02_evidence_extraction/method_subagent/source_inventory_eu_ready.jsonl `
  --evidence-units runs/<run_id>/02_evidence_extraction/method_subagent/evidence_units.jsonl `
  --goal-reported-tokens <GOAL_TOKEN_USAGE_IF_AVAILABLE> `
  --token-source "codex-ui-manual"
```

## Method Notes

Use this method when the research question is whether context isolation improves EU quality, source coverage, or reviewer burden.

The main risk is cross-tier inconsistency: different subagents may make slightly different granularity and dimension decisions. The main agent should run a light normalization pass after merging, but must not convert document-level EUs into cross-document synthesis.

## Resources

- `references/subagent-protocol.md`: tier partitioning, subagent prompt template, merge checks, and comparison notes.
