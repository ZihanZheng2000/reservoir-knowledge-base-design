"""Validate a report claim-evidence map for schema conformance and traceability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads((ROOT / "schemas" / "claim_evidence_map.schema.json").read_text(encoding="utf-8"))
REQUIRED = set(SCHEMA["required"])


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number} invalid JSON: {exc}") from exc
    return rows


def validate(claims: list[dict], sources: list[dict], evidence_units: list[dict], knowledge_cards: list[dict], synthesis_cards: list[dict], report: Path | None) -> dict:
    source_ids = {item.get("source_id") for item in sources}
    eu_ids = {item.get("eu_id") for item in evidence_units}
    kc_ids = {item.get("knowledge_card_id") for item in knowledge_cards}
    synthesis_ids = {item.get("synthesis_card_id") for item in synthesis_cards}
    errors: list[str] = []
    claim_ids: set[str] = set()
    if report is not None and not report.is_file():
        errors.append(f"report file not found: {report}")
    for index, claim in enumerate(claims, 1):
        label = claim.get("claim_id", f"row-{index}")
        missing = REQUIRED - claim.keys()
        if missing:
            errors.append(f"{label} missing fields: {sorted(missing)}")
        if label in claim_ids:
            errors.append(f"duplicate claim_id: {label}")
        claim_ids.add(label)
        cited = 0
        for key, allowed, label_name in (
            ("cited_source_ids", source_ids, "source"),
            ("cited_eu_ids", eu_ids, "EU"),
            ("cited_knowledge_card_ids", kc_ids, "KC"),
            ("cited_synthesis_card_ids", synthesis_ids, "Synthesis Card"),
        ):
            values = claim.get(key, [])
            if not isinstance(values, list):
                errors.append(f"{label} {key} must be a list")
                continue
            cited += len(values)
            for value in values:
                if value not in allowed:
                    errors.append(f"{label} unknown {label_name} ID: {value}")
        if not cited:
            errors.append(f"{label} has no cited evidence IDs")

    traceability_errors = [error for error in errors if "unknown " in error or "no cited evidence IDs" in error]
    schema_errors = [error for error in errors if error not in traceability_errors]
    return {
        "stage": "report_generation",
        "claim_count": len(claims),
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
    parser.add_argument("--claim-evidence-map", required=True, type=Path)
    parser.add_argument("--source-inventory", required=True, type=Path)
    parser.add_argument("--evidence-units", required=True, type=Path)
    parser.add_argument("--knowledge-cards", required=True, type=Path)
    parser.add_argument("--synthesis-cards", required=True, type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = validate(load_jsonl(args.claim_evidence_map), load_jsonl(args.source_inventory), load_jsonl(args.evidence_units), load_jsonl(args.knowledge_cards), load_jsonl(args.synthesis_cards), args.report)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
