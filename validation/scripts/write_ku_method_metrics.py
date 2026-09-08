#!/usr/bin/env python
"""Write one KU extraction method runtime/token metrics row."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path


FIELDS = [
    "run_id",
    "method_label",
    "method_type",
    "goal_objective",
    "goal_status",
    "started_at",
    "ended_at",
    "elapsed_seconds",
    "source_count",
    "ku_count",
    "candidate_passage_count",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "goal_reported_tokens",
    "token_source",
    "notes",
]


def read_jsonl_count(path: Path | None) -> int:
    if not path or not path.exists():
        return 0
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                count += 1
    return count


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


def existing_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in FIELDS})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--method-label", required=True)
    parser.add_argument("--method-type", required=True, choices=["direct", "subagent", "prefilter"])
    parser.add_argument("--goal-objective", default="")
    parser.add_argument("--goal-status", default="")
    parser.add_argument("--started-at")
    parser.add_argument("--ended-at")
    parser.add_argument("--source-inventory", type=Path)
    parser.add_argument("--kus", type=Path)
    parser.add_argument("--candidate-passages", type=Path)
    parser.add_argument("--prompt-tokens", default="")
    parser.add_argument("--completion-tokens", default="")
    parser.add_argument("--total-tokens", default="")
    parser.add_argument("--goal-reported-tokens", default="")
    parser.add_argument("--token-source", default="")
    parser.add_argument("--notes", default="")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()

    started = parse_time(args.started_at)
    ended = parse_time(args.ended_at) or datetime.now(timezone.utc)
    elapsed = ""
    if started and ended:
        elapsed = f"{max(0.0, (ended - started).total_seconds()):.1f}"

    row = {
        "run_id": args.run_id,
        "method_label": args.method_label,
        "method_type": args.method_type,
        "goal_objective": args.goal_objective,
        "goal_status": args.goal_status,
        "started_at": format_time(started),
        "ended_at": format_time(ended),
        "elapsed_seconds": elapsed,
        "source_count": str(read_jsonl_count(args.source_inventory)),
        "ku_count": str(read_jsonl_count(args.kus)),
        "candidate_passage_count": str(read_jsonl_count(args.candidate_passages)),
        "prompt_tokens": args.prompt_tokens,
        "completion_tokens": args.completion_tokens,
        "total_tokens": args.total_tokens,
        "goal_reported_tokens": args.goal_reported_tokens,
        "token_source": args.token_source,
        "notes": args.notes,
    }

    rows = existing_rows(args.out)
    if args.replace:
        rows = [
            old
            for old in rows
            if not (old.get("run_id") == args.run_id and old.get("method_label") == args.method_label)
        ]
    rows.append(row)
    write_rows(args.out, rows)
    print(json.dumps(row, indent=2))


if __name__ == "__main__":
    main()
