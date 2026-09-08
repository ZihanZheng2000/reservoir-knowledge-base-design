"""Acquire reservoir sources from a JSON manifest.

This is the Layer 1 runner for a fresh reservoir knowledge-base workflow:
manifest -> raw files -> extracted text -> source inventory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

MIN_EXTRACTED_TEXT_CHARS = 500


def slug(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return text[:80] or "source"


def strip_html(data: bytes) -> str:
    raw = data.decode("utf-8", errors="replace")
    raw = re.sub(r"(?is)<script.*?</script>", " ", raw)
    raw = re.sub(r"(?is)<style.*?</style>", " ", raw)
    raw = re.sub(r"(?is)<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    return re.sub(r"\s+", " ", raw).strip()


PDF_EXTRACTION_FAILURE_PREFIX = "[PDF text extraction "


def extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        return f"{PDF_EXTRACTION_FAILURE_PREFIX}skipped: pypdf unavailable: {exc}]"
    try:
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        return f"{PDF_EXTRACTION_FAILURE_PREFIX}failed: {exc}]"


def download(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 ReservoirKB/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read(), resp.headers.get("content-type", "")


def is_html_content_type(content_type: str) -> bool:
    lower = content_type.lower()
    return "text/html" in lower or "application/xhtml" in lower


def load_manifest(path: Path) -> list[dict]:
    if path.suffix.lower() == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "sources" in data:
        return list(data["sources"])
    if isinstance(data, list):
        return data
    raise ValueError("manifest must be a JSON list, JSON object with sources, or JSONL")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--reservoir-id", required=True)
    parser.add_argument("--reservoir-name", required=True)
    parser.add_argument("--method", default="curated_url_python_download")
    args = parser.parse_args()

    raw_dir = args.out_dir / "sources" / "raw"
    text_dir = args.out_dir / "sources" / "text"
    raw_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    access_date = datetime.now(timezone.utc).date().isoformat()
    rows: list[dict] = []
    seen_hashes: dict[str, str] = {}

    for src in load_manifest(args.manifest):
        source_id = src["source_id"]
        title = src["title"]
        url = src["url"]
        base = f"{source_id}_{slug(title)}"
        host = urlparse(url).netloc.lower()
        raw_path = raw_dir / f"{base}.bin"
        text_path = text_dir / f"{base}.txt"
        status = "ok"
        content_type = ""
        extracted = ""
        sha256 = ""
        duplicate_of = ""
        content_quality_flag = "usable_text"
        content_quality_note = ""
        followup_action = ""

        try:
            data, content_type = download(url)
            sha256 = hashlib.sha256(data).hexdigest()
            duplicate_of = seen_hashes.get(sha256, "")
            if not duplicate_of:
                seen_hashes[sha256] = source_id

            raw_path.write_bytes(data)
            lower_url = url.lower()
            if lower_url.endswith(".pdf") and is_html_content_type(content_type):
                final_raw = raw_path.with_suffix(".html")
                raw_path.replace(final_raw)
                raw_path = final_raw
                extracted = strip_html(data)
                content_quality_flag = "pdf_url_returned_html_review"
                content_quality_note = "The URL ends with .pdf but returned HTML. The HTML may still contain useful landing-page, abstract, or full-text information, but it may also be a paywall, redirect, or access-denied page."
                followup_action = "Review the preserved HTML. If it is not usable full text, search again for an alternate PDF, DOI landing page, official mirror, repository copy, OpenAlex open-access URL, or library-accessible source."
            elif "pdf" in content_type.lower() or lower_url.endswith(".pdf"):
                final_raw = raw_path.with_suffix(".pdf")
                raw_path.replace(final_raw)
                raw_path = final_raw
                extracted = extract_pdf(raw_path)
                if extracted.startswith(PDF_EXTRACTION_FAILURE_PREFIX):
                    status = f"failed: {extracted}"
                    content_quality_flag = "parser_issue"
                    content_quality_note = extracted
                    followup_action = (
                        "PDF text extraction failed (missing/broken pypdf or cryptography "
                        "dependency, or an unreadable PDF). Install the pinned dependencies "
                        "in requirements.txt and re-run acquisition for this source, or find "
                        "an alternate text source, before treating it as EU-ready."
                    )
            elif "json" in content_type.lower() or lower_url.endswith(".json"):
                final_raw = raw_path.with_suffix(".json")
                raw_path.replace(final_raw)
                raw_path = final_raw
                extracted = data.decode("utf-8", errors="replace")
            elif lower_url.endswith(".csv") or "csv" in content_type.lower():
                final_raw = raw_path.with_suffix(".csv")
                raw_path.replace(final_raw)
                raw_path = final_raw
                extracted = data.decode("utf-8", errors="replace")
            else:
                final_raw = raw_path.with_suffix(".html")
                raw_path.replace(final_raw)
                raw_path = final_raw
                extracted = strip_html(data)
            text_path.write_text(extracted, encoding="utf-8")
            if status == "ok" and len(extracted.strip()) < MIN_EXTRACTED_TEXT_CHARS:
                content_quality_flag = "short_text_review"
                content_quality_note = f"Extracted text is short ({len(extracted.strip())} chars). Short content can still be valid, but it should be reviewed before EU extraction."
                followup_action = "Review whether the short text contains usable source evidence. If not, search again for a better full-text source or alternate URL."
        except Exception as exc:
            status = f"failed: {exc}"
            content_quality_flag = "acquisition_failed"
            content_quality_note = str(exc)
            followup_action = "Search again for an alternate URL, DOI landing page, official mirror, repository copy, OpenAlex open-access URL, or replacement source."

        rows.append({
            "source_id": source_id,
            "reservoir_id": args.reservoir_id,
            "reservoir_name": args.reservoir_name,
            "title": title,
            "url": url,
            "raw_host": host,
            "official_owner": src.get("official_owner", ""),
            "document_type": src.get("document_type", "other"),
            "source_tier": src.get("source_tier", ""),
            "source_importance": src.get("source_importance", src.get("source_importance_hint", "")),
            "content_quality": src.get("content_quality", ""),
            "eu_readiness": src.get("eu_readiness", ""),
            "selection_reason": src.get("selection_reason", ""),
            "access_date": access_date,
            "acquisition_method": args.method,
            "content_type": content_type,
            "content_sha256": sha256,
            "duplicate_of": duplicate_of,
            "status": status,
            "content_quality_flag": content_quality_flag,
            "content_quality_note": content_quality_note,
            "followup_action": followup_action,
            "raw_file_saved": raw_path.exists(),
            "raw_file_path": str(raw_path) if raw_path.exists() else "",
            "extracted_text_saved": text_path.exists(),
            "extracted_text_path": str(text_path) if text_path.exists() else "",
            "extracted_text_length": len(extracted),
        })

    inventory_jsonl = args.out_dir / "sources" / "source_inventory.jsonl"
    inventory_csv = args.out_dir / "sources" / "source_inventory.csv"
    with inventory_jsonl.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    with inventory_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps({
        "sources": len(rows),
        "ok": sum(1 for row in rows if row["status"] == "ok"),
        "failed": [row["source_id"] for row in rows if row["status"] != "ok"],
        "duplicates_by_hash": {row["source_id"]: row["duplicate_of"] for row in rows if row["duplicate_of"]},
        "inventory": str(inventory_jsonl),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
