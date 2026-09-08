"""Check that a completed run has every canonical artifact and delivery gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from validate_stage_manifest import validate as validate_stage_manifest


STAGES = {
    "01_source_acquisition": ["source_manifest.json", "sources/candidate_inventory.jsonl", "sources/source_inventory.jsonl", "sources/raw", "sources/text"],
    "02_evidence_extraction": ["evidence_units.jsonl", "evidence_units.md", "source_navigation.md"],
    "03_knowledge_consolidation": ["knowledge_cards.jsonl", "knowledge_cards.md", "source_navigation.md"],
    "04_synthesis": ["synthesis_cards.jsonl", "synthesis_cards.md", "source_navigation.md"],
    "05_indexing": ["encoded_knowledge_records.jsonl", "index_manifest.json"],
    "06_report_generation": ["claim_evidence_map.jsonl"],
}


def json_file(path: Path, errors: list[str], label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read {label}: {exc}")
        return {}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir
    errors: list[str] = []; warnings: list[str] = []
    manifest = json_file(run_dir / "run_manifest.json", errors, "run_manifest.json")
    for field in ("run_id", "reservoir_id", "reservoir_id_system", "reservoir_name", "run_date"):
        if not manifest.get(field): errors.append(f"run_manifest.json missing {field}")
    if manifest.get("run_id") and manifest.get("run_id") != run_dir.name:
        errors.append("run manifest run_id does not match folder name")
    for folder, artifacts in STAGES.items():
        stage_dir = run_dir / folder
        if not stage_dir.is_dir():
            errors.append(f"missing stage directory: {folder}"); continue
        for relative in artifacts:
            if not (stage_dir / relative).exists(): errors.append(f"missing required artifact: {folder}/{relative}")
        for standard in ("stage_manifest.json", "stage_summary.md", "automated_validation.json", "human_review.json"):
            if not (stage_dir / standard).is_file(): errors.append(f"missing standard delivery artifact: {folder}/{standard}")
        if (stage_dir / "stage_manifest.json").is_file():
            stage_result = validate_stage_manifest(stage_dir / "stage_manifest.json", run_dir)
            for message in stage_result["errors"]:
                errors.append(f"{folder} delivery contract: {message}")
        automated = json_file(stage_dir / "automated_validation.json", errors, f"{folder}/automated_validation.json")
        if automated.get("status") in {"fail", "failed"} or automated.get("error_count", 0):
            errors.append(f"automated validation not clean: {folder}")
    candidate_path = run_dir / "01_source_acquisition" / "sources" / "candidate_inventory.jsonl"
    if candidate_path.is_file():
        rows = [json.loads(line) for line in candidate_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        if not rows: errors.append("candidate_inventory.jsonl is empty")
        for index, row in enumerate(rows, 1):
            missing = {"candidate_id", "title", "url", "codex_use", "codex_tier", "codex_selection_reason"} - row.keys()
            if missing: errors.append(f"candidate inventory row {index} missing {sorted(missing)}")
    report_dir = run_dir / "06_report_generation"
    if not any(path.suffix == ".md" and path.name != "stage_summary.md" for path in report_dir.glob("*.md")):
        errors.append("report generation has no final Markdown report")
    result = {"run_id": run_dir.name, "status": "fail" if errors else "pass", "error_count": len(errors), "warning_count": len(warnings), "errors": errors, "warnings": warnings}
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors: raise SystemExit(1)


if __name__ == "__main__":
    main()
