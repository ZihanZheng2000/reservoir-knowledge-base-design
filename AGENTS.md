# Agent Instructions

This project builds source-grounded reservoir operation knowledge-base datasets using an AI-native workflow.

## Operating Principles

- Preserve source evidence before extracting knowledge.
- Separate document-level Evidence Units (EUs), Knowledge Cards (KCs), and cross-document Synthesis Cards.
- Keep source links, EU IDs, KC IDs, synthesis IDs, and evidence locators traceable.
- Use Python for deterministic processing and validation.
- Use LLM reasoning for semantic screening, evidence extraction, knowledge consolidation, and synthesis.
- Use the agent to coordinate skills, scripts, validation checks, reruns, and versioned artifacts.
- Treat warnings as review signals, not automatic failures.
- Do not introduce unsupported claims in Knowledge Cards, Synthesis Cards, or reports.
- Use source wording, project taxonomy, or clearly defined terms; do not invent professional-sounding terminology that is not grounded in the source documents.
- Do not overwrite previous runs. Create a new folder under `runs/` for each reservoir/run.

## Routine Workflow Stages

1. **Source acquisition**
   - Skill: `skills/source-acquisition/`
   - Purpose: collect, screen, preserve, parse, and validate reservoir-related sources.
   - Output: preserved candidate inventory, acquired-source inventory, raw files, extracted text, parsing manifest.

2. **Evidence extraction**
   - Skill: `skills/evidence-extraction/`
   - Purpose: convert each source document into traceable, source-grounded document-level Evidence Units (EUs).
   - Output: canonical EU JSONL, a human-readable EU Markdown view, and EU validation.

3. **Knowledge consolidation**
   - Skill: `skills/knowledge-consolidation/`
   - Purpose: conservatively group EUs that answer the same operational question into Knowledge Cards (KCs), while preserving conditions, source context, and EU evidence chains.
   - Output: Knowledge Card JSONL, consolidation validation.

4. **Synthesis**
   - Skill: `skills/synthesis/`
   - Purpose: analyze cross-document relationships using validated EUs and KCs.
   - Output: Synthesis Card JSONL, synthesis report, synthesis validation.

5. **Indexing**
   - Skill: `skills/indexing/`
   - Purpose: encode validated EUs, KCs, and Synthesis Cards into index-ready records while preserving their IDs, metadata, and evidence chains.
   - Output: encoded knowledge records, index manifest.

6. **Report generation**
   - Skill: `skills/report-generation/`
   - Purpose: generate human-readable reports from validated structured knowledge.
   - Output: report, claim-evidence map, report validation notes.

**Run orchestration (entry point; not a seventh workflow stage)**
   - Skill: `skills/run-orchestration/`
   - Purpose: start a compliant run, enforce stage order, prepare review workpapers, and perform final acceptance checks.
   - Use this skill whenever starting, resuming, or handing off a reservoir run.

## Required Run Artifacts

Each run under `runs/<reservoir_id>_<run_date>/` should contain:

- `run_manifest.json`
- `01_source_acquisition/source_manifest.json`
- `01_source_acquisition/sources/candidate_inventory.jsonl`
- `01_source_acquisition/sources/source_inventory.jsonl`
- `01_source_acquisition/sources/raw/`
- `01_source_acquisition/sources/text/`
- `02_evidence_extraction/evidence_units.jsonl`
- `02_evidence_extraction/evidence_units.md`
- `03_knowledge_consolidation/knowledge_cards.jsonl`
- `03_knowledge_consolidation/knowledge_cards.md`
- `04_synthesis/synthesis_cards.jsonl`
- `04_synthesis/synthesis_cards.md`
- `05_indexing/encoded_knowledge_records.jsonl`
- `05_indexing/index_manifest.json`
- `06_report_generation/`
- `validation/`

Every numbered stage folder must also contain `stage_manifest.json` and
`stage_summary.md`, following `docs/run-artifact-contract.md`. The manifest is
the machine-readable delivery record; the summary is the fixed human-readable
handoff. Do not treat ad hoc filenames or free-form notes as substitutes.
Each stage must also contain `automated_validation.json` and `human_review.json`.
The first is written by the validator; the second is the human review record
prefilled from the stage's actual records. The human-review table must preserve
the Codex decision in one column and provide a separate human decision column;
it must not be an empty placeholder.

For stages 2--4, `human_review.json` must include resolvable relative links to
the relevant preserved PDF/text files and each stage must contain
`source_navigation.md`. Do not hand-write a review workpaper when
`validation/scripts/prepare_human_review.py` can generate it from the canonical
records.

## Run Rules

- Do not overwrite previous runs.
- Create a new run folder under `runs/` for each reservoir and run date.
- Preserve raw sources before extracting knowledge.
- Run available validation scripts before using a stage output downstream.
- Complete the stage manifest and stage summary only after the stage artifacts
  and automated validation result are available.
- After successful stage finalization, remove only reproducible execution
  intermediates according to `docs/run-artifact-contract.md`; preserve raw
  source evidence, canonical records, and validation results.
- Validate EUs before consolidation; validate KCs before synthesis; validate Synthesis Cards before indexing or report generation.
- Record warnings, failed acquisitions, parser fallbacks, validation errors, and unresolved issues in the run summary.
- If a stage is rerun, keep the previous output or write the rerun to a clearly named new folder or versioned file.
- Before a run is handed off, execute `validation/scripts/validate_run_contract.py`
  and save `validation/run_contract_validation.json`.

## Validation And Human Review

- Follow `docs/validation-framework.md` as the canonical validation design.
- Every stage must complete automated validation before its output is used downstream. The two automated indicators are **schema conformance** and **traceability integrity**; Source acquisition uses **acquisition success** instead of traceability integrity.
- Human review is a documented sampled evaluation, not a routine stage gate unless the run or study explicitly requires it. Each stage uses the three review indicators defined in the framework.
- Store validation with the artifact it evaluates: `<stage>/automated_validation.json` and `<stage>/human_review.json`. The run-level `validation/` folder contains summaries only.
- A review with all required decisions/scores filled is complete even if its
  initial `review_status` was not changed manually; the summary tooling must
  report this as `completed (inferred from filled fields)`.

## Boundary Rules

- Sources are evidence records.
- Evidence Units are document-level findings grounded in one source.
- Knowledge Cards are a separate knowledge layer: they conservatively consolidate repeated or complementary EUs that answer the same operational question, preserve relevant conditions and disagreements, and cite every supporting EU ID. Knowledge Cards are not new source evidence or higher-level analytical claims.
- Synthesis Cards are a separate analysis layer: they analyze supported cross-document relationships and must cite supporting EU IDs and, where useful, KC IDs.
- Important or contested synthesis/report claims should use EU locators to reread the original source sections before finalization.
- Evidence Units, Knowledge Cards, and Synthesis Cards are all knowledge-base records with different evidence roles; encoded index records preserve their IDs and evidence chains for search use.
- Reports are controlled transformations from validated records into readable outputs; they should not introduce unsupported claims.

## Stable Reservoir IDs

- Use a stable, externally maintained reservoir identifier supplied by the
  user or an authoritative source whenever one is available; record its system
  in `run_manifest.json` as `reservoir_id_system`.
- If no authoritative identifier is available, use a stable project ID of the
  form `PRJ-<UPPERCASE-RESERVOIR-SLUG>` and set
  `reservoir_id_system` to `project_assigned`; never silently replace it in a
  later run.
- The run folder is `<lowercase_reservoir_slug>_<YYYYMMDD>` and is not itself
  the reservoir ID.

## Legacy Materials

- Do not use files labelled `legacy`, historical KU/F2 workflows, or optional
  method-comparison assets as routine instructions. The routine contract is
  this file, `docs/run-artifact-contract.md`, and
  `docs/validation-framework.md`.

## Error Handling

- If source acquisition fails, search for alternate URLs, DOI pages, official mirrors, repository copies, OpenAlex open-access links, or replacement sources.
- If a PDF URL returns HTML, preserve the HTML when useful and mark the content quality issue rather than automatically discarding it.
- If extracted text is very short, mark it for review or recovery search instead of treating it as a hard failure.
- If validation fails, fix the issue or clearly mark it before downstream use.

## Review And Refinement Scope

Routine runs should proceed automatically after the workflow is defined. Human review, sampled validation, workflow refinement, and transfer validation are research-design activities documented in `docs/validation-framework.md`, not required stop points inside every routine run.

