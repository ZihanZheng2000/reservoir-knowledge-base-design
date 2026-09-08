# Prefilter EU Extraction Protocol

## Purpose

Use deterministic Python filtering to reduce the amount of text Codex reads before EU extraction. The prefilter finds broad candidate passages; Codex still decides whether a passage supports a valid document-level EU.

## Candidate Passages Are Not Evidence By Themselves

A candidate passage only means the text contains one or more operational signals. A valid EU still needs:

- a specific operational finding
- an evidence quote
- a source locator
- an approved engineering dimension
- a reason why the finding matters for reservoir operation

Do not create a EU merely because a passage contains a keyword.

## Recall-First Review

After running the prefilter:

1. Check `candidate_passages_summary.json`.
2. Confirm every EU-ready source has at least one candidate passage unless the source is genuinely not operationally useful.
3. For official operating manuals, technical appendices, operating plans, and water control documents, expect many candidate passages.
4. If a priority source has too few candidates, rerun with larger windows, lower score threshold, or additional keywords.

Useful rerun adjustments:

```powershell
python skills/evidence-extraction-prefilter/scripts/extract_candidate_passages.py `
  --inventory runs/<run_id>/02_evidence_extraction/method_prefilter/source_inventory_eu_ready.jsonl `
  --out runs/<run_id>/02_evidence_extraction/method_prefilter/candidate_passages.jsonl `
  --summary-out runs/<run_id>/02_evidence_extraction/method_prefilter/candidate_passages_summary.json `
  --window-chars 2400 `
  --overlap-chars 500 `
  --min-score 1
```

## EU Writing From Candidates

When reading candidates:

- Work source by source.
- Treat adjacent candidate passages as context for each other.
- Use the shortest evidence quote that supports the finding.
- Preserve names, values, units, dates, thresholds, model names, program names, and official terms.
- Keep different operational facts separate.
- Remove only duplicate candidates that state the same operational fact within the same source.
- Do not synthesize across sources.

## Comparison Notes

For method comparison, compare this method against direct full-reading and subagent extraction on:

- human `usefulness_0_2`
- human `faithfulness_0_2`
- human `dimension_correctness_0_2`
- EU count by source and source tier
- zero-candidate source count
- review time or token cost if available

Expected tradeoff:

- Advantage: lower LLM reading load and easier review of long sources.
- Cost: possible recall loss if relevant text does not match prefilter signals.
