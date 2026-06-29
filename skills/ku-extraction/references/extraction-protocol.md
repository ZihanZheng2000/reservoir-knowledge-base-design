# Extraction Protocol

## Purpose

Extract operational KUs: concise, source-grounded findings that help explain how a reservoir is operated, constrained, monitored, coordinated, or prioritized for future analysis.

A KU has two jobs:

1. **Summary:** state one operationally useful knowledge point in concise language.
2. **Locator:** point back to the source, page/section/chunk, and evidence quote so a researcher can inspect the original document.

KUs are an index and evidence-navigation layer, not a replacement for the original documents. Later analysis should use KUs to locate relevant evidence and then return to the source text when the question requires deeper interpretation.

## What Counts As A KU

A finding can become a KU when it answers at least one question:

- What reservoir purpose or operating objective is involved?
- What operating rule, threshold, guide curve, release schedule, trigger, or decision criterion matters?
- What dam, outlet, powerplant, intake, low-water infrastructure, or other physical feature affects operation?
- What real-time, drought, flood, emergency, or special-event action is described under a specific condition?
- What agency, agreement, law, planning process, or document governs operation?
- What operational dataset, monitoring record, forecast product, or data system supports decisions?
- What research, model, experiment, technical analysis, or scenario study has been conducted, and what operational role does it play?
- What uncertainty, evidence gap, unresolved issue, or future decision is identified?

Use these approved engineering dimensions:

- `Operation Purpose`: authorized purposes, management objectives, or operational priorities such as water delivery, storage protection, hydropower, flood control, recreation, ecology, temperature management, or compact compliance.
- `Operation Rules`: specific operating rules, thresholds, release tiers, release volumes, guide curves, triggers, if/then criteria, operating alternatives, or rule status such as current, projected, proposed, expired, or emergency.
- `Infrastructure`: physical infrastructure and operating limits, including dam structure, outlet works, penstocks, turbines, powerplant, bypass tubes, river outlet works, minimum power pool, dead pool, low-water infrastructure, release capacity, and infrastructure modification.
- `Real-Time / Emergency Operations`: actions taken or planned under immediate, drought, flood, emergency, maintenance, experimental, or special-event conditions. This category should describe an operational action under a condition, not merely the existence of a plan or agreement.
- `Coordination / Governance`: agencies, laws, agreements, consultation processes, environmental compliance, tribal or stakeholder coordination, basin governance, operating documents, and decision authority.
- `Operational Data`: datasets, monitoring records, forecasts, hydrologic products, reservoir elevation/release/inflow records, data portals, update frequency, variables, coverage, and how the data are used in operations.
- `Research / Modeling / Analysis`: studies, models, experiments, technical reports, scenario analysis, environmental analysis, sediment/ecology/hydropower analysis, or methods that produce knowledge about Lake Powell or Glen Canyon Dam operations.
- `Evidence Gap / Uncertainty`: missing evidence, weak source support, unresolved assumptions, data limitations, model uncertainty, future rule uncertainty, infrastructure uncertainty, or claims needing stronger official/data support.

## What Does Not Count

Do not extract:

- website navigation, menus, footers, contact blocks
- generic agency mission statements
- pure bibliographic metadata unless it identifies a usable data/model source
- duplicate claims already captured from the same source
- broad background with no operational implication
- cross-document statements such as "multiple documents show..." because those belong to synthesis

Do not write low-quality structured fields:

- `finding` must not simply copy the evidence quote with a generic prefix.
  - Bad: `The source identifies an operating rule or operating-guideline issue: Consistent with Section 6.C.1...`
  - Better: `For WY2026, Lake Powell is assigned to the Mid-Elevation Release Tier, with the cited guideline sections used to justify the projected release volume.`
- `why_it_matters` must not be a reusable template sentence.
  - Bad: `This KU preserves source-grounded operation rules evidence for later Lake Powell review, retrieval, and synthesis.`
  - Better: `This matters because the operating tier determines how Lake Powell release volumes are interpreted and compared across forecast updates, drought-response actions, and later synthesis.`
- `condition_or_trigger` must not repeat the engineering dimension name.
  - Bad: `operation_rules`
  - Bad: `data_models_forecasts`
  - Better: `WY2026 Mid-Elevation Release Tier under Section 6.C.1 / 6.E`
  - Better: `May 2026 most probable unregulated inflow forecast`

## Extraction Procedure

Use this pipeline:

```text
document -> page/section-aware chunks -> candidate KUs -> dedupe/consolidate -> validated KUs
```

1. Skim the packet metadata: `source_id`, `document_type`, `title`, `url`, owner.
2. Segment the document into logical sections when headings are available. For PDFs, preserve page numbers when available. For long unstructured text, create full-coverage chunks while preserving order.
3. Read each section or chunk for operational signals: numbers, thresholds, dates, rules, release values, operating tiers, guide curves, model names, datasets, agencies, alternatives, triggers, risk terms, infrastructure terms, and required coordination steps.
4. Draft candidate findings in plain language from each section or chunk.
5. Filter candidates by operational relevance.
6. Consolidate near-duplicates within the same source.
7. Merge candidates that are fragments of the same operational finding.
8. Attach a short evidence quote to each remaining KU.
9. Assign exactly one main engineering dimension.
10. Write JSONL records with field-specific content:
   - `finding`: analyst-written restatement of the operational point.
   - `why_it_matters`: specific operational implication of that point.
   - `condition_or_trigger`: actual trigger, threshold, scenario, date, rule status, data context, or decision condition when available; leave concise notes when no explicit condition exists.
11. Validate and repair.

## Priority Source Rule

Official operating manuals, operation guides, reservoir operation plans, water control manuals, annual operating plans, and agency technical appendices are priority sources. These documents often contain dense operational detail. For these sources, extract at a finer level than ordinary webpages:

- individual operating purposes and priorities
- release rules, thresholds, operating tiers, and decision criteria
- seasonal or scenario-specific operating procedures
- drought, flood, maintenance, experimental, or emergency triggers
- infrastructure capacities and low-water constraints
- required data inputs, forecasts, monitoring products, and reporting procedures
- responsible agencies, authorities, consultation steps, and documentation requirements

Do not collapse an official operating manual into one generic KU. A single high-value manual can legitimately produce many KUs if the findings are distinct and source-grounded.

## Chunking Standard

Do not extract KUs from only the first part of a long document. First-N-character truncation is acceptable only for a quick smoke test and must be labeled as incomplete.

For a formal run, use this hierarchy:

1. **Structure-aware parsing when possible.** Prefer Docling, Unstructured, or a similar document parser that preserves page numbers, headings, tables, and document elements.
2. **Section-first chunking.** Use headings or detected document structure as the first chunk boundary.
3. **Page-aware fallback for PDFs.** If reliable headings are not available, chunk by page or page ranges while preserving `page_start` and `page_end`.
4. **Window fallback for plain text.** If only plain extracted text is available, split the full text into overlapping chunks, preserving `chunk_index`, `char_start`, and `char_end`.

Recommended fallback window:

```text
target chunk size: 8,000-12,000 characters
overlap: 800-1,200 characters
```

Every extraction packet should include enough locator metadata to return to the source:

- `source_id`
- `source_title`
- `source_url`
- `chunk_id`
- `chunk_index`
- `chunk_count`
- page or section metadata when available
- character span when page metadata is unavailable

When page/section metadata is unavailable, record that limitation explicitly. Do not pretend that source-level traceability is page-level traceability.

## Relationship To Retrieval And Deep Synthesis

KU extraction should prepare the project for later retrieval-augmented analysis:

```text
KU = structured operational summary + pointer to source evidence
source text = evidence base
retrieval = route back to relevant source chunks
deep synthesis = cross-KU analysis verified against original evidence
```

For simple synthesis, reading validated KUs may be enough. For deep synthesis, conflict checks, high-stakes claims, or technical interpretation, the analyst or model should use KU IDs, source IDs, locations, and evidence quotes to retrieve and reread the relevant original sections.

This means KU locators matter as much as KU wording. A good KU should let a researcher quickly answer:

- Which source did this come from?
- Where in the source should I look?
- What short evidence quote supports it?
- What larger source chunk should be reread before making a synthesis claim?

## Count Policy

Do not use an artificial KU count cap. A source can yield zero, one, or many KUs depending on how many distinct operational findings it contains.

For short webpages, a small number of KUs is normal. For engineering manuals, operating plans, environmental impact statements, technical appendices, or data documentation, many KUs may be appropriate. The limiting rule is quality, not quantity.

Accept a KU only when it is:

- operationally relevant
- source-grounded with a supporting quote
- distinct from other KUs from the same source
- concise enough for retrieval
- specific enough to locate the source passage again
- useful for later synthesis or manual review

## Confidence Labels

- `high`: directly stated by the source with clear quote support.
- `medium`: supported by the source but requires mild interpretation or context.
- `low`: weakly supported; use rarely and prefer to exclude.

## Evidence Quote

Use the shortest quote that supports the finding. Keep quotes under 320 characters. If the source text is an extracted webpage, use `source_location` such as:

```text
extracted text; Current Operations section
```

For PDFs, use page/section when available.

## KU ID Pattern

Use stable IDs within a workflow run:

```text
KU-<reservoir-short>-<source-number>-<sequence>
```

Example:

```text
KU-LP-OFFICIAL-001
```

When appending to an existing KU file, inspect existing IDs first and continue the sequence.

## Quality Checklist

Before accepting a KU, check:

- Is this about reservoir operation, monitoring, constraints, governance, or future operating decisions?
- Is it one finding rather than a pile of facts?
- Would a user plausibly search for this later?
- Can the evidence quote support the finding?
- Is it separate from synthesis?
- Is the engineering dimension correct?
- For official operating manuals or guides, did extraction capture detailed rules and criteria rather than only the document purpose?

## Validation Strategy

Validation has two levels.

### Automated Validation

Automated validation checks whether the KU file is structurally usable:

- each line is valid JSON
- required fields are present
- `ku_id` values are unique
- `source_id` values match the source inventory
- `engineering_dimension` values use the approved dimension list
- `evidence_quote` exists and has a reasonable length
- `affected_operation_purposes` is a non-empty list

Automated validation does not prove that the KU is substantively correct, complete, or optimally classified. It only confirms that the output is machine-readable, traceable, and ready for human or downstream review.

### Research Validation

Research validation checks the quality of extraction:

- Source-grounding check: sample KUs and verify that the finding is directly supported by the evidence quote and source location.
- Coverage check: review each source to see whether major operational findings were missed.
- Over-extraction check: remove KUs that are metadata-only, too generic, or not operationally useful.
- Dimension check: confirm that the assigned engineering dimension is the best primary category.
- Gold comparison: for key engineering documents, ask a domain expert or human researcher to extract a reference set and compare precision, recall, evidence support, and dimension accuracy.

For development runs, sample-based review is acceptable. For core engineering documents, use human review or expert gold comparison before treating the KUs as accepted knowledge-base content.

Use LLM/Codex extraction as first-pass structured extraction, not as final authority.
