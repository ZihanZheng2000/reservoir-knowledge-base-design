# Report Generation Protocol

## Purpose

Report generation converts validated structured knowledge into a human-readable research artifact. It is a controlled transformation, not unconstrained writing.

## Evidence Inputs

Use these inputs:

- source inventory;
- validated source-level KUs;
- validated synthesis records;
- retrieval results when relevant;
- validation summaries and known limitations.

## Report Types

Common report types:

- **Technical report:** detailed method, data, findings, validation, limitations.
- **Short briefing:** concise explanation for supervisors or stakeholders.
- **Case-study report:** reservoir-specific dataset/workflow demonstration.
- **Validation report:** sampled metrics, failure modes, revisions, transfer results.

## Claim Rules

Every substantive claim should be assigned one of these support levels:

- `direct_ku_support`: claim is directly supported by one or more KUs.
- `synthesis_support`: claim is supported by a validated synthesis record.
- `source_checked`: claim has been checked against source text.
- `needs_more_evidence`: claim should be treated as tentative.

## Claim-Evidence Map

Create a claim-evidence map with:

- claim ID;
- report section;
- claim text;
- cited KU IDs;
- cited synthesis IDs;
- cited source IDs;
- support level;
- reviewer notes.

## Validation

Sample report claims and check:

- traceability rate;
- faithfulness rate;
- unsupported or overgeneralized claims;
- clarity and usefulness for the target reader.

