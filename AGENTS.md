# Agent Instructions

This project builds source-grounded reservoir operation knowledge-base datasets using an AI-native, human-gated workflow.

## Operating Principles

- Preserve source evidence before extracting knowledge.
- Separate document-level KUs from cross-document synthesis.
- Keep source links, KU IDs, synthesis IDs, and evidence locators traceable.
- Use Python for deterministic processing and validation.
- Use LLM reasoning for semantic screening, KU extraction, and synthesis.
- Use the agent to coordinate skills, scripts, human review gates, reruns, and versioned artifacts.
- Do not overwrite previous runs. Create a new folder under `runs/` for each reservoir/run.

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
   - Analyze relationships across validated KUs.
   - Produce synthesis records for recurring findings, complementary evidence, source discrepancies, operational tradeoffs, evidence gaps, and unresolved issues.
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
- `source_manifest.json`
- `sources/source_inventory.jsonl`
- `sources/raw/`
- `sources/text/`
- `sources/parsed_docling/` when available
- `kus/operational_kus.jsonl`
- `synthesis/synthesis_records.jsonl`
- `retrieval/retrieval_records.jsonl`
- `retrieval/benchmark_questions.jsonl`
- `validation/`
- `reports/`

## Human Gates

Use human approval before:

- finalizing source inclusion thresholds;
- accepting revised KU or synthesis schemas;
- treating a synthesis claim as report-ready;
- promoting a run into a dataset release;
- changing transfer validation results into development refinements.

