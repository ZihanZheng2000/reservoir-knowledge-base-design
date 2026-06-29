# Claude Code Instructions

This project builds source-grounded reservoir operation knowledge-base datasets using an AI-native, human-gated workflow.

## Operating Principles

- Preserve source evidence before extracting knowledge.
- Separate document-level KUs from cross-document synthesis.
- Keep source links, KU IDs, synthesis IDs, and evidence locators traceable.
- Use Python for deterministic processing and validation.
- Use LLM reasoning for semantic screening, KU extraction, and synthesis.
- Use the agent to coordinate skills, scripts, human review gates, reruns, and versioned artifacts.
- Do not overwrite previous runs. Create a new folder under `runs/` for each reservoir/run.

## Skills

Load the relevant skill before starting each workflow stage. Skills are in `skills/`:

| Stage | Skill folder | Load with |
|---|---|---|
| 1. Source acquisition | `skills/source-acquisition-suite/` | `/source-acquisition-suite` |
| 2. KU extraction | `skills/ku-extraction/` | `/ku-extraction` |
| 3. Synthesis | `skills/synthesis-analysis/` | `/synthesis-analysis` |
| 4. Retrieval/indexing | `skills/retrieval-indexing/` | `/retrieval-indexing` |
| 5. Report generation | `skills/report-generation/` | `/report-generation` |

Each skill folder contains a `SKILL.md` with its full protocol, a `references/` subfolder with detailed protocols, and a `scripts/` subfolder with Python helpers.

## Workflow Stages

1. **Source acquisition**
   - Discover candidate sources.
   - Screen by operational relevance and source tier.
   - Preserve raw files and extracted text.
   - Validate source inventory.

2. **KU extraction**
   - Parse documents into page/section-aware packets.
   - Extract source-grounded operational KUs.
   - Validate schema, evidence quote, source locator, and engineering dimension.

3. **Synthesis**
   - Consolidate validated KUs into dimension-level knowledge points (`consolidated_knowledge_points.jsonl`) first.
   - Then produce synthesis cards for recurring findings, complementary evidence, source discrepancies, operational tradeoffs, evidence gaps, and unresolved issues.
   - For important claims, return to source sections before finalizing.

4. **Retrieval/indexing**
   - Use `skills/retrieval-indexing/`.
   - Prepare retrieval-ready records, benchmark questions, and traceable top-k retrieval outputs.

5. **Report generation**
   - Use `skills/report-generation/`.
   - Draft human-readable reports only from validated KUs and synthesis records.
   - Preserve claim-evidence maps for sampled report validation.

6. **Workflow refinement and sampled validation**
   - Draw human-reviewed samples from each stage.
   - Compute stage-level metrics.
   - Identify failure modes.
   - Let the agent propose and implement approved revisions.
   - Rerun affected stages first for diagnosis; rerun the full workflow after major revisions.

7. **Transfer validation**
   - Apply the stabilized workflow to a second reservoir.
   - Use the same sampled validation protocol.
   - Avoid substantial redesign unless a major systematic failure appears.

## Required Run Artifacts

Each run under `runs/<reservoir_id>_<run_date>/` should contain:

- `run_manifest.json`
- `run_summary.md`
- `source_manifest.json`
- `sources/source_inventory.jsonl`
- `sources/raw/`
- `sources/text/`
- `sources/parsed_docling/` when available
- `kus/extraction_packets.jsonl`
- `kus/operational_kus.jsonl`
- `synthesis/consolidated_knowledge_points.jsonl`
- `synthesis/synthesis_records.jsonl`
- `retrieval/retrieval_records.jsonl`
- `retrieval/benchmark_questions.jsonl`
- `validation/`
- `reports/`

## Python Scripts

Always prefer the provided Python scripts for deterministic steps. Do not reimplement their logic inline.

```powershell
# Stage 1 — acquire sources
python skills/source-acquisition-suite/scripts/acquire_sources_from_manifest.py `
  --manifest runs/<run>/source_manifest.json `
  --out-dir runs/<run> `
  --reservoir-id <id> `
  --reservoir-name "<name>"

# Stage 1 — validate inventory
python skills/source-acquisition-suite/scripts/validate_source_inventory.py `
  --inventory runs/<run>/sources/source_inventory.jsonl `
  --out runs/<run>/validation/layer1_source_validation.json

# Stage 2 — build extraction packets
python skills/ku-extraction/scripts/make_extraction_packet.py `
  --inventory runs/<run>/sources/source_inventory.jsonl `
  --out runs/<run>/kus/extraction_packets.jsonl `
  --parse-manifest runs/<run>/sources/docling_parse_manifest.jsonl

# Stage 3 — validate synthesis cards
python skills/synthesis-analysis/scripts/validate_synthesis_cards.py `
  --kus runs/<run>/kus/operational_kus.jsonl `
  --synthesis runs/<run>/synthesis/synthesis_records.jsonl `
  --out runs/<run>/validation/layer3_synthesis_validation.json
```

## Human Gates

Use human approval before:

- finalizing source inclusion thresholds;
- accepting revised KU or synthesis schemas;
- treating a synthesis claim as report-ready;
- promoting a run into a dataset release;
- changing transfer validation results into development refinements.

## Source Tiers

- `TR-A`: official or authoritative operating evidence.
- `TR-B`: research or technical analysis.
- `TR-C`: media, stakeholder, public, or context evidence.

## Implementation Notes

- Python scripts handle deterministic processing, parsing, validation, and metrics.
- LLM calls support source screening, KU extraction, and synthesis.
- The agent organizes the overall research process, applies skill protocols, coordinates human gates, manages iteration, and preserves artifact links.
- The goal is a repeatable, inspectable, human-gated workflow — not a one-off prompt result.
