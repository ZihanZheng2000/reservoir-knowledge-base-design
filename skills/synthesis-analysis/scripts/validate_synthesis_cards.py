from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


REQUIRED = {
    "synthesis_id",
    "knowledge_layer",
    "reservoir_id",
    "reservoir_name",
    "analysis_type",
    "title",
    "summary",
    "based_on_ku_ids",
    "interpretation",
    "confidence",
    "next_step",
}

ANALYSIS_TYPES = {
    "recurring_finding",
    "complementary_evidence",
    "source_discrepancy",
    "operational_tradeoff",
    "evidence_gap",
    "outstanding_operational_issue",
}

CONFIDENCE = {"high", "medium", "low"}
EVIDENCE_DEPTH = {"ku_only", "source_checked", "source_checked_with_direct_quote"}
RESEARCH_RELEVANCE = {"supports_story", "needs_more_evidence", "background_only"}


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path} line {lineno} invalid JSON: {exc}") from exc
    return rows


def validate(kus: list[dict], synth: list[dict]) -> dict:
    errors: list[str] = []
    ku_ids = {row.get("ku_id") for row in kus}
    synth_ids: set[str] = set()

    for i, row in enumerate(synth, 1):
        sid = row.get("synthesis_id", f"row-{i}")
        missing = REQUIRED - row.keys()
        if missing:
            errors.append(f"{sid} missing fields: {sorted(missing)}")
        if sid in synth_ids:
            errors.append(f"duplicate synthesis_id: {sid}")
        synth_ids.add(sid)
        if row.get("knowledge_layer") != "synthesis_analysis":
            errors.append(f"{sid} invalid knowledge_layer")
        if row.get("analysis_type") not in ANALYSIS_TYPES:
            errors.append(f"{sid} invalid analysis_type: {row.get('analysis_type')}")
        if row.get("confidence") not in CONFIDENCE:
            errors.append(f"{sid} invalid confidence: {row.get('confidence')}")
        if "evidence_depth" in row and row.get("evidence_depth") not in EVIDENCE_DEPTH:
            errors.append(f"{sid} invalid evidence_depth: {row.get('evidence_depth')}")
        if "research_relevance" in row and row.get("research_relevance") not in RESEARCH_RELEVANCE:
            errors.append(f"{sid} invalid research_relevance: {row.get('research_relevance')}")
        if row.get("evidence_depth") in {"source_checked", "source_checked_with_direct_quote"}:
            if not row.get("source_locator_summary"):
                errors.append(f"{sid} source-checked card missing source_locator_summary")
            if not row.get("source_verification_note"):
                errors.append(f"{sid} source-checked card missing source_verification_note")
        based_on = row.get("based_on_ku_ids")
        if not isinstance(based_on, list) or not based_on:
            errors.append(f"{sid} based_on_ku_ids must be a non-empty list")
            based_on = []
        for kid in based_on:
            if kid not in ku_ids:
                errors.append(f"{sid} unknown KU id: {kid}")
        if len(row.get("summary", "")) < 40:
            errors.append(f"{sid} summary too short")
        if len(row.get("interpretation", "")) < 40:
            errors.append(f"{sid} interpretation too short")
        if row.get("analysis_type") == "next_step_priority":
            errors.append(f"{sid} next_step_priority is not an allowed analysis type")

    return {
        "ku_records": len(kus),
        "synthesis_records": len(synth),
        "analysis_type_counts": dict(Counter(row.get("analysis_type") for row in synth)),
        "referenced_ku_count": len({kid for row in synth for kid in row.get("based_on_ku_ids", []) if isinstance(row.get("based_on_ku_ids"), list)}),
        "error_count": len(errors),
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate reservoir synthesis cards against a KU JSONL file.")
    parser.add_argument("--kus", required=True, type=Path, help="Path to operational KU JSONL.")
    parser.add_argument("--synthesis", required=True, type=Path, help="Path to synthesis cards JSONL.")
    parser.add_argument("--out", type=Path, help="Optional path for validation JSON summary.")
    args = parser.parse_args()

    summary = validate(load_jsonl(args.kus), load_jsonl(args.synthesis))
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    if summary["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
