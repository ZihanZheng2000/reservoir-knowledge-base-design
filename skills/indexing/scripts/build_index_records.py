"""Build index-ready records from validated EU, KC, and Synthesis Card JSONL."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def compact(*parts: object) -> str:
    return "\n".join(str(part).strip() for part in parts if str(part).strip())


def build_records(evidence_units: list[dict], knowledge_cards: list[dict], synthesis_cards: list[dict]) -> list[dict]:
    records: list[dict] = []
    for row in evidence_units:
        record_id = row["eu_id"]
        records.append({
            "index_record_id": f"IDX-{record_id}", "record_type": "evidence_unit", "record_id": record_id,
            "reservoir_id": row.get("reservoir_id", ""), "reservoir_name": row.get("reservoir_name", ""),
            "index_text": compact(row.get("engineering_dimension"), row.get("finding"), row.get("why_it_matters")),
            "engineering_dimension": row.get("engineering_dimension", ""), "primary_pattern": "",
            "source_ids": [row.get("source_id", "")], "based_on_eu_ids": [record_id],
            "based_on_knowledge_card_ids": [], "source_locators": [row.get("source_location", "")],
            "confidence": row.get("confidence", ""), "evidence_depth": "source_grounded",
        })
    for row in knowledge_cards:
        record_id = row["knowledge_card_id"]
        records.append({
            "index_record_id": f"IDX-{record_id}", "record_type": "knowledge_card", "record_id": record_id,
            "reservoir_id": row.get("reservoir_id", ""), "reservoir_name": row.get("reservoir_name", ""),
            "index_text": compact(row.get("engineering_dimension"), row.get("operational_question"), row.get("consolidated_finding")),
            "engineering_dimension": row.get("engineering_dimension", ""), "primary_pattern": "",
            "source_ids": [], "based_on_eu_ids": row.get("based_on_eu_ids", []),
            "based_on_knowledge_card_ids": [record_id], "source_locators": [],
            "confidence": row.get("confidence", ""), "evidence_depth": "consolidated_evidence",
        })
    for row in synthesis_cards:
        record_id = row["synthesis_card_id"]
        records.append({
            "index_record_id": f"IDX-{record_id}", "record_type": "synthesis_card", "record_id": record_id,
            "reservoir_id": row.get("reservoir_id", ""), "reservoir_name": row.get("reservoir_name", ""),
            "index_text": compact(row.get("primary_pattern"), row.get("synthesis_claim"), row.get("operational_implication")),
            "engineering_dimension": "", "primary_pattern": row.get("primary_pattern", ""),
            "source_ids": [], "based_on_eu_ids": row.get("based_on_eu_ids", []),
            "based_on_knowledge_card_ids": row.get("based_on_knowledge_card_ids", []),
            "source_locators": [row.get("source_locator_summary", "")] if row.get("source_locator_summary") else [],
            "confidence": row.get("confidence", ""), "evidence_depth": row.get("evidence_depth", "eu_only"),
        })
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Build structured index-ready knowledge records.")
    parser.add_argument("--evidence-units", required=True, type=Path)
    parser.add_argument("--knowledge-cards", required=True, type=Path)
    parser.add_argument("--synthesis-cards", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--encoding-model", default="structured_text_only")
    args = parser.parse_args()

    records = build_records(load_jsonl(args.evidence_units), load_jsonl(args.knowledge_cards), load_jsonl(args.synthesis_cards))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in records) + ("\n" if records else ""), encoding="utf-8")
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(), "encoding_model": args.encoding_model,
        "record_count": len(records), "record_type_counts": dict(Counter(row["record_type"] for row in records)),
        "records_path": str(args.out), "encoding_status": "index_ready_text_records",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
