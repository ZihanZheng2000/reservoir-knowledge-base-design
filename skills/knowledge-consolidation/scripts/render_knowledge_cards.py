"""Render Knowledge Card JSONL into a human-readable Markdown reading view."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def render(cards: list[dict], title: str) -> str:
    lines = [f"# {title}", "", f"Total Knowledge Cards: {len(cards)}", ""]
    for card in cards:
        lines.extend([
            f"## {card.get('knowledge_card_id', '')} — {card.get('title', '')}",
            "",
            f"- Operational question: {card.get('operational_question', '')}",
            f"- Engineering dimension: {card.get('engineering_dimension', '')}",
            f"- Consolidation type: {card.get('consolidation_type', '')}",
            f"- Consolidated finding: {card.get('consolidated_finding', '')}",
            f"- Supporting EUs: {', '.join(f'`{eu_id}`' for eu_id in card.get('based_on_eu_ids', []))}",
            f"- Source coverage: {card.get('source_coverage_note', '')}",
            f"- Confidence: {card.get('confidence', '')}",
        ])
        if card.get("notes"):
            lines.append(f"- Note: {card['notes']}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Knowledge Card Markdown reading view.")
    parser.add_argument("--knowledge-cards", required=True, type=Path, help="knowledge_cards.jsonl")
    parser.add_argument("--out-md", required=True, type=Path, help="Markdown reading view output")
    parser.add_argument("--title", default="Knowledge Cards")
    args = parser.parse_args()

    cards = load_jsonl(args.knowledge_cards)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render(cards, args.title), encoding="utf-8")
    print(json.dumps({"knowledge_card_records": len(cards), "out_md": str(args.out_md)}))


if __name__ == "__main__":
    main()
