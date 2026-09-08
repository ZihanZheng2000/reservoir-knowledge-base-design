"""Remove allowlisted execution intermediates after a successful stage run."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


STAGE_FOLDERS = {
    "source_acquisition": "01_source_acquisition",
    "evidence_extraction": "02_evidence_extraction",
    "knowledge_consolidation": "03_knowledge_consolidation",
    "synthesis": "04_synthesis",
    "indexing": "05_indexing",
    "report_generation": "06_report_generation",
}
INTERMEDIATES = {
    "source_acquisition": ["deep_discovery", "sources/parsed_docling", "sources/docling_parse_manifest.jsonl", "sources/source_inventory.csv", "work"],
    "evidence_extraction": ["extraction_packets.jsonl", "source_inventory_eu_ready.jsonl", "evidence_units_preview.md", "evidence_units_summary.json", "work"],
    "knowledge_consolidation": ["work"],
    "synthesis": ["work"],
    "indexing": ["work"],
    "report_generation": ["work"],
}


def load_manifest(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("stage manifest must be a JSON object")
    return payload


def is_ready(manifest: dict) -> bool:
    if manifest.get("status") not in {"completed", "completed_with_warnings"}:
        return False
    automated = manifest.get("automated_validation", {})
    if not isinstance(automated, dict):
        return False
    indicators = [automated.get("schema_conformance", {}), automated.get("traceability_or_acquisition", {})]
    return all(isinstance(indicator, dict) and indicator.get("status") != "fail" for indicator in indicators)


def targets_for(run_dir: Path, stage: str) -> list[Path]:
    stage_dir = (run_dir / STAGE_FOLDERS[stage]).resolve()
    return [(stage_dir / relative).resolve() for relative in INTERMEDIATES[stage]]


def safe_target(stage_dir: Path, target: Path) -> bool:
    try:
        target.relative_to(stage_dir)
        return target != stage_dir
    except ValueError:
        return False


def update_summary_cleanup(summary_path: Path, removed: list[str]) -> None:
    text = summary_path.read_text(encoding="utf-8")
    removed_text = ", ".join(f"`{path}`" for path in removed) if removed else "none"
    replacement = "## 6. Cleanup\n\n- Status: completed\n- Removed intermediate paths: " + removed_text
    updated, count = re.subn(
        r"## 6\. Cleanup\r?\n\r?\n- Status:.*?\r?\n- Removed intermediate paths:.*?(?=\r?\n\r?\n## 7\.)",
        replacement,
        text,
        flags=re.DOTALL,
    )
    if count != 1:
        raise ValueError("stage_summary.md does not contain the required Cleanup section")
    summary_path.write_text(updated, encoding="utf-8")


def finalize_stage(run_dir: Path, stage: str, apply: bool) -> dict:
    stage_dir = (run_dir / STAGE_FOLDERS[stage]).resolve()
    manifest_path = stage_dir / "stage_manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"missing stage manifest: {manifest_path}")
    manifest = load_manifest(manifest_path)
    if manifest.get("stage") != stage:
        raise ValueError(f"manifest stage does not match requested stage: {stage}")
    if not is_ready(manifest):
        raise ValueError(f"stage is not eligible for cleanup: {stage}")

    existing = [target for target in targets_for(run_dir, stage) if target.exists()]
    for target in existing:
        if not safe_target(stage_dir, target):
            raise ValueError(f"unsafe cleanup target: {target}")
    removed = [target.relative_to(run_dir).as_posix() for target in existing]
    if apply:
        for target in existing:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        removed_set = set(removed)

        def was_removed(path: str) -> bool:
            return path in removed_set or any(path == r or path.startswith(f"{r}/") for r in removed_set)

        downgraded = []
        for output in manifest.get("outputs", []):
            if isinstance(output, dict) and isinstance(output.get("path"), str) and was_removed(output["path"]) and output.get("required") is not False:
                output["required"] = False
                downgraded.append(output["path"])

        manifest["cleanup"] = {"status": "completed", "removed_paths": removed}
        if downgraded:
            manifest["cleanup"]["downgraded_to_optional"] = downgraded
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        update_summary_cleanup(stage_dir / "stage_summary.md", removed)
    return {"stage": stage, "mode": "apply" if apply else "dry_run", "candidate_paths": removed, "removed_paths": removed if apply else []}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--stage", choices=[*STAGE_FOLDERS, "all"], required=True)
    parser.add_argument("--apply", action="store_true", help="Perform deletion; omit for dry-run output.")
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        parser.error(f"run directory does not exist: {run_dir}")
    stages = list(STAGE_FOLDERS) if args.stage == "all" else [args.stage]
    results = []
    for stage in stages:
        try:
            results.append(finalize_stage(run_dir, stage, args.apply))
        except ValueError as exc:
            results.append({"stage": stage, "error": str(exc)})
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if any("error" in result for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
