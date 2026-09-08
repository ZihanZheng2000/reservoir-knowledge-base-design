"""Validate reservoir Knowledge Card JSONL against Evidence Unit IDs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "knowledge_card.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
REQUIRED = set(SCHEMA["required"])
CONSOLIDATION_TYPES = set(SCHEMA["properties"]["consolidation_type"]["enum"])
CONFIDENCE = set(SCHEMA["properties"]["confidence"]["enum"])


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number} invalid JSON: {exc}") from exc
    return rows


def validate(evidence_units: list[dict], knowledge_cards: list[dict]) -> dict:
    eu_ids = {row.get("eu_id") for row in evidence_units}
    card_ids: set[str] = set()
    errors: list[str] = []

    for index, card in enumerate(knowledge_cards, 1):
        card_id = card.get("knowledge_card_id", f"row-{index}")
        missing = REQUIRED - card.keys()
        if missing:
            errors.append(f"{card_id} missing fields: {sorted(missing)}")
        if card_id in card_ids:
            errors.append(f"duplicate knowledge_card_id: {card_id}")
        card_ids.add(card_id)
        if card.get("knowledge_layer") != "knowledge_consolidation":
            errors.append(f"{card_id} invalid knowledge_layer")
        if card.get("consolidation_type") not in CONSOLIDATION_TYPES:
            errors.append(f"{card_id} invalid consolidation_type")
        if card.get("confidence") not in CONFIDENCE:
            errors.append(f"{card_id} invalid confidence")
        based_on = card.get("based_on_eu_ids")
        if not isinstance(based_on, list) or not based_on:
            errors.append(f"{card_id} based_on_eu_ids must be a non-empty list")
            based_on = []
        for eu_id in based_on:
            if eu_id not in eu_ids:
                errors.append(f"{card_id} unknown EU ID: {eu_id}")
        for field in ("operational_question", "title", "consolidated_finding"):
            if not str(card.get(field, "")).strip():
                errors.append(f"{card_id} missing {field}")

    traceability_errors = [error for error in errors if "unknown EU ID" in error]
    schema_errors = [error for error in errors if error not in traceability_errors]
    return {
        "evidence_unit_records": len(evidence_units),
        "knowledge_card_records": len(knowledge_cards),
        "consolidation_type_counts": dict(Counter(card.get("consolidation_type") for card in knowledge_cards)),
        "error_count": len(errors),
        "errors": errors,
        "warning_count": 0,
        "warnings": [],
        "stage": "knowledge_consolidation",
        "status": "fail" if errors else "pass",
        "automated_validation": {
            "schema_conformance": {
                "name": "schema_conformance",
                "status": "fail" if schema_errors else "pass",
                "issue_count": len(schema_errors),
            },
            "traceability_or_acquisition": {
                "name": "traceability_integrity",
                "status": "fail" if traceability_errors else "pass",
                "issue_count": len(traceability_errors),
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Knowledge Cards against Evidence Units.")
    parser.add_argument("--evidence-units", required=True, type=Path)
    parser.add_argument("--knowledge-cards", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = validate(load_jsonl(args.evidence_units), load_jsonl(args.knowledge_cards))
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    if result["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
