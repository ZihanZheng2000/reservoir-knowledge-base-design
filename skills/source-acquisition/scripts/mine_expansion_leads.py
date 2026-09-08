"""Mine text-informed source-discovery leads from preserved source text.

This helper does not decide inclusion. It scans extracted text for names,
document-title patterns, references, models, datasets, agencies, and governance
terms that can be fed back into follow-up discovery and candidate screening.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


KEYWORD_PATTERNS = {
    "operator_or_agency": re.compile(
        r"\b(?:Bureau of Reclamation|U\.?S\.? Army Corps of Engineers|USACE|"
        r"Department of Water Resources|Water Authority|Irrigation District|"
        r"Power Authority|River Authority|Conservancy District|Water District)\b",
        re.IGNORECASE,
    ),
    "model_or_tool": re.compile(
        r"\b(?:[A-Z][A-Za-z0-9-]*(?:\s+[A-Z][A-Za-z0-9-]*){0,4}\s+"
        r"(?:Model|Simulation|Decision Support System|DSS|Forecast|Study|Scenario|Dataset|API))\b"
    ),
    "operating_document": re.compile(
        r"\b(?:Water Control Manual|Reservoir Regulation Manual|Operation Plan|"
        r"Operating Plan|Operating Criteria|Operating Guidelines|Rule Curve|"
        r"Guide Curve|Record of Decision|Environmental Impact Statement|"
        r"Environmental Assessment|Technical Appendix|Technical Memorandum)\b",
        re.IGNORECASE,
    ),
    "governance_or_legal": re.compile(
        r"\b(?:Compact|Agreement|License|FERC|NEPA|Record of Decision|"
        r"Consultation|Treaty|Decree|Guidelines|Interim Guidelines)\b",
        re.IGNORECASE,
    ),
    "infrastructure_or_data": re.compile(
        r"\b(?:outlet works|spillway|penstock|turbine|powerplant|intake|"
        r"minimum pool|dead pool|release capacity|stream gage|data portal|"
        r"time series|forecast product)\b",
        re.IGNORECASE,
    ),
}

TITLEISH_PATTERN = re.compile(
    r"\b(?:Appendix|Chapter|Volume|Section|Report|Plan|Manual|Study|Assessment|"
    r"Memorandum|Guidelines|Documentation)\s+[A-Z0-9][A-Za-z0-9 .,:;()/&-]{8,120}"
)

REFERENCE_PATTERN = re.compile(
    r"\b(?:References|Bibliography|Literature Cited|Cited References)\b",
    re.IGNORECASE,
)


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def resolve_existing_path(raw_path: str, inventory: Path) -> Path | None:
    path = Path(raw_path)
    if path.is_absolute() and path.exists():
        return path

    candidates = [
        path,
        Path.cwd() / path,
        inventory.parent / path,
        inventory.parent.parent / path,
        inventory.parent.parent.parent / path,
    ]
    candidates.extend(parent / path for parent in Path.cwd().parents)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def snippet(text: str, start: int, end: int, width: int = 180) -> str:
    left = max(0, start - width)
    right = min(len(text), end + width)
    return re.sub(r"\s+", " ", text[left:right]).strip()


def add_lead(
    leads: list[dict],
    seen: set[tuple[str, str, str]],
    *,
    lead_type: str,
    lead_text: str,
    row: dict,
    evidence: str,
    reason: str,
) -> None:
    cleaned = re.sub(r"\s+", " ", lead_text).strip(" .,:;()[]")
    if len(cleaned) < 4:
        return
    key = (lead_type, cleaned.lower(), row.get("source_id", ""))
    if key in seen:
        return
    seen.add(key)
    reservoir = row.get("reservoir_name") or ""
    suggested_query = f"{reservoir} {cleaned}".strip()
    leads.append(
        {
            "lead_type": lead_type,
            "lead_text": cleaned,
            "source_id": row.get("source_id", ""),
            "source_title": row.get("title") or row.get("source_title") or "",
            "source_url": row.get("url") or row.get("source_url") or "",
            "evidence_snippet": evidence,
            "suggested_query": suggested_query,
            "reason": reason,
        }
    )


def mine_text(row: dict, text: str, max_per_source: int) -> list[dict]:
    leads: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    for lead_type, pattern in KEYWORD_PATTERNS.items():
        count = 0
        for match in pattern.finditer(text):
            add_lead(
                leads,
                seen,
                lead_type=lead_type,
                lead_text=match.group(0),
                row=row,
                evidence=snippet(text, match.start(), match.end()),
                reason=f"Matched {lead_type} pattern in extracted source text.",
            )
            count += 1
            if count >= max_per_source:
                break

    count = 0
    for match in TITLEISH_PATTERN.finditer(text):
        add_lead(
            leads,
            seen,
            lead_type="document_title_or_companion_source",
            lead_text=match.group(0),
            row=row,
            evidence=snippet(text, match.start(), match.end()),
            reason="Matched document-title or companion-source pattern.",
        )
        count += 1
        if count >= max_per_source:
            break

    if REFERENCE_PATTERN.search(text):
        add_lead(
            leads,
            seen,
            lead_type="reference_section",
            lead_text="references or bibliography section",
            row=row,
            evidence=snippet(text, REFERENCE_PATTERN.search(text).start(), REFERENCE_PATTERN.search(text).end()),
            reason="Source appears to contain references that may support backward search.",
        )

    return leads


def main() -> None:
    parser = argparse.ArgumentParser(description="Mine expansion leads from extracted source text.")
    parser.add_argument("--inventory", required=True, type=Path, help="Source inventory JSONL.")
    parser.add_argument("--out", required=True, type=Path, help="Output expansion leads JSONL.")
    parser.add_argument("--max-per-pattern-per-source", type=int, default=8)
    args = parser.parse_args()

    rows = read_jsonl(args.inventory)
    leads: list[dict] = []
    missing_text = 0

    for row in rows:
        text_path = row.get("text_file_path") or row.get("text_path") or row.get("extracted_text_path") or ""
        if not text_path:
            missing_text += 1
            continue
        path = resolve_existing_path(text_path, args.inventory)
        if not path:
            missing_text += 1
            continue
        if not path.exists():
            missing_text += 1
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            missing_text += 1
            continue
        leads.extend(mine_text(row, text, args.max_per_pattern_per_source))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for lead in leads:
            f.write(json.dumps(lead, ensure_ascii=False, sort_keys=True) + "\n")

    counts = Counter(lead["lead_type"] for lead in leads)
    print(
        json.dumps(
            {
                "leads": len(leads),
                "lead_type_counts": dict(sorted(counts.items())),
                "missing_text_records": missing_text,
                "out": str(args.out),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
