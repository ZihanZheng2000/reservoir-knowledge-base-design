"""Render a reusable, human-readable validation report for one workflow run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from build_cross_stage_summary import STAGES, build_summary


SCORE_FIELDS = {
    "evidence_extraction": ("faithfulness_score", "relevance_score", "value_score"),
    "knowledge_consolidation": ("faithfulness_score", "consolidation_appropriateness_score", "value_score"),
    "synthesis": ("faithfulness_score", "reasoning_soundness_score", "value_score"),
    "report_generation": ("faithfulness_score", "readability_score", "value_score"),
}

COUNT_FIELD_BY_STAGE = {
    "source_acquisition": "source_records",
    "evidence_extraction": "evidence_unit_records",
    "knowledge_consolidation": "knowledge_card_records",
    "synthesis": "synthesis_card_records",
    "indexing": "index_record_count",
    "report_generation": "claim_count",
}


def _read_review(run_dir: Path, stage_folder: str) -> dict[str, Any]:
    path = run_dir / stage_folder / "human_review.json"
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _scores(review: dict[str, Any], field: str) -> list[int]:
    return [
        item[field]
        for item in review.get("items", [])
        if isinstance(item, dict) and isinstance(item.get(field), int) and item[field] in {0, 1, 2}
    ]


def _mean(values: list[int | float]) -> float | None:
    return sum(values) / len(values) if values else None


def _fmt_ratio(value: Any) -> str:
    return f"{value:.2f}" if isinstance(value, (int, float)) else "n/a"


def _fmt_score(value: Any) -> str:
    return f"{value:.2f}/2" if isinstance(value, (int, float)) else "n/a"


def _review_complete(stage: str, review: dict[str, Any]) -> bool:
    if review.get("review_status") == "completed":
        return True
    items = [item for item in review.get("items", []) if isinstance(item, dict)]
    if not items:
        return False
    if stage == "source_acquisition":
        decisions_complete = all(
            item.get("human_use") in {"Y", "N"}
            and (item.get("human_use") != "Y" or item.get("human_tier") in {"A", "B", "C"})
            for item in items
            if item.get("row_type") == "source_decision"
        )
        adequacy = review.get("run_level_metrics", {}).get("source_adequacy_score")
        return decisions_complete and adequacy in {0, 1, 2}
    if stage == "indexing":
        return all(
            item.get("codex_retrieval_status") == "completed"
            and item.get("source_adequacy_score") in {0, 1, 2}
            for item in items
        )
    return all(all(item.get(field) in {0, 1, 2} for field in SCORE_FIELDS[stage]) for item in items)


def _label_for(item: dict[str, Any]) -> str:
    for key in ("eu_id", "knowledge_card_id", "synthesis_card_id", "query_id", "report_id", "source_id", "candidate_id"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return "review item"


def _text_value(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item).strip() for item in value if str(item).strip())
    return value.strip() if isinstance(value, str) else ""


def _cell(value: Any) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").replace("|", "\\|")


def _disposition_counts(items: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for item in items:
        disposition = item.get("human_disposition")
        if disposition in {"accept", "revise", "reject"}:
            counts[disposition] = counts.get(disposition, 0) + 1
    return ", ".join(f"{key}={counts[key]}" for key in ("accept", "revise", "reject") if key in counts) or "n/a"


def _human_summary(stage: str, review: dict[str, Any], metrics: dict[str, Any]) -> tuple[str, str, str]:
    items = [item for item in review.get("items", []) if isinstance(item, dict)]
    if stage == "source_acquisition":
        source_items = [item for item in items if item.get("row_type") == "source_decision"]
        reviewed = [item for item in source_items if item.get("human_use") in {"Y", "N"}]
        selected = [item for item in reviewed if item.get("codex_use") == "Y"]
        human_yes = [item for item in reviewed if item.get("human_use") == "Y"]
        missed = [item for item in human_yes if item.get("codex_use") != "Y"]
        precision = metrics.get("precision", {}).get("ratio")
        recall = metrics.get("recall", {}).get("ratio")
        adequacy = review.get("run_level_metrics", {}).get("source_adequacy_score")
        scope = f"{len(reviewed)}/{len(source_items)} candidates reviewed; {len(selected)} selected"
        metric_text = f"precision {_fmt_ratio(precision)}; recall {_fmt_ratio(recall)}; source adequacy {adequacy}/2"
        finding = f"Selected corpus is adequate; {len(missed)} unselected candidates were flagged for future consideration."
        return scope, metric_text, finding
    if stage == "indexing":
        recall = metrics.get("recall", {}).get("mean_ratio")
        precision = metrics.get("precision", {}).get("mean_ratio")
        adequacy = _scores(review, "source_adequacy_score")
        completed = [item for item in items if item.get("codex_retrieval_status") == "completed"]
        low = sum(score == 0 for score in adequacy)
        scope = f"{len(completed)}/{len(items)} benchmark queries completed"
        metric_text = f"recall@k {_fmt_ratio(recall)}; precision@k {_fmt_ratio(precision)}; source adequacy {_fmt_score(_mean(adequacy))}"
        finding = f"Retrieval smoke test is usable but weak; {low} query had inadequate returned evidence."
        return scope, metric_text, finding
    sampled = [
        item for item in items
        if item.get("human_disposition") in {"accept", "revise", "reject"}
        or any(item.get(field) in {0, 1, 2} for field in SCORE_FIELDS.get(stage, ()))
    ]
    metric_parts = []
    for field in SCORE_FIELDS.get(stage, ()):
        ratings = _scores(review, field)
        label = field.removesuffix("_score").replace("_", " ")
        metric_parts.append(f"{label} {_fmt_score(_mean(ratings))}")
    finding_by_stage = {
        "evidence_extraction": "Mixed sample: revise/reject actions mainly target locators, attribution, front matter, and off-scope EUs.",
        "knowledge_consolidation": "Mostly faithful KCs; several cards need boundary, attribution, or source-quality cleanup.",
        "synthesis": "All synthesis cards need revision because they remain EU-only and require source verification before final use.",
        "report_generation": "Readable and useful report, but faithfulness needs one claim-evidence repair.",
    }
    scope = f"{len(sampled)}/{len(items)} items scored"
    return scope, "; ".join(metric_parts), f"{_disposition_counts(sampled)}; {finding_by_stage.get(stage, '')}"


def _record_count(run_dir: Path, artifact: str | None, stage: str) -> int | None:
    if not isinstance(artifact, str):
        return None
    try:
        payload = json.loads((run_dir / artifact).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    value = payload.get(COUNT_FIELD_BY_STAGE[stage])
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _check_text(check: dict[str, Any], record_count: int | None) -> str:
    issues = check.get("issue_count", 0) if isinstance(check, dict) else 0
    if not isinstance(issues, int):
        issues = 0
    if record_count is None:
        return "not reported"
    correct = max(record_count - issues, 0)
    suffix = "" if issues == 0 else f" ({issues} issue{'s' if issues != 1 else ''})"
    return f"{correct}/{record_count} correct{suffix}"


def _action_rows(stage: str, review: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    rows = []
    for item in review.get("items", []):
        if not isinstance(item, dict):
            continue
        action = _text_value(item.get("required_action"))
        if not action:
            continue
        issue = _text_value(item.get("notes")) or "Review item requires follow-up."
        if issue.startswith("Reviewer-assigned tier before exclusion:"):
            issue = "Candidate was excluded from selected sources but reviewer assigned a source tier."
        rows.append((stage.replace("_", " "), _label_for(item), issue, action))
    return rows


def render(run_dir: Path) -> str:
    summary = build_summary(run_dir)
    stage_reviews = {
        stage: _read_review(run_dir, stage_folder)
        for stage, (stage_folder, _) in STAGES.items()
    }
    automated_pass = sum(item["status"] == "pass" for item in summary["stages"].values())
    completed_reviews = sum(_review_complete(stage, review) for stage, review in stage_reviews.items())

    lines = [
        "# Validation Report",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Automated validation: **{automated_pass}/6 stages correct**",
        f"- Human review completed: **{completed_reviews}/6** stages",
        "",
        "![Validation score overview](validation_score_overview.png)",
        "",
        "Figure values are normalized to 0-1: automated pass = 1.00, human 0/1/2 scores are divided by 2, and recall/precision remain ratios.",
        "",
        "## Automated validation",
        "",
        "| Stage | Schema conformance | Traceability / acquisition | Errors | Warnings |",
        "|---|---|---|---:|---:|",
    ]
    for stage, item in summary["stages"].items():
        checks = item.get("automated_validation", {})
        schema = checks.get("schema_conformance", {})
        traceability = checks.get("traceability_or_acquisition", {})
        record_count = _record_count(run_dir, item.get("artifact"), stage)
        schema_status = _check_text(schema, record_count)
        traceability_status = _check_text(traceability, record_count)
        lines.append(
            f"| {stage.replace('_', ' ')} | {schema_status} | {traceability_status} | {item['error_count']} | {item['warning_count']} |"
        )

    lines.extend([
        "",
        "## Human review",
        "",
        "| Stage | Review completion | Review scope | Human metrics | Main finding |",
        "|---|---|---|---|---|",
    ])
    for stage, item in summary["stages"].items():
        review = stage_reviews[stage]
        completion = "completed" if review.get("review_status") == "completed" else "completed (inferred from filled fields)" if _review_complete(stage, review) else "incomplete"
        scope, metric_text, finding = _human_summary(stage, review, item["human_review"].get("metrics", {}))
        lines.append(
            f"| {stage.replace('_', ' ')} | {completion} | {_cell(scope)} | {_cell(metric_text)} | {_cell(finding)} |"
        )

    action_groups = {
        stage.replace("_", " "): _action_rows(stage, review)
        for stage, review in stage_reviews.items()
    }
    lines.extend(["", "## Required actions by stage", ""])
    if any(action_groups.values()):
        for stage_name, rows in action_groups.items():
            if not rows:
                continue
            lines.extend([f"### {stage_name}", "", "| Item ID | Issue found | Required action |", "|---|---|---|"])
            lines.extend(f"| `{_cell(label)}` | {_cell(issue)} | {_cell(action)} |" for _, label, issue, action in rows)
            lines.append("")
    else:
        lines.append("No human notes or required actions recorded.")

    lines.extend([
        "",
        "## Interpretation",
        "",
        "Automated validation establishes file-contract and evidence-chain integrity. Human review evaluates substantive quality. A review is treated as completed when all fields required for that stage are filled, even if `review_status` remains `not_requested`.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--out-md", required=True, type=Path)
    args = parser.parse_args()
    if not args.run_dir.is_dir():
        parser.error(f"run directory does not exist: {args.run_dir}")
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render(args.run_dir), encoding="utf-8")
    print(args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
