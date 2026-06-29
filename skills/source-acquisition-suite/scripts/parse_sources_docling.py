"""Parse source-inventory PDF files with Docling.

This script is a Layer 1 parser: it preserves source traceability and creates
structured markdown for later KU extraction. It does not extract KUs.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "source"


def load_docling_converter():
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ImportError as exc:
        raise RuntimeError(
            "Docling is not installed in this Python environment. "
            "Install it with: python -m pip install docling"
        ) from exc

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = False

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )


def parse_pdf(converter: Any, raw_path: Path) -> str:
    result = converter.convert(raw_path)
    return result.document.export_to_markdown()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True, help="Source inventory JSONL.")
    parser.add_argument(
        "--out-dir",
        required=True,
        help="Directory where Docling markdown files will be written.",
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="JSONL parse manifest path.",
    )
    parser.add_argument(
        "--include-non-pdf",
        action="store_true",
        help="Record skipped non-PDF sources in the manifest.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=180,
        help="Per-PDF timeout when running Docling in isolated subprocess mode.",
    )
    parser.add_argument(
        "--parse-one",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument("--raw-path", help=argparse.SUPPRESS)
    parser.add_argument("--out-path", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.parse_one:
        if not args.raw_path or not args.out_path:
            raise ValueError("--parse-one requires --raw-path and --out-path")
        converter = load_docling_converter()
        markdown = parse_pdf(converter, Path(args.raw_path))
        Path(args.out_path).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_path).write_text(markdown, encoding="utf-8", newline="\n")
        print(json.dumps({"parsed_markdown_length": len(markdown)}))
        return 0

    inventory_path = Path(args.inventory)
    out_dir = Path(args.out_dir)
    manifest_path = Path(args.manifest)
    records = read_jsonl(inventory_path)

    manifest: list[dict[str, Any]] = []

    for record in records:
        source_id = str(record.get("source_id", "")).strip()
        raw_file_path = str(record.get("raw_file_path", "")).strip()
        raw_path = Path(raw_file_path) if raw_file_path else None
        suffix = raw_path.suffix.lower() if raw_path else ""

        base_manifest = {
            "source_id": source_id,
            "title": record.get("title", ""),
            "source_tier": record.get("source_tier", ""),
            "raw_file_path": raw_file_path,
            "parser": "docling_light_pdf",
            "ocr_enabled": False,
            "table_structure_enabled": False,
        }

        if suffix != ".pdf":
            if args.include_non_pdf:
                manifest.append(
                    {
                        **base_manifest,
                        "status": "skipped",
                        "reason": "non_pdf_source",
                    }
                )
            continue

        if not raw_path or not raw_path.exists():
            manifest.append(
                {
                    **base_manifest,
                    "status": "error",
                    "reason": "missing_raw_file",
                    "parsed_markdown_path": "",
                    "parsed_markdown_length": 0,
                }
            )
            continue

        out_path = out_dir / f"{safe_slug(source_id)}_{safe_slug(raw_path.stem)}.md"
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--inventory",
                    str(inventory_path),
                    "--out-dir",
                    str(out_dir),
                    "--manifest",
                    str(manifest_path),
                    "--parse-one",
                    "--raw-path",
                    str(raw_path),
                    "--out-path",
                    str(out_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=args.timeout_seconds,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    (completed.stderr or completed.stdout or "Docling subprocess failed").strip()
                )
            markdown_length = len(out_path.read_text(encoding="utf-8")) if out_path.exists() else 0
            manifest.append(
                {
                    **base_manifest,
                    "status": "ok",
                    "reason": "",
                    "parsed_markdown_path": str(out_path),
                    "parsed_markdown_length": markdown_length,
                }
            )
        except subprocess.TimeoutExpired as exc:
            manifest.append(
                {
                    **base_manifest,
                    "status": "error",
                    "reason": "TimeoutExpired",
                    "error_message": str(exc),
                    "parsed_markdown_path": "",
                    "parsed_markdown_length": 0,
                }
            )
        except Exception as exc:  # noqa: BLE001 - manifest should capture parser failures.
            manifest.append(
                {
                    **base_manifest,
                    "status": "error",
                    "reason": type(exc).__name__,
                    "error_message": str(exc),
                    "parsed_markdown_path": "",
                    "parsed_markdown_length": 0,
                }
            )

    write_jsonl(manifest_path, manifest)
    status_counts: dict[str, int] = {}
    for item in manifest:
        status = str(item.get("status", "unknown"))
        status_counts[status] = status_counts.get(status, 0) + 1
    print(
        json.dumps(
            {
                "inventory": str(inventory_path),
                "out_dir": str(out_dir),
                "manifest": str(manifest_path),
                "records": len(manifest),
                "status_counts": status_counts,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
