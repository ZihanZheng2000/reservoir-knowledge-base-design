# Synthesis Protocol

## Purpose

Turn document-level reservoir KUs into a separate synthesis layer with two parts:

1. **KU consolidation:** integrate the important source-grounded information already extracted in the KU layer.
2. **Cross-KU analysis:** identify cross-document patterns, evidence relationships, true discrepancies, operational tradeoffs, source-corpus evidence gaps, and unresolved operational issues.

Synthesis cards are not source-level findings. They must cite KU IDs rather than pretending to be direct evidence from documents.

For shallow synthesis, validated KU summaries can be enough to identify candidate patterns. For deep synthesis, KUs should be treated as pointers back to source evidence: the analyst or model should retrieve and reread the relevant original sections before making stronger claims about conflicts, tradeoffs, or unresolved operational issues.

V3 synthesis makes this explicit:

```text
KUs are first consolidated into dimension-level knowledge points.
Consolidated knowledge points identify candidate relationships.
KU locators route the analyst back to source chunks/sections.
Source context verifies, narrows, or rejects the synthesis claim.
The final synthesis card records how deeply the evidence was checked.
```

Do not force output categories. If there is no meaningful evidence for a KU dimension or analysis type, omit it and state in notes that the evidence was insufficient.

## Input

Use a KU JSONL file where each record has:

- `ku_id`
- `knowledge_layer = document_finding`
- `source_id`
- `engineering_dimension`
- `finding`
- `why_it_matters`
- `affected_operation_purposes`
- `condition_or_trigger`
- `evidence_quote`
- `source_location`

## Output

The stage should produce two outputs when possible.

### Output 1: Consolidated Knowledge Points

Use consolidated knowledge points to restate and organize what the KU layer already says. These are not high-level research claims. They are organized summaries of the KUs by operational dimension.

Recommended file:

```text
synthesis/consolidated_knowledge_points.jsonl
```

Recommended fields:

- `consolidated_id`
- `knowledge_layer = consolidated_ku_synthesis`
- `reservoir_id`
- `reservoir_name`
- `ku_dimension`
- `title`
- `consolidated_finding`
- `based_on_ku_ids`
- `source_coverage_note`
- `confidence`
- `notes`

Use the approved KU dimensions:

- `Operation Purpose`
- `Operation Rules`
- `Infrastructure`
- `Real-Time / Emergency Operations`
- `Coordination / Governance`
- `Operational Data`
- `Research / Modeling / Analysis`
- `Evidence Gap / Uncertainty`

For each dimension, collect the following information only when supported by KUs:

- **Operation Purpose:** authorized purposes, management objectives, operating priorities, and purpose conflicts preserved in source-level KUs.
- **Operation Rules:** rules, thresholds, operating tiers, release volumes, triggers, criteria, scenario conditions, decision stages, and whether the rule is current, projected, proposed, adjusted, or historical.
- **Infrastructure:** facilities, release pathways, elevation thresholds, minimum power pool, outlet works, penstocks, hydropower limitations, low-water constraints, and infrastructure modifications.
- **Real-Time / Emergency Operations:** actions under drought, flood, emergency, maintenance, experimental, or special-event conditions; include what condition triggered the action and what operational response was described.
- **Coordination / Governance:** agencies, legal authorities, agreements, NEPA processes, compact context, consultation, stakeholder/tribal coordination, and decision responsibilities.
- **Operational Data:** forecasts, 24-Month Study values, inflow/storage/elevation/release records, monitoring products, data portals, scenario inputs, update timing, and operational use.
- **Research / Modeling / Analysis:** models, studies, experiments, technical analyses, methods, main findings, operational implications, and limitations.
- **Evidence Gap / Uncertainty:** source-identified uncertainty or missing source evidence about reservoir operation. Do not include workflow limitations such as failure to parse a table.

### Output 2: Cross-KU Synthesis Cards

Use one JSON object per synthesis card. Every card must have:

- `synthesis_id`
- `knowledge_layer = synthesis_analysis`
- `reservoir_id`
- `reservoir_name`
- `analysis_type`
- `title`
- `summary`
- `based_on_ku_ids`
- `interpretation`
- `confidence`
- `next_step`
- optional `notes`
- optional `evidence_depth`
- optional `source_locator_summary`
- optional `source_verification_note`
- optional `research_relevance`

Use `evidence_depth` values as follows:

- `ku_only`: candidate synthesis based only on KU records.
- `source_checked`: relevant source sections/chunks were reread.
- `source_checked_with_direct_quote`: source sections/chunks were reread and the synthesis card includes or references direct source wording in the verification note.

Use `research_relevance` values as follows:

- `supports_story`: directly helps define the research story or central argument.
- `needs_more_evidence`: promising but requires more source coverage, data, or domain validation.
- `background_only`: useful context but not central to the research story.

## Analysis Types

### `recurring_finding`

A finding, rule, condition, or operational theme appears repeatedly across sources or KUs.

Use when answering:

- What do multiple KUs consistently show?
- What stable operating pattern should the KB preserve?
- What repeated condition matters across the source set?
- Which consolidated knowledge points keep appearing across multiple documents or source types?

Do not use for a single-source observation unless the source contains multiple independent KUs that establish a repeated internal pattern.

### `complementary_evidence`

Different sources, datasets, methods, or models support different parts of the same operational question.

Use when answering:

- Which source provides current status?
- Which source provides time-series data?
- Which source provides governance context?
- Which source provides modeling or impact evidence?
- How do methods or data sources complement each other?
- Do different values reflect different scenarios, release-status categories, dates, rule layers, or decision stages rather than a conflict?

Examples:

- A forecast source provides hydrologic status, a model source explains projected operations, and a governance source explains the decision authority.
- One source gives a projected release value while another gives an adjusted or implemented release value. If the context differs, this is complementary evidence plus metadata need, not a source discrepancy.

### `source_discrepancy`

Different KUs or sources make inconsistent claims about the same object under the same definition, date/status, scenario, and decision context.

Use when answering:

- Do two sources describe the same release value, rule, threshold, status, event, or authority differently under the same conditions?
- Does one source contradict another source rather than merely describe a different scenario or decision stage?
- Is a conflict still present after checking date, version, scenario, rule layer, and source authority?

This type is about evidence consistency. Do not use it for operational objective tradeoffs. Do not use it simply because numbers differ. First check whether the difference is explained by:

- forecast date
- scenario
- projected versus implemented status
- proposed versus final rule
- current versus historical policy
- different rule layer or legal authority
- emergency adjustment versus baseline operation

If the difference is explained by these factors, classify it as `complementary_evidence` or a metadata/status issue, not `source_discrepancy`.

### `operational_tradeoff`

Operational purposes, constraints, or impacts pull decisions in different directions.

Use when answering:

- Which operating objectives are in tension?
- What operational flexibility creates downstream consequences?
- What water supply, hydropower, ecological, flood, drought, or governance purposes must be balanced?
- Which infrastructure, rule, data, or governance constraints limit operational choices?

This type is about reservoir decision tradeoffs. Do not use it for document version differences.

### `evidence_gap`

The collected source corpus lacks enough evidence, technical detail, data coverage, or source depth to answer an operational question.

Use when answering:

- What information is missing?
- Which documents, datasets, or technical details are needed?
- Which part of the KB is under-supported?
- Which operational question cannot be answered confidently from the currently collected official, research, and context sources?

This type is about missing or thin source evidence. It is not a workflow limitation.

Do not classify the following as `evidence_gap`:

- Docling failed to parse a PDF.
- The workflow did not extract a table, figure, or time series.
- A KU record is too generic.
- The current prompt missed a sentence.

Those belong in workflow limitations, validation notes, or method improvement notes.

Classify as `evidence_gap` only when the source set itself is insufficient, for example:

- low-water outlet capacity is mentioned but not quantified in the available official/technical sources;
- a media source raises a downstream impact but the collected official/research sources do not support or quantify it;
- research sources identify uncertainty but do not explain how uncertainty is converted into operating thresholds;
- a governance document names a future decision but does not specify the operational rule or trigger.

### `outstanding_operational_issue`

An unresolved operational, governance, planning, or decision issue remains open in the evidence.

Use when answering:

- What operating problem remains unresolved?
- What future decision has not been settled?
- What issue should remain visible for planning or review?
- What operational-design problem remains after consolidating rules, infrastructure, data, research, and governance evidence?

This type is about the operation or decision problem itself, not merely missing evidence.

## Procedure

1. Load the KU file and skim all KU titles/findings.
2. Produce **KU consolidation** first:
   - group KUs by approved KU dimension;
   - merge repeated or overlapping findings;
   - preserve specific values, rules, thresholds, datasets, model names, agencies, and source status where available;
   - cite supporting KU IDs;
   - omit dimensions that have no meaningful evidence.
3. Group consolidated points and KUs by:
   - engineering dimension
   - source ID
   - affected operation purpose
   - condition or trigger
   - repeated named document, model, dataset, threshold, or rule
4. Draft candidate cross-KU synthesis observations.
5. For each important candidate, use the cited KUs as locators and reread the relevant original source passages when available.
6. Decide whether each candidate is:
   - repeated pattern
   - complementary evidence
   - true source discrepancy
   - operational tradeoff
   - source-corpus evidence gap
   - outstanding operational issue
7. Drop candidates that are just a restatement of one KU.
8. Drop unsupported categories rather than inventing a card.
9. Cite all supporting KU IDs.
10. Write a concise summary and a separate interpretation.
11. Add a next-step action when useful.
12. Validate the JSONL.

## Deep Synthesis Pattern

Use this pattern when the synthesis claim is important, technical, or potentially contested:

```text
read KUs -> identify candidate relationship -> retrieve source chunks -> reread original evidence -> write synthesis card
```

This differs from ordinary RAG in one important way: the KU layer gives the retrieval process a domain-aware starting point. Instead of asking the model to search all chunks blindly, the workflow first uses structured operational KUs to identify relevant rules, constraints, models, gaps, or governance issues, then returns to the original text for verification and richer interpretation.

Deep synthesis should use source rereading especially for:

- apparent source discrepancies
- operational tradeoffs
- outstanding operational issues
- high-confidence report claims
- claims involving values, thresholds, dates, release volumes, operating tiers, or legal/policy authority

For each deep synthesis card, record:

- which KU IDs triggered the synthesis candidate
- which source locations were reread
- whether the source context confirmed, narrowed, or complicated the claim
- whether the card supports the research story or mainly identifies a need for more evidence

## Anti-Patterns

Do not:

- create `next_step_priority` as an analysis type
- mix source discrepancies with operational tradeoffs
- label scenario/date/status/rule-layer differences as source discrepancies when they are explainable by context
- call missing evidence an outstanding operational issue unless the operation or decision itself is unresolved
- call workflow or extraction limitations source evidence gaps
- make claims that cannot be traced to cited KUs
- make deep synthesis claims from KU wording alone when the original source passage is available
- mark a card as `source_checked` without identifying the source locator context
- cite source IDs without citing KU IDs
- write synthesis that belongs in the document-level KU layer
- produce broad generic conclusions that do not help reservoir operations research
- fill every analysis type by default when the source/KU evidence does not support it

## Quality Checklist

Before accepting a synthesis card, check:

- Does it cite relevant KU IDs?
- Is the analysis type precise?
- Is it more than a single-KU summary?
- Does the summary state the pattern or issue clearly?
- Does the interpretation explain why it matters?
- Does the next step follow from the analysis rather than introduce a new unsupported claim?
- If this is `source_discrepancy`, is it a true same-object/same-status conflict after checking scenario, date, version, and rule layer?
- If this is `evidence_gap`, is the gap in the collected source evidence rather than in the workflow implementation?
- Did the run produce KU consolidation before cross-KU analysis?
