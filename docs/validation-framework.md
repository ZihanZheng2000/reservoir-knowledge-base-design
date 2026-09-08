# Validation Framework

## Purpose

This framework separates routine checks that make a run technically safe from human judgments about the usefulness of its outputs. It applies to every new run and all six workflow stages.

Each stage has exactly five quality indicators:

- two **automated validation** indicators;
- three **human review** indicators.

Automated validation is required before a stage output is used downstream. Human review is sampled evaluation and method refinement; it is not a routine stop point unless a run or study explicitly requires it.

## Two validation layers

### Automated validation

Automated validation asks only two questions:

1. **Schema conformance** — do the stage records and required artifacts conform to their JSON Schema and required file contract?
2. **Traceability integrity** — can a record's references resolve back through the preceding knowledge layer to its source evidence?

For Source acquisition, the second question is replaced with **acquisition success**, because no source-evidence chain exists before sources are downloaded and preserved.

Automated results are `pass`, `warning`, or `fail`.

- `fail`: do not use the affected output downstream until it is corrected or explicitly excluded.
- `warning`: may proceed, but record the issue and its impact in the run summary.
- `pass`: the applicable automated checks completed without blocking issues.

### Human review

Human review asks whether the validated output is substantively appropriate. It is performed on a documented sample, except for metrics explicitly marked as run-level or query-level below.

For each review, record the run ID, stage, reviewer, date, sample or benchmark definition, item-level decisions, metric-level findings, and required follow-up. Store it in the stage folder:

```text
runs/<run_id>/<numbered_stage>/human_review.json
```

Every stage contains this file; use `not_requested` or `not_reviewed` when
there is no completed human review.

When every required decision and score in a populated workpaper is filled, the
validation summary treats it as completed. Changing `review_status` to
`completed` is welcome but is not an additional review task.

Use the matching file in `templates/human_review/` to create the workpaper.
Before handoff, prefill its item-level table from the actual stage artifacts
and retain Codex's decision in a separate column from the human decision. For
Stage 1, this is the source-selection decision; for Stages 2–4 it is the
record disposition; for Stage 5 it is the returned-record/answer decision;
for Stage 6 it is the report-claim inclusion decision.

### Scoring and automatic aggregation

Use `0`, `1`, or `2` only with the metric-specific rubric below. A score has
no universal meaning across stages or metrics: for example, `1` for EU
relevance is not the same judgment as `1` for synthesis value. Recall and
precision are ratios from 0 to 1, not 0/1/2 scores.

For Source acquisition, enter `Y` or `N` in `human_use`; when the answer is
`Y`, enter the human source tier (`A`, `B`, or `C`). Preserve Codex's own tier
in `codex_tier`. Precision is calculated from Codex-selected sources and
human-use decisions. Recall is calculated from every human-reviewed source in
the stage's candidate inventory: it is the proportion of human-in-scope
sources that Codex selected. Precision and recall are **ratios from 0 to 1**;
they are never converted to 0/1/2 scores. They evaluate selection within the
documented candidate inventory, not discovery coverage beyond that inventory.
Score source adequacy directly in `run_level_metrics` using its Stage 1 rubric.

For scored criteria, the run summary may show the individual ratings and their
arithmetic mean as a descriptive summary. It must not translate that mean into
a universal quality band. Run the standard validation summary command after
editing the review JSON files to refresh these calculations.

## Stage matrix

| Stage | Automated validation: 2 indicators | Human review: 3 indicators |
|---|---|---|
| 1. Source acquisition | **Schema conformance**; **acquisition success** | **Recall**; **precision**; **source adequacy** |
| 2. Evidence extraction | **Schema conformance**; **traceability integrity** | **faithfulness**; **relevance**; **value** |
| 3. Knowledge consolidation | **Schema conformance**; **traceability integrity** | **faithfulness**; **consolidation appropriateness**; **value** |
| 4. Synthesis | **Schema conformance**; **traceability integrity** | **faithfulness**; **reasoning soundness**; **value** |
| 5. Indexing and retrieval evaluation | **Schema conformance**; **traceability integrity** | **recall**; **precision**; **source adequacy** |
| 6. Report generation | **Schema conformance**; **traceability integrity** | **faithfulness**; **readability**; **value** |

Indexing remains a construction stage: it encodes validated records only. The Stage 5 human review is a retrieval evaluation performed *after* indexing, using a documented question set; it does not make retrieval a separate knowledge-base construction stage.

## Human review by layer: focus and rubric

Use these definitions when entering human scores. They apply only to the
named metric at the named stage.

### 1. Source acquisition

**Review object:** the reviewed candidate source inventory as a corpus. Recall
and precision assess Codex's source-selection decisions; source adequacy
assesses whether the corpus can support the defined operational scope.

| Metric | 0 | 1 | 2 |
|---|---|---|---|
| Source adequacy | The acquired corpus cannot support the defined operational scope. | The corpus is usable for a limited pass, but material authoritative sources, conditions, or source families are missing. | The corpus is sufficiently authoritative, usable, and scoped to support the defined questions. |

Recall and precision are calculated ratios, not ratings.

### 2. Evidence extraction

**Review object:** each sampled Evidence Unit (EU), judged against its quote,
locator, and approved engineering-dimension topic.

| Metric | 0 | 1 | 2 |
|---|---|---|---|
| Faithfulness | The EU is unsupported, materially misstates the source, or loses a decisive qualifier. | The EU is broadly grounded but needs a material wording, condition, or locator correction. | The EU accurately represents the quoted, located source evidence and preserves material conditions. |
| Relevance | The EU does not address the agreed scope or its approved engineering-dimension topic. | The EU is contextual or only indirectly useful to the agreed scope. | The EU directly contributes operational information within the agreed scope and topic. |
| Value | The EU is duplicate, trivial, or unusable for downstream work. | The EU may be useful but offers limited or weakly differentiated information. | The EU adds distinct, usable operational evidence for consolidation, synthesis, or retrieval. |

### 3. Knowledge consolidation

**Review object:** each sampled Knowledge Card (KC), judged against all of its
supporting EUs and the operational question it is intended to organize.

| Metric | 0 | 1 | 2 |
|---|---|---|---|
| Faithfulness | The KC adds unsupported content or materially distorts supporting EUs. | The KC is broadly supported but loses an important condition, disagreement, or uncertainty. | The KC remains faithful to all supporting EUs and preserves material conditions and limits. |
| Consolidation appropriateness | The card combines EUs that should remain separate, or splits evidence without an operational reason. | The grouping is plausible but needs a clearer boundary, split, or context note. | The grouped EUs answer the same operational question and material distinctions remain visible. |
| Value | The KC obscures the evidence or adds no usable organization. | The KC offers modest organization but little improvement over reading the EUs separately. | The KC makes related evidence more usable without hiding disagreement or creating analysis. |

### 4. Synthesis

**Review object:** each sampled Synthesis Card, judged against its analysis
chain, cited EU/KC evidence, and any required rereading of the source.

| Metric | 0 | 1 | 2 |
|---|---|---|---|
| Faithfulness | The Synthesis Card contains an unsupported relationship, causal claim, or material overstatement. | The synthesis is partly supported but needs a qualifier, source rereading, or narrower scope. | Every substantive analytical claim is supported by the cited EU/KC evidence and required source rereading. |
| Reasoning soundness | The analysis chain makes an invalid leap or confuses observed fact, forecast, rule, and inference. | The chain is plausible but an evidential bridge, alternative explanation, or condition remains unclear. | The chain explicitly and validly connects the cited evidence to the stated cross-document relationship. |
| Value | The card only repeats its inputs or yields no useful operational insight. | The card offers a limited insight but has weak novelty or limited practical use. | The card provides a meaningful, supported insight beyond restating EU/KC records. |

### 5. Indexing and retrieval evaluation

**Review object:** each benchmark-query result at the chosen retrieval depth.
This evaluates whether encoded records can be returned for a directly
documented information need; it does not evaluate synthesis reasoning.

| Metric | 0 | 1 | 2 |
|---|---|---|---|
| Source adequacy | The returned records cannot support a responsible answer because essential evidence, conditions, or locators are absent. | The records support a partial answer, but material context, conditions, or evidence links are missing. | The returned records provide enough source-grounded evidence, conditions, and locators to answer the benchmark question responsibly. |

Recall@k and precision@k are calculated ratios, not ratings.

Define each benchmark question as one ordinary information need with a directly documented answer. Record the required gold index-record IDs, expected answer points, and retrieval depth before querying. Do not use a question that requires synthesis or novel reasoning to test indexing.

For each completed query, calculate recall and precision automatically from
the returned record IDs and predefined gold/acceptable record IDs. The human
reviewer scores only source adequacy (0/1/2) and may add notes or a required
action; they do not manually score recall or precision.

### 6. Report generation

**Review object:** the report as one whole output. The claim-evidence map
remains available for traceability audit, but the human reviewer does not give
separate scores to each claim.

| Metric | 0 | 1 | 2 |
|---|---|---|---|
| Faithfulness | The report contains material unsupported, overstated, or evidence-map-inconsistent content. | The report is generally supported but needs material correction, qualification, or claim-evidence repair. | The report as a whole is faithful to the claim-evidence map and preserves material limits. |
| Readability | The intended audience cannot reliably follow the report's structure, terms, evidence status, or limitations. | The report is understandable but needs material restructuring, clarification, or editing. | The intended audience can readily understand the structure, terminology, evidence status, and limitations. |
| Value | The report does not answer the agreed purpose or is not useful for its stated use. | The report is partly useful but omits material answers, context, or practical utility. | The report answers the agreed purpose and is useful for its stated case-study, technical, or prototype use. |

## Automated validation by stage

### 1. Source acquisition

- **Schema conformance:** the source manifest, final candidate inventory, and acquired-source inventory meet their schema; required raw/text paths, status fields, and metadata are present.
- **Acquisition success:** each selected source has a recorded acquisition outcome. Core sources must be preserved or have a documented recovery attempt and limitation; failed downloads may not disappear silently.

### 2. Evidence extraction

- **Schema conformance:** extraction packets and EUs meet their schemas, including required IDs, quotes, and locators.
- **Traceability integrity:** every EU resolves to an existing source inventory record and preserved source/text path.

### 3. Knowledge consolidation

- **Schema conformance:** KCs meet their schema and permitted consolidation types.
- **Traceability integrity:** every `based_on_eu_id` resolves to a validated EU, which in turn resolves to a source.

### 4. Synthesis

- **Schema conformance:** Synthesis Cards meet their schema and primary-pattern-specific requirements.
- **Traceability integrity:** every cited EU and KC exists and its evidence chain resolves to source evidence; required source-verification notes are present where applicable.

### 5. Indexing

- **Schema conformance:** index records and the index manifest meet their schemas.
- **Traceability integrity:** every index record resolves to its validated EU, KC, or Synthesis Card and preserves the applicable evidence-chain IDs and locators.

### 6. Report generation

- **Schema conformance:** the claim-evidence map and required report artifacts meet their file and schema contracts.
- **Traceability integrity:** every material report claim resolves through its map to validated records and ultimately to source evidence.

## Review unit and aggregation

The distinction between item-level and overall judgment must be retained in every review record.

For Stages 2--4, `human_disposition` is a non-numeric decision independent of
the three scores: use `accept` when the record may remain unchanged, `revise`
when it needs correction before downstream use, and `reject` when it should
not remain in the knowledge layer.

- **Item-level review:** an EU, KC, or Synthesis Card is judged individually. Faithfulness, relevance, consolidation appropriateness, reasoning soundness, and item-level value belong here.
- **Aggregate review:** judgment concerns the source corpus, report, or set of retrieval queries. Recall, source adequacy, readability, and report-level value belong here; item-level value may also be summarized.
- **Query-level review:** judgment concerns one benchmark question and its returned records. Stage 5 recall, precision, and source adequacy belong here.

Do not report a single run-level score without preserving the underlying sampled item or query decisions. Use the metric-specific rubric above and support borderline judgments with short notes.

## Relationship to skills, templates, and run artifacts

- `AGENTS.md` carries the project-level requirement to validate every stage and points to this framework.
- Each stage skill should link to this document, state the exact validator command, and place `automated_validation.json` and `human_review.json` in its own stage folder.
- `templates/` contains short conversation prompts, not the review rubric.
- `runs/<run_id>/validation/` contains only the JSON and Markdown run-level summaries; individual validation records stay with their stage artifacts.
