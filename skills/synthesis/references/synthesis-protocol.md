# Reservoir Synthesis Protocol

## Purpose And Boundary

Synthesis analyzes relationships across validated Evidence Units (EUs) and
Knowledge Cards (KCs). It is not another extraction or consolidation pass.

```text
EU = one source-grounded document finding
KC = conservative organization of EUs around one operational question
Synthesis Card = source-grounded analysis of an operational relationship
```

All synthesis claims remain traceable to EU IDs, KC IDs, and original source
locations. Use EU and KC records to find relevant evidence, then reread original
source passages whenever their context is material to the claim.

## Primary Patterns

### `decision_process`

Use when evidence supports a decision architecture:

```text
monitoring or forecast signal
-> condition or scenario classification
-> applicable rule, authority, or procedure
-> operational choice
-> implementation
```

Do not use for an agency list, a rule in isolation, or the mere existence of a
forecast. The source-supported relationship between inputs, authority, and
action must be explicit.

### `constraint_structure`

Use when multiple jointly relevant constraints shape the same operational
question. Explain which objective or decision variable is constrained, how the
constraints interact, and what flexibility remains. Do not invent a numerical
feasible range unless evidence states or supports its calculation.

### `operational_tradeoff`

Use when both sides of a tension are supported and interact through the same
operation or constrained resource. State the operating condition, action,
benefit or risk to each objective, affected parties when supported, and any
formal prioritization rule. Do not infer a tradeoff merely because a reservoir
has multiple objectives.

### `operating_regime_change`

Use when evidence establishes a change from one operating regime to another.
Identify the previous regime, trigger or context, changed rule/objective/
capability/authority, new regime, and decision implications. Check dates,
versions, and status against original sources. A different publication date,
proposed rule, or temporary deviation is not by itself a regime change.

### `historical_operation_failure`

Use only for a documented historical episode of complete or partial failure,
temporary loss of function, capacity degradation, target nonachievement,
emergency deviation, institutional or coordination failure, or uncertain failure
status. Preserve the distinction between source-documented causes, contributing
conditions, and synthesis uncertainty. Do not treat a drought, disagreement,
risk, or merely suboptimal result as failure without evidence of an unmet
requirement, lost function, or stated target.

For this pattern, record when supported:

- period and failed function or target;
- expected condition and observed outcome;
- failure class;
- direct causes, contributing causes, and underlying vulnerabilities;
- documented consequences, corrective actions, and current status.

### `operational_consequence`

Use when evidence supports an action, rule, decision, or regime and an outcome
linked to it. Set `consequence_basis` to exactly one of:

- `observed_consequence`;
- `modeled_consequence`;
- `projected_consequence`.

Do not merge these evidence bases. A modeled or planned consequence is not a
historical observed outcome. Do not turn correlation or sequence into causality.

## Original-Source Rereading

Source rereading is required for strong claims involving:

- numerical values, thresholds, release volumes, dates, or rule versions;
- legal authority, institutional approval, or implementation status;
- causal language, historical failure, or operational consequence;
- a claimed regime change, tradeoff, or constraint interaction;
- source wording that may be conditional, qualified, or contested.

Use `evidence_depth = eu_only` only for a clearly labelled candidate based on
validated EU records. Use `source_checked` when relevant passages were reread,
and `source_checked_with_direct_quote` when the verification note records direct
source wording. A source-checked card must state what the reread context did to
the candidate claim.

## Quality Checklist

- Is there exactly one primary pattern?
- Is the card more than an EU or KC restatement?
- Are all material EU and KC IDs included?
- Does each analysis-chain step have support?
- Are conditions, dates, scenarios, status, and exceptions preserved?
- Has original-source context been reread where needed?
- Does the card avoid unsupported causality, legal interpretation, or failure
  classification?
