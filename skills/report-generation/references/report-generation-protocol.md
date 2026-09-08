# Report Generation Protocol

## Purpose

Report generation converts validated structured knowledge into a human-readable research artifact. It is a controlled transformation, not unconstrained writing.

Write report outputs under `06_report_generation/` within the run folder.

## Evidence Inputs

Use these inputs:

- source inventory;
- validated source-level Evidence Units;
- validated Knowledge Cards;
- validated Synthesis Cards;
- validation summaries and known limitations.

## Report Types

Common report types:

- **Technical report:** detailed method, data, findings, validation, limitations.
- **Short briefing:** concise explanation for supervisors or stakeholders.
- **Case-study report:** reservoir-specific dataset/workflow demonstration.
- **Validation report:** sampled metrics, failure modes, revisions, transfer results.

## Claim Rules

Every substantive claim should be assigned one of these support levels:

- `direct_eu_support`: claim is directly supported by one or more EUs.
- `knowledge_card_support`: claim is supported by a validated Knowledge Card.
- `synthesis_card_support`: claim is supported by a validated Synthesis Card.
- `source_checked`: claim has been checked against source text.
- `needs_more_evidence`: claim should be treated as tentative.

## Claim-Evidence Map

Create a claim-evidence map with:

- claim ID;
- report section;
- claim text;
- cited EU IDs;
- cited KC IDs;
- cited Synthesis Card IDs;
- cited source IDs;
- support level;
- reviewer notes.

## Validation

Follow `docs/validation-framework.md`.

- Automated validation checks schema conformance of the claim-evidence map and
  traceability integrity from each material claim back to validated records and
  source evidence.
- Optional human review uses faithfulness, readability, and value. Review
  faithfulness on a documented claim sample; record readability and value at
  section/report level.
