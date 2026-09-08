"""Create an empty, non-overwriting six-stage reservoir run scaffold."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path


STAGES = ["01_source_acquisition", "02_evidence_extraction", "03_knowledge_consolidation", "04_synthesis", "05_indexing", "06_report_generation"]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", default="runs", type=Path)
    parser.add_argument("--reservoir-name", required=True)
    parser.add_argument("--reservoir-id", required=True)
    parser.add_argument("--reservoir-id-system", required=True)
    parser.add_argument("--run-date", default=date.today().isoformat())
    parser.add_argument("--scope", required=True)
    parser.add_argument("--intended-use", default="case study")
    parser.add_argument(
        "--run-id-suffix",
        default="",
        help="Extra suffix to disambiguate a same-day run for the same reservoir, e.g. 'smoke2' -> <slug>_<date>_smoke2.",
    )
    args = parser.parse_args()
    run_id = f"{slug(args.reservoir_name)}_{args.run_date.replace('-', '')}"
    if args.run_id_suffix:
        run_id = f"{run_id}_{slug(args.run_id_suffix)}"
    run_dir = args.runs_dir / run_id
    if run_dir.exists():
        raise SystemExit(f"refusing to overwrite existing run: {run_dir}")
    for stage in STAGES:
        (run_dir / stage).mkdir(parents=True)
    (run_dir / "validation").mkdir()
    manifest = {
        "run_id": run_id, "reservoir_id": args.reservoir_id,
        "reservoir_id_system": args.reservoir_id_system,
        "reservoir_name": args.reservoir_name, "basin_or_system": "",
        "run_date": args.run_date, "workflow_version": "v0.2",
        "case_role": args.intended_use,
        "skills": {"source_acquisition": "source-acquisition", "evidence_extraction": "evidence-extraction", "knowledge_consolidation": "knowledge-consolidation", "synthesis": "synthesis", "indexing": "indexing", "report_generation": "report-generation"},
        "inputs": {"source_scope": args.scope, "seed_sources": [], "search_queries": []},
        "outputs": {"source_manifest": "01_source_acquisition/source_manifest.json", "candidate_inventory": "01_source_acquisition/sources/candidate_inventory.jsonl", "source_inventory": "01_source_acquisition/sources/source_inventory.jsonl", "evidence_units": "02_evidence_extraction/evidence_units.jsonl", "knowledge_cards": "03_knowledge_consolidation/knowledge_cards.jsonl", "synthesis_cards": "04_synthesis/synthesis_cards.jsonl", "encoded_knowledge_records": "05_indexing/encoded_knowledge_records.jsonl", "validation_summary": "validation/run_validation_summary.json", "report": "06_report_generation/"},
        "human_review": {"required_for_this_run": False, "stage_review_filename": "human_review.json"},
        "notes": "Created by run-orchestration bootstrap; complete source plan before Stage 1."
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
