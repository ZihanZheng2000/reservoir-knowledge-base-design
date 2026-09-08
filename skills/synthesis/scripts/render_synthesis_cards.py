"""Render Synthesis Card JSONL into a human-readable Markdown reading view."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def ids(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values)


def render(cards: list[dict], title: str) -> str:
    lines = [f"# {title}", "", f"Total Synthesis Cards: {len(cards)}", ""]
    for card in cards:
        lines.extend([
            f"## {card.get('synthesis_card_id', '')} — {card.get('title', '')}",
            "",
            f"- Primary pattern: {card.get('primary_pattern', '')}",
            f"- Secondary lenses: {', '.join(card.get('secondary_lenses', [])) or 'none'}",
            f"- Operational question: {card.get('operational_question', '')}",
            f"- Synthesis claim: {card.get('synthesis_claim', '')}",
            f"- Scope and conditions: {card.get('scope_and_conditions', '')}",
            "",
            "### Analysis chain",
            "",
        ])
        for index, step in enumerate(card.get("analysis_chain", []), start=1):
            lines.append(f"{index}. **{step.get('stage', '')}** — {step.get('statement', '')} Evidence: {ids(step.get('based_on_eu_ids', []))}.")
        lines.extend([
            "",
            "### Evidence and source check",
            "",
            f"- Supporting EUs: {ids(card.get('based_on_eu_ids', []))}",
            f"- Supporting KCs: {ids(card.get('based_on_knowledge_card_ids', [])) or 'none'}",
            f"- Evidence depth: {card.get('evidence_depth', '')}",
            f"- Source locators: {card.get('source_locator_summary', '')}",
            f"- Verification note: {card.get('source_verification_note', '')}",
            "",
            "### Limits and implication",
            "",
            f"- Uncertainty or exception: {card.get('uncertainty_or_exception', '')}",
            f"- Operational implication: {card.get('operational_implication', '')}",
            f"- Next step: {card.get('next_step', '')}",
            f"- Confidence: {card.get('confidence', '')}",
        ])
        if card.get("notes"):
            lines.append(f"- Note: {card['notes']}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Synthesis Card Markdown reading view.")
    parser.add_argument("--synthesis-cards", required=True, type=Path, help="synthesis_cards.jsonl")
    parser.add_argument("--out-md", required=True, type=Path, help="Markdown reading view output")
    parser.add_argument("--title", default="Synthesis Cards")
    args = parser.parse_args()

    cards = load_jsonl(args.synthesis_cards)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)
    args.out_md.write_text(render(cards, args.title), encoding="utf-8")
    print(json.dumps({"synthesis_card_records": len(cards), "out_md": str(args.out_md)}))


if __name__ == "__main__":
    main()
