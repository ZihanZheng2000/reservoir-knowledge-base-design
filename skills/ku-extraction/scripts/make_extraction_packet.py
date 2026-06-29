"""Create full-coverage reservoir KU extraction packets from source inventory."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_parse_manifest(path: Path | None) -> dict[str, dict]:
    if not path or not path.exists():
        return {}
    rows = load_jsonl(path)
    parsed = {}
    for row in rows:
        if row.get("status") == "ok" and row.get("parsed_markdown_path"):
            parsed[row["source_id"]] = row
    return parsed


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_chunks(text: str, max_chars: int, overlap_chars: int) -> list[tuple[int, int, str]]:
    """Split full text into overlapping chunks without dropping the tail.

    This is a plain-text fallback. Prefer page/section-aware parsing upstream
    when PDF or HTML structure is available.
    """
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if overlap_chars < 0:
        raise ValueError("overlap_chars must be non-negative")
    if overlap_chars >= max_chars:
        raise ValueError("overlap_chars must be smaller than max_chars")

    chunks: list[tuple[int, int, str]] = []
    start = 0
    n = len(text)
    while start < n:
        hard_end = min(start + max_chars, n)
        end = hard_end
        if hard_end < n:
            window = text[start:hard_end]
            split_at = max(window.rfind("\n\n"), window.rfind(". "), window.rfind("; "))
            min_size = int(max_chars * 0.6)
            if split_at >= min_size:
                end = start + split_at + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append((start, end, chunk))
        if end >= n:
            break
        start = max(0, end - overlap_chars)
    return chunks


def select_text_path(source: dict, parse_manifest: dict[str, dict]) -> tuple[Path, str, str]:
    parsed = parse_manifest.get(source["source_id"])
    if parsed:
        parsed_path = Path(parsed["parsed_markdown_path"])
        if parsed_path.exists():
            return parsed_path, "docling_structured_markdown", "Docling markdown preferred over extracted plain text."
    return Path(source["extracted_text_path"]), "plain_text_extracted_full_coverage", "No parser output available; using extracted text."


def make_packets(source: dict, max_chars: int, overlap_chars: int, parse_manifest: dict[str, dict]) -> list[dict]:
    text_path, text_basis, text_note = select_text_path(source, parse_manifest)
    text = normalize_text(text_path.read_text(encoding="utf-8", errors="replace"))
    chunks = split_chunks(text, max_chars=max_chars, overlap_chars=overlap_chars)
    packets = []
    for idx, (start, end, chunk) in enumerate(chunks, start=1):
        chunk_id = f"{source['source_id']}-CHUNK-{idx:03d}"
        packets.append(
            {
                "source_id": source["source_id"],
                "reservoir_id": source.get("reservoir_id", ""),
                "reservoir_name": source.get("reservoir_name", ""),
                "title": source.get("title", ""),
                "url": source.get("url", ""),
                "official_owner": source.get("official_owner", ""),
                "document_type": source.get("document_type", ""),
                "raw_host": source.get("raw_host", ""),
                "access_date": source.get("access_date", ""),
                "selection_reason": source.get("selection_reason", ""),
                "text_path": str(text_path),
                "text_basis": text_basis,
                "text_length": len(text),
                "chunk_id": chunk_id,
                "chunk_index": idx,
                "chunk_count": len(chunks),
                "char_start": start,
                "char_end": end,
                "chunk_text": chunk,
                "packet_text": chunk,
                "packet_truncated": False,
                "chunking_method": f"{text_basis}_overlapping_chunks",
                "chunking_note": text_note,
            }
        )
    return packets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", required=True, help="Path to source inventory JSONL")
    parser.add_argument("--out", required=True, help="Output JSONL path")
    parser.add_argument("--parse-manifest", help="Optional Docling parse manifest JSONL")
    parser.add_argument("--max-chars", type=int, default=10000)
    parser.add_argument("--overlap-chars", type=int, default=1000)
    args = parser.parse_args()

    inventory = load_jsonl(Path(args.inventory))
    parse_manifest = load_parse_manifest(Path(args.parse_manifest) if args.parse_manifest else None)
    packets = []
    for src in inventory:
        if src.get("status") == "ok":
            packets.extend(make_packets(src, args.max_chars, args.overlap_chars, parse_manifest))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for packet in packets:
            f.write(json.dumps(packet, ensure_ascii=False, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "packets": len(packets),
                "sources": len({packet["source_id"] for packet in packets}),
                "docling_sources": len(
                    {packet["source_id"] for packet in packets if packet.get("text_basis") == "docling_structured_markdown"}
                ),
                "out": str(out),
                "max_chars": args.max_chars,
                "overlap_chars": args.overlap_chars,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
