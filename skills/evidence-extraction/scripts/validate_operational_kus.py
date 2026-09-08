"""Validate updated-schema reservoir operational Evidence Unit JSONL.

This validator checks structure and traceability only. It does not prove that
the Evidence Unit wording is substantively correct or complete.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "evidence_unit.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
DIMENSIONS = set(SCHEMA["properties"]["engineering_dimension"]["enum"])
REQUIRED = set(SCHEMA["required"])

DISALLOWED = {
    "affected_operation_purposes",
    "condition_or_trigger",
}

CONFIDENCE = set(SCHEMA["properties"]["confidence"]["enum"])


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno} invalid JSON: {exc}") from exc
    return rows


def validate(evidence_units: list[dict], source_ids: set[str] | None = None) -> dict:
    errors = []
    warnings = []
    eu_ids = set()

    for i, evidence_unit in enumerate(evidence_units, start=1):
        label = evidence_unit.get("eu_id") or f"row-{i}"
        missing = REQUIRED - evidence_unit.keys()
        if missing:
            errors.append(f"{label} missing fields: {sorted(missing)}")

        disallowed = DISALLOWED & evidence_unit.keys()
        if disallowed:
            errors.append(f"{label} has disallowed fields under updated schema: {sorted(disallowed)}")

        if label in eu_ids:
            errors.append(f"duplicate eu_id: {label}")
        eu_ids.add(label)

        if evidence_unit.get("knowledge_layer") != "document_finding":
            errors.append(f"{label} invalid knowledge_layer: {evidence_unit.get('knowledge_layer')}")

        if source_ids is not None and evidence_unit.get("source_id") not in source_ids:
            errors.append(f"{label} source_id not found in source inventory: {evidence_unit.get('source_id')}")

        dimension = evidence_unit.get("engineering_dimension")
        if dimension not in DIMENSIONS:
            errors.append(f"{label} invalid engineering_dimension: {dimension}")

        confidence = evidence_unit.get("confidence")
        if confidence not in CONFIDENCE:
            errors.append(f"{label} invalid confidence: {confidence}")

        quote = str(evidence_unit.get("evidence_quote", "")).strip()
        if not quote:
            errors.append(f"{label} missing evidence_quote")
        elif len(quote) > 320:
            errors.append(f"{label} evidence_quote too long: {len(quote)}")
        elif len(quote) < 20:
            warnings.append(f"{label} evidence_quote is very short: {len(quote)}")

        finding = str(evidence_unit.get("finding", "")).strip()
        if not finding:
            errors.append(f"{label} missing finding")

        why = str(evidence_unit.get("why_it_matters", "")).strip()
        if not why:
            errors.append(f"{label} missing why_it_matters")
        elif why.lower().startswith("this evidence unit preserves"):
            errors.append(f"{label} uses generic why_it_matters wording")

        if not str(evidence_unit.get("source_location", "")).strip():
            errors.append(f"{label} missing source_location")

    traceability_errors = [error for error in errors if "source_id not found in source inventory" in error]
    schema_errors = [error for error in errors if error not in traceability_errors]
    return {
        "evidence_unit_records": len(evidence_units),
        "source_count": len({row.get("source_id") for row in evidence_units if row.get("source_id")}),
        "dimension_counts": dict(Counter(row.get("engineering_dimension") for row in evidence_units)),
        "confidence_counts": dict(Counter(row.get("confidence") for row in evidence_units)),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "validation_scope": (
            "updated-schema structural validation only; no substantive human/domain validation"
        ),
        "stage": "evidence_extraction",
        "status": "fail" if errors else "warning" if warnings else "pass",
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
    parser = argparse.ArgumentParser(description="Validate operational Evidence Unit JSONL.")
    parser.add_argument("--evidence-units", required=True, type=Path, help="evidence_units.jsonl")
    parser.add_argument("--source-inventory", type=Path, help="Optional source inventory JSONL for source_id checks")
    parser.add_argument("--out", type=Path, help="Optional validation JSON output")
    args = parser.parse_args()

    source_ids = None
    if args.source_inventory:
        source_ids = {row.get("source_id") for row in load_jsonl(args.source_inventory)}

    summary = validate(load_jsonl(args.evidence_units), source_ids=source_ids)
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    if summary["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
