# Lake Powell / Glen Canyon Dam Operations Knowledge Base: Case Study Report

Run `lake_powell_20261025_kb`. This report is generated from the run's validated Evidence Units (EUs), Knowledge Cards (KCs), and Synthesis Cards (SCs). Each substantive statement in Sections 3-8 is a numbered claim: the record IDs in parentheses are its evidence, and the bracketed claim ID links to `claim_evidence_map.jsonl`, which also lists the source documents behind each claim.

## 1. Purpose and scope

The report summarizes what the knowledge base documents about how Lake Powell and Glen Canyon Dam are operated: the rules that set annual and hourly releases, the elevations at which operations change, the 2021-2026 drought response, high-flow experiments and fish management, the main operating tradeoffs, and the questions the evidence leaves open. It is a demonstration of the knowledge base, not an operating or legal analysis.

## 2. How the records were built

- Sources: 66 selected from 201 candidates; 50 marked usable for extraction, of which 3 were later found to be access-blocked pages (Section 9).
- Evidence Units: 442 source-grounded findings, each with a quote and locator.
- Knowledge Cards: 81 groupings of EUs that answer the same operational question.
- Synthesis Cards: 19 cross-document analyses. In this run, candidate relationships were screened across all 442 EUs (30 candidates; 19 selected, 1 merged, 10 rejected with reasons in `04_synthesis/candidate_screening.jsonl`), and every selected card was written after rereading the cited passages in the preserved source text.

Stages 1-3 (sources, EUs, KCs) are carried over unchanged from run `lake_powell_20260729_kb`; Stages 4-6 were redone.

## 3. The governing operating framework

- The 1970 Long-Range Operating Criteria set the objective of a minimum annual release of 8.23 maf from Lake Powell. (SC-LP-013; KC-LP-OPR-08) [CLM-001]
- The Colorado River Compact requires that the Upper Division states not deplete flow at Lee Ferry below 75 maf over any ten consecutive years, which CRS describes, together with the 1944 treaty share, as an average of at least 8.25 maf per year passing to the Lower Basin. (SC-LP-010) [CLM-002]
- Under the 2007 Interim Guidelines the operating tier is set from the projected January 1 Lake Powell elevation, and the annual release is implemented each year through the Annual Operating Plan. (SC-LP-003; KC-LP-OPR-11; KC-LP-REG-07) [CLM-003]
- In the Equalization and Balancing Tiers the scheduled water-year release is adjusted each month as inflow forecasts and projected September 30 storage change, so an annual release figure is a dated projection rather than a fixed value. (SC-LP-003; KC-LP-STG-08) [CLM-004]
- Hourly and daily releases are bounded by minimum flows of 8,000 cfs by day and 5,000 cfs at night, a 25,000 cfs maximum for power generation, and a daily fluctuation range that LTEMP sets at 9 or 10 times the monthly volume in kaf but never above 8,000 cfs. (SC-LP-007; KC-LP-OPR-01; KC-LP-OPR-03) [CLM-005]
- Sub-annual operations moved from hydropower peaking before 1991 to conservative interim limits in 1991; the 1996 ROD raised the maximum release to 25,000 cfs and the up-ramp to 4,000 cfs/hr to enhance power flexibility, and the 2016 LTEMP ROD raised the down-ramp limit from 1,500 to 2,500 cfs/hr. (SC-LP-012; KC-LP-OPR-16; KC-LP-OPR-17) [CLM-006]
- The Adaptive Management Work Group advises, while the Secretary of the Interior retains sole discretion over how operations and experiments are carried out each year. (SC-LP-005; KC-LP-REG-08; KC-LP-EMR-16) [CLM-007]

## 4. Elevation thresholds and low-elevation release limits

- Different instruments attach operating meaning to a descending set of Lake Powell elevations: 3,575 ft and 3,525 ft as tier boundaries, 3,525 ft as the DROA target, 3,500 ft as the elevation Section 6.E seeks to maintain, 3,490 ft as minimum power pool, and about 3,370 ft as the river outlet works intake. (SC-LP-008; KC-LP-OPR-11; KC-LP-EMR-04; KC-LP-OPR-06) [CLM-008]
- Below 3,490 ft all water must pass through the river outlet works, whose design capacity of 15,000 cfs at 3,490 ft declines with head; one study cited by CRS estimated 10,200 cfs, about 7.41 maf per year, at 3,430 ft. (SC-LP-006; KC-LP-UNC-01; KC-LP-OPR-07) [CLM-009]
- Reclamation's March 2024 guidance limits flow per outlet conduit to reduce cavitation damage and recommends not relying on the outlet works as the sole means of releasing water below minimum power pool. (SC-LP-006; KC-LP-UNC-02) [CLM-010]
- The only operation of the outlet works near minimum power pool documented in these sources, on April 20, 1965, coincided with undermining and partial collapse of the tailrace slab, which Reclamation attributes to a recirculating eddy strengthened by low-head outlet operation. (SC-LP-016; KC-LP-UNC-02) [CLM-011]
- In September 2005, with Lake Powell at its lowest level in decades, oxygen-depleted water just above the penstock intakes was released and river dissolved oxygen fell below 4.0 mg/L. (SC-LP-014; KC-LP-UNC-10) [CLM-012]

## 5. Drought response and the 2026 actions

- The August 2025 24-Month Study placed Lake Powell in the Mid-Elevation Release Tier with a projected WY2026 release of 7.48 maf. (SC-LP-001; KC-LP-OPR-09) [CLM-013]
- To protect the 3,525 ft DROA target, December 2025-April 2026 monthly releases were reduced by 0.598 maf, and when Lake Powell was projected below 3,500 ft Interior cut the WY2026 release from 7.48 to 6.00 maf under Section 6.E. (SC-LP-001; KC-LP-EMR-04; KC-LP-OPR-13) [CLM-014]
- The release reduction was paired with DROA releases of about 0.66-1.0 maf from Flaming Gorge Reservoir by April 2027. (SC-LP-001; KC-LP-EMR-06) [CLM-015]
- Lake Powell fell below the 3,525 ft DROA target in March 2023, reaching 3,520 ft despite drought-response actions in 2021 and 2022, and was again below it at 3,522.90 ft on July 26, 2026. (SC-LP-017; KC-LP-EMR-04; KC-LP-EMR-05) [CLM-016]
- The July 2026 Most Probable 24-Month Study, which includes the 6.00 maf release, projects Lake Powell to fall below 3,500 ft from February to April 2027 and to reach 3,491.75 ft in April 2027, 1.75 ft above minimum power pool, before spring runoff. (SC-LP-018; KC-LP-STG-01) [CLM-017]
- Reclamation acknowledged that the reduced Lake Powell releases will accelerate Lake Mead's decline, with potential for up to an additional 40% reduction in Hoover Dam's generating capacity. (SC-LP-010; KC-LP-EMR-06) [CLM-018]
- The 2007 Interim Guidelines, the 2019 Drought Contingency Plans, and Minutes 323 and 330 are set to expire at the end of 2026, and the post-2026 No Action Alternative would revert to annual Annual Operating Plan determinations under pre-2007 guidance. (SC-LP-013; KC-LP-REG-02) [CLM-019]

## 6. High-flow experiments, sediment, and fish management

- A sediment trigger makes a High-Flow Experiment eligible but not automatic: an extended-duration fall HFE is not implemented if annual release volume would be affected, the 2024 SEIS assumes no HFE below 3,500 ft, and fall HFEs were forgone in 2015, 2021, and 2022 because of warm release temperatures and nonnative-fish risk. (SC-LP-002; KC-LP-OPR-05; KC-LP-EMR-08) [CLM-020]
- The 1997 Test Flow and the 2000 experiment failed to build sandbars, the first because sand had already been exported and its magnitude was insufficient and the second because the Paria River supplied little sediment, and later HFEs were timed to follow tributary sand inputs. (SC-LP-015; KC-LP-UNC-11) [CLM-021]
- From 2004 to 2020 net sand deposition occurred at 86% of long-term monitoring sites, but separation bars and undifferentiated eddy bars continued to decline, and usable campsite area fell 37% from 2002 to 2016, mainly because of vegetation encroachment. (SC-LP-019; KC-LP-UNC-12; KC-LP-MOD-06) [CLM-022]
- Humpback chub management escalates by population threshold: Tier 1 conservation actions below a combined adult estimate of 9,000, and mechanical removal of nonnative fish below 7,000 if Tier 1 has not halted the decline. (SC-LP-004) [CLM-023]
- Unlike the Tier 1 and Tier 2 actions, Trout Management Flows change dam releases: triggered by predicted high young-of-year trout recruitment, they use high releases followed by a rapid drop to 5,000-8,000 cfs. (SC-LP-004; KC-LP-OPR-18) [CLM-024]

## 7. Operating tradeoffs

- The 1996 ROD accepted an estimated hydropower loss of $15.1-44.2 million per year (1991 dollars) to protect downstream resources, and an ex post analysis estimated the realized average at $26.3 million per year in 1991 dollars. (SC-LP-009; KC-LP-UNC-07) [CLM-025]
- The LTEMP decision analysis found no alternative that dominated across all metrics, and the selected Alternative D was expected to reduce average daily generation by 1.1% and firm capacity by 6.7% relative to No Action. (SC-LP-009; KC-LP-MOD-07) [CLM-026]
- Because the penstock intakes are fixed, low storage raises release temperatures, which may help humpback chub but also favors warmwater nonnative fish; the 2024 Cool Mix operation, which bypassed about 0.894 maf in July-November 2024 to cool releases, has the largest hydropower impacts of the SEIS alternatives. (SC-LP-011; KC-LP-UNC-08; KC-LP-EMR-15) [CLM-027]
- Protecting Lake Powell's elevation shifts risk downstream: the DROA describes its target as balancing infrastructure protection and Compact obligations, and the post-2026 DEIS describes delivery reductions versus reservoir storage as its central tradeoff. (SC-LP-010; KC-LP-OPR-20) [CLM-028]

## 8. Uncertainty and unresolved questions

- Sources disagree on the 2021 DROA upstream release volume (161,000 af on the DROA page and 180,000 af in a CRS report), and the knowledge base keeps both figures. (SC-LP-017; KC-LP-EMR-05) [CLM-029]
- Sources give both August and November 1991 for the interim operating criteria. (SC-LP-012; KC-LP-REG-14) [CLM-030]
- The DROA states that drought response operations will not extend beyond the 2007 Interim Guidelines term ending December 31, 2025, yet a 2026 Drought Response Operations Plan is described in the July 2026 24-Month Study; the evidence set does not explain how these fit together. (SC-LP-013) [CLM-031]
- Whether the 2026 release reduction causes a Compact shortfall at Lee Ferry cannot be determined from this evidence set, which contains no ten-year Lee Ferry totals; the claim that it will appears only in a media source. (SC-LP-010) [CLM-032]

## 9. Validation status

- Automated validation (schema conformance and traceability integrity) passed for the Synthesis Cards, the index records, and this report's claim-evidence map; see `../validation/validation_report.md` for every stage.
- Human review has not been performed for any stage; each stage's `human_review.json` is a prefilled, unscored review form.
- Known limitations carried over from Stages 1-3: 9 of the largest documents were extracted by sampling rather than in full, 3 sources marked usable were actually access-blocked pages, and two EU quotes do not match their sources verbatim (EU-LP-OFF-006-12, EU-LP-OFF-023-06).

## 10. How to use this knowledge base

Start from a Synthesis Card for a cross-document question, follow its EU IDs to the quoted source passages, and use `source_navigation.md` in Stages 2-4 to open the preserved source files locally. Figures that change over time (forecasts, 24-Month Study projections, elevations) should always be quoted with the date of the document that reports them.
