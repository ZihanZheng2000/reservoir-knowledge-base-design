"""Run a deterministic lexical top-k baseline against encoded index records."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


STOPWORDS = {
    "a", "an", "and", "are", "at", "does", "for", "how", "in", "is", "it", "of",
    "or", "the", "to", "under", "what", "which", "with",
}


def tokens(text: str) -> list[str]:
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def rank(question: str, records: list[dict], depth: int) -> list[str]:
    query = Counter(tokens(question))
    ranked: list[tuple[int, str]] = []
    for record in records:
        record_id = record.get("index_record_id")
        if not isinstance(record_id, str):
            continue
        document = Counter(tokens(str(record.get("index_text", ""))))
        score = sum(min(count, document[token]) for token, count in query.items())
        ranked.append((score, record_id))
    return [record_id for _, record_id in sorted(ranked, key=lambda item: (-item[0], item[1]))[:depth]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--index-records", required=True, type=Path)
    args = parser.parse_args()

    review = json.loads(args.review.read_text(encoding="utf-8-sig"))
    if not isinstance(review, dict) or not isinstance(review.get("items"), list):
        parser.error("review must be a JSON object with an items array")
    records = load_jsonl(args.index_records)
    result_rows = []
    for item in review["items"]:
        if not isinstance(item, dict):
            continue
        question = item.get("benchmark_question")
        depth = item.get("retrieval_depth")
        if not isinstance(question, str) or not isinstance(depth, int) or depth < 1:
            parser.error("each review item needs benchmark_question and positive integer retrieval_depth")
        returned = rank(question, records, depth)
        for legacy_field in ("codex_decision", "human_sufficiency_decision", "recall_score", "precision_score"):
            item.pop(legacy_field, None)
        item["codex_retrieval_method"] = "deterministic_lexical_token_overlap_baseline"
        item["codex_retrieval_status"] = "completed"
        item["codex_returned_index_record_ids"] = returned
        result_rows.append({"query_id": item.get("query_id"), "returned_index_record_ids": returned})

    args.review.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"method": "deterministic_lexical_token_overlap_baseline", "queries": result_rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
