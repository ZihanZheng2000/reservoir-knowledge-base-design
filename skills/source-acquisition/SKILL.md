---
name: source-acquisition
description: Reservoir source-acquisition workflow. Use when the agent needs to discover candidate sources, screen candidates for download, download selected sources, extract text including optional Docling parsing, review source quality and importance, and validate source inventories before EU extraction.
---

# Reservoir Source Acquisition

## Overview

Use this workflow to build Layer 1 evidence sources for a reservoir knowledge-base workflow. It keeps discovery, screening, download, text extraction, quality review, and inventory validation in a fixed order.

Core boundary:

```text
Deep Source Discovery -> Candidate Screening -> Source Download
Source Download -> Text Extraction -> Quality Review -> Inventory Validation
Text Extraction -> Text-Informed Expansion -> Candidate Screening when useful
validated source inventory -> EU extraction later
```

This skill ends when a validated source inventory and preserved text files are ready for EU extraction.

The canonical record contract is `schemas/source_inventory.schema.json`.

## Stage 1 Workflow

1. Read the relevant protocol:
   - Discovery: `references/deep-source-discovery-protocol.md`
   - Screening/quality review: `references/candidate-screening-protocol.md`
   - Download/text extraction: `references/source-download-text-extraction-protocol.md`

2. **Deep Source Discovery**
   - Find a broad candidate pool from official sites, agency repositories, OpenAlex/Crossref/library-style search, backward/forward citation search, and credible media/context search.
   - Output: candidate records with titles, URLs/DOIs, metadata, discovery route, and relevance notes.

3. **Candidate Screening**
   - Before formal download, decide whether each candidate is worth attempting to download.
   - Use metadata, title, abstract, URL/domain, DOI, source type, search context, and light inspection.
   - Do not make final quality judgments here. A/B/C may be recorded only as a provisional source-family hint.
   - Output: screened candidates, an approved source manifest, and one retained concise candidate inventory for selection evaluation.

4. **Source Download**
   - Download or locally preserve selected sources with `scripts/acquire_sources_from_manifest.py`.
   - Preserve raw PDF/HTML/landing pages, assign stable source IDs, and record download status, redirects, paywalls, or access failures.
   - Output: `01_source_acquisition/sources/raw/` and initial source inventory records.

5. **Text Extraction**
   - Extract readable text from downloaded sources.
   - Use plain-text extraction for robustness and optional Docling parsing for PDFs when available.
   - Docling belongs here, not as a separate workflow stage.
   - Output: `01_source_acquisition/sources/text/`, `01_source_acquisition/sources/parsed_docling/` when available, and parse manifests.

   Optional expansion loop: mine extracted text for reservoir-specific terms and deep-research source-chain leads with `scripts/mine_expansion_leads.py`. Feed useful leads back into Deep Source Discovery and Candidate Screening when they can improve source-family coverage or source quality.

6. **Quality Review**
   - After download and text extraction, confirm final source family, document type, source importance, content quality, accessibility, and EU-readiness.
   - Source family A/B/C is not a quality score.
   - Use the quality-review rules in `references/candidate-screening-protocol.md`.
   - Output: reviewed source inventory with quality and importance fields or notes.

7. **Inventory Validation**
   - Validate required fields, source IDs, file paths, statuses, warnings, and readiness for EU extraction with `scripts/validate_source_inventory.py`.
   - For failed, short-content, paywall, redirect, or low-quality records, attempt recovery search when the evidence need remains important.
   - Record discovered candidate counts, selected-for-download counts, downloaded-source counts, text-extracted counts, EU-ready counts, acquisition limits, parser failures, recovery attempts, and next search targets.

## Validation

Follow `docs/validation-framework.md`. Before Evidence extraction, write the
automated result to `01_source_acquisition/automated_validation.json` and assess:

1. schema conformance of the source manifest, candidate inventory, and acquired-source inventory;
2. acquisition success, including recorded outcomes and recovery attempts for
   unavailable core sources.

When human review is requested, use recall, precision, and source adequacy and
write the documented review in `01_source_acquisition/human_review.json`.
Generate the workpaper with `validation/scripts/prepare_human_review.py`.
Its source rows must come from `sources/candidate_inventory.jsonl`, not only
the downloaded sources, so recall and precision use the documented candidate
universe.

## Source Family, Quality, And Importance

- `A`: official operating authority, government agency, dam/reservoir operator, formal legal/policy document, official engineering source, or official data/model system.
- `B`: peer-reviewed, agency-linked, university, lab, or technical research source relevant to operations, constraints, hydrology, infrastructure, ecology, hydropower, governance, or model/data assumptions.
- `C`: credible context source such as media, engineering journalism, stakeholder-facing summaries, or event narratives. Tier C can raise issues but should not finalize technical claims without Tier A/B support.

Do not require every Tier B source to say `reservoir operation`. Include sources that explain operational mechanisms or constraints even if their titles focus on temperature, hydropower, ecology, sediment, policy uncertainty, or governance.

Tier A/B/C is a source-family label, not a quality or importance score. Track source quality and source importance separately after download/text extraction. For example, a Tier C source can be important context for an operational event, while a Tier A source can still be a low-value navigation page.

Recommended quality/importance fields:

- `source_importance`: `core`, `supporting`, `background`, or `low_value`
- `content_quality`: `usable`, `short_review`, `metadata_only`, `paywall_or_redirect`, `parser_issue`, or `failed`
- `eu_readiness`: `ready`, `needs_recovery`, `background_only`, or `not_ready`

## Script Quick Reference

```powershell
# OpenAlex discovery from query file
python skills/source-acquisition/scripts/openalex_expand_sources.py `
  --queries queries.txt `
  --out runs/<run_id>/01_source_acquisition/deep_discovery/openalex_candidates.jsonl

# Screen candidates
python skills/source-acquisition/scripts/screen_source_candidates.py `
  --candidates runs/<run_id>/01_source_acquisition/deep_discovery/openalex_candidates.jsonl `
  --out-jsonl runs/<run_id>/01_source_acquisition/deep_discovery/screened_candidates.jsonl `
  --out-md runs/<run_id>/01_source_acquisition/deep_discovery/screened_candidates.md

# Retain only the final reviewable candidate universe before cleaning discovery files
python skills/source-acquisition/scripts/write_candidate_inventory.py `
  --screened-candidates runs/<run_id>/01_source_acquisition/deep_discovery/screened_candidates.jsonl `
  --approved-manifest runs/<run_id>/01_source_acquisition/source_manifest.json `
  --reservoir-id <reservoir_id> `
  --out runs/<run_id>/01_source_acquisition/sources/candidate_inventory.jsonl

# Acquire approved manifest
python skills/source-acquisition/scripts/acquire_sources_from_manifest.py `
  --manifest runs/<run_id>/01_source_acquisition/source_manifest.json `
  --out-dir runs/<run_id>/01_source_acquisition `
  --reservoir-id 597 `
  --reservoir-name "<Reservoir Name>"

# Docling parse PDFs
.\.venv\Scripts\python.exe skills/source-acquisition/scripts/parse_sources_docling.py `
  --inventory runs/<run_id>/01_source_acquisition/sources/source_inventory.jsonl `
  --out-dir runs/<run_id>/01_source_acquisition/sources/parsed_docling `
  --manifest runs/<run_id>/01_source_acquisition/sources/docling_parse_manifest.jsonl `
  --include-non-pdf

# Validate inventory
python skills/source-acquisition/scripts/validate_source_inventory.py `
  --inventory runs/<run_id>/01_source_acquisition/sources/source_inventory.jsonl `
  --candidate-inventory runs/<run_id>/01_source_acquisition/sources/candidate_inventory.jsonl `
  --out runs/<run_id>/01_source_acquisition/automated_validation.json

# Mine text-informed expansion leads after text extraction
python skills/source-acquisition/scripts/mine_expansion_leads.py `
  --inventory runs/<run_id>/01_source_acquisition/sources/source_inventory.jsonl `
  --out runs/<run_id>/01_source_acquisition/deep_discovery/text_informed_expansion_leads.jsonl
```

## Output Contract

Also write `stage_manifest.json` and `stage_summary.md` at the root of
`01_source_acquisition/`, following `docs/run-artifact-contract.md`.
After successful validation, finalize the stage to remove discovery and parse
intermediates while retaining the source manifest, inventory, raw files, and
extracted text.

A completed Layer 1 run should contain, per `docs/run-artifact-contract.md`:

- `01_source_acquisition/source_manifest.json` for approved sources
- `01_source_acquisition/sources/candidate_inventory.jsonl` for the final screened candidate universe
- `01_source_acquisition/sources/raw/` for preserved raw files
- `01_source_acquisition/sources/text/` for extracted text
- `01_source_acquisition/sources/source_inventory.jsonl`
- `01_source_acquisition/automated_validation.json`
- `01_source_acquisition/human_review.json`
- `run_summary.md` describing counts, failures, and acquisition limits

`01_source_acquisition/deep_discovery/` (including
`text_informed_expansion_leads.jsonl`), `sources/parsed_docling/`,
`sources/docling_parse_manifest.jsonl`, and `sources/source_inventory.csv`
are working artifacts used during the stage; `validation/scripts/
finalize_stage_artifacts.py` removes them after successful validation and
they are not part of the retained deliverable set.
