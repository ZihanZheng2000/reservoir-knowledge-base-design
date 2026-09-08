# Canonical Data Schemas

This directory contains the canonical JSON Schema contracts for records written
by the six workflow stages. JSONL artifacts contain one object per line, and
each object must conform to the schema for its record type.

| Schema | Canonical artifact |
|---|---|
| `source_manifest.schema.json` | `01_source_acquisition/source_manifest.json` |
| `source_candidate_inventory.schema.json` | `01_source_acquisition/sources/candidate_inventory.jsonl` |
| `source_inventory.schema.json` | `01_source_acquisition/sources/source_inventory.jsonl` |
| `extraction_packet.schema.json` | intermediate only: `02_evidence_extraction/extraction_packets.jsonl` |
| `evidence_unit.schema.json` | `02_evidence_extraction/evidence_units.jsonl` |
| `knowledge_card.schema.json` | `03_knowledge_consolidation/knowledge_cards.jsonl` |
| `synthesis_card.schema.json` | `04_synthesis/synthesis_cards.jsonl` |
| `index_record.schema.json` | `05_indexing/encoded_knowledge_records.jsonl` |
| `index_manifest.schema.json` | `05_indexing/index_manifest.json` |
| `claim_evidence_map.schema.json` | `06_report_generation/claim_evidence_map.jsonl` |
| `run_manifest.schema.json` | `run_manifest.json` |
| `stage_manifest.schema.json` | `<numbered_stage>/stage_manifest.json` |

The Python validators additionally check cross-record relationships that JSON
Schema alone cannot establish: ID uniqueness, referenced EU/KC IDs, source IDs,
source-file availability, and source-context requirements.

These schemas are prospective contracts for new runs. Historical run artifacts
are not rewritten solely to match a newer schema.

Folder-level delivery requirements, canonical filenames, and the fixed
human-readable stage summary are defined in `docs/run-artifact-contract.md`.
The required reading views (`evidence_units.md`, `knowledge_cards.md`, and
`synthesis_cards.md`) mirror their JSONL records and are not separate schemas.
