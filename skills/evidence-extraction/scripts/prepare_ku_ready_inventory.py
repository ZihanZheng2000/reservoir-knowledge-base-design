"""Create an EU-ready source inventory from a Layer 1 source inventory.

This script is deterministic plumbing for Evidence extraction. It does not decide
whether text contains Evidence Units; it only filters source records that are ready to be
chunked into extraction packets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Filter source inventory to EU-ready records.")
    parser.add_argument("--inventory", required=True, type=Path, help="Layer 1 source_inventory.jsonl")
    parser.add_argument("--out", required=True, type=Path, help="Output EU-ready inventory JSONL")
    parser.add_argument(
        "--include-short-review",
        action="store_true",
        help="Include status=ok sources with content_quality=short_review even if eu_readiness is not ready.",
    )
    args = parser.parse_args()

    rows = load_jsonl(args.inventory)
    ready = []
    skipped = []
    for row in rows:
        status_ok = row.get("status") == "ok"
        has_text = bool(row.get("extracted_text_saved")) and bool(row.get("extracted_text_path"))
        readiness = row.get("eu_readiness")
        short_review = row.get("content_quality") == "short_review"
        include = status_ok and has_text and (readiness == "ready" or (args.include_short_review and short_review))
        if include:
            ready.append(row)
        else:
            skipped.append(
                {
                    "source_id": row.get("source_id", ""),
                    "status": row.get("status", ""),
                    "eu_readiness": readiness,
                    "content_quality": row.get("content_quality", ""),
                    "reason": "not_status_ok_or_not_eu_ready_or_missing_text",
                }
            )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in ready) + ("\n" if ready else ""),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "input_records": len(rows),
                "eu_ready_records": len(ready),
                "skipped_records": len(skipped),
                "out": str(args.out),
                "skipped": skipped,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
