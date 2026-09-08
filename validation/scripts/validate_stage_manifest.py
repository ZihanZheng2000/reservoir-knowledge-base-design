"""Validate a stage manifest and its declared run artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STAGE_FOLDERS = {
    "source_acquisition": "01_source_acquisition",
    "evidence_extraction": "02_evidence_extraction",
    "knowledge_consolidation": "03_knowledge_consolidation",
    "synthesis": "04_synthesis",
    "indexing": "05_indexing",
    "report_generation": "06_report_generation",
}
REVIEW_REQUIRED_FIELDS = {
    "source_acquisition": {"source_id", "codex_use", "codex_tier", "human_use", "human_tier"},
    "evidence_extraction": {"eu_id", "engineering_dimension", "source_pdf_link", "source_text_link", "codex_decision", "human_disposition", "faithfulness_score", "relevance_score", "value_score"},
    "knowledge_consolidation": {"knowledge_card_id", "engineering_dimension", "title", "consolidated_finding", "consolidation_type", "supporting_evidence", "codex_decision", "human_disposition", "faithfulness_score", "consolidation_appropriateness_score", "value_score"},
    "synthesis": {"synthesis_card_id", "primary_pattern", "title", "synthesis_claim", "scope_and_conditions", "analysis_chain", "supporting_evidence", "uncertainty_or_exception", "operational_implication", "codex_decision", "human_disposition", "faithfulness_score", "reasoning_soundness_score", "value_score"},
    "indexing": {"query_id", "benchmark_question", "gold_index_record_ids", "expected_answer_points", "retrieval_depth", "codex_retrieval_status", "codex_returned_index_record_ids", "source_adequacy_score"},
    "report_generation": {"report_id", "report_file_link", "claim_evidence_map_link", "codex_decision", "faithfulness_score", "readability_score", "value_score"},
}
REQUIRED = {
    "run_id", "stage", "workflow_version", "status", "inputs", "outputs",
    "automated_validation", "human_review", "cleanup", "warnings", "unresolved_issues",
    "downstream_readiness",
}


def safe_path(run_dir: Path, relative_path: str) -> Path | None:
    candidate = Path(relative_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    return run_dir / candidate


def validate_review_link(run_dir: Path, stage_dir: Path, value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"human_review.json missing {label}")
        return
    target = (stage_dir / value).resolve()
    try:
        target.relative_to(run_dir.resolve())
    except ValueError:
        errors.append(f"human_review.json {label} leaves the run directory: {value}")
        return
    if not target.is_file():
        errors.append(f"human_review.json {label} does not resolve to a file: {value}")


def validate(manifest_path: Path, run_dir: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"error_count": 1, "warning_count": 0, "errors": [f"cannot read manifest: {exc}"], "warnings": []}
    if not isinstance(manifest, dict):
        return {"error_count": 1, "warning_count": 0, "errors": ["stage manifest must be a JSON object"], "warnings": []}

    missing = REQUIRED - manifest.keys()
    if missing:
        errors.append(f"missing fields: {sorted(missing)}")
    stage = manifest.get("stage")
    stage_folder = STAGE_FOLDERS.get(stage)
    if stage_folder is None:
        errors.append(f"invalid stage: {stage}")
    elif manifest_path.parent.name != stage_folder:
        errors.append(f"manifest must be located in {stage_folder}/")
    if manifest.get("run_id") != run_dir.name:
        errors.append("run_id does not match run directory name")

    for label in ("inputs", "outputs"):
        artifacts = manifest.get(label)
        if not isinstance(artifacts, list):
            errors.append(f"{label} must be a list")
            continue
        for index, artifact in enumerate(artifacts, 1):
            if not isinstance(artifact, dict):
                errors.append(f"{label}[{index}] must be an object")
                continue
            path = artifact.get("path")
            required = artifact.get("required")
            if not isinstance(path, str) or not path:
                errors.append(f"{label}[{index}] missing path")
                continue
            resolved = safe_path(run_dir, path)
            if resolved is None:
                errors.append(f"{label}[{index}] path must be a safe relative path: {path}")
            elif required is True and not resolved.exists():
                errors.append(f"required {label} artifact not found: {path}")
            elif required is False and not resolved.exists():
                warnings.append(f"optional {label} artifact not found: {path}")

    automated = manifest.get("automated_validation", {})
    if not isinstance(automated, dict):
        errors.append("automated_validation must be an object")
    else:
        expected_second = "acquisition_success" if stage == "source_acquisition" else "traceability_integrity"
        first = automated.get("schema_conformance", {})
        second = automated.get("traceability_or_acquisition", {})
        if not isinstance(first, dict) or first.get("name") != "schema_conformance":
            errors.append("automated_validation missing schema_conformance indicator")
        if not isinstance(second, dict) or second.get("name") != expected_second:
            errors.append(f"automated_validation requires {expected_second} indicator")
        validation_path = automated.get("artifact_path")
        resolved = safe_path(run_dir, validation_path) if isinstance(validation_path, str) else None
        if resolved is None or not resolved.is_file():
            errors.append("automated validation artifact_path does not resolve to a file")

    review = manifest.get("human_review", {})
    if not isinstance(review, dict):
        errors.append("human_review must be an object")
    else:
        review_path = review.get("artifact_path")
        resolved = safe_path(run_dir, review_path) if isinstance(review_path, str) else None
        expected_review_path = f"{stage_folder}/human_review.json" if stage_folder else None
        if resolved is None or not resolved.is_file():
            errors.append("human review artifact_path does not resolve to a file")
        elif review_path != expected_review_path:
            errors.append("human review artifact_path must be the stage's human_review.json")
        else:
            try:
                review_payload = json.loads(resolved.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"cannot read human_review.json: {exc}")
                review_payload = {}
            rows = review_payload.get("items") if isinstance(review_payload, dict) else None
            if not isinstance(review_payload, dict) or not isinstance(review_payload.get("review_status"), str):
                errors.append("human_review.json must contain a review_status string")
            if not isinstance(rows, list) or not rows:
                errors.append("human_review.json must contain prefilled review items")
            elif not all(isinstance(row, dict) for row in rows):
                errors.append("human_review.json items must be objects")
            else:
                actual_fields = set().union(*(set(row) for row in rows))
                missing_fields = REVIEW_REQUIRED_FIELDS.get(stage, set()) - actual_fields
                if missing_fields:
                    errors.append(f"human_review.json missing required item fields: {sorted(missing_fields)}")
                if stage in {"evidence_extraction", "knowledge_consolidation", "synthesis"}:
                    navigation = manifest_path.parent / "source_navigation.md"
                    if not navigation.is_file():
                        errors.append("source_navigation.md is required for this stage")
                for row_number, row in enumerate(rows, 1):
                    disposition = row.get("human_disposition")
                    if disposition not in {None, "", "accept", "revise", "reject"}:
                        errors.append(f"human_review.json row {row_number} has invalid human_disposition: {disposition!r}")
                    if stage == "evidence_extraction":
                        validate_review_link(run_dir, manifest_path.parent, row.get("source_pdf_link"), f"row {row_number} source_pdf_link", errors)
                        validate_review_link(run_dir, manifest_path.parent, row.get("source_text_link"), f"row {row_number} source_text_link", errors)
                    if stage in {"knowledge_consolidation", "synthesis"}:
                        for evidence_index, evidence in enumerate(row.get("supporting_evidence") or [], 1):
                            if evidence.get("record_type") == "knowledge_card":
                                continue
                            validate_review_link(run_dir, manifest_path.parent, evidence.get("source_pdf_link"), f"row {row_number} supporting_evidence {evidence_index} source_pdf_link", errors)
                            validate_review_link(run_dir, manifest_path.parent, evidence.get("source_text_link"), f"row {row_number} supporting_evidence {evidence_index} source_text_link", errors)
                if stage == "report_generation":
                    validate_review_link(run_dir, manifest_path.parent, rows[0].get("report_file_link"), "report_file_link", errors)

    cleanup = manifest.get("cleanup", {})
    if not isinstance(cleanup, dict) or cleanup.get("status") not in {"not_run", "completed", "skipped"}:
        errors.append("cleanup must record a valid status")
    elif not isinstance(cleanup.get("removed_paths"), list):
        errors.append("cleanup.removed_paths must be a list")

    summary_path = manifest_path.parent / "stage_summary.md"
    if not summary_path.is_file():
        errors.append("stage_summary.md is missing from the stage folder")

    return {
        "stage": stage,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "status": "fail" if errors else "warning" if warnings else "pass",
    }


def merge_with_automated_result(stage_result: dict[str, Any], result_path: Path) -> dict[str, Any]:
    """Include stage-delivery checks in the existing two-indicator result."""
    try:
        result = json.loads(result_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "stage": stage_result.get("stage"),
            "error_count": stage_result["error_count"] + 1,
            "warning_count": stage_result["warning_count"],
            "errors": [f"cannot read primary automated result: {exc}", *stage_result["errors"]],
            "warnings": stage_result["warnings"],
            "status": "fail",
            "automated_validation": {},
        }
    if not isinstance(result, dict):
        raise ValueError("primary automated result must be a JSON object")

    result_errors = result.get("errors", [])
    result_warnings = result.get("warnings", [])
    if not isinstance(result_errors, list):
        result_errors = []
    if not isinstance(result_warnings, list):
        result_warnings = []
    combined_errors = [*result_errors, *(f"stage delivery: {message}" for message in stage_result["errors"])]
    combined_warnings = [*result_warnings, *(f"stage delivery: {message}" for message in stage_result["warnings"])]

    automated = result.get("automated_validation")
    if not isinstance(automated, dict):
        automated = {}
    schema = automated.get("schema_conformance")
    if isinstance(schema, dict):
        schema = dict(schema)
        schema["issue_count"] = int(schema.get("issue_count", 0)) + stage_result["error_count"]
        if stage_result["error_count"]:
            schema["status"] = "fail"
        automated["schema_conformance"] = schema

    error_count = len(combined_errors)
    warning_count = len(combined_warnings)
    stated = str(result.get("status", "")).lower()
    result.update({
        "stage": result.get("stage", stage_result.get("stage")),
        "error_count": error_count,
        "warning_count": warning_count,
        "errors": combined_errors,
        "warnings": combined_warnings,
        "status": "fail" if error_count or stated == "fail" else "warning" if warning_count or stated == "warning" else "pass",
        "automated_validation": automated,
        "stage_delivery_checked": True,
    })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--automated-result", type=Path, help="Existing stage automated_validation.json to merge with delivery checks")
    args = parser.parse_args()
    result = validate(args.manifest, args.run_dir)
    if args.automated_result:
        result = merge_with_automated_result(result, args.automated_result)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
