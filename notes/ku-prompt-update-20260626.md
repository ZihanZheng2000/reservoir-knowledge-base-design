# KU Prompt Update - 2026-06-26

## Reason

The first Lake Powell KU extraction showed that the extraction content was generally useful, but the category design and prompt needed clearer instructions.

Key issues:

- `Data / Models` was too broad and should be split into operational data sources and research/modeling/analysis.
- `Infrastructure Constraints` was too narrow; the KU layer should record infrastructure more broadly, including facilities, release pathways, capacities, and low-water limitations.
- `Real-Time / Emergency Operations` needs to mean operational actions under specific conditions, not simply the existence of a plan or agreement.
- Official operating manuals, operation guides, reservoir operation plans, water control manuals, annual operating plans, and technical appendices can contain many detailed rules and should be mined more deeply than ordinary webpages.

## Updated KU Dimensions

1. Operation Purpose
2. Operation Rules
3. Infrastructure
4. Real-Time / Emergency Operations
5. Coordination / Governance
6. Operational Data
7. Research / Modeling / Analysis
8. Evidence Gap / Uncertainty

## Prompt Principle Added

Official operation documents are treated as high-density priority sources. A single official manual can produce many KUs if the findings are distinct, source-grounded, and operationally useful. The extraction should look for detailed rules, thresholds, release criteria, triggers, infrastructure limits, data inputs, responsible agencies, and documentation requirements rather than only summarizing the document at a high level.

## Files Updated

- `skills/ku-extraction/SKILL.md`
- `skills/ku-extraction/references/extraction-protocol.md`
- `skills/ku-extraction/agents/openai.yaml`

