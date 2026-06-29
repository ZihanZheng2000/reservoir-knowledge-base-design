---
name: source-acquisition-suite
description: Modular reservoir evidence-source acquisition suite. Use when the agent needs to discover candidate reservoir sources through official search, OpenAlex/Crossref/library-style deep discovery, screen candidates into Tier A/B/C, download and preserve raw files, extract text, run Docling PDF parsing, and validate source inventories before KU extraction.
---

# Reservoir Source Acquisition Suite

## Overview

Use this suite to build Layer 1 evidence sources for a reservoir knowledge-base workflow. It keeps source discovery, candidate screening, source preservation, structured parsing, and validation close together without mixing their responsibilities.

Core boundary:

```text
deep discovery -> candidate screening -> approved source manifest
approved source manifest -> raw/text preservation -> structured parsing -> validated source inventory
validated source inventory -> KU extraction later
```

Do not extract KUs or write synthesis in this suite.

## Module Router

Choose the module based on the user request:

- **Deep Source Discovery**: Use when the user wants broader literature/source discovery, OpenAlex/Crossref/library-style search, backward search from references, forward search from citing works, or a larger candidate pool.
- **Candidate Screening**: Use when the user wants to decide which candidates belong in Tier A/B/C and which should be included, excluded, or manually reviewed.
- **Source Preservation And Text Extraction**: Use when the user has an approved manifest and wants raw files, extracted text, source inventory JSONL/CSV, and stable source IDs.
- **Structured Parsing**: Use when PDFs should be parsed with Docling into structured markdown for better section/chunk localization.
- **Inventory Validation**: Use before handing sources to KU extraction.

## Workflow

1. Read the relevant protocol:
   - Discovery: `references/deep-source-discovery-protocol.md`
   - Screening: `references/candidate-screening-protocol.md`
   - Preservation/parsing: `references/source-preservation-and-parsing-protocol.md`
2. Define the reservoir, scope, source families, and evidence needs.
3. If discovery is needed, generate candidate sources with `scripts/openalex_expand_sources.py` plus official/site/library searches.
4. Screen candidates into `include`, `maybe`, `manual_review`, or `exclude` using `scripts/screen_source_candidates.py` and human judgment.
5. Convert approved sources into a source manifest.
6. Download and preserve approved sources with `scripts/acquire_sources_from_manifest.py`.
7. Parse PDFs with `scripts/parse_sources_docling.py` when Docling is available.
8. Validate inventory with `scripts/validate_source_inventory.py`.
9. For failed, short-content, paywall, redirect, or otherwise low-quality records, attempt recovery search for alternate URLs, official mirrors, DOI landing pages, repository copies, OpenAlex OA URLs, or replacement sources covering the same evidence need.
10. Record acquisition limits, inaccessible candidates, parser failures, recovery attempts, and next search targets.

## Tier Logic

- `A`: official operating authority, government agency, dam/reservoir operator, formal legal/policy document, official engineering source, or official data/model system.
- `B`: peer-reviewed, agency-linked, university, lab, or technical research source relevant to operations, constraints, hydrology, infrastructure, ecology, hydropower, governance, or model/data assumptions.
- `C`: credible context source such as media, engineering journalism, stakeholder-facing summaries, or event narratives. Tier C can raise issues but should not finalize technical claims without Tier A/B support.

Do not require every Tier B source to say `reservoir operation`. Include sources that explain operational mechanisms or constraints even if their titles focus on temperature, hydropower, ecology, sediment, policy uncertainty, or governance.

## Script Quick Reference

```powershell
# OpenAlex discovery from query file
python skills/source-acquisition-suite/scripts/openalex_expand_sources.py `
  --queries queries.txt `
  --out artifacts/<run>/deep_discovery/openalex_candidates.jsonl

# Screen candidates
python skills/source-acquisition-suite/scripts/screen_source_candidates.py `
  --candidates artifacts/<run>/deep_discovery/openalex_candidates.jsonl `
  --out-jsonl artifacts/<run>/deep_discovery/screened_candidates.jsonl `
  --out-md artifacts/<run>/deep_discovery/screened_candidates.md

# Acquire approved manifest
python skills/source-acquisition-suite/scripts/acquire_sources_from_manifest.py `
  --manifest artifacts/<run>/source_manifest.json `
  --out-dir artifacts/<run> `
  --reservoir-id 597 `
  --reservoir-name "<Reservoir Name>"

# Docling parse PDFs
.\.venv\Scripts\python.exe skills/source-acquisition-suite/scripts/parse_sources_docling.py `
  --inventory artifacts/<run>/sources/source_inventory.jsonl `
  --out-dir artifacts/<run>/sources/parsed_docling `
  --manifest artifacts/<run>/sources/docling_parse_manifest.jsonl `
  --include-non-pdf

# Validate inventory
python skills/source-acquisition-suite/scripts/validate_source_inventory.py `
  --inventory artifacts/<run>/sources/source_inventory.jsonl `
  --out artifacts/<run>/validation/layer1_source_validation.json
```

## Output Contract

A completed Layer 1 run should contain:

- `source_manifest.json` for approved sources
- `deep_discovery/` for candidate discovery and screening artifacts when used
- `sources/raw/` for preserved raw files
- `sources/text/` for extracted text
- `sources/parsed_docling/` for structured PDF markdown when available
- `sources/source_inventory.jsonl` and `.csv`
- `sources/docling_parse_manifest.jsonl`
- `validation/layer1_source_validation.json`
- `run_summary.md` describing counts, failures, and acquisition limits
