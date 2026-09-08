"""Create a prefilled, stage-specific human-review workpaper from run records.

Refuses to overwrite a review file unless --overwrite is supplied, so completed
human judgments are never silently lost.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


STAGES = {
    "source_acquisition": "01_source_acquisition", "evidence_extraction": "02_evidence_extraction",
    "knowledge_consolidation": "03_knowledge_consolidation", "synthesis": "04_synthesis",
    "indexing": "05_indexing", "report_generation": "06_report_generation",
}


def rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def relative(target: str, base: Path, project: Path) -> str | None:
    if not target:
        return None
    candidate = Path(target)
    if not candidate.is_absolute():
        candidate = project / candidate
    if not candidate.exists():
        return None
    return os.path.relpath(candidate, base).replace("\\", "/")


def source_links(source: dict, stage_dir: Path, project: Path) -> dict:
    return {
        "source_pdf_link": relative(str(source.get("raw_file_path") or ""), stage_dir, project),
        "source_text_link": relative(str(source.get("extracted_text_path") or ""), stage_dir, project),
    }


def navigation(stage_dir: Path, source_map: dict, project: Path) -> None:
    lines = ["# Source Navigation", "", "Direct links to preserved source files used by this stage.", "", "| Source ID | PDF / raw | Extracted text |", "|---|---|---|"]
    for source_id, source in sorted(source_map.items()):
        links = source_links(source, stage_dir, project)
        raw = f"[open]({links['source_pdf_link']})" if links["source_pdf_link"] else "unavailable"
        text = f"[open]({links['source_text_link']})" if links["source_text_link"] else "unavailable"
        lines.append(f"| {source_id} | {raw} | {text} |")
    (stage_dir / "source_navigation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def payload_for(run_dir: Path, stage: str) -> dict:
    project = run_dir.parents[1]
    stage_dir = run_dir / STAGES[stage]
    source_rows = rows(run_dir / "01_source_acquisition" / "sources" / "source_inventory.jsonl")
    source_map = {row.get("source_id"): row for row in source_rows if row.get("source_id")}
    base = {"review_status": "not_requested", "stage": stage, "reviewer": None, "review_date": None,
            "metric_rubric_reference": "docs/validation-framework.md#human-review-by-layer-focus-and-rubric"}
    if stage == "source_acquisition":
        candidates = rows(stage_dir / "sources" / "candidate_inventory.jsonl") or source_rows
        base["candidate_inventory_scope"] = "Complete retained candidate inventory; recall and precision are calculated within this documented set."
        base["items"] = [{"row_type": "source_decision", "source_id": str(r.get("acquisition_source_id") or r.get("candidate_id") or r.get("source_id")), "source_title": r.get("title", ""), "source_url": r.get("url", ""), "codex_use": str(r.get("codex_use") or "Y"), "codex_tier": str(r.get("codex_tier") or r.get("source_tier") or "B").upper(), "human_use": None, "human_tier": None, "notes": None, "required_action": None} for r in candidates]
        base["run_level_metrics"] = {"source_adequacy_score": None, "notes": None, "required_action": None}
        return base
    evidence = rows(run_dir / "02_evidence_extraction" / "evidence_units.jsonl")
    eu_map = {row.get("eu_id"): row for row in evidence if row.get("eu_id")}
    if stage == "evidence_extraction":
        base["items"] = []
        for eu in evidence:
            source = source_map.get(eu.get("source_id"), {})
            base["items"].append({"row_type": "review_item", "eu_id": eu.get("eu_id"), "source_id": eu.get("source_id"), "engineering_dimension": eu.get("engineering_dimension"), "finding": eu.get("finding"), "source_location": eu.get("source_location"), **source_links(source, stage_dir, project), "codex_decision": "retain as EU", "human_disposition": None, "faithfulness_score": None, "relevance_score": None, "value_score": None, "notes": None, "required_action": None})
        navigation(stage_dir, source_map, project)
        return base
    cards = rows(run_dir / "03_knowledge_consolidation" / "knowledge_cards.jsonl")
    card_map = {row.get("knowledge_card_id"): row for row in cards if row.get("knowledge_card_id")}
    if stage == "knowledge_consolidation":
        base["items"] = []
        for card in cards:
            support = []
            for eu_id in card.get("based_on_eu_ids", []):
                eu = eu_map.get(eu_id, {}); source = source_map.get(eu.get("source_id"), {})
                support.append({"eu_id": eu_id, "source_id": eu.get("source_id"), "engineering_dimension": eu.get("engineering_dimension"), "finding": eu.get("finding"), "source_location": eu.get("source_location"), **source_links(source, stage_dir, project)})
            base["items"].append({"row_type": "review_item", "knowledge_card_id": card.get("knowledge_card_id"), "engineering_dimension": card.get("engineering_dimension"), "title": card.get("title"), "operational_question": card.get("operational_question"), "consolidated_finding": card.get("consolidated_finding"), "consolidation_type": card.get("consolidation_type"), "source_coverage_note": card.get("source_coverage_note"), "supporting_evidence": support, "knowledge_card_reading_view_link": "knowledge_cards.md", "evidence_unit_reading_view_link": "../02_evidence_extraction/evidence_units.md", "codex_decision": "retain as KC", "human_disposition": None, "faithfulness_score": None, "consolidation_appropriateness_score": None, "value_score": None, "notes": None, "required_action": None})
        navigation(stage_dir, source_map, project)
        return base
    if stage == "synthesis":
        syntheses = rows(stage_dir / "synthesis_cards.jsonl"); base["items"] = []
        for card in syntheses:
            support = []
            for eu_id in card.get("based_on_eu_ids", []):
                eu = eu_map.get(eu_id, {}); source = source_map.get(eu.get("source_id"), {})
                support.append({"record_id": eu_id, "record_type": "evidence_unit", "summary": eu.get("finding"), "source_location": eu.get("source_location"), **source_links(source, stage_dir, project)})
            for kc_id in card.get("based_on_knowledge_card_ids", []):
                kc = card_map.get(kc_id, {})
                support.append({"record_id": kc_id, "record_type": "knowledge_card", "summary": kc.get("consolidated_finding"), "source_location": None, "source_pdf_link": None, "source_text_link": None})
            base["items"].append({"row_type": "review_item", "synthesis_card_id": card.get("synthesis_card_id"), "primary_pattern": card.get("primary_pattern"), "secondary_lenses": card.get("secondary_lenses", []), "title": card.get("title"), "operational_question": card.get("operational_question"), "synthesis_claim": card.get("synthesis_claim"), "scope_and_conditions": card.get("scope_and_conditions"), "analysis_chain": card.get("analysis_chain"), "supporting_evidence": support, "uncertainty_or_exception": card.get("uncertainty_or_exception"), "operational_implication": card.get("operational_implication"), "evidence_depth": card.get("evidence_depth"), "source_verification_note": card.get("source_verification_note"), "synthesis_card_reading_view_link": "synthesis_cards.md", "codex_decision": "retain as Synthesis Card", "human_disposition": None, "faithfulness_score": None, "reasoning_soundness_score": None, "value_score": None, "notes": None, "required_action": None})
        navigation(stage_dir, source_map, project)
        return base
    if stage == "indexing":
        raise ValueError("Define simple benchmark questions first in 05_indexing/human_review.json; a script must not invent semantic evaluation questions.")
    reports = sorted(stage_dir.glob("*.md")); report = next((p for p in reports if p.name != "stage_summary.md"), None)
    base["items"] = [{"row_type": "report_review", "report_id": report.stem if report else "report", "report_title": report.stem.replace("_", " ").title() if report else "Report", "report_file_link": report.name if report else "<report>.md", "claim_evidence_map_link": "claim_evidence_map.jsonl", "report_scope": "Review the whole report for its stated intended use.", "codex_decision": "generated from validated structured knowledge", "faithfulness_score": None, "readability_score": None, "value_score": None, "notes": None, "required_action": None}]
    return base


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--stage", choices=STAGES, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    output = args.run_dir / STAGES[args.stage] / "human_review.json"
    if output.exists() and not args.overwrite:
        raise SystemExit(f"refusing to overwrite review workpaper: {output}; use --overwrite only before human scoring")
    output.write_text(json.dumps(payload_for(args.run_dir, args.stage), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
