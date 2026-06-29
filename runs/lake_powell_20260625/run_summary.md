# Lake Powell Stage 1 Source Acquisition Run Summary

Date: 2026-06-25
Run ID: `lake_powell_20260625`

## Scope

Reservoir/system: Lake Powell / Glen Canyon Dam / Colorado River.

Stage 1 followed the clean project `AGENTS.md` and `source-acquisition-suite` skill. The boundary was source discovery, screening, preservation, parsing, and inventory validation. No KU extraction or synthesis was performed.

## Discovery

- OpenAlex candidate discovery output: `deep_discovery/openalex_candidates.jsonl`
- OpenAlex candidates discovered: 384
- Screened candidate output: `deep_discovery/screened_openalex_candidates.jsonl`

| Screening action | Count |
|---|---:|
| exclude | 105 |
| include | 177 |
| manual_review | 9 |
| maybe | 93 |

Official and media/context candidates were supplemented from web discovery and then merged into the approved source manifest.

## Approved Source Manifest

The provisional approved manifest contains 49 sources. This is a relevance-first manifest, not a fixed target count.

| Tier | Count |
|---|---:|
| TR-A | 21 |
| TR-B | 20 |
| TR-C | 8 |

## Preservation Result

| Status | Count |
|---|---:|
| failed: <urlopen error [Errno 11001] getaddrinfo failed> | 1 |
| failed: HTTP Error 307: Temporary Redirect | 1 |
| failed: HTTP Error 403: Forbidden | 4 |
| ok | 43 |

Downloaded/preserved successfully: 43 / 49.

Failed sources recorded in inventory:

- `LP-20260625-B-004`: Turbidity, light, temperature, and hydropeaking control primary productivity in the Colorado River, Grand Canyon - failed: HTTP Error 403: Forbidden
- `LP-20260625-B-005`: Collaborative Planning and Adaptive Management in Glen Canyon: A Cautionary Tale - failed: <urlopen error [Errno 11001] getaddrinfo failed>
- `LP-20260625-B-013`: Understanding Uncertainties in Future Colorado River Streamflow - failed: HTTP Error 403: Forbidden
- `LP-20260625-B-014`: Sustainable water deliveries from the Colorado River in a changing climate - failed: HTTP Error 403: Forbidden
- `LP-20260625-B-016`: A simplified water temperature model for the Colorado River below Glen Canyon Dam - failed: HTTP Error 403: Forbidden
- `LP-20260625-C-003`: Mavens Notebook: Colorado River Post-2026 Operations Lower Basin proposal and next steps - failed: HTTP Error 307: Temporary Redirect

## Structured Parsing

Docling was run using the existing Docling environment from the prior design project. Plain text extraction remains the fallback for failed Docling parses.

| Docling status | Count |
|---|---:|
| error | 20 |
| ok | 3 |
| skipped | 26 |

Valid Docling markdown files retained: 3.
Stale partial Docling outputs from an earlier timed-out parse attempt were removed so that `parsed_docling/` matches `docling_parse_manifest.jsonl`.

Docling errors are documented in `sources/docling_parse_manifest.jsonl`; failed Docling parsing does not invalidate the source if raw files and plain text are preserved.

## Inventory Validation

- Source records: 49
- Validation errors: 0
- Validation warnings: 19

Document type counts:

| Document type | Count |
|---|---:|
| agency_webpage | 6 |
| data_system_documentation | 1 |
| environmental_report | 5 |
| event_case_report | 11 |
| operating_plan | 3 |
| research_paper | 18 |
| technical_memo | 5 |

## Stage 1 Output Files

- `run_manifest.json`
- `source_manifest.json`
- `source_manifest_preview.md`
- `deep_discovery/openalex_candidates.jsonl`
- `deep_discovery/screened_openalex_candidates.jsonl`
- `deep_discovery/screened_openalex_candidates.md`
- `sources/source_inventory.jsonl`
- `sources/source_inventory.csv`
- `sources/docling_parse_manifest.jsonl`
- `validation/layer1_source_validation.json`

## Human Gate

Before treating this Stage 1 run as final, review the 49-source manifest and decide whether to replace failed sources or accept the current 43 preserved sources as sufficient for Stage 2 KU extraction.
