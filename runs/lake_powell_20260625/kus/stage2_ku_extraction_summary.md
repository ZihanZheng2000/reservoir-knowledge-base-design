# Lake Powell Stage 2 KU Extraction Summary

Date: 2026-06-25
Run ID: `lake_powell_20260625`

## Scope

Stage 2 used the current Stage 1 core source set: 43 preserved sources. The output is the document-level KU layer only. No cross-document synthesis was performed.

## Extraction Method

- Source inventory: `sources/source_inventory.jsonl`
- Docling parse manifest: `sources/docling_parse_manifest.jsonl`
- Extraction packets: `kus/extraction_packets.jsonl`
- KU output: `kus/operational_kus.jsonl`

The extraction followed the `ku-extraction` skill boundary: `document -> page/section-aware chunks -> candidate KUs -> dedupe/consolidate -> validated KUs`. Because most PDFs did not produce Docling markdown, extraction packets used full-coverage overlapping text chunks as fallback.

## Version Note

An initial locator-style KU file was generated and archived as `kus/operational_kus_v1_locator_style.jsonl`. It was too generic and sometimes captured webpage navigation text. The active file `kus/operational_kus.jsonl` is the improved v2 sentence-grounded output, which only accepts body-text evidence sentences and passed quote-hygiene validation. Two low-value landing-page KUs were removed after preview inspection.

## Output Counts

- Extraction packets: 349
- Sources covered by packets: 43
- Operational KUs generated: 84
- Sources covered by KUs: 41
- Sources skipped by v2 extractor: 1
- Low-value KUs removed after preview: 2

Skipped source:

- `LP-20260625-B-003`: Designing flows to resolve human and environmental water needs in a dam-regulated river - no acceptable operational evidence sentence found by v2 extractor

Removed low-value KUs:

- `KU-LP-20260625-007` from `LP-20260625-A-004` - landing-page/file-list style evidence
- `KU-LP-20260625-008` from `LP-20260625-A-004` - landing-page/file-list style evidence

## KU Counts By Engineering Dimension

| Engineering dimension | Count |
|---|---:|
| Operation Rules | 20 |
| Data / Models | 7 |
| Infrastructure Constraints | 22 |
| Coordination / Governance | 10 |
| Operation Purpose | 11 |
| Evidence Gap / Uncertainty | 8 |
| Real-Time / Emergency Operations | 6 |

## Confidence Counts

| Confidence | Count |
|---|---:|
| high | 78 |
| medium | 6 |

## Validation

- Structural validation errors: 0
- Structural validation warnings: 0
- Basic quote hygiene validation: passed
- Human/domain validation: not yet performed

## Important Limitation

This is a first-pass automated KU layer. The active KUs are sentence-grounded and structurally valid, but they still require sampled human review for faithfulness, coverage, and category quality before being treated as an accepted dataset release.

## Stage 2 Output Files

- `kus/extraction_packets.jsonl`
- `kus/operational_kus.jsonl`
- `kus/operational_kus_preview.md`
- `kus/operational_kus_v1_locator_style.jsonl`
- `kus/skipped_sources_v2.json`
- `kus/removed_low_value_kus_v2.json`
- `validation/layer2_ku_validation.json`

## Recommended Human Review Sample

Review at least:

- 5 TR-A official KUs from Post-2026 / 24-Month Study / DROA sources;
- 5 TR-B research KUs from hydropower, temperature/ecology, and uncertainty sources;
- 3 TR-C context KUs;
- all KUs with medium confidence;
- any KUs used later for high-level synthesis claims.
