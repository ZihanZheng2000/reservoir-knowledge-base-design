# Knowledge Consolidation Protocol

## Purpose

Knowledge consolidation turns validated, document-level Evidence Units (EUs)
into Knowledge Cards (KCs). It improves organization and retrieval without
changing the evidence status of the underlying source material.

```text
EU: one source-grounded finding from one document
KC: conservative organization of EUs answering one operational question
Synthesis Card: cross-document analysis built later from EUs and KCs
```

## Consolidation Key

Engineering dimension is only the first grouping key. The actual consolidation
key is the operational question answered by the EUs. Keep EUs separate if they
describe different rules, thresholds, facilities, locations, dates, scenarios,
statuses, or decision contexts.

## Allowed Consolidation Types

- `repeated_fact`: more than one EU states the same operational fact.
- `complementary_facts`: EUs supply different, compatible parts of one
  operational question.
- `contested_or_unresolved`: EUs appear inconsistent or incomplete after
  preserving time, scenario, status, version, and decision context.

## Procedure

1. Load validated EUs and group them by engineering dimension.
2. Identify the precise operational question each EU addresses.
3. Group only EUs that answer the same question.
4. Write a Knowledge Card that preserves all material conditions and cites all
   included EU IDs.
5. Keep a proposed rule and a final rule separate unless the card explicitly
   records their status relationship.
6. Do not make a higher-level claim about recurring patterns, source
   discrepancy, tradeoff, evidence gap, or unresolved operational issue. Those
   belong to Synthesis.
7. Validate the records.

## Quality Checklist

- Is the operational question explicit and narrow enough?
- Does each cited EU actually support the card?
- Are dates, scenarios, rule status, and decision conditions retained?
- Is the card an organization of evidence rather than an interpretation?
- Does its `consolidation_type` reflect the evidence relationship?
