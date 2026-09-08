# Subagent EU Extraction Protocol

## Purpose

Use tier-specific subagents to isolate source reading from the main agent's active context while preserving the same EU schema and quality rules as the base EU extraction skill.

## Tier Assignment

Partition by `source_tier` from `source_inventory_eu_ready.jsonl`.

- `TR-A`: official, authoritative, or core sources.
- `TR-B`: research, technical, or supporting sources.
- `TR-C`: context, news, advocacy, commentary, or weaker sources.

If a source has no tier, assign it to `tier_unknown_evidence_units.jsonl` and record the issue in the run summary.

## Subagent Prompt Template

Use a prompt like this, replacing the placeholders:

```text
Use the repo skill at skills/evidence-extraction to extract document-level reservoir operation EUs from only the assigned <TIER> sources in <RUN_DIR>.

Inputs:
- EU-ready inventory: <RUN_DIR>/02_evidence_extraction/method_subagent/source_inventory_eu_ready.jsonl
- Extraction packets: <RUN_DIR>/02_evidence_extraction/method_subagent/extraction_packets.jsonl
- Assigned source_tier: <TIER>

Output:
- Write JSONL to <RUN_DIR>/02_evidence_extraction/method_subagent/<TIER_FILE>_evidence_units.jsonl.
- Set extraction_method to "ku-extraction-subagent".
- Use EU IDs with prefix EU-<RUN_LABEL>-<TIER_FILE>-001, 002, ...

Rules:
- Use only assigned sources.
- Extract document-level EUs, not cross-document synthesis.
- Preserve evidence quotes and source locators.
- Use the approved engineering dimensions from skills/evidence-extraction.
- Remove only duplicate candidates that state the same operational fact within the same source.
- Keep different operational facts separate.
- Validate your JSONL with skills/evidence-extraction/scripts/validate_operational_kus.py before reporting completion.

Return only:
- output path
- EU count
- validation result
- unresolved issues
```

## Main-Agent Merge Checks

After all tier files are complete:

1. Confirm every EU has a unique `eu_id`.
2. Confirm every `source_id` appears in the EU-ready inventory.
3. Confirm no EU uses an unapproved `engineering_dimension`.
4. Confirm `extraction_method` is `ku-extraction-subagent`.
5. Check for accidental cross-document language:
   - "multiple sources show"
   - "across documents"
   - "the literature indicates"
   - "overall"
6. Merge tier files in stable order: Tier A, Tier B, Tier C, unknown.
7. Run the base validator on the merged file.

## Comparison Notes

For method comparison, evaluate this method against the direct main-agent method and the prefilter method using the same human review metrics:

- `usefulness_0_2`
- `faithfulness_0_2`
- `dimension_correctness_0_2`

Expected tradeoff:

- Advantage: less main-agent context contamination and cleaner separation by source tier.
- Cost: more total token use and possible inconsistency across subagents.
