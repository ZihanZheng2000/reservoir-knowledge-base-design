# Candidate Screening And Quality Review Protocol

## Purpose

Control source relevance, importance, and quality before the source set is passed to EU extraction.

This protocol covers two related checks:

1. **Candidate Screening** before formal download: decide whether a candidate is worth attempting to download.
2. **Quality Review** after download and text extraction: confirm source family, importance, content quality, and EU-readiness.

The main screening question is:

```text
Is this candidate worth attempting to download or preserve?
```

The main quality-review question is:

```text
Is this preserved source useful enough, clear enough, and important enough for EU extraction or later background use?
```

Candidate screening uses metadata, title, URL, abstract, DOI, publisher/source type, search context, and light inspection. Quality review uses the preserved raw file, extracted text, parsed markdown when available, and inventory record.

## Screening Decisions

Use these decisions:

- `include`: likely useful and accessible enough to preserve.
- `maybe`: relevant but overlapping, weak, or needs prioritization.
- `manual_review`: promising but requires institutional access, better URL resolution, or human judgment.
- `exclude`: not operationally relevant, duplicate, inaccessible without metadata value, or too weak.

## Inclusion Criteria

Include or prioritize a candidate when it is likely to provide source-grounded evidence for at least one reservoir-operation question and is accessible or important enough to attempt download.

Evaluate candidates using these criteria:

1. **Reservoir relevance**
   - The candidate is about the target reservoir, dam, operator, project, river basin, upstream/downstream system, or a linked operating program.
   - Do not include a source only because it briefly mentions the reservoir.

2. **Operational relevance**
   - The candidate can help explain reservoir operation, release decisions, storage management, flood/drought response, infrastructure limits, hydropower, environmental flow/temperature/sediment objectives, operational data, models, governance, uncertainty, or operational impacts.
   - Do not require the exact phrase `reservoir operation`.

3. **Evidence value**
   - The candidate adds information not already covered by stronger sources, or it provides a more authoritative, more detailed, more recent, or more technically useful version of an existing source.
   - Weak duplicates should be excluded or marked low priority.

4. **Source role**
   - Official, research/technical, and media/context sources can all be included, but they serve different roles.
   - Tier C/media/context sources may identify events, stakeholder concerns, or public issues, but technical claims should later be supported by Tier A/B sources when possible.

5. **Accessibility and preservation**
   - The candidate has a usable URL, DOI, PDF, HTML page, data portal, repository copy, official mirror, or other path that can reasonably be preserved.
   - If full text is not accessible but the candidate appears important, mark it `manual_review` or use it as a discovery lead.

6. **Expected EU usefulness**
   - The candidate is likely to produce useful EUs or source leads.
   - Navigation pages, generic landing pages, empty metadata records, or very weak background sources should not be selected unless they point to better sources.

7. **Importance estimate**
   - `core`: central source likely to produce many or important EUs, such as an operation manual, operating plan, major official report, technical appendix, data/model documentation, or high-relevance research report.
   - `supporting`: useful source that supports a narrower operational point.
   - `background`: context source that helps explain setting, events, stakeholders, or public issues but should not drive technical claims.
   - `low_value`: weak, duplicate, generic, or unlikely to support useful EUs.

## Provisional Source-Family Hint

Candidate screening may assign a provisional source-family hint when obvious:

- `A`: likely official authority, operating rule, official data/model product, official engineering/infrastructure, or formal legal/policy document.
- `B`: likely research/technical source that explains operation mechanisms, constraints, assumptions, impacts, or uncertainty.
- `C`: likely context source that raises an event, public issue, stakeholder concern, or contested operational problem.

This hint is not final. Confirm final A/B/C after download and text extraction.

## Source Importance And Quality

During screening, importance and quality are estimates. During quality review, they become final inventory fields or explicit inventory notes.

Use these fields:

- `source_importance`: `core`, `supporting`, `background`, or `low_value`.
- `content_quality`: `usable`, `short_review`, `metadata_only`, `paywall_or_redirect`, `parser_issue`, or `failed`.
- `eu_readiness`: `ready`, `needs_recovery`, `background_only`, or `not_ready`.

Use `core` for sources likely to produce many or central EUs, such as operating rules, official operation plans, major technical appendices, key datasets, and high-relevance research reports.

Use `supporting` for useful but narrower evidence.

Use `background` for sources that provide context but should not drive technical claims.

Use `low_value` for weak duplicates, navigation pages, generic mentions, or sources that are technically related but unlikely to support useful EUs.

## Quality Review Checks

After source download and text extraction, confirm:

- Does the extracted text contain substantive source content rather than only navigation, metadata, or access-denied text?
- Is the source family A/B/C correct after seeing the preserved source?
- Is the source `core`, `supporting`, `background`, or `low_value` for this reservoir workflow?
- Is the source ready for EU extraction, or should it be marked `needs_recovery`, `background_only`, or `not_ready`?
- If text is short, is it a legitimate short source such as an official notice, or a failed extraction/paywall/redirect?
- If a source is Tier C, does it only provide context, or does it raise an issue that needs Tier A/B support?
- If a source is weak but points to a better document, should the better document be searched instead?

## Evidence Families

Assign one or more:

- `operation_rules`
- `infrastructure_constraints`
- `data_models_forecasts`
- `real_time_emergency`
- `hydropower`
- `temperature_ecology`
- `adaptive_management`
- `governance_policy`
- `uncertainty_scenarios`
- `storage_capacity_sediment`
- `media_context`

## Screening Questions

- Does the source help answer an operational question?
- Does it add evidence not already covered by stronger sources?
- Is the full source preservable?
- Is there a usable URL, DOI, landing page, repository copy, or official mirror to try?
- If only metadata is available, is it worth manual access?
- Could it support EU extraction, or is it only a discovery lead?
- Is it likely core, supporting, background, or a low-value duplicate?

## Anti-Patterns

Do not select sources only because they mention the reservoir. Do not spend download effort on many weak duplicates when a stronger official or technical source is available. Do not reject a candidate only because its title does not say `reservoir operation` if it may explain an operational mechanism, constraint, dataset, model, governance issue, or impact. Do not use A/B/C as a quality ranking; it is a source-family label.
