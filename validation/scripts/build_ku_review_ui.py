#!/usr/bin/env python
"""Build a standalone KU review UI for human 0/1/2 scoring."""

from __future__ import annotations

import argparse
import csv
import html
import json
from pathlib import Path


SCORE_COLUMNS = [
    "usefulness_0_2",
    "faithfulness_0_2",
    "dimension_correctness_0_2",
]


def read_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                records.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{line_no}: invalid JSONL: {exc}") from exc
    return records


def read_review_csv(path: Path | None) -> dict[str, dict]:
    if not path or not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {row.get("ku_id", ""): row for row in rows if row.get("ku_id")}


def write_review_csv(path: Path, kus: list[dict], existing: dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "ku_id",
        "source_id",
        *SCORE_COLUMNS,
        "review_comment",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for ku in kus:
            old = existing.get(ku["ku_id"], {})
            writer.writerow(
                {
                    "ku_id": ku["ku_id"],
                    "source_id": ku.get("source_id", ""),
                    "usefulness_0_2": old.get("usefulness_0_2", ""),
                    "faithfulness_0_2": old.get("faithfulness_0_2", ""),
                    "dimension_correctness_0_2": old.get("dimension_correctness_0_2", ""),
                    "review_comment": old.get("review_comment", ""),
                }
            )


def source_map(path: Path | None) -> dict[str, dict]:
    if not path or not path.exists():
        return {}
    return {row.get("source_id", ""): row for row in read_jsonl(path)}


def rel_url(path_value: str, base_dir: Path) -> str:
    if not path_value:
        return ""
    path = Path(path_value)
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_uri()


def make_payload(kus: list[dict], sources: dict[str, dict], base_dir: Path) -> list[dict]:
    payload = []
    for ku in kus:
        source = sources.get(ku.get("source_id", ""), {})
        payload.append(
            {
                "ku_id": ku.get("ku_id", ""),
                "source_id": ku.get("source_id", ""),
                "source_tier": source.get("source_tier", ""),
                "source_title": ku.get("source_title") or source.get("title", ""),
                "source_url": ku.get("source_url") or source.get("url", ""),
                "raw_file": rel_url(source.get("raw_file_path", ""), base_dir),
                "text_file": rel_url(source.get("extracted_text_path", ""), base_dir),
                "document_type": ku.get("document_type", ""),
                "engineering_dimension": ku.get("engineering_dimension", ""),
                "finding": ku.get("finding", ""),
                "why_it_matters": ku.get("why_it_matters", ""),
                "evidence_quote": ku.get("evidence_quote", ""),
                "source_location": ku.get("source_location", ""),
                "confidence": ku.get("confidence", ""),
                "notes": ku.get("notes", ""),
            }
        )
    return payload


def render_html(payload: list[dict], existing: dict[str, dict], run_label: str) -> str:
    escaped_payload = json.dumps(payload, ensure_ascii=False)
    escaped_existing = json.dumps(existing, ensure_ascii=False)
    escaped_title = html.escape(run_label)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>KU Review UI - {escaped_title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f5f7fb;
      --panel: #ffffff;
      --ink: #172033;
      --muted: #647083;
      --line: #d9e0ea;
      --accent: #0f766e;
      --accent-soft: #d9f3ef;
      --warn: #8a5a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, "Segoe UI", Arial, sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header {{
      position: sticky;
      top: 0;
      z-index: 2;
      display: flex;
      gap: 16px;
      align-items: center;
      justify-content: space-between;
      padding: 12px 18px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0;
      font-size: 17px;
      font-weight: 650;
      letter-spacing: 0;
    }}
    main {{
      display: grid;
      grid-template-columns: 320px minmax(0, 1fr);
      min-height: calc(100vh - 58px);
    }}
    aside {{
      border-right: 1px solid var(--line);
      background: var(--panel);
      overflow: auto;
      max-height: calc(100vh - 58px);
    }}
    .filters {{
      position: sticky;
      top: 0;
      background: var(--panel);
      padding: 12px;
      border-bottom: 1px solid var(--line);
    }}
    input, select, textarea {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 9px;
      font: inherit;
      background: #fff;
      color: var(--ink);
    }}
    textarea {{
      resize: vertical;
      min-height: 72px;
    }}
    .filter-row {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-top: 8px;
    }}
    .list {{
      display: flex;
      flex-direction: column;
    }}
    .item {{
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      cursor: pointer;
    }}
    .item:hover, .item.active {{
      background: #eef6f5;
    }}
    .item-title {{
      display: flex;
      justify-content: space-between;
      gap: 8px;
      font-size: 13px;
      font-weight: 650;
    }}
    .item-meta, .small {{
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }}
    .done {{
      color: var(--accent);
      font-weight: 650;
    }}
    .content {{
      padding: 18px;
      overflow: auto;
      max-height: calc(100vh - 58px);
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.65fr);
      gap: 16px;
      align-items: start;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    h2 {{
      margin: 0 0 8px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    h3 {{
      margin: 16px 0 8px;
      font-size: 13px;
      text-transform: uppercase;
      color: var(--muted);
      letter-spacing: 0.04em;
    }}
    p {{
      margin: 0;
      line-height: 1.52;
    }}
    blockquote {{
      margin: 0;
      padding: 12px 14px;
      border-left: 4px solid var(--accent);
      background: #f0faf8;
      line-height: 1.55;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin: 10px 0 14px;
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 4px 8px;
      background: #eef1f5;
      color: #3d495a;
      font-size: 12px;
    }}
    .links {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }}
    a, button {{
      color: var(--accent);
    }}
    button {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      background: #fff;
      font: inherit;
      cursor: pointer;
    }}
    button.primary {{
      border-color: var(--accent);
      background: var(--accent);
      color: #fff;
    }}
    .score-row {{
      margin-bottom: 14px;
    }}
    .score-row label {{
      display: block;
      margin-bottom: 7px;
      font-weight: 650;
      font-size: 13px;
    }}
    .score-options {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7px;
    }}
    .score-options button {{
      color: var(--ink);
      min-height: 44px;
    }}
    .score-options button.selected {{
      border-color: var(--accent);
      background: var(--accent-soft);
      color: #064d48;
      font-weight: 700;
    }}
    .rubric {{
      margin-top: 4px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }}
    .toolbar {{
      display: flex;
      gap: 8px;
      align-items: center;
      justify-content: flex-end;
      flex-wrap: wrap;
    }}
    .status {{
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}
    .empty {{
      padding: 18px;
      color: var(--warn);
    }}
    @media (max-width: 900px) {{
      main, .grid {{
        grid-template-columns: 1fr;
      }}
      aside {{
        max-height: none;
        border-right: 0;
        border-bottom: 1px solid var(--line);
      }}
      .content {{
        max-height: none;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>KU Review UI - {escaped_title}</h1>
    <div class="toolbar">
      <span class="status" id="progress"></span>
      <button id="exportCsv" class="primary">Export CSV</button>
      <button id="clearLocal">Clear local scores</button>
    </div>
  </header>
  <main>
    <aside>
      <div class="filters">
        <input id="search" placeholder="Search KU, source, dimension, finding">
        <div class="filter-row">
          <select id="dimensionFilter"><option value="">All dimensions</option></select>
          <select id="sourceFilter"><option value="">All sources</option></select>
        </div>
      </div>
      <div class="list" id="kuList"></div>
    </aside>
    <section class="content">
      <div id="detail" class="empty">Select a KU to review.</div>
    </section>
  </main>
  <script>
    const KUS = {escaped_payload};
    const INITIAL_REVIEWS = {escaped_existing};
    const STORAGE_KEY = "ku-review-ui:" + location.pathname;
    const SCORE_FIELDS = ["usefulness_0_2", "faithfulness_0_2", "dimension_correctness_0_2"];
    const RUBRICS = {{
      usefulness_0_2: "0 = no use; 1 = maybe useful; 2 = clearly useful for retrieval, CKP, or synthesis",
      faithfulness_0_2: "0 = unsupported or shifted meaning; 1 = partly faithful but incomplete/imprecise; 2 = same meaning and scope as the source",
      dimension_correctness_0_2: "0 = wrong dimension; 1 = acceptable but another dimension also fits; 2 = clearly belongs here"
    }};
    const LABELS = {{
      usefulness_0_2: "Usefulness",
      faithfulness_0_2: "Faithfulness",
      dimension_correctness_0_2: "Dimension correctness"
    }};
    let reviews = loadReviews();
    let selectedId = KUS.length ? KUS[0].ku_id : "";

    function loadReviews() {{
      const base = {{}};
      for (const ku of KUS) {{
        const old = INITIAL_REVIEWS[ku.ku_id] || {{}};
        base[ku.ku_id] = {{
          ku_id: ku.ku_id,
          source_id: ku.source_id,
          usefulness_0_2: old.usefulness_0_2 || "",
          faithfulness_0_2: old.faithfulness_0_2 || "",
          dimension_correctness_0_2: old.dimension_correctness_0_2 || "",
          review_comment: old.review_comment || ""
        }};
      }}
      try {{
        const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{{}}");
        for (const [kuId, row] of Object.entries(saved)) {{
          if (base[kuId]) base[kuId] = {{ ...base[kuId], ...row }};
        }}
      }} catch (err) {{
        console.warn("Could not load local review state", err);
      }}
      return base;
    }}

    function saveReviews() {{
      localStorage.setItem(STORAGE_KEY, JSON.stringify(reviews));
      updateProgress();
      renderList();
    }}

    function escapeText(value) {{
      return String(value || "").replace(/[&<>"']/g, ch => ({{
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      }}[ch]));
    }}

    function populateFilters() {{
      const dim = document.getElementById("dimensionFilter");
      const src = document.getElementById("sourceFilter");
      [...new Set(KUS.map(k => k.engineering_dimension).filter(Boolean))].sort().forEach(value => {{
        dim.insertAdjacentHTML("beforeend", `<option value="${{escapeText(value)}}">${{escapeText(value)}}</option>`);
      }});
      [...new Set(KUS.map(k => k.source_id).filter(Boolean))].sort().forEach(value => {{
        src.insertAdjacentHTML("beforeend", `<option value="${{escapeText(value)}}">${{escapeText(value)}}</option>`);
      }});
    }}

    function filteredKus() {{
      const q = document.getElementById("search").value.trim().toLowerCase();
      const dim = document.getElementById("dimensionFilter").value;
      const src = document.getElementById("sourceFilter").value;
      return KUS.filter(ku => {{
        if (dim && ku.engineering_dimension !== dim) return false;
        if (src && ku.source_id !== src) return false;
        if (!q) return true;
        return [ku.ku_id, ku.source_id, ku.source_title, ku.engineering_dimension, ku.finding, ku.evidence_quote]
          .join(" ").toLowerCase().includes(q);
      }});
    }}

    function isDone(kuId) {{
      const row = reviews[kuId] || {{}};
      return SCORE_FIELDS.every(field => ["0", "1", "2"].includes(String(row[field])));
    }}

    function renderList() {{
      const list = document.getElementById("kuList");
      const rows = filteredKus();
      if (!rows.length) {{
        list.innerHTML = `<div class="empty">No KUs match the current filters.</div>`;
        return;
      }}
      list.innerHTML = rows.map(ku => `
        <div class="item ${{ku.ku_id === selectedId ? "active" : ""}}" data-ku-id="${{escapeText(ku.ku_id)}}">
          <div class="item-title">
            <span>${{escapeText(ku.ku_id)}}</span>
            <span class="${{isDone(ku.ku_id) ? "done" : ""}}">${{isDone(ku.ku_id) ? "done" : "open"}}</span>
          </div>
          <div class="item-meta">${{escapeText(ku.source_id)}} · ${{escapeText(ku.engineering_dimension)}}</div>
        </div>
      `).join("");
      list.querySelectorAll(".item").forEach(item => {{
        item.addEventListener("click", () => {{
          selectedId = item.dataset.kuId;
          renderList();
          renderDetail();
        }});
      }});
    }}

    function linkHtml(href, label) {{
      if (!href) return "";
      return `<a href="${{escapeText(href)}}" target="_blank" rel="noreferrer">${{escapeText(label)}}</a>`;
    }}

    function scoreControl(field, value) {{
      return `
        <div class="score-row">
          <label>${{LABELS[field]}}</label>
          <div class="score-options" data-field="${{field}}">
            ${{[0, 1, 2].map(score => `
              <button class="${{String(value) === String(score) ? "selected" : ""}}" data-score="${{score}}">${{score}}</button>
            `).join("")}}
          </div>
          <div class="rubric">${{RUBRICS[field]}}</div>
        </div>
      `;
    }}

    function renderDetail() {{
      const ku = KUS.find(row => row.ku_id === selectedId);
      const detail = document.getElementById("detail");
      if (!ku) {{
        detail.className = "empty";
        detail.textContent = "Select a KU to review.";
        return;
      }}
      const row = reviews[ku.ku_id];
      detail.className = "grid";
      detail.innerHTML = `
        <article class="card">
          <h2>${{escapeText(ku.ku_id)}}</h2>
          <div class="small">${{escapeText(ku.source_title)}}</div>
          <div class="meta">
            <span class="pill">${{escapeText(ku.source_id)}}</span>
            <span class="pill">${{escapeText(ku.source_tier || "tier unknown")}}</span>
            <span class="pill">${{escapeText(ku.document_type || "type unknown")}}</span>
            <span class="pill">${{escapeText(ku.engineering_dimension)}}</span>
            <span class="pill">confidence: ${{escapeText(ku.confidence || "unknown")}}</span>
          </div>

          <h3>Finding</h3>
          <p>${{escapeText(ku.finding)}}</p>

          <h3>Evidence Quote</h3>
          <blockquote>${{escapeText(ku.evidence_quote)}}</blockquote>
          <div class="small" style="margin-top:8px;">${{escapeText(ku.source_location)}}</div>

          <h3>Why It Matters</h3>
          <p>${{escapeText(ku.why_it_matters)}}</p>

          ${{ku.notes ? `<h3>Notes</h3><p>${{escapeText(ku.notes)}}</p>` : ""}}

          <div class="links">
            ${{linkHtml(ku.source_url, "Open source URL")}}
            ${{linkHtml(ku.raw_file, "Open raw file")}}
            ${{linkHtml(ku.text_file, "Open extracted text")}}
          </div>
        </article>
        <aside class="card">
          <h2>Human Review</h2>
          ${{SCORE_FIELDS.map(field => scoreControl(field, row[field])).join("")}}
          <label for="comment"><strong>Optional comment</strong></label>
          <textarea id="comment" placeholder="Only write when a score needs explanation.">${{escapeText(row.review_comment || "")}}</textarea>
          <div class="links">
            <button id="prevKu">Previous</button>
            <button id="nextKu" class="primary">Next</button>
          </div>
        </aside>
      `;
      detail.querySelectorAll(".score-options button").forEach(button => {{
        button.addEventListener("click", () => {{
          const field = button.parentElement.dataset.field;
          reviews[ku.ku_id][field] = button.dataset.score;
          saveReviews();
          renderDetail();
        }});
      }});
      detail.querySelector("#comment").addEventListener("input", event => {{
        reviews[ku.ku_id].review_comment = event.target.value;
        saveReviews();
      }});
      detail.querySelector("#prevKu").addEventListener("click", () => moveSelection(-1));
      detail.querySelector("#nextKu").addEventListener("click", () => moveSelection(1));
    }}

    function moveSelection(offset) {{
      const rows = filteredKus();
      const index = rows.findIndex(row => row.ku_id === selectedId);
      if (index === -1) return;
      const next = rows[Math.min(rows.length - 1, Math.max(0, index + offset))];
      selectedId = next.ku_id;
      renderList();
      renderDetail();
    }}

    function updateProgress() {{
      const done = KUS.filter(ku => isDone(ku.ku_id)).length;
      document.getElementById("progress").textContent = `${{done}} / ${{KUS.length}} reviewed`;
    }}

    function csvEscape(value) {{
      const text = String(value ?? "");
      return `"${{text.replace(/"/g, '""')}}"`;
    }}

    function exportCsv() {{
      const fields = ["ku_id", "source_id", ...SCORE_FIELDS, "review_comment"];
      const lines = [fields.map(csvEscape).join(",")];
      for (const ku of KUS) {{
        const row = reviews[ku.ku_id];
        lines.push(fields.map(field => csvEscape(row[field] || "")).join(","));
      }}
      const blob = new Blob([lines.join("\\n") + "\\n"], {{ type: "text/csv;charset=utf-8" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "human_ku_item_review_0_2.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }}

    document.getElementById("search").addEventListener("input", renderList);
    document.getElementById("dimensionFilter").addEventListener("change", renderList);
    document.getElementById("sourceFilter").addEventListener("change", renderList);
    document.getElementById("exportCsv").addEventListener("click", exportCsv);
    document.getElementById("clearLocal").addEventListener("click", () => {{
      if (!confirm("Clear saved scores in this browser for this review UI?")) return;
      localStorage.removeItem(STORAGE_KEY);
      reviews = loadReviews();
      renderList();
      renderDetail();
      updateProgress();
    }});
    document.addEventListener("keydown", event => {{
      if (event.target.matches("input, textarea, select")) return;
      if (event.key === "ArrowLeft") moveSelection(-1);
      if (event.key === "ArrowRight") moveSelection(1);
    }});

    populateFilters();
    renderList();
    renderDetail();
    updateProgress();
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kus", required=True, type=Path)
    parser.add_argument("--source-inventory", type=Path)
    parser.add_argument("--review-csv", type=Path)
    parser.add_argument("--out-html", required=True, type=Path)
    parser.add_argument("--out-csv", type=Path)
    parser.add_argument("--run-label", default="KU Review")
    args = parser.parse_args()

    kus = read_jsonl(args.kus)
    sources = source_map(args.source_inventory)
    existing = read_review_csv(args.review_csv)
    payload = make_payload(kus, sources, args.out_html.parent)

    args.out_html.parent.mkdir(parents=True, exist_ok=True)
    args.out_html.write_text(render_html(payload, existing, args.run_label), encoding="utf-8")
    if args.out_csv:
        write_review_csv(args.out_csv, kus, existing)

    print(f"Wrote {args.out_html}")
    if args.out_csv:
        print(f"Wrote {args.out_csv}")
    print(f"Included {len(kus)} KUs")


if __name__ == "__main__":
    main()
