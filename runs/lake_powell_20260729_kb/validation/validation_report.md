# Validation Report

- Run ID: `lake_powell_20260729_kb`
- Automated validation: **4/6 stages passed without warnings**
- Human review completed: **0/6** stages

![Validation score overview](validation_score_overview.png)

Figure values are normalized to 0-1: automated pass = 1.00, human 0/1/2 scores are divided by 2, and recall/precision remain ratios.

## Automated validation

| Stage | Schema conformance | Traceability / acquisition | Errors | Warnings |
|---|---|---|---:|---:|
| source acquisition | 66/66 correct | 24/66 correct (42 issues) | 0 | 43 |
| evidence extraction | 442/442 correct | 442/442 correct | 0 | 1 |
| knowledge consolidation | 81/81 correct | 81/81 correct | 0 | 0 |
| synthesis | 15/15 correct | 15/15 correct | 0 | 0 |
| indexing | 538/538 correct | 538/538 correct | 0 | 0 |
| report generation | 30/30 correct | 30/30 correct | 0 | 0 |

## Human review

| Stage | Review completion | Review scope | Human metrics | Main finding |
|---|---|---|---|---|
| source acquisition | incomplete | 0/201 candidates reviewed; 0 selected | precision n/a; recall n/a; source adequacy n/a | Not reviewed. |
| evidence extraction | incomplete | 0/442 items scored | faithfulness n/a; relevance n/a; value n/a | Not reviewed. |
| knowledge consolidation | incomplete | 0/81 items scored | faithfulness n/a; consolidation appropriateness n/a; value n/a | Not reviewed. |
| synthesis | incomplete | 0/15 items scored | faithfulness n/a; reasoning soundness n/a; value n/a | Not reviewed. |
| indexing | incomplete | 8/8 benchmark queries completed | recall@k 0.67; precision@k 0.15; source adequacy n/a | Automated benchmark only; source adequacy not human-scored. |
| report generation | incomplete | 0/1 items scored | faithfulness n/a; readability n/a; value n/a | Not reviewed. |

## Required actions by stage

No human notes or required actions recorded.

## Interpretation

Automated validation establishes file-contract and evidence-chain integrity. Human review evaluates substantive quality. A review is treated as completed when all fields required for that stage are filled, even if `review_status` remains `not_requested`.
