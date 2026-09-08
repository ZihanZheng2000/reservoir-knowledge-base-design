"""Write the retained, reviewable candidate universe for Source acquisition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def approved_urls(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    rows = data.get("sources", []) if isinstance(data, dict) else data
    return {str(row.get("url")) for row in rows if isinstance(row, dict) and row.get("url")}


def tier(row: dict) -> str:
    value = str(row.get("source_tier") or row.get("source_tier_suggestion") or "B").upper()
    return value if value in {"A", "B", "C"} else "B"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screened-candidates", required=True, type=Path)
    parser.add_argument("--reservoir-id", required=True)
    parser.add_argument("--approved-manifest", type=Path, help="Final approved source manifest; when supplied it defines Codex selections.")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    selected_urls = approved_urls(args.approved_manifest)
    rows = []
    for number, row in enumerate(load_rows(args.screened_candidates), 1):
        action = str(row.get("codex_selection_decision") or row.get("recommended_action") or "").lower()
        url = str(row.get("url") or row.get("oa_url") or row.get("primary_location") or "missing-url")
        use = "Y" if (url in selected_urls if selected_urls is not None else action in {"include", "selected", "approve"}) else "N"
        rows.append({
            "candidate_id": str(row.get("candidate_id") or row.get("source_id") or f"CAND-{number:04d}"),
            "reservoir_id": args.reservoir_id,
            "title": str(row.get("title") or "Untitled candidate"),
            "url": url,
            "document_type": str(row.get("document_type") or "other"),
            "codex_use": use,
            "codex_tier": tier(row),
            "codex_selection_reason": str(row.get("selection_reason") or row.get("relevance_note") or f"screening action: {action or 'not recorded'}"),
            "acquisition_source_id": str(row.get("source_id") or ""),
            "notes": str(row.get("notes") or ""),
        })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    print(json.dumps({"candidate_records": len(rows), "selected": sum(row["codex_use"] == "Y" for row in rows), "out": str(args.out)}))


if __name__ == "__main__":
    main()
