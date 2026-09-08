# Reservoir Knowledge Base Agentic Workflow

This project is the clean framework version of the reservoir operation knowledge-base work.

It is organized around the current article logic:

1. Build a source-grounded reservoir operation knowledge-base dataset.
2. Use an AI-native, human-reviewable workflow to construct, refine, and validate the dataset.
3. Demonstrate the workflow through reservoir case studies such as Lake Powell.

This repository intentionally does not include old pilot artifacts, archived Tavily results, local virtual environments, or historical demo outputs from the earlier design project.

## Core Idea

Reservoir operation evidence is fragmented across official operating documents, technical reports, research papers, datasets, and public/context sources. This workflow turns those heterogeneous sources into:

- preserved source inventories;
- source-level Evidence Units (EUs);
- Knowledge Cards that conservatively consolidate related EUs;
- source-grounded Synthesis Cards that analyze operational relationships;
- index-ready and report-ready evidence chains;
- automated validation records and optional sampled human-review records.

## Project Structure

| Folder | Purpose |
|---|---|
| `docs/` | Framework paper/proposal and design notes |
| `skills/` | Agent-usable protocols for the six workflow stages |
| `schemas/` | Machine-readable schemas and controlled vocabularies |
| `templates/` | Reusable templates for runs, manifests, human review, and validation |
| `runs/` | Per-reservoir workflow runs; generated outputs should go here |
| `datasets/` | Curated dataset releases assembled from validated runs |
| `validation/` | Reusable validation tooling and optional method/transfer-study assets |
| `reports/` | Reader-facing reports and case-study outputs |

The canonical routine validation design is documented in
[`docs/validation-framework.md`](docs/validation-framework.md). Reusable
cross-run tooling and optional study assets are described in
[`validation/README.md`](validation/README.md).

## Setup

Create a local virtual environment and install the pinned dependencies before
running any stage script (PDF text extraction silently degrades without
`pypdf`/`cryptography`):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Main Workflow

The intended workflow is:

```text
source acquisition
-> evidence extraction
-> knowledge consolidation
-> synthesis
-> indexing
-> report generation
```

## Skill Groups

The workflow uses six stage-specific skill groups:

| Stage | Skill | Role |
|---|---|---|
| 1. Source acquisition | `skills/source-acquisition/` | Discover, screen, preserve, parse, and validate source inventories |
| 2. Evidence extraction | `skills/evidence-extraction/` | Extract source-grounded Evidence Units from parsed sources |
| 3. Knowledge consolidation | `skills/knowledge-consolidation/` | Consolidate related Evidence Units into Knowledge Cards |
| 4. Synthesis | `skills/synthesis/` | Produce Synthesis Cards from validated Evidence Units and Knowledge Cards |
| 5. Indexing | `skills/indexing/` | Encode validated knowledge-base records into index-ready records |
| 6. Report generation | `skills/report-generation/` | Generate evidence-grounded reports and claim-evidence maps |

## Source Tiers

- `TR-A`: official or authoritative operating evidence.
- `TR-B`: research or technical analysis.
- `TR-C`: media, stakeholder, public, or context evidence.

Source inclusion should be based on operational relevance and expected information value, not a fixed target count. Highly documented reservoirs may justify larger source inventories; smaller reservoirs may have only 10-20 high-value sources.

## Implementation Strategy

This project uses a hybrid implementation:

- Python scripts handle deterministic processing, parsing, validation, and metrics.
- LLM calls support source screening, Evidence extraction, Knowledge consolidation, and Synthesis.
- The agent organizes the overall research process, applies skill protocols, runs automated validation, prepares optional human review, manages iteration, and preserves artifact links.

The goal is not a one-off prompt result. The goal is a repeatable, inspectable, human-reviewable workflow for building reservoir operation knowledge-base datasets.

