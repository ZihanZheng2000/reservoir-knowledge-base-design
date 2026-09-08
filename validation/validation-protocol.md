# Validation Protocol

Use [`docs/validation-framework.md`](../docs/validation-framework.md) as the
authoritative protocol for every routine run.

This directory may hold study-specific protocol addenda for method comparison,
benchmark construction, reviewer blinding, or transfer validation. Such an
addendum must state its study ID, preserve raw judgments, and remain compatible
with the six-stage matrix:

- two automated indicators per stage: schema conformance plus traceability
  integrity; Source acquisition uses acquisition success instead;
- three human-review indicators per stage, as specified in the framework.

Do not use legacy KU/F2 or `retrieval/indexing` terminology as the routine
workflow contract. Retrieval evaluation is an optional human-review activity
after the Indexing construction stage.
