# Source Preservation And Parsing Protocol

## Purpose

Turn approved sources into a preserved, validated Layer 1 evidence set.

## Required Outputs

- raw files in `sources/raw/`
- extracted text in `sources/text/`
- source inventory JSONL and CSV
- Docling structured markdown for PDFs when available
- parse manifest
- validation report
- run summary

## Preservation Rules

- Preserve the raw file or landing page used as source evidence.
- Record URL, host, owner, document type, tier, selection reason, access date, and content hash.
- Dedupe by canonical URL, title/owner, PDF filename, document ID, and raw content hash.
- Do not silently drop failed sources. Record status and reason.
- Treat paywalled library records as discovery leads unless an accessible full text can be preserved.
- Do not treat all short text or PDF URLs returning HTML as automatic failures. HTML landing pages, abstracts, notices, and short official pages may still contain useful evidence.
- Separate acquisition status from content quality:
  - `status` records whether the file was downloaded and preserved.
  - `content_quality_flag` records whether the preserved content needs review before KU extraction.
  - `followup_action` records what the agent should try next.
- When acquisition fails, content is too short to assess, or a PDF URL returns HTML that appears to be a paywall/redirect/access-denied page, Codex should attempt source recovery before giving up. Recovery actions include searching for:
  - DOI landing pages;
  - publisher HTML full text;
  - official agency mirrors;
  - university or repository copies;
  - OpenAlex open-access URLs;
  - Crossref metadata;
  - report title plus `PDF`;
  - replacement sources covering the same evidence need.

## Parsing Rules

- HTML: save raw HTML and extract readable text while expecting some navigation noise.
- PDF: first extract plain text for robustness; then use Docling structured markdown when available.
- Data/API: preserve landing page and describe fields, temporal coverage, update frequency, and access path.
- Scanned/image-heavy PDF: mark OCR required or fallback to plain text/manual extraction.

## Docling Policy

Run Docling in lightweight mode by default:

- OCR off
- table-structure recognition off
- one PDF per subprocess when possible

If Docling fails, keep the raw PDF and plain text extraction. Mark the parse failure in `docling_parse_manifest.jsonl` and allow KU extraction to fall back to plain text.

## Validation Checklist

- Every source has stable ID, tier, document type, URL, owner, and selection reason.
- Raw file and extracted text are saved or a failure status is recorded.
- Short, HTML-returned, or suspected paywall records include content-quality flags and follow-up actions.
- Source tiers match source roles.
- Failed downloads or parser failures are documented.
- Failed or low-quality sources have been considered for alternate-source search before the evidence family is treated as unavailable.
- A later researcher can return to the original source.
