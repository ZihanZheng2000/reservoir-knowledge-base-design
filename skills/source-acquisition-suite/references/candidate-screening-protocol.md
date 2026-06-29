# Candidate Screening Protocol

## Purpose

Convert a broad candidate pool into a human-reviewable list of sources that should be included, excluded, or manually checked.

## Screening Decisions

Use these decisions:

- `include`: likely useful and accessible enough to preserve.
- `maybe`: relevant but overlapping, weak, or needs prioritization.
- `manual_review`: promising but requires institutional access, better URL resolution, or human judgment.
- `exclude`: not operationally relevant, duplicate, inaccessible without metadata value, or too weak.

## Tier Assignment

- Tier A: official authority, operating rules, official data/model products, official engineering/infrastructure, formal legal/policy documents.
- Tier B: research/technical source that explains operation mechanisms, constraints, assumptions, impacts, or uncertainty.
- Tier C: context source that raises an event, public issue, stakeholder concern, or contested operational problem.

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
- Is it official, technical, or context?
- Is the full source preservable?
- If only metadata is available, is it worth manual access?
- Could it support KU extraction, or is it only a discovery lead?

## Anti-Patterns

Do not include sources only because they mention the reservoir. Do not let Tier C sources finalize technical claims. Do not include many weak duplicates when a stronger official or technical source is available.
