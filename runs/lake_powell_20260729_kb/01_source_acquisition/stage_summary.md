# Stage Summary: Source Acquisition

## 1. Stage status

- Run ID: lake_powell_20260729_kb
- Stage: 01_source_acquisition
- Status: completed_with_warnings
- Workflow version: v0.2

## 2. Inputs used

| Artifact | Path | Record count / scope |
|---|---|---|
| OpenAlex deep-discovery query sweep (30 general/reservoir/operation/drought/model query families) | `deep_discovery/openalex_candidates.jsonl` (removed at cleanup) | 161 |
| Official/legal/CRS/media candidates hand-added from targeted official-site search (USBR, Federal Register, congress.gov, GCDAMP, LTEMP EIS site) | `deep_discovery/screened_candidates_full.jsonl` (removed at cleanup) | 40 |
| Combined screened candidate universe | `deep_discovery/screened_candidates_full.jsonl` (removed at cleanup) | 201 |
| Approved source manifest (Codex-selected) | `source_manifest.json` | 66 |

## 3. Outputs produced

| Artifact | Path | Format | Record count | Required |
|---|---|---|---:|---|
| Candidate inventory (full reviewed universe) | `sources/candidate_inventory.jsonl` | jsonl | 201 | yes |
| Source inventory (jsonl) | `sources/source_inventory.jsonl` | jsonl | 66 | yes |
| Source inventory (csv) | `sources/source_inventory.csv` | csv | 66 | no |
| Raw preserved files | `sources/raw/` | directory | 55 | yes |
| Extracted plain text | `sources/text/` | directory | 53 | yes |

Provenance mix of the 66 approved/attempted sources: Tier A (official/legal/engineering) 41, Tier B (peer-reviewed/technical research + CRS) 23, Tier C (media/context) 2. Document types: legal_policy_document 12, research_paper 26, technical_memo 8, environmental_report 6, agency_webpage 5, event_case_report 3, data_system_documentation 3, engineering_manual 2, operating_plan 1.

**50 of 66 sources are `eu_readiness=ready`** (47 `content_quality=usable`, 3 `short_review`) and proceed to Stage 2. The other 16 are `not_ready` (13 publisher-paywalled research papers with documented HTTP 403/DNS failures, 3 reclassified redirect/bot-challenge pages) and are excluded from EU extraction while remaining visible in the inventory for traceability.

Representative core sources acquired: 2007 Colorado River Interim Guidelines ROD, 2024 Near-term Operations SEIS ROD, 2016 LTEMP ROD + FEIS chapters/appendices, 1996 Operation of Glen Canyon Dam ROD, 1970 Coordinated Long-Range Operating Criteria, Colorado River Compact (1922), Upper Colorado River Basin Compact (1948), Post-2026 Operations Draft EIS + CRSS Model Documentation Appendix + Alternatives Report, Draft 2026 Annual Operating Plan, July 2026 24-Month Study, March 2024 Low-Reservoir-Level Technical Decision Memorandum, Drought Response Operations Agreement, 2019 DCP transmittal, SECURE Water Act Colorado Basin reports (2016, 2021), plus USGS/OSTI technical studies on Lake Powell elevation-capacity loss, LTEMP decision analysis, Glen Canyon Dam sandbar/sediment response, and hydropower economics of ROD operating restrictions.

## 4. Automated validation

| Indicator | Status | Issue count | Validation artifact |
|---|---|---:|---|
| Schema conformance | pass | 0 | `automated_validation.json` |
| Acquisition success | warning | 42 | `automated_validation.json` |

The 42 warning-level issues are the expected raw/text/status flags on the 16 not-ready sources (3 flags each) plus 2 short-text notes; there are zero schema errors and zero silently-dropped sources.

## 5. Human review

- Status: not_requested
- Review artifact: `human_review.json` (prefilled with all 201 candidate rows, Codex `codex_use`/`codex_tier` decisions, `human_use`/`human_tier` left null pending an explicit review request)
- Applicable criteria: recall, precision, source adequacy (deferred; not requested for this routine run)

## 6. Cleanup

- Status: completed
- Removed intermediate paths: `01_source_acquisition/deep_discovery`, `01_source_acquisition/sources/source_inventory.csv`

## 7. Warnings and unresolved issues

- Deep source discovery combined an OpenAlex query sweep (161 candidates from 30 query families covering operation rules, infrastructure, drought/emergency, hydropower, temperature/ecology, adaptive management, governance, storage/sediment, and data/models) with targeted official-site search for USBR/Federal Register/congress.gov/LTEMP-EIS/GCDAMP documents. From the 201-record combined candidate universe, 66 were selected as genuinely on-topic and non-redundant (26 research papers curated from OpenAlex results after excluding ~38 tangential or thematically redundant Colorado River Basin-wide climate/ecology papers; 40 official/legal/CRS/media documents).
- 13 supporting-tier research papers (RES-001,002,003,004,006,007,008,009,011,012,016,017,022) could not be acquired: 12 returned HTTP 403 Forbidden from Wiley, ASCE, AMS, or PNAS (publisher bot-blocking of scripted requests) and 1 (RES-001, a CADSWES thesis) failed DNS resolution. Wayback Machine recovery was attempted for a sample of these and did not succeed within this run. None are `source_importance=core`; all remain listed with documented failure reasons in `source_inventory.jsonl` rather than silently dropped.
- 3 sources (RES-005, RES-010, RES-021) initially reported `status: ok` (HTTP 200) but on quality review the "extracted text" was actually a publisher redirect stub or JavaScript bot-challenge notice, not source content. These were reclassified to `status: failed` / `eu_readiness: not_ready` / `content_quality: parser_issue` during quality review rather than left as false-positive successes feeding EU extraction.
- 7 core/near-core sources (OFF-001, OFF-003, OFF-004, OFF-025, OFF-031, CRS-001, CRS-002, RES-025 — 8 total) initially failed: usbr.gov returned a site "Down For Maintenance" placeholder for 3 URLs (OFF-001, OFF-025, OFF-031), `ltempeis.anl.gov` returned HTTP 403 to scripted requests for the LTEMP ROD and FEIS chapters (OFF-003, OFF-004, OFF-005, OFF-006), `congress.gov`'s `crs-product` pages returned HTTP 403 (CRS-001, CRS-002), and OSTI's direct PDF `servlets/purl` endpoint returned HTTP 403 (RES-025). All were recovered: the usbr.gov and ltempeis.anl.gov documents via Wayback Machine snapshots, the CRS reports via `congress.gov/crs_external_products/.../*.pdf` direct paths, and RES-025 via the OSTI bibliographic landing page (metadata/abstract only, marked `content_quality: short_review`). This confirms the pinned-dependency and recovery workflow held up correctly at this larger scale; the failures encountered were live third-party network/bot-protection conditions, not a repeat of the earlier pypdf/cryptography dependency bug (both packages installed cleanly from `requirements.txt` before this run and no PDF-extraction placeholder text was observed anywhere in the 53 preserved text files).
- `sources/source_inventory.csv` was regenerated by hand from the final JSONL after the quality-review pass (no dedicated helper script produces `content_quality`/`eu_readiness`; a short ad hoc Python pass was used, matching prior-run practice noted in `lake_powell_smoke2_20260728`).

## 8. Downstream readiness and next action

- Readiness: ready
- Next action: proceed to `02_evidence_extraction` using the 50 `eu_readiness=ready` sources in `source_inventory.jsonl`.
