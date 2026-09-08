"""Validate index-ready records for schema conformance and evidence traceability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "schemas" / "index_record.schema.json").read_text(encoding="utf-8"))
REQUIRED = set(SCHEMA["required"])
RECORD_TYPES = set(SCHEMA["properties"]["record_type"]["enum"])
MANIFEST_SCHEMA = json.loads((ROOT / "schemas" / "index_manifest.schema.json").read_text(encoding="utf-8"))
MANIFEST_REQUIRED = set(MANIFEST_SCHEMA["required"])


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number} invalid JSON: {exc}") from exc
    return rows


def validate(records: list[dict], manifest: dict, evidence_units: list[dict], knowledge_cards: list[dict], synthesis_cards: list[dict]) -> dict:
    eu_ids = {item.get("eu_id") for item in evidence_units}
    kc_ids = {item.get("knowledge_card_id") for item in knowledge_cards}
    synthesis_ids = {item.get("synthesis_card_id") for item in synthesis_cards}
    errors: list[str] = []
    record_ids: set[str] = set()

    missing_manifest = MANIFEST_REQUIRED - manifest.keys()
    if missing_manifest:
        errors.append(f"index manifest missing fields: {sorted(missing_manifest)}")

    expected = {
        "evidence_unit": eu_ids,
        "knowledge_card": kc_ids,
        "synthesis_card": synthesis_ids,
    }
    for index, record in enumerate(records, 1):
        label = record.get("index_record_id", f"row-{index}")
        missing = REQUIRED - record.keys()
        if missing:
            errors.append(f"{label} missing fields: {sorted(missing)}")
        if label in record_ids:
            errors.append(f"duplicate index_record_id: {label}")
        record_ids.add(label)
        record_type = record.get("record_type")
        if record_type not in RECORD_TYPES:
            errors.append(f"{label} invalid record_type: {record_type}")
        elif record.get("record_id") not in expected[record_type]:
            errors.append(f"{label} record_id does not resolve to validated {record_type}: {record.get('record_id')}")
        for eu_id in record.get("based_on_eu_ids", []):
            if eu_id not in eu_ids:
                errors.append(f"{label} unknown EU ID: {eu_id}")
        for kc_id in record.get("based_on_knowledge_card_ids", []):
            if kc_id not in kc_ids:
                errors.append(f"{label} unknown KC ID: {kc_id}")

    traceability_errors = [
        error for error in errors
        if "does not resolve to validated" in error or "unknown EU ID" in error or "unknown KC ID" in error
    ]
    schema_errors = [error for error in errors if error not in traceability_errors]
    return {
        "stage": "indexing",
        "index_record_count": len(records),
        "error_count": len(errors),
        "warning_count": 0,
        "errors": errors,
        "warnings": [],
        "status": "fail" if errors else "pass",
        "automated_validation": {
            "schema_conformance": {"name": "schema_conformance", "status": "fail" if schema_errors else "pass", "issue_count": len(schema_errors)},
            "traceability_or_acquisition": {"name": "traceability_integrity", "status": "fail" if traceability_errors else "pass", "issue_count": len(traceability_errors)},
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index-records", required=True, type=Path)
    parser.add_argument("--index-manifest", required=True, type=Path)
    parser.add_argument("--evidence-units", required=True, type=Path)
    parser.add_argument("--knowledge-cards", required=True, type=Path)
    parser.add_argument("--synthesis-cards", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.index_manifest.read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict):
        parser.error("--index-manifest must contain a JSON object")
    result = validate(load_jsonl(args.index_records), manifest, load_jsonl(args.evidence_units), load_jsonl(args.knowledge_cards), load_jsonl(args.synthesis_cards))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
