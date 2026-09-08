from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse, urlunparse


SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "source_inventory.schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
REQUIRED = set(SCHEMA["required"])
CANDIDATE_REQUIRED = {"candidate_id", "reservoir_id", "title", "url", "codex_use", "codex_tier", "codex_selection_reason"}
DOCUMENT_TYPES = set(SCHEMA["properties"]["document_type"]["enum"])
SOURCE_IMPORTANCE = set(SCHEMA["properties"]["source_importance"]["enum"])
CONTENT_QUALITY = set(SCHEMA["properties"]["content_quality"]["enum"])
EU_READINESS = set(SCHEMA["properties"]["eu_readiness"]["enum"])


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


def validate(rows: list[dict], candidate_rows: list[dict] | None = None) -> dict:
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

        importance = str(row.get("source_importance", "")).strip()
        if not importance:
            warnings.append(f"{sid} missing source_importance; expected one of {sorted(SOURCE_IMPORTANCE)}")
        elif importance not in SOURCE_IMPORTANCE:
            warnings.append(f"{sid} invalid source_importance: {importance}")

        quality = str(row.get("content_quality", "")).strip()
        if quality and quality not in CONTENT_QUALITY:
            warnings.append(f"{sid} invalid content_quality: {quality}")

        readiness = str(row.get("eu_readiness", "")).strip()
        if not readiness:
            warnings.append(f"{sid} missing eu_readiness; expected one of {sorted(EU_READINESS)}")
        elif readiness not in EU_READINESS:
            warnings.append(f"{sid} invalid eu_readiness: {readiness}")

        cq_flag = str(row.get("content_quality_flag", "")).strip()
        if cq_flag and any(token in cq_flag for token in ["short", "paywall", "redirect", "failed"]):
            if readiness == "ready":
                warnings.append(f"{sid} has content_quality_flag={cq_flag} but eu_readiness=ready")

    candidate_rows = candidate_rows or []
    candidate_ids: set[str] = set()
    for number, row in enumerate(candidate_rows, 1):
        candidate_id = str(row.get("candidate_id") or f"row-{number}")
        missing = CANDIDATE_REQUIRED - row.keys()
        if missing:
            errors.append(f"candidate {candidate_id} missing fields: {sorted(missing)}")
        if candidate_id in candidate_ids:
            errors.append(f"duplicate candidate_id: {candidate_id}")
        candidate_ids.add(candidate_id)
        if row.get("codex_use") not in {"Y", "N"}:
            errors.append(f"candidate {candidate_id} codex_use must be Y or N")
        if row.get("codex_tier") not in {"A", "B", "C"}:
            errors.append(f"candidate {candidate_id} codex_tier must be A, B, or C")
    if candidate_rows and not any(row.get("codex_use") == "Y" for row in candidate_rows):
        warnings.append("candidate inventory contains no Codex-selected source")

    acquisition_issues = [
        warning for warning in warnings
        if "raw file not saved" in warning or "text not extracted" in warning or "status is not ok" in warning
    ]
    return {
        "source_records": len(rows),
        "candidate_records": len(candidate_rows),
        "document_type_counts": dict(Counter(row.get("document_type") for row in rows)),
        "status_counts": dict(Counter(row.get("status") for row in rows)),
        "source_importance_counts": dict(Counter(row.get("source_importance", "") for row in rows)),
        "eu_readiness_counts": dict(Counter(row.get("eu_readiness", "") for row in rows)),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "stage": "source_acquisition",
        "status": "fail" if errors else "warning" if warnings else "pass",
        "automated_validation": {
            "schema_conformance": {
                "name": "schema_conformance",
                "status": "fail" if errors else "pass",
                "issue_count": len(errors),
            },
            "traceability_or_acquisition": {
                "name": "acquisition_success",
                "status": "warning" if acquisition_issues else "pass",
                "issue_count": len(acquisition_issues),
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate reservoir source inventory JSONL.")
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--candidate-inventory", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    summary = validate(load_jsonl(args.inventory), load_jsonl(args.candidate_inventory) if args.candidate_inventory else None)
    text = json.dumps(summary, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text)
    if summary["error_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
