"""Build an auditable source-selection ledger and precision/recall metrics."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse, urlunparse


RELEVANT = {"relevant", "include", "yes", "1"}
NOT_RELEVANT = {"not_relevant", "exclude", "no", "0"}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def canonical_url(url: str) -> str:
    parsed = urlparse(url.strip())
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), "", parsed.query, ""))


def group_id(source: dict) -> str:
    return str(source.get("recovery_attempt_for") or source["source_id"])


def group_sources(manifest: list[dict], inventory: list[dict]) -> list[dict]:
    inventory_by_id = {row["source_id"]: row for row in inventory}
    groups: dict[str, list[dict]] = {}
    for source in manifest:
        groups.setdefault(group_id(source), []).append(source)

    rows = []
    for root_id, sources in groups.items():
        primary = next((source for source in sources if source["source_id"] == root_id), sources[0])
        inventory_rows = [inventory_by_id[source["source_id"]] for source in sources if source["source_id"] in inventory_by_id]
        successful = [row for row in inventory_rows if row.get("status") == "ok"]
        ready = [row for row in successful if row.get("eu_readiness") == "ready"]
        file_name = Path(successful[0]["raw_file_path"]).name if successful and successful[0].get("raw_file_path") else ""
        download_status = "eu_ready" if ready else ("downloaded_not_eu_ready" if successful else "download_failed")
        rows.append({
            "candidate_id": f"SOURCE:{root_id}",
            "evaluation_unit_id": f"SOURCE:{root_id}",
            "file_name": file_name,
            "title": primary["title"],
            "url": primary["url"],
            "discovery_origin": "codex_curated_source_manifest",
            "codex_should_use": "yes",
            "codex_actual_selection": "selected_for_download",
            "codex_heuristic_recommendation": "",
            "codex_decision_reason": primary.get("selection_reason", ""),
            "source_ids": ";".join(source["source_id"] for source in sources),
            "download_attempt_count": len(inventory_rows),
            "successful_download_count": len(successful),
            "eu_ready_source_count": len(ready),
            "download_status": download_status,
            "source_tier": primary.get("source_tier", ""),
        })
    return rows


def openalex_rows(path: Path, selected_urls: set[str]) -> list[dict]:
    rows = []
    for candidate in load_jsonl(path):
        url = candidate.get("url") or candidate.get("oa_url") or candidate.get("primary_location") or ""
        if url and canonical_url(url) in selected_urls:
            continue
        candidate_id = candidate.get("candidate_id") or candidate.get("openalex_id") or candidate["title"]
        rows.append({
            "candidate_id": f"OPENALEX:{candidate_id}",
            "evaluation_unit_id": f"OPENALEX:{candidate_id}",
            "file_name": "",
            "title": candidate.get("title", ""),
            "url": url,
            "discovery_origin": "openalex_search",
            "codex_should_use": "no",
            "codex_actual_selection": "not_selected_within_logged_universe",
            "codex_heuristic_recommendation": candidate.get("recommended_action", ""),
            "codex_decision_reason": "Not added to the approved source manifest during this run.",
            "source_ids": "",
            "download_attempt_count": 0,
            "successful_download_count": 0,
            "eu_ready_source_count": 0,
            "download_status": "not_downloaded",
            "source_tier": candidate.get("source_tier_suggestion", ""),
        })
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


REVIEW_FIELDS = [
    "candidate_id", "evaluation_unit_id", "file_name", "title", "url", "source_ids",
    "discovery_origin", "source_tier", "codex_should_use", "codex_actual_selection",
    "codex_heuristic_recommendation", "codex_decision_reason", "download_status",
    "download_attempt_count", "successful_download_count", "eu_ready_source_count",
    "human_final_use", "human_reason", "reviewer_id", "adjudicated_relevance",
    "include_in_metrics",
]


def write_review_template(path: Path, rows: list[dict]) -> None:
    if path.exists():
        existing = list(csv.DictReader(path.open(encoding="utf-8")))
        labels = ["human_final_use", "human_selection", "human_relevance_label", "adjudicated_relevance"]
        if any((record.get(field) or "").strip() for record in existing for field in labels):
            return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "human_final_use": "", "human_reason": "", "reviewer_id": "", "adjudicated_relevance": "", "include_in_metrics": "yes"})


def label(row: dict) -> str:
    value = (row.get("adjudicated_relevance") or row.get("human_final_use") or row.get("human_relevance_label") or "").strip().lower()
    if value in RELEVANT:
        return "relevant"
    if value in NOT_RELEVANT:
        return "not_relevant"
    return "unlabeled"


def compute_metrics(rows: list[dict], review_path: Path, source_groups: list[dict], manifest: list[dict], inventory: list[dict]) -> dict:
    review_rows = list(csv.DictReader(review_path.open(encoding="utf-8"))) if review_path.exists() else []
    review_by_id = {row["candidate_id"]: row for row in review_rows}
    labeled = []
    selected_unlabeled = 0
    for row in rows:
        review = review_by_id.get(row["candidate_id"], {})
        if (review.get("include_in_metrics") or "yes").strip().lower() == "no":
            continue
        state = label(review)
        selected = row["codex_actual_selection"] == "selected_for_download"
        if state == "unlabeled":
            if selected:
                selected_unlabeled += 1
            continue
        labeled.append((selected, state == "relevant"))

    confusion = Counter()
    for selected, relevant in labeled:
        confusion[(selected, relevant)] += 1
    tp = confusion[(True, True)]
    fp = confusion[(True, False)]
    fn = confusion[(False, True)]
    tn = confusion[(False, False)]
    eligible_count = sum(1 for row in rows if (review_by_id.get(row["candidate_id"], {}).get("include_in_metrics") or "yes").strip().lower() != "no")
    all_labeled = len(labeled) == eligible_count
    precision = None if selected_unlabeled else (tp / (tp + fp) if tp + fp else None)
    recall = (tp / (tp + fn)) if all_labeled and tp + fn else None
    f1 = (2 * precision * recall / (precision + recall)) if precision is not None and recall is not None and precision + recall else None

    selected_group_count = len(source_groups)
    groups_downloaded = sum(1 for row in source_groups if row["successful_download_count"] > 0)
    groups_ready = sum(1 for row in source_groups if row["eu_ready_source_count"] > 0)
    attempt_success = sum(1 for row in inventory if row.get("status") == "ok")
    return {
        "metric_status": "complete" if all_labeled else "awaiting_human_labels",
        "candidate_universe": {
            "definition": "Frozen union of logged OpenAlex candidates and Codex-curated source groups; it does not estimate recall beyond logged discovery routes.",
            "count": len(rows),
            "human_labeled_count": len(labeled),
            "human_label_coverage": len(labeled) / eligible_count if eligible_count else None,
        },
        "codex_vs_human_selection": {
            "true_positive": tp if not selected_unlabeled else None,
            "false_positive": fp if not selected_unlabeled else None,
            "false_negative": fn if all_labeled else None,
            "true_negative": tn if all_labeled else None,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "precision_status": "available" if precision is not None else "awaiting_labels_for_codex_selected_candidates",
            "recall_status": "available" if recall is not None else "awaiting_labels_for_all_candidates",
        },
        "acquisition_funnel": {
            "codex_selected_unique_document_groups": selected_group_count,
            "downloaded_unique_document_groups": groups_downloaded,
            "download_success_rate_by_document_group": groups_downloaded / selected_group_count if selected_group_count else None,
            "eu_ready_unique_document_groups": groups_ready,
            "eu_ready_rate_given_downloaded_group": groups_ready / groups_downloaded if groups_downloaded else None,
            "download_attempt_records": len(manifest),
            "successful_download_attempt_records": attempt_success,
            "download_success_rate_by_attempt": attempt_success / len(manifest) if manifest else None,
            "used_in_evidence_units": None,
            "usage_status": "not_run",
        },
        "definitions": {
            "precision": "human-relevant candidates selected by Codex / all candidates selected by Codex",
            "recall": "human-relevant candidates selected by Codex / all human-relevant candidates in the frozen candidate universe",
            "human_gold": "adjudicated_relevance when present; otherwise human_relevance_label",
        },
    }


def write_metrics_csv(path: Path, metrics: dict) -> None:
    selection = metrics["codex_vs_human_selection"]
    funnel = metrics["acquisition_funnel"]
    universe = metrics["candidate_universe"]
    rows = [
        {"metric": "candidate_universe_count", "value": universe["count"], "status": metrics["metric_status"]},
        {"metric": "human_label_coverage", "value": universe["human_label_coverage"], "status": metrics["metric_status"]},
        {"metric": "precision", "value": selection["precision"], "status": selection["precision_status"]},
        {"metric": "recall", "value": selection["recall"], "status": selection["recall_status"]},
        {"metric": "f1", "value": selection["f1"], "status": metrics["metric_status"]},
        {"metric": "codex_selected_unique_document_groups", "value": funnel["codex_selected_unique_document_groups"], "status": "available"},
        {"metric": "download_success_rate_by_document_group", "value": funnel["download_success_rate_by_document_group"], "status": "available"},
        {"metric": "download_success_rate_by_attempt", "value": funnel["download_success_rate_by_attempt"], "status": "available"},
        {"metric": "eu_ready_rate_given_downloaded_group", "value": funnel["eu_ready_rate_given_downloaded_group"], "status": "available"},
        {"metric": "used_in_evidence_units", "value": funnel["used_in_evidence_units"], "status": funnel["usage_status"]},
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value", "status"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True, type=Path)
    args = parser.parse_args()
    run_dir = args.run_dir
    stage = run_dir / "01_source_acquisition"
    output_dir = run_dir / "validation/source_selection"
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((stage / "source_manifest.json").read_text(encoding="utf-8"))["sources"]
    inventory = load_jsonl(stage / "sources/source_inventory.jsonl")
    source_groups = group_sources(manifest, inventory)
    selected_urls = {canonical_url(source["url"]) for source in manifest if source.get("url")}
    candidates = source_groups + openalex_rows(stage / "deep_discovery/openalex_candidates.jsonl", selected_urls)
    candidates.sort(key=lambda row: (row["codex_actual_selection"] != "selected_for_download", row["candidate_id"]))
    write_jsonl(output_dir / "candidate_selection_ledger.jsonl", candidates)
    review_path = output_dir / "human_source_selection_review.csv"
    write_review_template(review_path, candidates)
    metrics = compute_metrics(candidates, review_path, source_groups, manifest, inventory)
    (output_dir / "source_selection_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_metrics_csv(output_dir / "source_selection_metrics.csv", metrics)
    print(json.dumps({"candidate_count": len(candidates), "source_group_count": len(source_groups), "review_path": str(review_path), "metrics_path": str(output_dir / 'source_selection_metrics.json')}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
