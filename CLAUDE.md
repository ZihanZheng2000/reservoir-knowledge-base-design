# Project Instructions For Claude

Follow [`AGENTS.md`](AGENTS.md) as the authoritative project instruction file.
It defines the active six-stage workflow, Evidence Unit / Knowledge Card /
Synthesis Card boundaries, run artifacts, and operational rules.

Use [`docs/validation-framework.md`](docs/validation-framework.md) as the
authoritative validation design:

- every stage completes two automated indicators before downstream use;
- Source acquisition uses schema conformance and acquisition success;
- later stages use schema conformance and traceability integrity;
- human review is a documented sampled evaluation using the stage-specific
  three criteria, not a routine gate unless explicitly requested.

Do not use legacy KU, five-stage, or retrieval-as-construction instructions
from historical documents or runs as the current workflow contract.
