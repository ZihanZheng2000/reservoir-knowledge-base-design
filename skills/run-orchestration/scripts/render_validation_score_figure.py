"""Render a six-panel validation score overview for one workflow run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from build_cross_stage_summary import STAGES, build_summary


STAGE_TITLES = {
    "source_acquisition": "Source acquisition",
    "evidence_extraction": "Evidence extraction",
    "knowledge_consolidation": "Knowledge consolidation",
    "synthesis": "Synthesis",
    "indexing": "Indexing",
    "report_generation": "Report generation",
}

METRIC_COLORS = {
    "schema conformance": "#6B8FB3",
    "traceability integrity": "#86A7C2",
    "acquisition success": "#86A7C2",
    "precision": "#D7A26A",
    "recall": "#C78B7A",
    "source adequacy": "#C9A85D",
    "faithfulness": "#D08B6B",
    "relevance": "#C9977E",
    "value": "#BFA56A",
    "consolidation appropriateness": "#C47C73",
    "reasoning soundness": "#B9897A",
    "readability": "#B79A7E",
}

HUMAN_SCORE_FIELDS = {
    "evidence_extraction": ("faithfulness_score", "relevance_score", "value_score"),
    "knowledge_consolidation": ("faithfulness_score", "consolidation_appropriateness_score", "value_score"),
    "synthesis": ("faithfulness_score", "reasoning_soundness_score", "value_score"),
    "report_generation": ("faithfulness_score", "readability_score", "value_score"),
}


def read_review(run_dir: Path, stage: str) -> dict[str, Any]:
    stage_folder = STAGES[stage][0]
    path = run_dir / stage_folder / "human_review.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def mean(values: list[int | float]) -> float:
    return sum(values) / len(values) if values else 0.0


def score_values(review: dict[str, Any], field: str) -> list[int]:
    return [
        item[field]
        for item in review.get("items", [])
        if isinstance(item, dict) and isinstance(item.get(field), int) and item[field] in {0, 1, 2}
    ]


def automated_metrics(stage_result: dict[str, Any]) -> list[tuple[str, float]]:
    checks = stage_result.get("automated_validation", {})
    rows = []
    for key in ("schema_conformance", "traceability_or_acquisition"):
        check = checks.get(key, {})
        if not isinstance(check, dict):
            continue
        name = str(check.get("name", key)).replace("_", " ")
        rows.append((name, 1.0 if check.get("status") == "pass" else 0.0))
    return rows


def human_metrics(stage: str, review: dict[str, Any], stage_result: dict[str, Any]) -> list[tuple[str, float]]:
    metrics = stage_result.get("human_review", {}).get("metrics", {})
    if stage == "source_acquisition":
        adequacy = (review.get("run_level_metrics") or {}).get("source_adequacy_score")
        return [
            ("precision", float(metrics.get("precision", {}).get("ratio", 0.0))),
            ("recall", float(metrics.get("recall", {}).get("ratio", 0.0))),
            ("source adequacy", float(adequacy) / 2 if adequacy in {0, 1, 2} else 0.0),
        ]
    if stage == "indexing":
        adequacy = score_values(review, "source_adequacy_score")
        return [
            ("precision", float(metrics.get("precision", {}).get("mean_ratio", 0.0))),
            ("recall", float(metrics.get("recall", {}).get("mean_ratio", 0.0))),
            ("source adequacy", mean(adequacy) / 2),
        ]
    rows = []
    for field in HUMAN_SCORE_FIELDS.get(stage, ()):
        label = field.removesuffix("_score").replace("_", " ")
        rows.append((label, mean(score_values(review, field)) / 2))
    return rows


def short_label(label: str) -> str:
    return {
        "schema conformance": "schema",
        "traceability integrity": "traceability",
        "acquisition success": "acquisition",
        "source adequacy": "source\nadequacy",
        "faithfulness": "faithful",
        "relevance": "relevant",
        "consolidation appropriateness": "consol.",
        "reasoning soundness": "reasoning",
        "readability": "readable",
    }.get(label, label.replace(" ", "\n") if len(label) > 11 else label)


def draw_panel(ax: Any, letter: str, stage: str, auto_rows: list[tuple[str, float]], human_rows: list[tuple[str, float]]) -> None:
    rows = [("Auto", *row) for row in auto_rows] + [("Human", *row) for row in human_rows]
    gap_after_auto = 0.55
    x_positions = []
    for index, row in enumerate(rows):
        x_positions.append(index + (gap_after_auto if row[0] == "Human" else 0))

    colors = [METRIC_COLORS.get(label, "#94A3B8") for _, label, _ in rows]
    values = [value for _, _, value in rows]
    labels = [short_label(label) for _, label, _ in rows]
    ax.bar(x_positions, values, color=colors, width=0.68)

    for x, value in zip(x_positions, values):
        ax.text(x, min(value + 0.045, 1.25), f"{value:.2f}", ha="center", va="bottom", fontsize=22)

    split = len(auto_rows) - 0.5 + gap_after_auto / 2
    ax.axvline(split, color="#CBD5E1", linewidth=1)
    ax.set_title(f"{letter}) {STAGE_TITLES[stage]}", loc="left", fontsize=24, fontweight="bold", pad=14)
    ax.set_ylim(0, 1.35)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels, fontsize=22)
    ax.set_yticks([0, 0.5, 1.0])
    ax.set_yticklabels(["0", "0.5", "1.0"], fontsize=22)
    ax.grid(axis="y", color="#E2E8F0", linewidth=0.7)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#CBD5E1")
    ax.spines["bottom"].set_color("#CBD5E1")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if not args.run_dir.is_dir():
        parser.error(f"run directory does not exist: {args.run_dir}")

    summary = build_summary(args.run_dir)
    stages = list(STAGES)
    fig, axes = plt.subplots(3, 2, figsize=(22, 15), constrained_layout=True)
    for index, (ax, stage) in enumerate(zip(axes.flatten(), stages), start=1):
        review = read_review(args.run_dir, stage)
        stage_result = summary["stages"][stage]
        draw_panel(
            ax,
            chr(ord("a") + index - 1),
            stage,
            automated_metrics(stage_result),
            human_metrics(stage, review, stage_result),
        )

    fig.suptitle("Lake Powell Run Validation: Automated Checks and Human Review Metrics", fontsize=30, fontweight="bold")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=240, bbox_inches="tight")
    plt.close(fig)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


