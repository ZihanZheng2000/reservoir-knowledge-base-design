from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse, urlunparse


REQUIRED = {
    "source_id",
    "reservoir_id",
    "reservoir_name",
    "title",
    "url",
    "document_type",
    "selection_reason",
    "status",
    "raw_file_saved",
    "raw_file_path",
    "extracted_text_saved",
    "extracted_text_path",
    "extracted_text_length",
}

DOCUMENT_TYPES = {
    "engineering_manual",
    "operating_plan",
    "technical_memo",
    "environmental_report",
    "data_system_documentation",
    "legal_policy_document",
    "event_case_report",
    "research_paper",
    "agency_webpage",
    "other",
}


def canonical_url(url: str) -> str:
    parsed = urlparse(url.strip())
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/")
    return urlunparse((scheme, netloc, path, "", parsed.query, ""))


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path} line {lineno} invalid JSON: {exc}") from exc
    return rows


def validate(rows: list[dict]) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    source_ids: set[str] = set()
    urls: dict[str, str] = {}

    for i, row in enumerate(rows, 1):
        sid = row.get("source_id", f"row-{i}")
        missing = REQUIRED - row.keys()
        if missing:
            errors.append(f"{sid} missing fields: {sorted(missing)}")
        if sid in source_ids:
            errors.append(f"duplicate source_id: {sid}")
        source_ids.add(sid)

        url = row.get("url", "")
        if not url:
            errors.append(f"{sid} missing url")
        else:
            canon = canonical_url(url)
            if canon in urls:
                warnings.append(f"{sid} may duplicate {urls[canon]} by canonical URL: {canon}")
            urls[canon] = sid

        doc_type = row.get("document_type")
        if doc_type not in DOCUMENT_TYPES:
            errors.append(f"{sid} invalid document_type: {doc_type}")

        raw_path = row.get("raw_file_path", "")
        raw_saved = bool(row.get("raw_file_saved"))
        if raw_saved and (not raw_path or not Path(raw_path).exists()):
            errors.append(f"{sid} raw_file_saved true but raw_file_path missing or not found: {raw_path}")
        if not raw_saved:
            warnings.append(f"{sid} raw file not saved")

        text_path = row.get("extracted_text_path", "")
        text_saved = bool(row.get("extracted_text_saved"))
        if text_saved and (not text_path or not Path(text_path).exists()):
            errors.append(f"{sid} extracted_text_saved true but path missing or not found: {text_path}")
        if text_saved:
            length = row.get("extracted_text_length", 0)
            try:
                length = int(length)
            except Exception:
                errors.append(f"{sid} extracted_text_length is not integer-like: {length}")
                length = 0
            if length < 200:
                warnings.append(f"{sid} extracted text is short: {length}")
        else:
            warnings.append(f"{sid} text not extracted")

        if row.get("status") != "ok":
            warnings.append(f"{sid} status is not ok: {row.get('status')}")

    return {
        "source_records": len(rows),
        "document_type_counts": dict(Counter(row.get("document_type") for row in rows)),
        "status_counts": dict(Counter(row.get("status") for row in rows)),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate reservoir source inventory JSONL.")
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    summary = validate(load_jsonl(args.inventory))
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    if summary["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
