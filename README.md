# Reservoir Knowledge Base Agentic Workflow

This project is the clean framework version of the reservoir operation knowledge-base work.

It is organized around the current article logic:

1. Build a source-grounded reservoir operation knowledge-base dataset.
2. Use an AI-native, human-gated workflow to construct, refine, and validate the dataset.
3. Demonstrate the workflow through reservoir case studies such as Lake Powell.

This repository intentionally does not include old pilot artifacts, archived Tavily results, local virtual environments, or historical demo outputs from the earlier design project.

## Core Idea

Reservoir operation evidence is fragmented across official operating documents, technical reports, research papers, datasets, and public/context sources. This workflow turns those heterogeneous sources into:

- preserved source inventories;
- source-level operational Knowledge Units (KUs);
- cross-document synthesis records;
- retrieval-ready and report-ready evidence chains;
- sampled validation records for human review.

## Project Structure

| Folder | Purpose |
|---|---|
| `docs/` | Framework paper/proposal and design notes |
| `skills/` | Agent-usable protocols for the five workflow stages |
| `schemas/` | Machine-readable schemas and controlled vocabularies |
| `templates/` | Reusable templates for runs, manifests, human review, and validation |
| `runs/` | Per-reservoir workflow runs; generated outputs should go here |
| `datasets/` | Curated dataset releases assembled from validated runs |
| `validation/` | Cross-run validation summaries and sampled review results |
| `reports/` | Reader-facing reports and case-study outputs |

## Main Workflow

The intended workflow is:

```text
source discovery
-> relevance screening and tier assignment
-> source preservation and parsing
-> source-grounded KU extraction
-> cross-document synthesis
-> retrieval/report preparation
-> sampled validation and refinement
-> transfer validation on a second reservoir
```

## Skill Groups

The workflow uses five stage-specific skill groups:

| Stage | Skill | Role |
|---|---|---|
| 1. Source acquisition | `skills/source-acquisition-suite/` | Discover, screen, preserve, parse, and validate source inventories |
| 2. KU extraction | `skills/ku-extraction/` | Extract source-grounded operational KUs from parsed sources |
| 3. Synthesis | `skills/synthesis-analysis/` | Produce cross-document synthesis records from validated KUs |
| 4. Retrieval/indexing | `skills/retrieval-indexing/` | Build retrieval-ready records and benchmark retrieval outputs |
| 5. Report generation | `skills/report-generation/` | Generate evidence-grounded reports and claim-evidence maps |

## Source Tiers

- `TR-A`: official or authoritative operating evidence.
- `TR-B`: research or technical analysis.
- `TR-C`: media, stakeholder, public, or context evidence.

Source inclusion should be based on operational relevance and expected information value, not a fixed target count. Highly documented reservoirs may justify larger source inventories; smaller reservoirs may have only 10-20 high-value sources.

## Implementation Strategy

This project uses a hybrid implementation:

- Python scripts handle deterministic processing, parsing, validation, and metrics.
- LLM calls support source screening, KU extraction, and synthesis.
- The agent organizes the overall research process, applies skill protocols, coordinates human gates, manages iteration, and preserves artifact links.

The goal is not a one-off prompt result. The goal is a repeatable, inspectable, human-gated workflow for building reservoir operation knowledge-base datasets.

