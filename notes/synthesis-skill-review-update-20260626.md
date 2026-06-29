# Synthesis Skill Review Update - 2026-06-26

## Reason

The Lake Powell Stage 3 synthesis run showed clear improvement over the earlier version, but the review identified two important issues in the synthesis skill:

1. `source_discrepancy` was too loose. Different release values such as 7.48 maf, 6.0 maf, and 8.23 maf may reflect different rule layers, forecast dates, release-status categories, or decision stages rather than true conflict.
2. `evidence_gap` was too close to workflow limitations. A failed table/time-series extraction is a method limitation, not a source-corpus evidence gap.

The review also confirmed that synthesis should have two parts:

1. Consolidate the KU layer by restating and integrating what the source-level KUs say under the approved KU dimensions.
2. Then perform higher-level cross-KU analysis using recurring findings, complementary evidence, true source discrepancies, operational tradeoffs, source-corpus evidence gaps, and outstanding operational issues.

## Updated Skill Decisions

- Synthesis must first produce dimension-level consolidated knowledge points before cross-KU analysis.
- Do not force every KU dimension or analysis type to appear.
- Omit unsupported categories rather than inventing weak cards.
- `source_discrepancy` requires a real inconsistency about the same object under the same definition, date/status, scenario, and decision context.
- `evidence_gap` means the collected source corpus lacks enough evidence to answer an operational question.
- Workflow limitations such as Docling failure, table parsing gaps, or prompt misses belong in run notes or validation notes, not synthesis cards.

## Files Updated

- `skills/synthesis-analysis/SKILL.md`
- `skills/synthesis-analysis/references/synthesis-protocol.md`
- `skills/synthesis-analysis/agents/openai.yaml`

