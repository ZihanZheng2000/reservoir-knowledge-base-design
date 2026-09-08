# Deep Source Discovery Protocol

## Purpose

Generate a reviewable candidate pool before candidate screening and formal download, and support follow-up discovery after selected sources have been downloaded and text-extracted.

This protocol has two discovery modes:

1. **Initial discovery:** use general reservoir-operation query families before download.
2. **Text-informed expansion:** after selected sources are downloaded and text is extracted, mine the preserved text for reservoir-specific terms, source-chain leads, references, model names, dataset names, agency/program names, and document titles, then run follow-up discovery.

Discovery does not decide final inclusion, download sources, extract text, or create EU-ready source records. It creates candidate leads that must pass candidate screening.

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

## A. General Query Families

Use these general families for the first pass. They should work across reservoirs and should not hard-code terms from a single reservoir or basin case.

- reservoir/dam/system: reservoir name, dam name, owner/operator, river, basin, project name, system name
- operation documents: `water control manual`, `reservoir regulation manual`, `operation plan`, `operating plan`, `operating rules`, `operating criteria`, `rule curve`, `guide curve`
- release and storage operations: `release`, `outflow`, `storage`, `elevation`, `flood control`, `drought operation`, `emergency operation`, `seasonal operation`, `conservation storage`
- infrastructure: `spillway`, `outlet works`, `intake`, `gate`, `penstock`, `turbine`, `powerplant`, `dead pool`, `minimum pool`, `low water`, `release capacity`
- operational data: `inflow`, `outflow`, `reservoir storage`, `reservoir elevation`, `forecast`, `snowpack`, `stream gage`, `data portal`, `API`, `time series`
- models and methods: `reservoir simulation`, `operation model`, `decision support model`, `hydrologic model`, `scenario analysis`, `uncertainty analysis`
- consequences and objectives: `hydropower`, `water supply`, `ecological flow`, `environmental flow`, `temperature`, `sediment`, `water quality`, `recreation`, `navigation`
- governance and decisions: `agreement`, `compact`, `license`, `FERC`, `NEPA`, `EIS`, `record of decision`, `consultation`, `stakeholder`, `tribal`, `delivery obligation`

Do not require the exact phrase `reservoir operation`.

## B. Reservoir-Specific Expansion Terms

After initial discovery and especially after text extraction, identify reservoir-specific terms and use them for targeted follow-up searches.

Do not hard-code basin-specific terms as universal query terms. Terms such as a specific model, program, agency office, guideline, or operating agreement should be discovered from the target reservoir's sources and then used in follow-up discovery.

Mine for:

- operator, owner, agency, district, region, or project office names;
- project/program names;
- operating document titles;
- model names and decision-support systems;
- dataset, data portal, API, or forecast product names;
- legal agreements, licenses, compacts, Records of Decision, EIS/EA titles, and policy documents;
- upstream/downstream reservoir names and system names;
- named experiments, drought plans, flood plans, emergency actions, or special operations;
- major stakeholder, tribal, environmental, hydropower, or governance program names.

Example pattern:

```text
target reservoir + general query -> discover operator/model/program/document names
discovered names -> targeted follow-up queries
```

## C. Deep Research Expansion Chain

Use source relationships, not only keywords, to expand the candidate pool.

After seed sources are identified, expand through:

- backward search: references cited by key papers, reports, EIS documents, manuals, and technical appendices;
- forward search: later papers or reports that cite a key source;
- document-family search: companion volumes, appendices, environmental assessments, technical memoranda, model documentation, datasets, and decision records;
- agency/project chain: operator pages, district/region pages, program pages, project pages, and data portals;
- model/data chain: model names, dataset names, API names, scenario names, and forecast products found inside sources;
- legal/governance chain: licenses, compacts, agreements, Records of Decision, consultation documents, operating guidelines, and rulemaking pages;
- event chain: drought, flood, emergency, maintenance, experimental, or incident documents linked to operational plans, press releases, monitoring reports, and after-action material.

Text-informed expansion should loop back into candidate screening:

```text
downloaded/text-extracted sources -> expansion leads -> follow-up discovery -> candidate screening -> selected sources
```

Stop expanding when new candidates become mostly duplicates, background-only, inaccessible, or no longer improve source-family coverage.

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

For text-informed expansion leads, also preserve:

- `lead_type`
- `lead_text`
- `source_id`
- `source_title`
- `evidence_snippet`
- `suggested_query`
- `reason`

## Boundary

Do not use search snippets as evidence. Discovery candidates must pass through candidate screening, source download, text extraction, quality review, and inventory validation before EU extraction.
