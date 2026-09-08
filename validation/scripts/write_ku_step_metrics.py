#!/usr/bin/env python
"""Append one KU extraction step timing row."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


FIELDS = [
    "run_id",
    "method_label",
    "step_label",
    "step_type",
    "started_at",
    "ended_at",
    "elapsed_seconds",
    "output_path",
    "record_count",
    "status",
    "notes",
]


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SystemExit(f"Invalid ISO datetime: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def format_time(value: datetime | None) -> str:
    if not value:
        return ""
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def count_records(path: Path | None) -> str:
    if not path or not path.exists() or not path.is_file():
        return ""
    if path.suffix.lower() == ".json":
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return ""
        if isinstance(value, list):
            return str(len(value))
        if isinstance(value, dict):
            for key in ("ku_count", "total_candidates", "records", "record_count"):
                if key in value and isinstance(value[key], int):
                    return str(value[key])
        return ""
    count = 0
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.strip():
                count += 1
    if path.suffix.lower() == ".csv" and count:
        count -= 1
    return str(max(count, 0))


def existing_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--method-label", required=True)
    parser.add_argument("--step-label", required=True)
    parser.add_argument("--step-type", default="")
    parser.add_argument("--started-at")
    parser.add_argument("--ended-at")
    parser.add_argument("--output-path", type=Path)
    parser.add_argument("--record-count", default="")
    parser.add_argument("--status", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    started = parse_time(args.started_at)
    ended = parse_time(args.ended_at) or datetime.now(timezone.utc)
    elapsed = ""
    if started and ended:
        elapsed = f"{max(0.0, (ended - started).total_seconds()):.1f}"

    output_path = str(args.output_path) if args.output_path else ""
    row = {
        "run_id": args.run_id,
        "method_label": args.method_label,
        "step_label": args.step_label,
        "step_type": args.step_type,
        "started_at": format_time(started),
        "ended_at": format_time(ended),
        "elapsed_seconds": elapsed,
        "output_path": output_path,
        "record_count": args.record_count or count_records(args.output_path),
        "status": args.status,
        "notes": args.notes,
    }

    rows = existing_rows(args.out)
    if args.replace:
        rows = [
            old
            for old in rows
            if not (
                old.get("run_id") == args.run_id
                and old.get("method_label") == args.method_label
                and old.get("step_label") == args.step_label
            )
        ]
    rows.append(row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for item in rows:
            writer.writerow({field: item.get(field, "") for field in FIELDS})
    print(json.dumps(row, indent=2))


if __name__ == "__main__":
    main()
