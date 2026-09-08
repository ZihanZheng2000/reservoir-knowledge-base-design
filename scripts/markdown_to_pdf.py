#!/usr/bin/env python
"""Convert a Markdown paper to PDF through Pandoc HTML and Chrome print.

The script intentionally keeps conversion separate from editing. If a section
contains long display equations, especially in appendices, edit the Markdown to
use shorter formulas, lists, or prose definitions before running this script.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_INPUT = Path("docs/ai-native-framework-for-reservoir-operation-kb.md")
DEFAULT_OUTPUT = Path("docs/ai-native-framework-for-reservoir-operation-kb.pdf")
TEMP_DIR = Path("tmp/pdfs")


def find_chrome() -> str:
    candidates = [
        shutil.which("chrome"),
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("msedge"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise FileNotFoundError("Chrome or Edge executable was not found.")


def require_tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise FileNotFoundError(f"Required tool not found on PATH: {name}")
    return path


def build_css(font_size: float, table_font_size: float, margin_in: float) -> str:
    return f"""
@page {{
  size: letter;
  margin: {margin_in}in;
}}

html {{
  font-size: {font_size}pt;
}}

body {{
  margin: 0;
  color: #111;
  font-family: Georgia, "Times New Roman", serif;
  line-height: 1.42;
}}

h1 {{
  font-size: {font_size * 1.75:.2f}pt;
  line-height: 1.16;
  margin: 0 0 0.24in;
}}

h2 {{
  font-size: {font_size * 1.27:.2f}pt;
  line-height: 1.2;
  margin: 0.24in 0 0.09in;
}}

h3 {{
  font-size: {font_size * 1.07:.2f}pt;
  line-height: 1.2;
  margin: 0.18in 0 0.07in;
}}

p {{
  margin: 0 0 0.11in;
}}

table {{
  width: 100%;
  margin: 0.14in 0 0.2in 0;
  border-collapse: collapse;
  table-layout: auto;
  font-size: {table_font_size}pt;
  line-height: 1.28;
}}

th,
td {{
  padding: 5pt 7pt;
  vertical-align: top;
  text-align: left;
  border-top: 0.5pt solid #333;
  border-bottom: 0.5pt solid #aaa;
}}

th {{
  font-weight: 700;
}}

table th:first-child,
table td:first-child {{
  width: 1%;
  white-space: nowrap;
}}

table:nth-of-type(1) th:nth-child(1),
table:nth-of-type(1) td:nth-child(1) {{
  width: 12%;
}}

table:nth-of-type(1) th:nth-child(2),
table:nth-of-type(1) td:nth-child(2) {{
  width: 22%;
}}

table:nth-of-type(1) th:nth-child(3),
table:nth-of-type(1) td:nth-child(3) {{
  width: 30%;
}}

table:nth-of-type(1) th:nth-child(4),
table:nth-of-type(1) td:nth-child(4) {{
  width: 36%;
}}

table:nth-of-type(2) th:nth-child(1),
table:nth-of-type(2) td:nth-child(1) {{
  width: 8%;
}}

table:nth-of-type(2) th:nth-child(2),
table:nth-of-type(2) td:nth-child(2) {{
  width: 92%;
}}

code {{
  font-family: Consolas, "Liberation Mono", monospace;
  font-size: 0.92em;
  overflow-wrap: anywhere;
  word-break: break-word;
  white-space: normal;
}}

pre {{
  border: 0.5pt solid #ddd;
  padding: 7pt;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
  font-size: {table_font_size}pt;
  line-height: 1.3;
}}

pre code {{
  display: block;
  font-size: 1em;
  overflow-wrap: anywhere;
  white-space: pre-wrap;
}}

math[display="block"] {{
  margin: 0.14in 0;
}}
"""


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def render_check(pdf_path: Path) -> None:
    try:
        import fitz  # type: ignore
    except ImportError:
        print("PyMuPDF is not installed; skipped render validation.")
        return

    doc = fitz.open(pdf_path)
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(0.35, 0.35), alpha=False)
        if pix.width <= 0 or pix.height <= 0:
            raise RuntimeError(f"Bad render on page {page.number + 1}")
    print(f"Render validation passed: {len(doc)} pages.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--font-size", type=float, default=12.0)
    parser.add_argument("--table-font-size", type=float, default=10.5)
    parser.add_argument("--margin", type=float, default=0.75)
    parser.add_argument("--keep-html", action="store_true")
    parser.add_argument("--skip-render-check", action="store_true")
    args = parser.parse_args()

    md_path = args.input
    pdf_path = args.output
    if not md_path.exists():
        raise FileNotFoundError(md_path)

    pandoc = require_tool("pandoc")
    chrome = find_chrome()
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    css_path = TEMP_DIR / f"{md_path.stem}.css"
    html_path = TEMP_DIR / f"{md_path.stem}.html"

    css_path.write_text(
        build_css(args.font_size, args.table_font_size, args.margin),
        encoding="utf-8",
    )
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    run(
        [
            pandoc,
            str(md_path),
            "--from",
            "markdown+tex_math_single_backslash+tex_math_dollars",
            "--standalone",
            "--embed-resources",
            "--mathml",
            "-t",
            "html5",
            "--css",
            str(css_path),
            "-o",
            str(html_path),
        ]
    )

    html_url = html_path.resolve().as_uri()
    run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path.resolve()}",
            html_url,
        ]
    )

    if not args.skip_render_check:
        render_check(pdf_path)

    if not args.keep_html:
        html_path.unlink(missing_ok=True)
        css_path.unlink(missing_ok=True)

    print(f"Wrote {pdf_path.resolve()}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
