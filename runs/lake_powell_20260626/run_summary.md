# Lake Powell Run Summary - 2026-06-26

## Stage 1: Source Acquisition

- Discovery approach: official/core manifest plus cached OpenAlex deep-discovery candidate pool; live OpenAlex rerun failed due external 502/timeout.
- Approved source manifest: 49 sources.
- Download/text extraction: 43 ok / 49 total; 1 ok source is flagged for content-quality review because a PDF URL returned short HTML text.
- Source validation: 0 errors, 19 warnings.
- Docling parsing: see `sources/docling_parse_manifest.jsonl`; this run fell back to plain-text chunks for KU extraction.

Tier counts:

| Tier | Count |
|---|---:|
| TR-A | 21 |
| TR-B | 20 |
| TR-C | 8 |

Failed sources:

- LP-20260626-B-004: Turbidity, light, temperature, and hydropeaking control primary productivity in the Colorado River, Grand Canyon ? failed: HTTP Error 403: Forbidden
- LP-20260626-B-005: Collaborative Planning and Adaptive Management in Glen Canyon: A Cautionary Tale ? failed: <urlopen error [Errno 11001] getaddrinfo failed>
- LP-20260626-B-013: Understanding Uncertainties in Future Colorado River Streamflow ? failed: HTTP Error 403: Forbidden
- LP-20260626-B-014: Sustainable water deliveries from the Colorado River in a changing climate ? failed: HTTP Error 403: Forbidden
- LP-20260626-B-016: A simplified water temperature model for the Colorado River below Glen Canyon Dam ? failed: HTTP Error 403: Forbidden
- LP-20260626-C-003: Mavens Notebook: Colorado River Post-2026 Operations Lower Basin proposal and next steps ? failed: HTTP Error 307: Temporary Redirect

## Stage 2: KU Extraction

- Extraction packets: 350 from 43 sources.
- Operational KUs: 236.
- Sources represented by KUs: 42.
- KU validation: 0 errors, 0 warnings.
- KU extraction used the updated 8-dimension taxonomy and stricter first-pass filters.

KU dimension counts:

| Dimension | Count |
|---|---:|
| Operation Purpose | 19 |
| Operation Rules | 35 |
| Infrastructure | 46 |
| Real-Time / Emergency Operations | 19 |
| Coordination / Governance | 63 |
| Operational Data | 21 |
| Research / Modeling / Analysis | 7 |
| Evidence Gap / Uncertainty | 26 |


## Stage 3: Synthesis Analysis

- Stage 3 was rerun using the updated two-step synthesis protocol.
- Step 1 consolidated the KU layer into 8 dimension-level knowledge points.
- Step 2 generated 8 cross-KU synthesis records.
- Referenced KUs in synthesis records: 38.
- Validation: 0 errors.

Two-step output files:

- `synthesis/consolidated_knowledge_points.jsonl`
- `synthesis/consolidated_knowledge_points.md`
- `synthesis_stage3_rerun_20260626_two_step/synthesis_records.jsonl`
- `synthesis_stage3_rerun_20260626_two_step/synthesis_report.md`
- `validation/layer3_synthesis_validation.json`

Analysis type counts from the two-step rerun:

| Analysis Type | Count |
|---|---:|
| recurring_finding | 2 |
| complementary_evidence | 2 |
| source_discrepancy | 0 |
| operational_tradeoff | 2 |
| evidence_gap | 1 |
| outstanding_operational_issue | 1 |

## Current Limits

- OpenAlex live discovery did not complete in this run; cached discovery from the previous run was used to keep the workflow moving.
- Docling structured parsing did not produce successful parsed markdown in this run; KU extraction used full-coverage plain-text chunks.
- KUs are automated first-pass outputs. They need sampled human/domain validation for grounding, coverage, and category accuracy.
- Some borderline KUs may still require cleanup, especially citation-like research records and broad governance/data sentences.
- LP-20260626-B-003 remains `status: ok` but is flagged with `content_quality_flag` for short HTML text returned from a PDF URL; it should trigger recovery search or manual review before future KU extraction.
