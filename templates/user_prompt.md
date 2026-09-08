# New Reservoir Knowledge-Base: Codex Prompt Template

Use these short prompts in sequence. The project instructions, skills, schemas, and validators define how Codex performs the work; do not repeat those rules in each conversation.

## 1. Start a new run

```text
Start a new reservoir knowledge-base run for [reservoir name] ([reservoir ID]).

Scope: [operational topic or research question].
Priority sources: [agencies, document types, or known links].
Intended use: [e.g., case study / technical brief / prototype].

First, review the project instructions and confirm the proposed run ID, scope, source plan, and any essential missing inputs. Do not begin source acquisition yet.
```

## 2. Source acquisition

```text
Proceed with source acquisition for this run. Prioritize sources that can answer the agreed operational scope, preserve the acquired material, validate the source inventory, and report the source coverage and any important gaps.
```

## 3. Evidence extraction

```text
Proceed with evidence extraction from the validated, EU-ready sources. Validate the resulting Evidence Units and report source coverage, EU count, and material warnings.
```

## 4. Knowledge consolidation

```text
Proceed with knowledge consolidation from the validated Evidence Units. Validate the Knowledge Cards and report the cards created, their EU coverage, and any unresolved distinctions that should remain separate.
```

## 5. Synthesis

```text
Proceed with synthesis from the validated Evidence Units and Knowledge Cards. Create and validate only well-supported Synthesis Cards; return to the original sources whenever the project rules require source verification. Report the main findings and remaining uncertainty.
```

## 6. Indexing

```text
Proceed with indexing the validated knowledge-base records. Validate the index output and report record counts and index status.
```

## 7. Report generation

```text
Proceed with report generation for [audience and purpose]. Validate the claim-evidence mapping and report the deliverables, main supported conclusions, and limitations.
```

## Optional control sentence

Add this to the end of any stage prompt if you want to approve the next stage yourself:

```text
Stop after this stage, report the result, and wait for my next instruction.
```

## Optional human review prompt

```text
Prepare a documented sampled human review for [stage]. Follow docs/validation-framework.md, use the matching JSON template in `templates/human_review/`, prefill it with the actual review units and Codex decisions, and write the completed workpaper to that stage's `human_review.json`.
```

## Final handoff

```text
Provide a concise handoff for this run: artifact locations, validation status, EU/KC/Synthesis Card/index record counts, key supported conclusions, and unresolved source or evidence issues.
```
