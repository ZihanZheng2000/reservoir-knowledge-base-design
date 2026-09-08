# Extraction Protocol

## Purpose

Extract operational EUs: concise, source-grounded findings that help explain how a reservoir is operated, constrained, monitored, coordinated, or prioritized for future analysis.

A EU has two jobs:

1. **Summary:** state one operationally useful knowledge point in concise language.
2. **Locator:** point back to the source, page/section/chunk, and evidence quote so a researcher can inspect the original document.

EUs are an index and evidence-navigation layer, not a replacement for the original documents. Later analysis should use EUs to locate relevant evidence and then return to the source text when the question requires deeper interpretation.

## What Counts As A EU

A finding can become a EU when it answers at least one question:

- What reservoir purpose or operating objective is involved?
- What operating rule, threshold, guide curve, release schedule, trigger, or decision criterion matters?
- What dam, outlet, powerplant, intake, low-water infrastructure, or other physical feature affects operation?
- What real-time, drought, flood, emergency, or special-event action is described under a specific condition?
- What agency, agreement, law, planning process, or document governs operation?
- What operational dataset, monitoring record, forecast product, or data system supports decisions?
- What research, model, experiment, technical analysis, or scenario study has been conducted, and what operational role does it play?
- What uncertainty, evidence gap, unresolved issue, or future decision is identified?

Use these approved engineering dimensions:

- `Operation Purposes`: authorized purposes, management objectives, or operational priorities, described directly in plain language.
- `Multiple Objectives`: cases where the source explicitly describes more than one operating objective, competing purpose, or need to balance different reservoir functions.
- `Storage Capacity and Storage Targets`: storage capacity, storage targets, elevation targets, minimum pool, dead pool, low-storage thresholds, target elevations, storage protection, and storage-related operating limits.
- `Operation Rules`: specific operating rules, thresholds, release schedules, guide curves, triggers, if/then criteria, operating alternatives, release volumes, operating tiers, or rule status such as current, projected, proposed, expired, or emergency.
- `Emergency Operations`: drought, flood, infrastructure, safety, or other emergency actions that change normal operations under defined conditions.
- `Real-Time Operations`: near-term or real-time operational adjustments, monitoring-based decisions, short-term forecasts, daily/monthly release adjustments, maintenance operations, or special-event operations.
- `Regulation / Governance`: agencies, laws, agreements, consultation processes, environmental compliance, basin governance, operating documents, decision authority, and stakeholder or tribal coordination.
- `Uncertainty and Risk Management`: hydrologic uncertainty, forecast uncertainty, model uncertainty, future rule uncertainty, infrastructure risk, planning risk, scenario uncertainty, and risk-management actions.
- `Observation and Data`: datasets, monitoring records, inflow/storage/elevation/release records, hydrologic observations, forecast products, data portals, update frequency, variables, coverage, and how the data are used in operations.
- `Inflow Forecast`: inflow forecasts, forecast horizons, forecast scenarios, forecast updates, probabilistic inflow assumptions, and how inflow forecasts affect operating decisions.
- `Modeling`: reservoir operation models, hydrologic models, scenario models, climate or decision models, technical analyses, experiments, and modeling assumptions that support operational understanding.
- `Stakeholders`: water users, agencies, tribes, local communities, power customers, environmental groups, recreational users, or other stakeholder groups whose interests, roles, concerns, or coordination processes affect reservoir operations.
- `Operation Failure`: operational failure modes, unresolved operational problems, inability to meet targets, release-capacity limitations, low-storage failures, hydropower loss, ecological failures, governance deadlock, or other cases where reservoir operations do not achieve intended purposes.

## Dimension Decision Rules

Use the most specific dimension supported by the source text. Do not assign a EU to `Storage Capacity and Storage Targets` merely because the sentence mentions storage, elevation, or reservoir levels. Choose the dimension based on the main operational function of the finding:

- Use `Inflow Forecast` when the finding is mainly about forecasted inflow volume, forecast horizon, forecast date, probable/minimum/maximum scenario, forecast update, or how an inflow forecast affects operations.
- Use `Observation and Data` when the finding is mainly about observed or monitored data, historical records, data portals, variables, coverage, update frequency, or operational datasets.
- Use `Modeling` when the finding is mainly about a model, simulation system, decision framework, scenario analysis, technical method, or modeling assumption. Model names, model inputs, and model outputs belong here unless the EU is explicitly stating an operating rule.
- Use `Regulation / Governance` when the finding is mainly about law, compact, agreement, agency authority, NEPA or consultation process, decision responsibility, stakeholder coordination, or documentation requirement.
- Use `Operation Rules` when the finding states a rule, threshold, release schedule, operating tier, guide curve, if/then criterion, formal trigger, or rule status.
- Use `Storage Capacity and Storage Targets` when the finding is mainly about storage capacity, elevation target, minimum pool, dead pool, low-storage threshold, storage protection target, or storage-related operating limit.
- Use `Emergency Operations` when the finding describes an emergency, drought, flood, infrastructure, or safety action that changes normal operation under defined conditions.
- Use `Real-Time Operations` when the finding describes near-term operational adjustment, monitoring-based action, short-term release operation, maintenance operation, or special-event implementation.
- Use `Multiple Objectives` only when the source explicitly frames more than one operating objective or tradeoff in the same finding.
- Use `Stakeholders` only when the stakeholder role, concern, participation, or coordination process is the main finding. If a stakeholder is merely named as part of governance, use `Regulation / Governance`.
- Use `Operation Failure` when the source identifies an operating problem, failure mode, inability to meet a target, loss of function, unresolved operational breakdown, or system condition where intended purposes may not be achieved.
- Use `Uncertainty and Risk Management` when the finding is mainly about uncertainty, risk, scenario vulnerability, planning risk, or actions taken to manage risk. Do not use it for every forecast value; use `Inflow Forecast` for forecast values unless the source emphasizes uncertainty or risk.

Common misclassification checks:

- A forecast value that implies storage risk is still `Inflow Forecast` unless the EU is primarily about a storage target or threshold.
- A model result that reports reservoir elevation is still `Modeling` if the point is about the model, method, or scenario analysis.
- A legal agreement that includes storage language is still `Regulation / Governance` if the point is authority, process, or obligation.
- A storage threshold used as an if/then operating trigger may be `Operation Rules`; a storage threshold described as a physical or target condition may be `Storage Capacity and Storage Targets`.
- A drought response plan is `Emergency Operations` only when the EU describes an action under drought/emergency conditions. If the EU describes who approves the plan or what agreement governs it, use `Regulation / Governance`.

## Operation Purpose Writing Rules

Describe operation purposes directly using the terminology in the source. Do
not add a separate `affected_operation_purposes` field. Not every EU has an
identifiable operation purpose, and forcing a purpose label creates noisy
metadata. Do not infer a purpose only because a stakeholder, structure, or
downstream effect is mentioned.

<!--
Previous EU dimension set retained for reference only:

- `Operation Purpose`: authorized purposes, management objectives, or operational priorities such as water delivery, storage protection, hydropower, flood control, recreation, ecology, temperature management, or compact compliance.
- `Operation Rules`: specific operating rules, thresholds, release tiers, release volumes, guide curves, triggers, if/then criteria, operating alternatives, or rule status such as current, projected, proposed, expired, or emergency.
- `Infrastructure`: physical infrastructure and operating limits, including dam structure, outlet works, penstocks, turbines, powerplant, bypass tubes, river outlet works, minimum power pool, dead pool, low-water infrastructure, release capacity, and infrastructure modification.
- `Real-Time / Emergency Operations`: actions taken or planned under immediate, drought, flood, emergency, maintenance, experimental, or special-event conditions. This category should describe an operational action under a condition, not merely the existence of a plan or agreement.
- `Coordination / Governance`: agencies, laws, agreements, consultation processes, environmental compliance, tribal or stakeholder coordination, basin governance, operating documents, and decision authority.
- `Operational Data`: datasets, monitoring records, forecasts, hydrologic products, reservoir elevation/release/inflow records, data portals, update frequency, variables, coverage, and how the data are used in operations.
- `Research / Modeling / Analysis`: studies, models, experiments, technical reports, scenario analysis, environmental analysis, sediment/ecology/hydropower analysis, or methods that produce knowledge about the target reservoir, dam, or reservoir system operations.
- `Evidence Gap / Uncertainty`: missing evidence, weak source support, unresolved assumptions, data limitations, model uncertainty, future rule uncertainty, infrastructure uncertainty, or claims needing stronger official/data support.
-->

## What Does Not Count

Do not extract:

- website navigation, menus, footers, contact blocks
- generic agency mission statements
- pure bibliographic metadata unless it identifies a usable data/model source
- broad background with no operational implication
- cross-document statements such as "multiple documents show..." because those belong to synthesis

Do not write low-quality structured fields:

- `finding` may reuse exact source wording when it is already clear, precise, and
  suitable as a standalone EU. Do not require paraphrasing. Preserve official
  names, rule names, model names, program names, technical terms, and defined
  terminology exactly; do not replace them with approximate synonyms.
  Phrases such as `The source identifies...` and `The source states...` are
  allowed, but the sentence must express a specific operational claim.
  - Weak: `The source identifies an operating rule: Consistent with Section 6.C.1...`
  - Weak: `The source identifies a storage condition: Inflow Forecasts and Model Projections...`
  - Acceptable: `The source identifies hydropower generation as an authorized reservoir purpose and links that purpose to maintaining releases through the powerplant.`
  - Preferred when source attribution is unnecessary: `Hydropower generation is an authorized reservoir purpose that depends on maintaining releases through the powerplant.`
  - Preferred: `The May forecast projects below-average unregulated inflow, which informs the reservoir's short-term release and storage outlook.`
- `why_it_matters` must not be a reusable template sentence.
  - Bad: `This EU preserves source-grounded operation rules evidence for later reservoir review, retrieval, and synthesis.`
  - Better: `This matters because the operating tier determines how release volumes are interpreted and compared across forecast updates, drought-response actions, and later synthesis.`
- Do not add a separate `condition_or_trigger` field. If a trigger, threshold, scenario, date, rule status, data context, or decision condition is important, include it directly in the `finding`, `why_it_matters`, evidence quote, or `notes`.

## Extraction Procedure

Use this pipeline:

```text
document -> page/section-aware chunks -> candidate EUs -> validated EUs
```

1. Skim the packet metadata: `source_id`, `document_type`, `title`, `url`, owner.
2. Segment the document into logical sections when headings are available. For PDFs, preserve page numbers when available. For long unstructured text, create full-coverage chunks while preserving order.
3. Read each section or chunk for operational signals: numbers, thresholds, dates, rules, release values, operating tiers, guide curves, model names, datasets, agencies, alternatives, triggers, risk terms, infrastructure terms, and required coordination steps.
4. Draft candidate findings in plain language from each section or chunk.
5. Filter candidates by operational relevance.
6. Compare candidates by operational meaning. When two candidates state the
   same fact, retain one EU with the clearest evidence and source locator.
7. Keep different operational facts separate even when they occur in the same
   section or use the same engineering dimension. Do not merge by topic alone.
8. Attach a short evidence quote to each supported EU.
9. Assign exactly one main engineering dimension.
10. Write JSONL records with field-specific content:
   - `finding`: a clear operational statement that may preserve exact source
     wording and must preserve source-defined names and technical terms.
   - `why_it_matters`: specific operational implication of that point.
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

Do not collapse an official operating manual into one generic EU. A single high-value manual can legitimately produce many EUs if the findings are distinct and source-grounded.

## Chunking Standard

Do not extract EUs from only the first part of a long document. First-N-character truncation is acceptable only for a quick smoke test and must be labeled as incomplete.

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

EU extraction should prepare the project for later retrieval-augmented analysis:

```text
EU = structured operational summary + pointer to source evidence
source text = evidence base
retrieval = route back to relevant source chunks
deep synthesis = cross-EU analysis verified against original evidence
```

For simple synthesis, reading validated EUs may be enough. For deep synthesis, conflict checks, high-stakes claims, or technical interpretation, the analyst or model should use EU IDs, source IDs, locations, and evidence quotes to retrieve and reread the relevant original sections.

This means EU locators matter as much as EU wording. A good EU should let a researcher quickly answer:

- Which source did this come from?
- Where in the source should I look?
- What short evidence quote supports it?
- What larger source chunk should be reread before making a synthesis claim?

## Count Policy

Do not use an artificial EU count cap. A source can yield zero, one, or many EUs depending on how many distinct operational findings it contains.

For short webpages, a small number of EUs is normal. For engineering manuals, operating plans, environmental impact statements, technical appendices, or data documentation, many EUs may be appropriate. The limiting rule is quality, not quantity.

Accept a EU only when it is:

- operationally relevant
- source-grounded with a supporting quote
- distinct from other EUs from the same source
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

## EU ID Pattern

Use stable IDs within a workflow run:

```text
EU-<reservoir-short>-<source-number>-<sequence>
```

Example:

```text
EU-LP-OFFICIAL-001
```

When appending to an existing EU file, inspect existing IDs first and continue the sequence.

## Quality Checklist

Before accepting a EU, check:

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

Use `scripts/validate_operational_kus.py` after the LLM/Codex extraction writes `evidence_units.jsonl`, then use `scripts/render_ku_preview.py` to create the required `evidence_units.md` reading view.

Automated validation checks whether the EU file is structurally usable:

- each line is valid JSON
- required fields are present
- `eu_id` values are unique
- `source_id` values match the source inventory
- `engineering_dimension` values use the approved dimension list
- `evidence_quote` exists and has a reasonable length
- disallowed fields such as `affected_operation_purposes` and `condition_or_trigger` are absent
- empty template findings and generic `why_it_matters` wording are rejected;
  source-attribution phrases are permitted when the resulting claim is specific

Automated validation does not prove that the EU is substantively correct, complete, or optimally classified. It only confirms that the output is machine-readable, traceable, and ready for human or downstream review.

### Research Validation

Research validation checks the quality of extraction:

- Source-grounding check: sample EUs and verify that the finding is directly supported by the evidence quote and source location.
- Coverage check: review each source to see whether major operational findings were missed.
- Over-extraction check: remove EUs that are metadata-only, too generic, or not operationally useful.
- Dimension check: confirm that the assigned engineering dimension is the best primary category.
- Gold comparison: for key engineering documents, ask a domain expert or human researcher to extract a reference set and compare precision, recall, evidence support, and dimension accuracy.

For development runs, sample-based review is acceptable. For core engineering documents, use human review or expert gold comparison before treating the EUs as accepted knowledge-base content.

Use LLM/Codex extraction as first-pass structured extraction, not as final authority.
