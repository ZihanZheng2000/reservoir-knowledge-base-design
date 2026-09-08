"""Validate deep Synthesis Cards against Evidence Units and Knowledge Cards."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "synthesis_card.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
REQUIRED = set(SCHEMA["required"])
PATTERNS = set(SCHEMA["properties"]["primary_pattern"]["enum"])
CONFIDENCE = set(SCHEMA["properties"]["confidence"]["enum"])
EVIDENCE_DEPTH = set(SCHEMA["properties"]["evidence_depth"]["enum"])
CONSEQUENCE_BASES = set(SCHEMA["properties"]["consequence_basis"]["enum"])
FAILURE_CLASSES = set(SCHEMA["properties"]["failure_episode"]["properties"]["failure_class"]["enum"])


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


def validate(evidence_units: list[dict], cards: list[dict], knowledge_cards: list[dict]) -> dict:
    eu_ids = {row.get("eu_id") for row in evidence_units}
    kc_ids = {row.get("knowledge_card_id") for row in knowledge_cards}
    card_ids: set[str] = set()
    errors: list[str] = []

    for index, card in enumerate(cards, 1):
        card_id = card.get("synthesis_card_id", f"row-{index}")
        missing = REQUIRED - card.keys()
        if missing:
            errors.append(f"{card_id} missing fields: {sorted(missing)}")
        if card_id in card_ids:
            errors.append(f"duplicate synthesis_card_id: {card_id}")
        card_ids.add(card_id)
        if card.get("knowledge_layer") != "synthesis_analysis":
            errors.append(f"{card_id} invalid knowledge_layer")
        primary = card.get("primary_pattern")
        if primary not in PATTERNS:
            errors.append(f"{card_id} invalid primary_pattern: {primary}")
        secondary = card.get("secondary_lenses")
        if not isinstance(secondary, list) or any(pattern not in PATTERNS for pattern in secondary):
            errors.append(f"{card_id} secondary_lenses must contain valid patterns")
        elif primary in secondary:
            errors.append(f"{card_id} primary_pattern must not appear in secondary_lenses")
        if card.get("confidence") not in CONFIDENCE:
            errors.append(f"{card_id} invalid confidence")
        if card.get("evidence_depth") not in EVIDENCE_DEPTH:
            errors.append(f"{card_id} invalid evidence_depth")
        if card.get("evidence_depth") in {"source_checked", "source_checked_with_direct_quote"}:
            if not str(card.get("source_locator_summary", "")).strip():
                errors.append(f"{card_id} source-checked card missing source_locator_summary")
            if not str(card.get("source_verification_note", "")).strip():
                errors.append(f"{card_id} source-checked card missing source_verification_note")
        based_on_eus = card.get("based_on_eu_ids")
        if not isinstance(based_on_eus, list) or not based_on_eus:
            errors.append(f"{card_id} based_on_eu_ids must be a non-empty list")
            based_on_eus = []
        for eu_id in based_on_eus:
            if eu_id not in eu_ids:
                errors.append(f"{card_id} unknown EU ID: {eu_id}")
        based_on_kcs = card.get("based_on_knowledge_card_ids")
        if not isinstance(based_on_kcs, list):
            errors.append(f"{card_id} based_on_knowledge_card_ids must be a list")
        else:
            for kc_id in based_on_kcs:
                if kc_id not in kc_ids:
                    errors.append(f"{card_id} unknown KC ID: {kc_id}")
        chain = card.get("analysis_chain")
        if not isinstance(chain, list) or len(chain) < 2:
            errors.append(f"{card_id} analysis_chain must contain at least two supported steps")
        else:
            for step in chain:
                if not isinstance(step, dict) or not str(step.get("stage", "")).strip() or not str(step.get("statement", "")).strip():
                    errors.append(f"{card_id} invalid analysis_chain step")
                    continue
                step_eus = step.get("based_on_eu_ids", [])
                if not isinstance(step_eus, list) or not step_eus:
                    errors.append(f"{card_id} analysis_chain step missing based_on_eu_ids")
                elif any(eu_id not in eu_ids for eu_id in step_eus):
                    errors.append(f"{card_id} analysis_chain step cites unknown EU ID")
        role_map = card.get("evidence_role_map")
        if not isinstance(role_map, list) or not role_map:
            errors.append(f"{card_id} evidence_role_map must be a non-empty list")
        elif any(not isinstance(item, dict) or not str(item.get("role", "")).strip() or not isinstance(item.get("eu_ids"), list) or not item["eu_ids"] for item in role_map):
            errors.append(f"{card_id} invalid evidence_role_map")
        if primary == "operational_consequence" and card.get("consequence_basis") not in CONSEQUENCE_BASES:
            errors.append(f"{card_id} operational_consequence requires valid consequence_basis")
        if primary == "historical_operation_failure":
            episode = card.get("failure_episode")
            if not isinstance(episode, dict):
                errors.append(f"{card_id} historical_operation_failure requires failure_episode")
            elif episode.get("failure_class") not in FAILURE_CLASSES:
                errors.append(f"{card_id} failure_episode has invalid failure_class")
        for field in ("title", "operational_question", "synthesis_claim", "scope_and_conditions", "uncertainty_or_exception", "operational_implication"):
            if not str(card.get(field, "")).strip():
                errors.append(f"{card_id} missing {field}")

    traceability_errors = [
        error for error in errors
        if "unknown EU ID" in error or "unknown KC ID" in error or "cites unknown EU ID" in error
    ]
    schema_errors = [error for error in errors if error not in traceability_errors]
    return {
        "evidence_unit_records": len(evidence_units),
        "knowledge_card_records": len(knowledge_cards),
        "synthesis_card_records": len(cards),
        "primary_pattern_counts": dict(Counter(card.get("primary_pattern") for card in cards)),
        "error_count": len(errors),
        "errors": errors,
        "warning_count": 0,
        "warnings": [],
        "stage": "synthesis",
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
    parser = argparse.ArgumentParser(description="Validate deep Synthesis Cards.")
    parser.add_argument("--evidence-units", required=True, type=Path)
    parser.add_argument("--synthesis-cards", required=True, type=Path)
    parser.add_argument("--knowledge-cards", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = validate(load_jsonl(args.evidence_units), load_jsonl(args.synthesis_cards), load_jsonl(args.knowledge_cards))
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    if result["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
