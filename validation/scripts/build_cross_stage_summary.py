"""Build a six-stage automated-validation summary for one workflow run."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STAGES = {
    "source_acquisition": ("01_source_acquisition", ("source_acquisition_validation.json", "layer1_source_validation.json")),
    "evidence_extraction": ("02_evidence_extraction", ("evidence_extraction_validation.json", "layer2_ku_validation.json")),
    "knowledge_consolidation": ("03_knowledge_consolidation", ("knowledge_consolidation_validation.json",)),
    "synthesis": ("04_synthesis", ("synthesis_validation.json", "layer3_synthesis_validation.json")),
    "indexing": ("05_indexing", ("indexing_validation.json", "retrieval_validation.json")),
    "report_generation": ("06_report_generation", ("report_generation_validation.json", "report_validation.json")),
}
SCORE_COLUMNS = {
    "evidence_extraction": ("faithfulness_score", "relevance_score", "value_score"),
    "knowledge_consolidation": ("faithfulness_score", "consolidation_appropriateness_score", "value_score"),
    "synthesis": ("faithfulness_score", "reasoning_soundness_score", "value_score"),
    "report_generation": ("faithfulness_score", "readability_score", "value_score"),
}


def _count(payload: dict[str, Any], key: str) -> int:
    explicit = payload.get(f"{key}_count")
    if isinstance(explicit, int) and not isinstance(explicit, bool):
        return max(explicit, 0)
    values = payload.get(f"{key}s", [])
    return len(values) if isinstance(values, list) else 0


def _status(payload: dict[str, Any], errors: int, warnings: int) -> str:
    stated = str(payload.get("status", "")).lower()
    if errors or stated in {"fail", "failed", "invalid", "error"} or payload.get("passed") is False:
        return "fail"
    if warnings or stated in {"warning", "pass_with_warnings"}:
        return "warning"
    return "pass"


def _find(run_dir: Path, stage_folder: str, legacy_names: tuple[str, ...]) -> Path | None:
    stage_result = run_dir / stage_folder / "automated_validation.json"
    if stage_result.is_file():
        return stage_result
    validation_dir = run_dir / "validation"
    return next((validation_dir / name for name in legacy_names if (validation_dir / name).is_file()), None)


def _numeric_scores(rows: list[dict[str, str]], column: str) -> tuple[list[int], list[str]]:
    scores: list[int] = []
    errors: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        raw_value = row.get(column)
        if raw_value is None or raw_value == "":
            continue
        value = str(raw_value).strip().translate(str.maketrans("０１２", "012"))
        if value not in {"0", "1", "2"}:
            errors.append(f"row {row_number} has invalid {column}: {raw_value!r}; use 0, 1, or 2")
        else:
            scores.append(int(value))
    return scores, errors


def _human_review(run_dir: Path, stage: str, stage_folder: str) -> dict[str, Any]:
    manifest_path = run_dir / stage_folder / "stage_manifest.json"
    review: dict[str, Any] = {}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        review = manifest.get("human_review", {})
        if isinstance(review, dict):
            result: dict[str, Any] = {"status": review.get("status", "not_reviewed"), "artifact": review.get("artifact_path")}
        else:
            result = {"status": "not_reviewed", "artifact": None}
    except (OSError, ValueError, json.JSONDecodeError):
        result = {"status": "not_reviewed", "artifact": None}

    artifact = result.get("artifact")
    review_path = run_dir / artifact if isinstance(artifact, str) else None
    if review_path is None or not review_path.is_file():
        return result
    try:
        if review_path.suffix.lower() == ".json":
            review_payload = json.loads(review_path.read_text(encoding="utf-8-sig"))
            if not isinstance(review_payload, dict) or not isinstance(review_payload.get("items"), list):
                raise ValueError("human review JSON must contain an items array")
            rows = [row for row in review_payload["items"] if isinstance(row, dict)]
            result["status"] = review_payload.get("review_status", result["status"])
            if stage == "source_acquisition":
                run_metrics = review_payload.get("run_level_metrics", {})
                if isinstance(run_metrics, dict):
                    rows.append({"row_type": "run_metric", **run_metrics})
        else:
            with review_path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
    except (OSError, ValueError, json.JSONDecodeError, csv.Error) as exc:
        result["validation_errors"] = [f"cannot read human review: {exc}"]
        return result

    statuses = {(row.get("review_status") or "").strip() for row in rows if (row.get("review_status") or "").strip()}
    if len(statuses) == 1:
        result["status"] = statuses.pop()
    elif len(statuses) > 1:
        result["status"] = "in_progress"
        result["validation_errors"] = ["review_status values are inconsistent across rows"]

    metrics: dict[str, Any] = {}
    validation_errors: list[str] = list(result.get("validation_errors", []))
    if stage == "source_acquisition":
        source_rows = [row for row in rows if (row.get("row_type") or "").strip() == "source_decision"]
        for row_number, row in enumerate(rows, start=2):
            row_type = (row.get("row_type") or "").strip()
            codex_use = (row.get("codex_use") or "").strip().upper()
            human_use = (row.get("human_use") or "").strip().upper()
            human_tier = (row.get("human_tier") or "").strip().upper()
            if row_type == "source_decision" and codex_use not in {"Y", "N"}:
                validation_errors.append(f"row {row_number} has invalid codex_use: {codex_use!r}; use Y or N")
            if row_type == "source_decision" and human_use:
                if human_use not in {"Y", "N"}:
                    validation_errors.append(f"row {row_number} has invalid human_use: {human_use!r}; use Y or N")
                elif human_use == "Y" and human_tier not in {"A", "B", "C"}:
                    validation_errors.append(f"row {row_number} has human_use Y but no human_tier A, B, or C")
                elif human_use == "N" and human_tier:
                    validation_errors.append(f"row {row_number} has human_use N but also a human_tier")
        reviewed = [row for row in source_rows if (row.get("human_use") or "").upper() in {"Y", "N"}]
        codex_selected = [row for row in reviewed if (row.get("codex_use") or "").upper() == "Y"]
        human_in_scope = [row for row in reviewed if (row.get("human_use") or "").upper() == "Y"]
        true_positives = [row for row in codex_selected if (row.get("human_use") or "").upper() == "Y"]
        if codex_selected:
            metrics["precision"] = {
                "reviewed_count": len(codex_selected),
                "ratio": len(true_positives) / len(codex_selected),
                "definition": "human-in-scope Codex selections / reviewed Codex selections",
            }
        if human_in_scope:
            metrics["recall"] = {
                "reviewed_count": len(human_in_scope),
                "ratio": len(true_positives) / len(human_in_scope),
                "definition": "human-in-scope Codex selections / reviewed human-in-scope sources in the candidate inventory",
            }
        adequacy, errors = _numeric_scores(rows, "source_adequacy_score")
        validation_errors.extend(errors)
        if adequacy:
            metrics["source_adequacy"] = {"reviewed_count": len(adequacy), "mean_score": sum(adequacy) / len(adequacy)}
    elif stage == "indexing":
        recall_values: list[float] = []
        precision_values: list[float] = []
        for row_number, row in enumerate(rows, start=2):
            if str(row.get("codex_retrieval_status", "")).strip().lower() != "completed":
                continue
            gold = row.get("gold_index_record_ids")
            supporting = row.get("acceptable_supporting_index_record_ids", [])
            returned = row.get("codex_returned_index_record_ids")
            if not isinstance(gold, list) or not all(isinstance(item, str) and item for item in gold):
                validation_errors.append(f"row {row_number} needs a nonempty gold_index_record_ids array")
                continue
            if not isinstance(supporting, list) or not all(isinstance(item, str) and item for item in supporting):
                validation_errors.append(f"row {row_number} has invalid acceptable_supporting_index_record_ids")
                continue
            if not isinstance(returned, list) or not all(isinstance(item, str) and item for item in returned):
                validation_errors.append(f"row {row_number} has invalid codex_returned_index_record_ids")
                continue
            gold_set = set(gold)
            returned_set = set(returned)
            relevant_set = gold_set | set(supporting)
            recall_values.append(len(gold_set & returned_set) / len(gold_set))
            precision_values.append(sum(record_id in relevant_set for record_id in returned) / len(returned) if returned else 0.0)
        if recall_values:
            metrics["recall"] = {"reviewed_count": len(recall_values), "mean_ratio": sum(recall_values) / len(recall_values)}
            metrics["precision"] = {"reviewed_count": len(precision_values), "mean_ratio": sum(precision_values) / len(precision_values)}
        adequacy, errors = _numeric_scores(rows, "source_adequacy_score")
        validation_errors.extend(errors)
        if adequacy:
            mean = sum(adequacy) / len(adequacy)
            metrics["source_adequacy"] = {"reviewed_count": len(adequacy), "mean_score": mean}
    else:
        for column in SCORE_COLUMNS.get(stage, ()):
            scores, errors = _numeric_scores(rows, column)
            validation_errors.extend(errors)
            if scores:
                mean = sum(scores) / len(scores)
                metrics[column.removesuffix("_score")] = {"reviewed_count": len(scores), "mean_score": mean}
    result["metrics"] = metrics
    if validation_errors:
        result["validation_errors"] = validation_errors
    return result


def build_summary(run_dir: Path) -> dict[str, Any]:
    stages: dict[str, dict[str, Any]] = {}
    for stage, (stage_folder, legacy_names) in STAGES.items():
        artifact = _find(run_dir, stage_folder, legacy_names)
        human_review = _human_review(run_dir, stage, stage_folder)
        if artifact is None:
            stages[stage] = {"status": "not_run", "artifact": None, "human_review": human_review, "error_count": 0, "warning_count": 0, "automated_validation": {}}
            continue
        try:
            payload = json.loads(artifact.read_text(encoding="utf-8-sig"))
            if not isinstance(payload, dict):
                raise ValueError("top-level JSON must be an object")
            errors, warnings = _count(payload, "error"), _count(payload, "warning")
            stages[stage] = {
                "status": _status(payload, errors, warnings),
                "artifact": artifact.relative_to(run_dir).as_posix(),
                "human_review": human_review,
                "error_count": errors,
                "warning_count": warnings,
                "automated_validation": payload.get("automated_validation", {}),
            }
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            stages[stage] = {"status": "fail", "artifact": artifact.relative_to(run_dir).as_posix(), "human_review": human_review, "error_count": 1, "warning_count": 0, "automated_validation": {}, "summary_read_error": str(exc)}

    counts = {
        "stages_passed": sum(item["status"] == "pass" for item in stages.values()),
        "stages_with_warnings": sum(item["status"] == "warning" for item in stages.values()),
        "stages_failed": sum(item["status"] == "fail" for item in stages.values()),
        "stages_not_run": sum(item["status"] == "not_run" for item in stages.values()),
        "errors": sum(item["error_count"] for item in stages.values()),
        "warnings": sum(item["warning_count"] for item in stages.values()),
    }
    overall = "fail" if counts["stages_failed"] else "incomplete" if counts["stages_not_run"] else "warning" if counts["stages_with_warnings"] else "pass"
    return {"schema_version": "2.0", "run_id": run_dir.name, "generated_at": datetime.now(timezone.utc).isoformat(), "overall_status": overall, "stages": stages, "totals": counts}


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Run Validation Summary",
        "",
        f"- Run ID: {summary['run_id']}",
        f"- Overall automated status: {summary['overall_status']}",
        "",
        "| Stage | Automated status | Errors | Warnings | Human review |",
        "|---|---|---:|---:|---|",
    ]
    for stage, item in summary["stages"].items():
        lines.append(f"| {stage.replace('_', ' ')} | {item['status']} | {item['error_count']} | {item['warning_count']} | {item['human_review']['status']} |")
    human_metrics = [(stage, item["human_review"].get("metrics", {})) for stage, item in summary["stages"].items() if item["human_review"].get("metrics")]
    if human_metrics:
        lines.extend(["", "## Human review metrics", ""])
        for stage, metrics in human_metrics:
            lines.extend([f"### {stage.replace('_', ' ')}", "", "| Metric | Reviewed units | Mean / ratio |", "|---|---:|---:|"])
            for metric, values in metrics.items():
                mean_or_ratio = values.get("mean_score", values.get("mean_ratio", values.get("ratio")))
                lines.append(f"| {metric.replace('_', ' ')} | {values['reviewed_count']} | {mean_or_ratio:.2f} |")
    lines.extend([
        "",
        "Each stage contains its own `automated_validation.json` and `human_review.json`.",
        "This directory contains only this run-level summary.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--out-md", type=Path, help="Optional human-readable Markdown summary")
    args = parser.parse_args()
    if not args.run_dir.is_dir():
        parser.error(f"run directory does not exist: {args.run_dir}")
    summary = build_summary(args.run_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary["totals"], indent=2))
    return 1 if summary["overall_status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
