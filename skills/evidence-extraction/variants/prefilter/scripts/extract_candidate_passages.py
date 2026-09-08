#!/usr/bin/env python
"""Extract broad reservoir-operation candidate passages from EU-ready sources."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


KEYWORD_GROUPS: dict[str, list[str]] = {
    "operation_rules": [
        "operating rule",
        "operation rule",
        "operating criteria",
        "release schedule",
        "release volume",
        "release rate",
        "guide curve",
        "trigger",
        "threshold",
        "tier",
        "if ",
        "shall",
        "must",
        "record of decision",
        "rod",
    ],
    "storage_capacity_targets": [
        "storage",
        "capacity",
        "elevation",
        "minimum pool",
        "minimum power pool",
        "dead pool",
        "active conservation",
        "target elevation",
        "reservoir level",
        "acre-feet",
        "maf",
    ],
    "purposes_objectives": [
        "hydropower",
        "power generation",
        "water supply",
        "water delivery",
        "flood control",
        "recreation",
        "navigation",
        "fish",
        "wildlife",
        "ecology",
        "ecosystem",
        "compact compliance",
    ],
    "emergency_real_time": [
        "drought",
        "flood",
        "emergency",
        "maintenance",
        "real-time",
        "near-term",
        "daily",
        "monthly",
        "adjustment",
        "special event",
        "experimental flow",
    ],
    "data_forecast": [
        "forecast",
        "inflow",
        "outflow",
        "unregulated inflow",
        "monitoring",
        "observed",
        "dataset",
        "data portal",
        "time series",
        "24-month study",
        "probable",
    ],
    "modeling_uncertainty": [
        "model",
        "simulation",
        "scenario",
        "alternative",
        "uncertainty",
        "risk",
        "vulnerability",
        "sensitivity",
        "crss",
        "dmdu",
    ],
    "governance_stakeholders": [
        "agreement",
        "compact",
        "law",
        "consultation",
        "nepa",
        "agency",
        "reclamation",
        "tribe",
        "tribal",
        "state",
        "stakeholder",
        "water user",
    ],
    "infrastructure_failure": [
        "dam",
        "outlet",
        "outlet works",
        "penstock",
        "turbine",
        "spillway",
        "bypass",
        "intake",
        "cavitation",
        "failure",
        "cannot release",
        "reduced generation",
        "infrastructure",
    ],
}


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
    return records


def resolve_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return Path.cwd() / path


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def windows(text: str, window_chars: int, overlap_chars: int):
    if window_chars <= overlap_chars:
        raise SystemExit("--window-chars must be greater than --overlap-chars")
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(text_len, start + window_chars)
        yield start, end, text[start:end].strip()
        if end == text_len:
            break
        start = end - overlap_chars


def score_passage(text: str) -> tuple[int, list[str], list[str]]:
    lowered = text.lower()
    matched_groups: list[str] = []
    matched_terms: list[str] = []
    score = 0
    for group, terms in KEYWORD_GROUPS.items():
        group_matches = [term for term in terms if term in lowered]
        if group_matches:
            matched_groups.append(group)
            matched_terms.extend(group_matches[:8])
            score += len(group_matches)
    number_hits = len(re.findall(r"\b\d+(?:[.,]\d+)?\s*(?:cfs|maf|mw|feet|ft|acre-feet|af|%)\b", lowered))
    if number_hits:
        score += min(number_hits, 5)
        matched_groups.append("quantified_operation_signal")
    return score, sorted(set(matched_groups)), sorted(set(matched_terms))


def line_locator(text: str, start: int) -> int:
    return text.count("\n", 0, start) + 1


def candidate_records(
    inventory: list[dict],
    window_chars: int,
    overlap_chars: int,
    min_score: int,
    max_per_source: int,
) -> tuple[list[dict], dict]:
    records: list[dict] = []
    summary: dict = {
        "total_sources": len(inventory),
        "total_candidates": 0,
        "sources": {},
        "keyword_group_counts": {},
        "zero_candidate_sources": [],
    }
    group_counter: Counter[str] = Counter()

    for source in inventory:
        source_id = source.get("source_id", "")
        text_path_value = source.get("extracted_text_path", "")
        source_summary = {
            "source_tier": source.get("source_tier", ""),
            "title": source.get("title", ""),
            "candidate_count": 0,
            "max_score": 0,
        }
        if not text_path_value:
            source_summary["issue"] = "missing extracted_text_path"
            summary["sources"][source_id] = source_summary
            summary["zero_candidate_sources"].append(source_id)
            continue

        text_path = resolve_path(text_path_value)
        if not text_path.exists():
            source_summary["issue"] = f"text file not found: {text_path}"
            summary["sources"][source_id] = source_summary
            summary["zero_candidate_sources"].append(source_id)
            continue

        text = normalize_text(text_path.read_text(encoding="utf-8", errors="replace"))
        source_candidates: list[dict] = []
        for idx, (start, end, passage) in enumerate(windows(text, window_chars, overlap_chars), start=1):
            score, groups, terms = score_passage(passage)
            if score < min_score:
                continue
            group_counter.update(groups)
            source_summary["max_score"] = max(source_summary["max_score"], score)
            source_candidates.append(
                {
                    "reservoir_id": source.get("reservoir_id", ""),
                    "reservoir_name": source.get("reservoir_name", ""),
                    "source_id": source_id,
                    "source_tier": source.get("source_tier", ""),
                    "source_title": source.get("title", ""),
                    "source_url": source.get("url", ""),
                    "document_type": source.get("document_type", ""),
                    "candidate_id": f"{source_id}-CAND-{idx:04d}",
                    "candidate_method": "keyword_window_prefilter",
                    "char_start": start,
                    "char_end": end,
                    "line_start_approx": line_locator(text, start),
                    "score": score,
                    "matched_groups": groups,
                    "matched_terms": terms,
                    "text": passage,
                }
            )

        source_candidates.sort(key=lambda row: (-row["score"], row["char_start"]))
        if max_per_source > 0:
            source_candidates = source_candidates[:max_per_source]
        source_candidates.sort(key=lambda row: row["char_start"])
        source_summary["candidate_count"] = len(source_candidates)
        if not source_candidates:
            summary["zero_candidate_sources"].append(source_id)
        summary["sources"][source_id] = source_summary
        records.extend(source_candidates)

    summary["total_candidates"] = len(records)
    summary["keyword_group_counts"] = dict(sorted(group_counter.items()))
    tier_counts: defaultdict[str, int] = defaultdict(int)
    for row in records:
        tier_counts[row.get("source_tier") or "unknown"] += 1
    summary["candidate_count_by_tier"] = dict(sorted(tier_counts.items()))
    return records, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--summary-out", type=Path)
    parser.add_argument("--window-chars", type=int, default=1800)
    parser.add_argument("--overlap-chars", type=int, default=350)
    parser.add_argument("--min-score", type=int, default=1)
    parser.add_argument("--max-per-source", type=int, default=0, help="0 means no cap")
    args = parser.parse_args()

    inventory = read_jsonl(args.inventory)
    records, summary = candidate_records(
        inventory=inventory,
        window_chars=args.window_chars,
        overlap_chars=args.overlap_chars,
        min_score=args.min_score,
        max_per_source=args.max_per_source,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    if args.summary_out:
        args.summary_out.parent.mkdir(parents=True, exist_ok=True)
        args.summary_out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(records)} candidate passages to {args.out}")
    if args.summary_out:
        print(f"Wrote summary to {args.summary_out}")
    if summary["zero_candidate_sources"]:
        print(f"Zero-candidate sources: {', '.join(summary['zero_candidate_sources'])}")


if __name__ == "__main__":
    main()
