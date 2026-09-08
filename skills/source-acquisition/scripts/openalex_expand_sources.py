"""Discover reservoir source candidates with OpenAlex.

This script is a discovery helper, not an acquisition runner. It writes
candidate metadata that must be screened before sources are preserved.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path


OPENALEX = "https://api.openalex.org"


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "ReservoirKB/1.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8"))


def openalex_url(path: str, params: dict | None = None) -> str:
    url = f"{OPENALEX}/{path.lstrip('/')}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return url


def normalize_work(work: dict, method: str, query_or_seed: str) -> dict:
    location = work.get("primary_location") or {}
    open_access = work.get("open_access") or {}
    return {
        "candidate_id": work.get("id", "").rsplit("/", 1)[-1],
        "discovery_method": method,
        "query_or_seed": query_or_seed,
        "title": work.get("title") or "",
        "year": work.get("publication_year"),
        "doi": work.get("doi") or "",
        "url": open_access.get("oa_url") or location.get("landing_page_url") or work.get("doi") or work.get("id") or "",
        "openalex_id": work.get("id") or "",
        "primary_location": location.get("landing_page_url") or "",
        "is_open_access": open_access.get("is_oa"),
        "oa_url": open_access.get("oa_url") or "",
        "cited_by_count": work.get("cited_by_count"),
        "source_display_name": ((location.get("source") or {}).get("display_name") if location else "") or "",
        "raw_openalex_type": work.get("type") or "",
    }


def load_queries(path: Path | None, inline: list[str]) -> list[str]:
    queries = list(inline or [])
    if path:
        if path.suffix.lower() == ".jsonl":
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    queries.append(row.get("query") or row.get("title") or "")
        else:
            queries.extend(line.strip() for line in path.read_text(encoding="utf-8").splitlines())
    return [q for q in queries if q]


def resolve_seed(seed: str, mailto: str) -> dict | None:
    seed = seed.strip()
    if not seed:
        return None
    if seed.startswith("https://openalex.org/"):
        return get_json(openalex_url("works/" + seed.rsplit("/", 1)[-1], {"mailto": mailto}))
    if seed.lower().startswith("10."):
        return get_json(openalex_url("works/doi:" + seed, {"mailto": mailto}))
    if seed.lower().startswith("https://doi.org/"):
        return get_json(openalex_url("works/doi:" + seed.rsplit("/", 1)[-1], {"mailto": mailto}))
    data = get_json(openalex_url("works", {"search": seed, "per-page": 1, "mailto": mailto}))
    results = data.get("results") or []
    return results[0] if results else None


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenAlex reservoir source discovery.")
    parser.add_argument("--queries", type=Path, help="Text or JSONL file of search queries.")
    parser.add_argument("--query", action="append", default=[], help="Inline search query; repeatable.")
    parser.add_argument("--seeds", type=Path, help="Text file of seed titles, DOIs, or OpenAlex IDs.")
    parser.add_argument("--out", required=True, type=Path, help="Output candidate JSONL.")
    parser.add_argument("--per-page", type=int, default=10)
    parser.add_argument("--mailto", default="reservoir-kb-demo@example.com")
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args()

    rows: list[dict] = []
    seen: set[str] = set()

    for query in load_queries(args.queries, args.query):
        data = get_json(openalex_url("works", {
            "search": query,
            "per-page": args.per_page,
            "filter": "from_publication_date:1990-01-01",
            "mailto": args.mailto,
        }))
        for work in data.get("results", []):
            row = normalize_work(work, "openalex_search", query)
            key = row["openalex_id"] or row["doi"] or row["title"].lower()
            if key not in seen:
                seen.add(key)
                rows.append(row)
        time.sleep(args.sleep)

    if args.seeds:
        for seed in args.seeds.read_text(encoding="utf-8").splitlines():
            work = resolve_seed(seed, args.mailto)
            if not work:
                continue
            seed_id = work.get("id", "")
            seed_label = work.get("doi") or work.get("title") or seed
            row = normalize_work(work, "seed_resolved", seed_label)
            key = row["openalex_id"] or row["doi"] or row["title"].lower()
            if key not in seen:
                seen.add(key)
                rows.append(row)

            for ref_url in (work.get("referenced_works") or [])[:50]:
                try:
                    ref = get_json(openalex_url("works/" + ref_url.rsplit("/", 1)[-1], {"mailto": args.mailto}))
                    row = normalize_work(ref, "backward_reference", seed_label)
                    key = row["openalex_id"] or row["doi"] or row["title"].lower()
                    if key not in seen:
                        seen.add(key)
                        rows.append(row)
                    time.sleep(args.sleep)
                except Exception as exc:
                    rows.append({
                        "candidate_id": "",
                        "discovery_method": "backward_reference_error",
                        "query_or_seed": seed_label,
                        "title": "",
                        "error": str(exc),
                    })

            if seed_id:
                data = get_json(openalex_url("works", {
                    "filter": "cites:" + seed_id.rsplit("/", 1)[-1],
                    "per-page": args.per_page,
                    "mailto": args.mailto,
                }))
                for citing in data.get("results", []):
                    row = normalize_work(citing, "forward_citation", seed_label)
                    key = row["openalex_id"] or row["doi"] or row["title"].lower()
                    if key not in seen:
                        seen.add(key)
                        rows.append(row)
                time.sleep(args.sleep)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({"candidates": len(rows), "out": str(args.out)}, indent=2))


if __name__ == "__main__":
    main()
