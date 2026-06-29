# Proposal: An AI-Native Framework for Automatic Reservoir Operation Knowledge Base Construction

## 1. Background and Motivation

**Reservoir operation knowledge** is scattered across **heterogeneous sources**, including operator manuals, government reports, environmental assessments, journal articles, technical documents, datasets, and news articles. These sources differ substantially in structure, level of detail, perspective, reliability, and intended audience. They often emphasize different aspects of reservoir operations, contain overlapping or complementary information, and may present inconsistent or conflicting descriptions.

**Traditional retrieval systems** primarily index documents or text chunks and return relevant passages based on keyword or semantic matching. They still leave users responsible for reading, interpreting, comparing, and synthesizing information from multiple sources. When evidence is distributed across documents with different focuses or conflicting viewpoints, researchers must manually reconcile those differences to form a coherent understanding. This process is labor-intensive, difficult to scale, and prone to omissions or inconsistent interpretations.

This project aims to develop an **AI-native workflow** that automatically transforms heterogeneous textual sources into a **structured, validated, and traceable reservoir operation knowledge base**. The framework is designed to minimize manual effort after development while maintaining **transparency**, **evidence traceability**, and support for downstream **retrieval, reasoning, and report generation**.

## 2. Overall Framework

The proposed framework is organized around **five research objectives**: collecting reservoir-related public sources, extracting structured atomic **Knowledge Units (KUs)**, synthesizing document-level KUs into **refined cross-document knowledge representations**, building a **searchable knowledge base** for semantic retrieval and reasoning, and generating **human-readable reports** for inspection and downstream research.

These objectives are implemented through **five major stages**. **Validation** is not treated as a separate stage; instead, it is embedded throughout the workflow through **schema checks**, **source traceability checks**, **retrieval benchmarks**, and **manual review** on representative reservoirs.

| Step | Objective | Input | Output | Validation Focus |
|---|---|---|---|---|
| 1. Data Collection | Collect reservoir-related information from diverse public sources | Search results, curated URLs, source leads | Preserved source inventory and extracted text | Candidate Inclusion F2 Score, Source Family Accuracy |
| 2. Initial KU Extraction | Extract structured atomic KUs from unstructured documents | Individual documents and extracted text | Source-grounded initial KUs | KU Extraction F2 Score, Engineering Dimension Accuracy, Traceability Rate, Faithfulness Rate |
| 3. Knowledge Synthesis and Refined KU Generation | Synthesize document-level KUs into refined cross-document knowledge representations | Initial KUs and source locators | Refined KUs / synthesis cards | Synthesis F2 Score, Traceability Rate, Faithfulness Rate, Human Quality Score |
| 4. Embedding and Vector Database Construction | Build a searchable knowledge base for semantic retrieval and reasoning | Refined KUs and metadata | Searchable semantic index | Retrieval F2 Score, Traceability Rate |
| 5. Human-Readable Report Generation | Support automatic report generation for human inspection and downstream research | Refined KUs, synthesis cards, source metadata | Structured reservoir operation report | Traceability Rate, Faithfulness Rate, Human Quality Score |

At the implementation level, the framework is not only a conceptual pipeline. It is executed as a **repeatable AI-native workflow** in which **Codex** coordinates **project-specific skills**, **deterministic scripts**, **structured schemas**, and **validation gates**. Codex handles source discovery decisions, extraction prompting, synthesis reasoning, and report drafting, while **Python scripts** handle repeatable tasks such as source preservation, document parsing, packet construction, JSONL/schema validation, and artifact organization.

The central design principle is to separate **machine assistance** from **evidence authority**. AI models help transform, summarize, and synthesize information, but every generated output must preserve a **traceable path back to source documents** through source IDs, KU IDs, source locations, and evidence quotes. This makes the system inspectable rather than a black-box text generator.

## 3. Framework Stages

The following stages describe how the framework is implemented in practice. In this workflow, **Codex serves as the orchestration agent** rather than as a single text-generation model. It reads the **project protocols**, selects the appropriate **stage-specific skill**, runs supporting scripts, manages artifact folders, applies structured prompts, and checks validation outputs before moving to the next stage. This design allows the workflow to combine **flexible AI reasoning** with **repeatable engineering controls** such as schemas, local file preservation, JSONL records, and validation scripts.

### Step 1: Data Collection

The framework collects reservoir-related information from three clearly separated source families, defined by who produced or published the source:

- **Official sources:** materials published by reservoir operators, government agencies, regulatory bodies, or official data providers. Examples include operation manuals, agency reports, technical reports, management plans, environmental assessments, legal or policy documents, official data systems, and operator webpages.
- **Research sources:** materials produced by academic researchers, research institutes, universities, or scientific publishers. Examples include journal papers, conference papers, research articles, academic book chapters, and researcher-authored model or dataset papers.
- **Public and media sources:** materials produced for public communication rather than formal operation or research. Examples include news articles, public-facing explainers, stakeholder statements, interviews, media reports about droughts or floods, infrastructure incidents, policy negotiations, and operational controversies. 

The output is a **preserved document repository** for each reservoir. Each source is stored with metadata, raw-file preservation status, extracted-text path, source tier, document type, and selection rationale.

**Implementation method:**

- Define the reservoir name, operator, basin context, source families, and inclusion criteria, and assign a stable reservoir identifier to ensure that each reservoir is uniquely represented in the knowledge base.
- Use the **source-acquisition skill** and its source-acquisition protocol to build candidate source lists from official webpages, document repositories, scholarly metadata, and public media sources.
- **Deduplicate** candidate sources by URL, title, document identity, and content role.
- Save each accepted source locally as a **raw file**, parse it into text or structured markdown, and record it in a **source inventory**.
- Validate the inventory to ensure that required metadata fields exist and that raw and extracted files can be located.

### Step 2: Initial Knowledge Unit Extraction

Each document is processed independently to extract **atomic Knowledge Units**. An **initial KU** corresponds to a single factual statement obtained directly from one source without cross-document reasoning.

Formal KU categories follow the project's approved **engineering-dimension schema**:

- **Operation Purpose:** operating objectives, authorized purposes, and priority tradeoffs.
- **Operation Rules:** release rules, thresholds, guide curves, seasonal rules, and decision criteria.
- **Infrastructure Constraints:** dam, outlet, intake, hydropower, storage, conveyance, and physical operating limits.
- **Data / Models:** forecasts, monitoring systems, datasets, simulation models, and modeling assumptions used for operation.
- **Real-Time / Emergency Operations:** drought response, flood response, emergency actions, short-term operating decisions, and incident-driven operations.
- **Coordination / Governance:** agencies, agreements, laws, planning processes, stakeholder coordination, and institutional responsibilities.
- **Evidence Gap / Uncertainty:** missing information, unresolved decisions, uncertain assumptions, conflicting evidence, and future research or planning needs.

Each KU preserves links to its original source, including source ID, source title, URL, source location, and a short evidence quote. This makes the KU layer an **evidence-grounded index** rather than an unsupported summary.

**Implementation method:**

- Use **Docling-based structured parsing** when available to preserve document structure such as headings, pages, and tables before KU extraction.
- Build **section-aware extraction packets** from the parsed document text rather than sending whole documents or truncated first-page text directly to the model.
- Apply the **KU extraction skill** and its KU extraction protocol to each packet to draft candidate KUs.
- Consolidate repeated statements within the same source when they express the same finding, while still allowing one file to produce multiple KUs under the same engineering dimension when those KUs capture distinct operational findings.
- Write validated **JSONL records** and run automated checks for required fields, source IDs, unique KU IDs, approved categories, evidence quotes, and traceability fields.

### Step 3: Knowledge Synthesis and Refined KU Generation

Initial KUs extracted from different documents may contain duplicated, overlapping, complementary, or conflicting information. The **synthesis stage** performs **cross-document analysis** to:

- merge redundant knowledge;
- identify supporting evidence;
- detect source discrepancies and operational tradeoffs;
- record uncertainty and evidence gaps;
- organize information into coherent themes.

This stage also produces the **refined knowledge layer**. Unlike initial KUs, **refined KUs** represent consolidated knowledge supported by one or more source-level KUs. For example, several document-specific statements about drought operations may be combined into one refined KU that captures the common finding while retaining links to all supporting initial KUs and original documents.

The framework keeps a clear distinction between the **evidence layer** and the **synthesis layer**:

- **Initial KUs** are document-level findings.
- **Refined KUs / synthesis cards** are cross-document interpretations grounded in initial KUs.
- **Reports and retrieval outputs** cite refined KUs while preserving the path back to initial KUs and source documents.

**Implementation method:**

- Organize validated initial KUs as the evidence base for synthesis, using dimensions such as **engineering dimension**, **operating purpose**, **condition or trigger**, **source family**, and other synthesis grouping criteria (**to be determined**).
- Add synthesis-level outputs on top of the initial KU layer, such as refined KUs, synthesis cards, or other cross-document result types (**to be determined**).
- For strong cross-document claims, return from KU summaries to the **original source sections** before finalizing the synthesis.
- Record supporting KU IDs, confidence, source verification status, and unresolved uncertainty in each refined KU or synthesis card.

### Step 4: Embedding and Vector Database Construction

Refined KUs are converted into **semantic embeddings** and indexed in a **vector database**. Each indexed record contains:

- refined KU content;
- reservoir identifier;
- engineering category;
- source tier and document-type metadata;
- citations to supporting initial KUs;
- citations to original source documents;
- uncertainty or conflict markers when applicable.

The initial KUs are preserved as an evidence layer for traceability, while refined KUs serve as the **primary retrieval objects** for semantic search and downstream reasoning.

**Implementation method:**

- Convert each refined KU into an **embedding-ready record** with normalized metadata.
- Use the text field for semantic retrieval.
- Use metadata fields for filtering by reservoir, source family, engineering dimension, confidence, evidence depth, and document type.
- Return both the **synthesized statement** and its **evidence chain** so that downstream reasoning can inspect the supporting KUs and original sources.

### Step 5: Human-Readable Report Generation

The final stage converts refined KUs into **structured, human-readable reservoir operation reports**. These reports support manual inspection, direct citation, and downstream research use.

A typical report may include:

- reservoir overview;
- operation objectives;
- general operating policies;
- seasonal strategies;
- flood, drought, and emergency operations;
- infrastructure and hydropower constraints;
- available datasets and models;
- previous research;
- source discrepancies, uncertainties, and remaining knowledge gaps.

Unlike raw KUs, which are optimized for machine indexing and retrieval, the reports organize synthesized knowledge into **coherent sections** that can be easily reviewed and referenced by users.

**Implementation method:**

- Use the **refined KU layer** as the report outline and evidence base.
- Draft section-level prose from relevant refined KUs.
- Attach citations to KU IDs or source IDs.
- Explicitly mark evidence gaps, conflicts, or uncertain claims.
- Treat report generation as a **controlled transformation** from validated structured knowledge into a readable research artifact, rather than as an unconstrained writing task.

## 4. AI-Native Workflow Structure

The framework will be developed as a **Codex-orchestrated automation architecture**, not as a sequence of isolated LLM prompts. **Codex acts as the workflow controller**, while skill groups, scripts, schemas, validators, run manifests, and human review templates provide the operational structure that makes the workflow repeatable, inspectable, and transferable to additional reservoirs.

### Automation Components

The most important execution units are the **skill groups**, because each framework stage is implemented through a dedicated skill group. The other components are also essential: they define project-wide rules, enforce structured outputs, record provenance, and support human validation.

| Component | Role in the Automation Strategy | Why It Matters |
|---|---|---|
| **Project-level agent instructions** | An `AGENTS.md` file defines the overall project goal, the five-stage workflow, artifact conventions, validation-gate rules, and boundaries between source evidence, initial KUs, synthesis outputs, retrieval records, and reports. | Gives Codex a stable project-level operating manual so the workflow is not reinvented in each run. |
| **Skill groups** | Each stage has a dedicated skill group with a protocol, expected inputs, expected outputs, scripts, and validation requirements. | Serves as the core execution layer of the framework; one skill group corresponds to one framework stage. |
| **Scripts** | Python scripts handle repeatable tasks such as source preservation, Docling parsing, extraction packet construction, schema validation, indexing, and report assembly. | Keeps deterministic processing separate from model reasoning and makes repeated runs reproducible. |
| **Schemas** | Machine-readable schemas define the required structure of source inventories, operational KUs, synthesis outputs, retrieval records, benchmark questions, and report claims. | Ensures that outputs can be validated, linked across stages, and reused downstream. |
| **Validators** | Validation scripts check whether outputs are structurally complete, internally consistent, traceable, and ready to move to the next stage. | Creates explicit gates between stages instead of relying on informal inspection. |
| **Run manifests** | Each full workflow run records the reservoir ID, run ID, date, skill group versions, input files, output files, validation results, and human-review status. | Preserves provenance and makes each run auditable. |
| **Human review templates** | Annotation templates support source screening, reference KU creation, synthesis review, benchmark question design, and report review. | Makes manual validation consistent across reservoirs and reviewers. |

### Skill Group Design

The proposed automation strategy uses **one skill group for each framework stage**. The current project organizes all five framework stages as skill groups.

| Step | Skill Group | Current Status | Role in Workflow | Main Outputs |
|---|---|---|---|---|
| 1. Data Collection | `source-acquisition` | Implemented as `source-acquisition-suite` | Collect, dedupe, preserve, and parse operation-related sources | source inventory, raw files, extracted text, parsing manifest |
| 2. Initial KU Extraction | `ku-extraction` | Implemented as `ku-extraction` | Convert source text into source-grounded initial KUs | extraction packets, initial KU JSONL, KU preview |
| 3. Knowledge Synthesis and Refined KU Generation | `synthesis-analysis` | Implemented as `synthesis-analysis` | Synthesize validated KUs into refined cross-document knowledge outputs | refined KUs or synthesis cards, validation output, synthesis report |
| 4. Embedding and Vector Database Construction | `retrieval-indexing` | Implemented as `retrieval-indexing` | Convert refined KUs into embedding-ready records, build the vector index, and evaluate benchmark retrieval | embedding-ready records, vector index, retrieval benchmark results |
| 5. Human-Readable Report Generation | `report-generation` | Implemented as `report-generation` | Transform refined KUs and synthesis outputs into structured readable reports | reservoir operation report, citation map, report validation notes |

The intended automated run pattern is:

1. **Initialize reservoir run:** create a reservoir-specific artifact directory and define source scope, reservoir identifiers, and inclusion criteria.
2. **Acquire and preserve sources:** use the source-acquisition skill group to build a deduplicated source inventory, save raw files, extract text, and validate local file paths and metadata.
3. **Parse long-form documents:** use Docling or fallback parsers to preserve document structure, including headings, pages, and tables when available.
4. **Generate extraction packets:** create section-aware packets so long documents are processed with full coverage rather than first-page or first-character truncation.
5. **Extract initial KUs:** use the KU-extraction skill group, write JSONL records, and validate against the operational KU schema.
6. **Synthesize and refine knowledge:** use the synthesis-analysis skill group to organize initial KUs, generate source-grounded synthesis outputs or refined KUs, and validate citations and analysis types.
7. **Build retrieval assets:** use the retrieval-indexing skill group to embed refined KUs, attach metadata and citation chains, and evaluate retrieval with benchmark questions.
8. **Generate report outputs:** use the report-generation skill group to convert refined KUs and synthesis outputs into a structured reservoir operation report with citations, uncertainty notes, and evidence gaps.
9. **Run validation gates:** apply schema checks, source traceability checks, retrieval benchmarks, and manual review on representative reservoirs.

This strategy separates **development-time human supervision** from **deployment-time automation**. During development, representative reservoirs are manually inspected to refine prompts, extraction rules, synthesis strategies, and validation criteria. Once the workflow demonstrates stable performance across those cases, the same skill-based pipeline can be applied to additional reservoirs with minimal manual intervention.

## 5. Workflow Refinement and Sampled Validation

This section describes how the workflow is improved and evaluated without requiring exhaustive manual annotation of the full reservoir corpus. The central idea is to use one well-documented reservoir as a development case, review small samples at each stage, revise the workflow based on observed errors, and then test the stabilized workflow on a different reservoir.

### 5.1 Development Case

Lake Powell is used as the primary development case because it has abundant official documents, research literature, public data products, and media/context sources. Its operation is also shaped by drought conditions, infrastructure constraints, hydropower concerns, ecological objectives, and post-2026 governance debates. This makes it a useful case for exposing weaknesses in source acquisition, KU extraction, synthesis, retrieval, and report generation.

In the development case, the workflow is allowed to change. Prompts, skills, schemas, source relevance rules, KU categories, synthesis types, and validation gates can be revised when sampled review reveals systematic problems. Lake Powell therefore serves to refine the workflow; it is not treated as the final unbiased test case.

### 5.2 Human-Reviewed Samples

The framework does not require humans to manually annotate every source, KU, synthesis output, retrieval result, or report claim. Instead, human-reviewed samples are drawn from each major stage. These samples provide a practical reference set for diagnosing errors and computing stage-level metrics.

Typical review samples include:

- source candidates for inclusion/exclusion and tier assignment;
- source inventory records for metadata completeness and source preservation;
- document sections or extraction packets for KU extraction review;
- generated KUs for category accuracy, traceability, and faithfulness;
- synthesis cards or refined KUs for cross-document reasoning quality;
- benchmark retrieval questions and retrieved records;
- report claims that require evidence support.

These samples are used to answer whether the workflow is producing useful, traceable, and evidence-supported outputs. They also make validation feasible without turning the project into a full manual corpus annotation effort.

### 5.3 Refinement Cycle

Workflow refinement follows a human-gated cycle. Human reviewers provide judgment, but the AI agent performs the concrete revision work.

1. **Run the workflow:** the AI agent executes the current workflow on the development case.
2. **Prepare review samples:** the AI agent selects representative samples from source acquisition, KU extraction, synthesis, retrieval, and reporting outputs.
3. **Review the samples:** human reviewers inspect the samples and identify incorrect, weak, missing, or unsupported outputs.
4. **Compute sampled metrics:** the AI agent calculates stage-level metrics on the reviewed samples.
5. **Summarize failure modes:** the AI agent and human reviewers identify recurring problems, such as weak source relevance, unstable tier labels, missed KUs, overly broad KUs, unsupported synthesis claims, or weak report evidence.
6. **Propose revisions:** the AI agent proposes changes to prompts, skill protocols, schemas, relevance thresholds, extraction packet design, synthesis categories, or validation rules.
7. **Approve and implement revisions:** human reviewers approve or revise the proposed changes, and the AI agent implements the approved revisions.
8. **Rerun and compare:** small revisions may first trigger reruns of only the affected stage for diagnosis; major revisions should trigger a full workflow rerun to check whether upstream and downstream outputs remain consistent.

Iteration stops when major failure modes are resolved and sampled metrics no longer show large avoidable errors. This makes prompt and skill refinement auditable: each change is tied to observed failure modes and reviewed outputs rather than informal prompt rewriting.

### 5.4 Transfer Validation

After the workflow stabilizes on the development case, it is applied to at least one additional reservoir as a transfer validation case. The purpose is to test whether the workflow can generalize to a different reservoir context, not to continue routine tuning.

The transfer validation case uses the same stage-level sampled evaluation as the development case. However, prompts, schemas, thresholds, and skill protocols should not be substantially revised during transfer validation unless the new reservoir exposes a major systematic failure. If such a failure occurs, the workflow should return to the development refinement stage before being evaluated again.

This design avoids framing the project as a conventional machine-learning train/validation/test split. The framework does not train model parameters. It develops and evaluates a human-gated AI-native workflow. The development case refines the workflow, and the transfer validation case tests whether the refined workflow remains useful outside the original reservoir.

### 5.5 Stage-Level Metrics

Validation is performed at the stage level because each stage produces a different type of output. The same metric families are used in both the development case and the transfer validation case, but the results serve different purposes: in the development case, metrics guide workflow revision; in the transfer case, metrics assess generalizability and document remaining limitations.

| Stage | Reviewed sample | Main metrics |
|---|---|---|
| Source acquisition | Candidate sources and included source records | Candidate inclusion F2, source tier accuracy, relevance-threshold precision |
| KU extraction | Document sections, extraction packets, and generated KUs | KU extraction F2, engineering-dimension accuracy, traceability rate, faithfulness rate |
| Synthesis | Synthesis cards or refined KUs and their cited evidence | Synthesis quality score, traceability rate, faithfulness rate, source-check rate |
| Retrieval/indexing | Benchmark questions and top-k retrieved records | Retrieval F2, top-k precision/recall, traceability rate |
| Report generation | Evidence-requiring report claims | Claim traceability rate, claim faithfulness rate, human quality score |

For F2-based metrics, precision is defined as `P = TP / (TP + FP)` and recall is defined as `R = TP / (TP + FN)`. **TP** refers to correct system outputs, **FP** refers to incorrect or irrelevant outputs, and **FN** refers to expected outputs missed by the system. The exact output type depends on the stage, such as included sources, extracted KUs, synthesis outputs, retrieved records, or evidence-supported report claims. The F2 score is used because the workflow places greater weight on avoiding missed useful evidence while still controlling irrelevant or unsupported outputs.

Traceability and faithfulness are used across stages. **Traceability** asks whether an output preserves links to source documents, KUs, source locations, or evidence quotes. **Faithfulness** asks whether the output is actually supported by the cited evidence. Together, these checks ensure that the workflow produces not only plausible text but reviewable reservoir-operation knowledge.
## 6. Expected Contributions

The proposed research is expected to contribute:

- a **source-grounded reservoir operation knowledge base dataset**, including source-level Knowledge Units and cross-document synthesis records;
- an **AI-native, human-gated workflow** for constructing, refining, and validating the dataset from heterogeneous reservoir-operation sources;
- a **Lake Powell case study** demonstrating how the dataset and workflow support reviewable operational knowledge synthesis and identify remaining evidence gaps.

## 7. Why Agent-Based Organization Is Needed

There are three possible ways to implement this type of reservoir knowledge-base workflow.

The first option is a **pure Python pipeline**. This approach is appropriate for deterministic tasks such as downloading files, parsing documents, extracting tables, validating JSONL schemas, computing metrics, and organizing artifacts. However, a pure Python pipeline is not sufficient for this project because the core tasks involve semantic judgment: deciding which sources are operationally relevant, identifying meaningful KUs from heterogeneous documents, synthesizing cross-document relationships, and revising the workflow after human review.

The second option is a **Python-led pipeline with LLM calls**. In this design, Python controls the overall workflow and calls an LLM for specific tasks such as source screening, KU extraction, or synthesis. This is more capable than a pure Python pipeline and may be suitable once the task is fully stabilized. However, it assumes that the sequence of steps, prompts, schemas, thresholds, review logic, and rerun strategy are already well defined. During research development, these elements are still evolving. The workflow needs to decide what to inspect next, how to respond to failure modes, which stage should be rerun, and how to revise prompts or skills after human feedback.

The third option is an **agent-based workflow that orchestrates Python scripts and LLM reasoning**. This is the design adopted in this project. Python still performs deterministic and reproducible processing, while the agent organizes the research process: selecting and applying skill protocols, coordinating LLM-based extraction and synthesis, preparing human review samples, interpreting validation results, proposing workflow revisions, implementing approved changes, and maintaining versioned artifacts.

The reason for using an agent-based organization is therefore not that Python is unimportant. Rather, Python handles the stable execution layer, while the agent handles the evolving research-control layer. The agent is useful when the workflow requires:

- open-ended source discovery and relevance screening;
- domain-aware KU extraction from heterogeneous documents;
- cross-document synthesis that distinguishes recurring findings, discrepancies, tradeoffs, evidence gaps, and unresolved issues;
- human-gated refinement of prompts, skills, schemas, thresholds, and validation rules;
- selective reruns or full reruns after revisions;
- preservation of evidence links across sources, KUs, synthesis records, retrieval outputs, and reports.

In later deployment, parts of the workflow may be converted into a more conventional Python-led pipeline once the prompts, schemas, validation gates, and rerun logic become stable. During method development, however, an agent-based workflow is more appropriate because it can combine executable processing, LLM-based interpretation, and human-guided research iteration in a single inspectable process.



