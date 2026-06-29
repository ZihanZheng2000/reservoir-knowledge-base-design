# Deep Source Discovery Protocol

## Purpose

Generate a reviewable candidate pool before formal source acquisition. This module is for discovery, not evidence preservation.

## Inputs

- Reservoir name and aliases
- Dam name and project/program names
- River basin/system name
- Seed official reports, research papers, or data products
- Optional user-supplied search questions

## Discovery Routes

Use multiple routes:

- Official/site search for Tier A candidates.
- OpenAlex/Crossref/Semantic Scholar/library metadata for Tier B candidates.
- Backward search from seed references.
- Forward search from papers or reports citing a seed.
- Lateral search by author, agency, report series, project/program, or DOI cluster.
- Credible media/context search for Tier C candidates.

## Query Families

Search by named system plus evidence-family terms:

- reservoir/dam/system: target reservoir name, dam name, operator, basin, and related operating system names
- program: `LTEMP`, `Adaptive Management Program`, `24-Month Study`, `Post-2026 Operations`
- operation: `release`, `operating policy`, `drought response`, `operating tier`
- infrastructure: `minimum power pool`, `outlet works`, `penstocks`, `low water`
- data/model: `forecast`, `scenario`, `CRSS`, `DMDU`, `uncertainty`
- consequences: `hydropower`, `temperature`, `ecological flow`, `high flow experiment`
- governance: `compact`, `delivery obligation`, `adaptive management`, `post-2026`

Do not require the exact phrase `reservoir operation`.

## Candidate Output Fields

Each candidate should include:

- `candidate_id`
- `discovery_method`
- `query_or_seed`
- `title`
- `year`
- `doi`
- `url`
- `openalex_id` or other metadata ID
- `source_tier_suggestion`
- `evidence_family`
- `access_status`
- `relevance_note`
- `recommended_action`

## Boundary

Do not use search snippets as evidence. Discovery candidates must be screened and then passed into source preservation before KU extraction.
