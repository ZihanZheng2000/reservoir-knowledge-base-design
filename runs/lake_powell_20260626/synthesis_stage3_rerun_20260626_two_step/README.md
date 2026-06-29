# Stage 3 Rerun - Two-Step Synthesis

This folder is a rerun of Stage 3 using the updated two-step synthesis skill.

It does not overwrite the original `synthesis/` folder.

## Step 1: KU Consolidation

Outputs:

- `consolidated_knowledge_points.jsonl`
- `consolidated_knowledge_points.md`
- `consolidated_knowledge_points_validation.json`

Purpose:

Consolidate the Stage 2 KUs by approved KU dimension before higher-level analysis.

## Step 2: Cross-KU Synthesis Analysis

Outputs:

- `synthesis_records.jsonl`
- `synthesis_report.md`
- `synthesis_validation.json`

Purpose:

Generate cross-KU analysis cards only when supported by the KU/source evidence.

This rerun intentionally does not force a `source_discrepancy` card. The release values found in the KUs appear to reflect different rule layers, scenarios, and release-status contexts rather than a verified same-object/same-status conflict.

