"""Render Evidence Unit JSONL into a human-readable Markdown view and summary JSON."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


DIMENSION_ORDER = [
    "Operation Purposes",
    "Multiple Objectives",
    "Storage Capacity and Storage Targets",
    "Operation Rules",
    "Emergency Operations",
    "Real-Time Operations",
    "Regulation / Governance",
    "Uncertainty and Risk Management",
    "Observation and Data",
    "Inflow Forecast",
    "Modeling",
    "Stakeholders",
    "Operation Failure",
]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def render(evidence_units: list[dict], title: str) -> str:
    counts = Counter(row.get("engineering_dimension") for row in evidence_units)
    lines = [
        f"# {title}",
        "",
        f"Total Evidence Units: {len(evidence_units)}",
        f"Sources represented: {len({row.get('source_id') for row in evidence_units if row.get('source_id')})}",
        "",
        "## Dimension Counts",
        "",
        "| Dimension | Count |",
        "|---|---:|",
    ]
    known = set(DIMENSION_ORDER)
    for dim in DIMENSION_ORDER:
        if counts.get(dim):
            lines.append(f"| {dim} | {counts[dim]} |")
    for dim, count in sorted(counts.items()):
        if dim not in known:
            lines.append(f"| {dim or 'missing'} | {count} |")

    for dim in DIMENSION_ORDER:
        subset = [row for row in evidence_units if row.get("engineering_dimension") == dim]
        if not subset:
            continue
        lines.extend(["", f"## {dim}", ""])
        for evidence_unit in subset:
            lines.append(f"- **{evidence_unit.get('eu_id', '')}** ({evidence_unit.get('source_id', '')}) {evidence_unit.get('finding', '')}")
            if evidence_unit.get("why_it_matters"):
                lines.append(f"  - Why it matters: {evidence_unit['why_it_matters']}")
            if evidence_unit.get("evidence_quote"):
                lines.append(f"  - Evidence: \"{evidence_unit['evidence_quote']}\"")
            if evidence_unit.get("source_location"):
                lines.append(f"  - Location: {evidence_unit['source_location']}")
            if evidence_unit.get("notes"):
                lines.append(f"  - Notes: {evidence_unit['notes']}")
    return "\n".join(lines) + "\n"


def summary(evidence_units: list[dict]) -> dict:
    return {
        "evidence_unit_records": len(evidence_units),
        "source_count": len({row.get("source_id") for row in evidence_units if row.get("source_id")}),
        "dimension_counts": dict(Counter(row.get("engineering_dimension") for row in evidence_units)),
        "confidence_counts": dict(Counter(row.get("confidence") for row in evidence_units)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an Evidence Unit Markdown reading view.")
    parser.add_argument("--evidence-units", required=True, type=Path, help="evidence_units.jsonl")
    parser.add_argument("--out-md", required=True, type=Path, help="Markdown reading view output")
    parser.add_argument("--out-summary", type=Path, help="Optional summary JSON output")
    parser.add_argument("--title", default="Evidence Units")
    args = parser.parse_args()

    evidence_units = load_jsonl(args.evidence_units)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render(evidence_units, args.title), encoding="utf-8")
    info = summary(evidence_units)
    if args.out_summary:
        args.out_summary.parent.mkdir(parents=True, exist_ok=True)
        args.out_summary.write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**info, "out_md": str(args.out_md), "out_summary": str(args.out_summary or "")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
