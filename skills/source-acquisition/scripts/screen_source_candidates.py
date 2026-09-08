"""Heuristically screen reservoir source candidates.

The output is a first-pass review aid. Human or Codex review should confirm
inclusion before writing an approved source manifest.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse


FAMILY_TERMS = {
    "operation_rules": [
        "operation", "operating", "release", "guideline", "rule", "criteria",
        "rule curve", "guide curve", "water control", "reservoir regulation",
    ],
    "infrastructure_constraints": [
        "dam", "outlet", "spillway", "gate", "intake", "penstock", "turbine",
        "powerplant", "minimum pool", "dead pool", "low water", "release capacity",
    ],
    "data_models_forecasts": [
        "forecast", "model", "simulation", "scenario", "data", "dataset",
        "api", "time series", "stream gage", "snowpack",
    ],
    "real_time_emergency": ["emergency", "drought", "flood", "shortage", "contingency", "incident"],
    "hydropower": ["hydropower", "powerplant", "generation", "power", "turbine"],
    "temperature_ecology": [
        "temperature", "ecology", "fish", "environmental flow", "ecological flow",
        "sediment", "water quality", "flow experiment",
    ],
    "adaptive_management": ["adaptive management", "monitoring", "experiment"],
    "governance_policy": [
        "governance", "agreement", "compact", "policy", "legal", "license",
        "ferc", "nepa", "eis", "record of decision", "consultation",
    ],
    "uncertainty_scenarios": ["uncertainty", "scenario", "robust", "climate"],
    "storage_capacity_sediment": ["storage", "capacity", "sediment", "bathymetry"],
    "media_context": ["news", "stakeholder", "public", "controversy", "lawsuit"],
}

OFFICIAL_HOST_TERMS = ["usbr.gov", "usgs.gov", "doi.gov", "data.gov", "noaa.gov", "osti.gov", "pnnl.gov", "anl.gov"]
MEDIA_HOST_TERMS = ["apnews.com", "circleofblue.org", "enr.com", "theguardian.com", "newyorker.com"]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evidence_families(text: str) -> list[str]:
    lower = text.lower()
    families = []
    for family, terms in FAMILY_TERMS.items():
        if any(term in lower for term in terms):
            families.append(family)
    return families


def tier_suggestion(url: str, title: str) -> str:
    host = urlparse(url or "").netloc.lower()
    lower = f"{title} {url}".lower()
    if any(term in host for term in OFFICIAL_HOST_TERMS):
        return "A" if any(x in lower for x in ["operations", "guideline", "study", "data", "dam", "reservoir"]) else "B"
    if any(term in host for term in MEDIA_HOST_TERMS):
        return "C"
    if any(x in lower for x in ["journal", "doi.org", "proceedings", "science", "research", "university"]):
        return "B"
    return "B"


def access_status(row: dict) -> str:
    url = row.get("url") or row.get("oa_url") or row.get("primary_location") or ""
    if row.get("is_open_access") or row.get("oa_url"):
        return "open_access_candidate"
    if re.search(r"\.pdf($|[?#])", url, flags=re.I):
        return "direct_pdf_candidate"
    if url:
        return "landing_page_candidate"
    return "metadata_only"


def source_importance_hint(families: list[str], title: str, tier: str, status: str) -> str:
    lower = title.lower()
    core_terms = [
        "water control manual", "reservoir regulation manual", "operation plan",
        "operating plan", "operating criteria", "operating guidelines",
        "environmental impact statement", "record of decision", "technical appendix",
        "model documentation", "data portal",
    ]
    if any(term in lower for term in core_terms):
        return "core"
    if tier == "A" and families:
        return "core"
    if status == "metadata_only":
        return "low_value"
    if families:
        return "supporting"
    return "background"


def download_decision(reservoir_hit: bool, families: list[str], status: str, importance: str) -> str:
    if status == "metadata_only" and importance != "core":
        return "manual_review" if reservoir_hit or families else "exclude"
    if reservoir_hit and families:
        return "include"
    if importance == "core" and status != "metadata_only":
        return "include"
    if families and status != "metadata_only":
        return "maybe"
    if reservoir_hit:
        return "manual_review"
    return "exclude"


def screen(row: dict, reservoir_terms: list[str]) -> dict:
    title = row.get("title") or ""
    url = row.get("url") or row.get("oa_url") or row.get("primary_location") or ""
    text = " ".join(str(row.get(k) or "") for k in ["title", "source_display_name", "url", "query_or_seed"])
    families = evidence_families(text)
    reservoir_hit = any(term.lower() in text.lower() for term in reservoir_terms)
    tier = tier_suggestion(url, title)
    status = access_status(row)
    importance = source_importance_hint(families, title, tier, status)
    action = download_decision(reservoir_hit, families, status, importance)

    return {
        **row,
        "source_tier_suggestion": tier,
        "evidence_family": families,
        "access_status": status,
        "source_importance_hint": importance,
        "recommended_action": action,
        "relevance_note": "; ".join([
            "matches reservoir/system terms" if reservoir_hit else "no direct reservoir/system term match",
            "families=" + ",".join(families) if families else "no operational evidence family detected",
            "importance_hint=" + importance,
            status,
        ]),
    }


def write_markdown(path: Path, rows: list[dict]) -> None:
    counts = Counter(row["recommended_action"] for row in rows)
    lines = ["# Screened Source Candidates", ""]
    lines.append("## Counts")
    lines.append("")
    lines.append("| Action | Count |")
    lines.append("|---|---:|")
    for action, count in sorted(counts.items()):
        lines.append(f"| {action} | {count} |")
    lines.append("")
    lines.append("## Candidates")
    lines.append("")
    lines.append("| Action | Tier Hint | Importance Hint | Families | Title | URL |")
    lines.append("|---|---|---|---|---|---|")
    for row in rows:
        families = ", ".join(row.get("evidence_family") or [])
        title = (row.get("title") or "").replace("|", "\\|")
        url = row.get("url") or ""
        lines.append(f"| {row['recommended_action']} | {row['source_tier_suggestion']} | {row.get('source_importance_hint', '')} | {families} | {title} | {url} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Screen reservoir source candidates.")
    parser.add_argument("--candidates", required=True, type=Path)
    parser.add_argument("--out-jsonl", required=True, type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--reservoir-term", action="append", default=[])
    args = parser.parse_args()

    screened = [screen(row, args.reservoir_term) for row in load_jsonl(args.candidates)]
    args.out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with args.out_jsonl.open("w", encoding="utf-8") as f:
        for row in screened:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    if args.out_md:
        write_markdown(args.out_md, screened)
    print(json.dumps({
        "candidates": len(screened),
        "action_counts": Counter(row["recommended_action"] for row in screened),
        "out_jsonl": str(args.out_jsonl),
        "out_md": str(args.out_md) if args.out_md else "",
    }, indent=2))


if __name__ == "__main__":
    main()
