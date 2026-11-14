# Auditing Annual Generator-Fleet Transitions and Hourly Data Consistency for Reproducible Power-System Modeling: A 2024–2025 California ISO Case Study

**Manuscript draft v0.1 — 2026-11-10.** Research manuscript; not yet submission-ready. All numerical results below come from archived source and CI evidence. No empirical multi-year PyPSA dispatch is claimed.

## Abstract

Annual generator inventories and hourly balancing-authority observations are widely used to assemble power-system models, but their apparent completeness can obscure differences in reporting scope, status classification, temporal precision and source consistency. We present an auditable 2024–2025 case study for the California Independent System Operator (CISO) using annual U.S. Energy Information Administration (EIA) Form 860 generator and plant records and hourly EIA-930 observations. We construct an identity-matched, mutually exclusive accounting bridge for annual operable (OP) generator records, inspect reported operating-year cohorts and cross-check plant balancing-authority codes against original year-specific worksheets. Reported CISO OP nameplate increased from 85,634.2 MW in 2024 to 92,530.0 MW in 2025 (+6,895.8 MW, 8.05%). Newly present records contributed +6,339.3 MW; records absent in 2025, status transitions and nameplate revisions contributed −379.9, +862.4 and +74.0 MW, respectively. Batteries and solar photovoltaic accounted for 82.83% of the net OP nameplate change. However, three pumped-storage generators totaling 1,053 MW changed status from OA to OP while retaining reported June 1984 operating dates and CISO plant assignment in both years. Among 157 new-to-inventory records, 29 reported operating years before 2025. A targeted same-run EIA-930 audit also identified a 2,271 MWh disagreement between reported regional net generation and signed fuel-category sums for one hour. These findings show why annual inventory change and hourly source consistency must be separately validated before interpreting reported capacity as commissioning, availability or modeled dispatch. The contribution is an evidence-gated data-validation workflow, not an empirical generation-dispatch simulation.

**Keywords:** EIA-860; EIA-930; CISO; generator inventory; data provenance; power-system modeling; PyPSA; balancing authority.

## 1. Introduction

Reproducible electricity-system analysis depends on combining observations reported at different spatial, temporal and institutional resolutions. Annual generator records identify plants, generators, status and nameplate capacity; hourly balancing-authority series report operational quantities. A mechanically successful join between these sources does not establish that plant-level balancing-authority assignments match an operational network boundary, that annual status is hourly availability, or that reported operating dates identify an exact commissioning hour.

Open-source power-system tools such as PyPSA provide flexible multi-period simulation and optimization capabilities (Brown et al., 2018), while open-data model generators such as OSeMOSYS Global demonstrate that reproducible model construction is an established research direction (Barnes et al., 2022). Prior work has also developed screening and imputation of EIA-930 balancing-authority demand (Developing reliable hourly electricity demand data through screening and imputation, 2020), and Catalyst Cooperative's PUDL provides longitudinal EIA-860M generator-characteristic changelogs. NIST's Generator Fleet Characteristics Model already combines EIA-860 generator inputs and EIA-930 operating series. Accordingly, neither anomaly detection in EIA-930 nor longitudinal generator-ID matching nor combining these public sources is new by itself. Our novelty claim is therefore **not** the use of open data or the existence of a PyPSA workflow. It is the documented, identity-matched reconciliation of annual inventory changes with original plant-level BA evidence and an independent hourly cross-endpoint consistency check, with explicit limits on downstream inference.

These distinctions matter when comparing adjacent years. A generator may first appear in a balancing-authority subset because of a reporting or membership change; an existing generator may change reported status without new construction; and nameplate power for storage does not identify its energy capacity or duration. Hourly observations can introduce an independent class of problems when apparently related series disagree.

This study asks: (1) How does reported CISO operable nameplate change between the 2024 and 2025 annual inventories when exact generator identity and mutually exclusive transition classes are respected? (2) What do reported operating years and original Plant-sheet balancing-authority assignments reveal about newly present records? (3) Can a bounded cross-endpoint audit detect source-level inconsistency that should prevent unqualified downstream modeling claims?

Our contribution is a narrow, reproducible validation case study. We do not estimate hourly generation by technology, new-build commissioning, reliability, emissions, costs or the performance of an empirical PyPSA dispatch model.

## 2. Data and Methods

### 2.1 Sources and provenance

We use annual EIA-860 2024 and final 2025 releases, specifically the original Plant and Generator Operable worksheets. The 2025 annual release status was checked against the EIA publication record. Original source ZIP hashes and source URLs are preserved in the project's private audit trail. The year-specific Plant worksheet provides the reported `Balancing Authority Code`; generator records provide plant code, generator ID, technology, status, nameplate MW and operating month/year. EIA-930 hourly CISO demand and regional/fuel net-generation endpoints provide an independent operational-data audit.

**Scope caveat:** filtering by EIA-860 plant BA code CISO is an inventory selection rule, not a validated equivalence to the physical or dispatch-operational CISO boundary.

### 2.2 Generator identity and OP accounting

We identify generator records by exact `(Plant Code, Generator ID)` pairs and compare annual CISO subsets. For a record present in both years, we classify changes using an ordered first-match rule: membership change; status change; technology change; nameplate change; otherwise unchanged. This makes classes mutually exclusive. We calculate annual OP nameplate as the sum of positive recorded nameplate MW for accepted `Status=OP` records. For each change class, its contribution is 2025 OP MW minus 2024 OP MW. The class contributions must sum to the difference between annual OP totals.

This decomposition measures **reported inventory** changes. It does not distinguish actual construction, reporting corrections, transfers or operational availability without additional evidence.

### 2.3 Operating-year and Plant-sheet checks

For generator records newly present in the 2025 CISO subset, we separate reported operating year 2025 from earlier years and report both generator counts and 2025 OP MW. For the earlier-year subgroup, we inspect original Plant worksheets in both releases, matching Plant Code and comparing annual BA assignments. Plant absence in a prior worksheet is not treated as proof of nonexistence or commissioning.

We separately examine the three pumped-storage records contributing the largest salient status-change component, including year-specific operating month/year and plant BA code.

### 2.4 Hourly data checks and model acceptance boundary

We report normalized EIA-930 CISO demand coverage for calendar years 2024 and 2025. For a targeted five-hour period (2025-07-31T19 through T23, EIA hour-ending labels), we retrieve the regional net-generation endpoint and the fuel-type endpoint in the same CI run. We sum fuel categories **with their signs preserved** and calculate `fuel-category total − regional net generation` for each hour. Original JSON responses, SHA256 digests and the audit manifest are preserved privately. This targeted case does not estimate the prevalence of anomalies across the full year.

PyPSA asset staging and a synthetic solver smoke test are treated as software checks only. Empirical dispatch remains gated on independently validated hourly availability, storage MWh and efficiency, interchange, operating boundaries and costs.

## 3. Results

### 3.1 Hourly coverage

The normalized CISO EIA-930 demand dataset contains 8,784 hourly records for leap-year 2024 and 8,760 for 2025. The corresponding recorded annual demand sums are 224,030,258 and 224,023,764 MWh (Table 1). Complete normalized time coverage does not imply every observation is free of source anomalies.

**Table 1.** Normalized hourly CISO demand coverage from EIA-930.

| Year | Hour-ending records | Recorded annual demand (MWh) | Interpretation |
|---|---:|---:|---|
| 2024 | 8,784 | 224,030,258 | Full normalized leap-year grid; source-level validation remains distinct |
| 2025 | 8,760 | 224,023,764 | Full normalized non-leap-year grid; targeted anomaly remains unresolved |

### 3.2 Annual OP fleet accounting

Reported OP generator records number 2,645 in 2024 and 2,786 in 2025. OP nameplate increased from 85,634.2 to 92,530.0 MW (+6,895.8 MW; 8.05%). The accounting bridge is given in Table 2. Batteries increased by 3,862.2 MW and solar photovoltaic by 1,849.4 MW, together representing 82.83% of the **net** OP nameplate increase (Figure 1). Negative technology contributions are retained in the technology-level plot.

**Table 2.** Mutually exclusive first-match accounting bridge for CISO OP nameplate capacity.

| Generator-record classification | OP nameplate change (MW) |
|---|---:|
| New to 2025 CISO inventory | +6,339.3 |
| Missing from 2025 CISO inventory | −379.9 |
| Status changed | +862.4 |
| Nameplate revised | +74.0 |
| Technology changed | 0.0 |
| **Total** | **+6,895.8** |

**Figure 1.** Technology-specific net change in reported OP nameplate capacity (MW), CISO annual EIA-860 inventory, 2025 minus 2024. Positive and negative changes are displayed without clipping. The battery-plus-solar 82.83% statistic is relative to the **net change**, not to total generation or total capacity.

### 3.3 Operating-year cohorts and plant membership

Among 157 generator records newly present in the 2025 CISO inventory, 128 report operating year 2025 and contribute 6,201.2 MW OP. The other 29 report an earlier operating year and contribute 138.1 MW OP (Figure 2). Within the latter 29, 23 records have OP status, one OS and five SB; non-OP records contribute zero OP MW.

**Table 3.** Reported operating-year distribution of the 29 pre-2025 entrants in the 2025 CISO EIA-860 inventory. Values are source-verified against the archived annual fleet-transition artifact; OP MW excludes OS/SB records. This table describes *first appearance in the selected annual inventory*, not physical commissioning.

| Reported operating year | OP records | OS records | SB records | OP nameplate (MW) |
|---|---:|---:|---:|---:|
| 2012 | 0 | 1 | 0 | 0.0 |
| 2014 | 2 | 0 | 0 | 3.8 |
| 2018 | 1 | 0 | 0 | 2.3 |
| 2020 | 1 | 0 | 0 | 2.0 |
| 2021 | 5 | 0 | 0 | 7.2 |
| 2023 | 11 | 0 | 0 | 88.1 |
| 2024 | 3 | 0 | 5 | 34.7 |
| **Total** | **23** | **1** | **5** | **138.1** |

The 2023 operating-year cohort contributes 88.1 MW (63.8% of the 138.1 MW OP subtotal), while the 2024 cohort contributes 34.7 MW (25.1%). The capacity distribution is concentrated: the two largest OP records (50.0 MW and 30.0 MW) together contribute 80.0 MW, or 57.9% of the 138.1-MW subtotal. Within the 2023 reported-operating-year group, its two largest records (50.0 MW and 20.0 MW) contribute 70.0 of 88.1 MW (79.5%). Consequently, record counts and nameplate-capacity shares should not be interpreted interchangeably. These proportions characterize reported operating-year metadata among annual-inventory entrants; they do not establish when or why each generator first entered CISO reporting.


Original Plant-sheet checks identify four plant IDs present with BA=CISO in both annual releases (six newly present generator records, 103.6 MW OP) and 16 plant IDs absent from the 2024 Plant worksheet but present in 2025 with BA=CISO (23 records, 34.5 MW OP). These findings distinguish two source-level pathways for first appearance without identifying their administrative or physical causes.

Three 351-MW generators at Helms Pumped Storage (Plant 6100) report operating dates of June 1984 in both years and status OA→OP. The plant reports BA=CISO in both annual Plant worksheets. The associated +1,053.0 MW OP change therefore reflects an annual status transition rather than verified 2025 construction or a plant-level BA transfer.

**Figure 2.** New-to-2025-CISO generator records grouped by reported operating year (2025 versus pre-2025), showing generator-record counts (128 versus 29) separately from OP nameplate MW (6,201.2 versus 138.1). Records and MW have different denominators; not all records are OP.

### 3.4 Targeted EIA-930 cross-endpoint inconsistency

For 2025-07-31T19–T23, regional net generation and signed fuel-category sums differ by 0, −1, +2,271, 0 and +1 MWh, respectively. The large difference is localized to T21 in this five-hour case. The T21 difference numerically matches the reported nuclear fuel category, but this equality alone does not establish nuclear omission or any particular upstream cause. No source correction is applied.

## 4. Discussion

This study should be interpreted against existing PUDL generator changelogs and published EIA-930 demand-screening methods. The present two-year, one-BA case does not establish a new general-purpose record-linkage algorithm or a superior anomaly-detection method. Its contribution is the bounded, source-traceable accounting interpretation and a deliberately fail-closed model-input gate. A cross-check against monthly PUDL changelog histories would strengthen interpretation of first appearances but has **not** yet been performed.

The annual CISO inventory shows a substantial shift in reported OP nameplate, particularly for batteries and solar. Yet the interpretation changes materially when generator identity, reported operating year and annual status are respected. A first appearance in a BA-filtered inventory is not synonymous with first physical operation, as shown by the earlier-year entrant cohort. Likewise, the 1,053 MW pumped-storage change arises from status transitions for historically operating generators, not evidence of construction. The original Plant-sheet crosswalk narrows some possible explanations but cannot independently resolve reporting history or boundary equivalence.

EIA's own EIA-930 documentation describes balancing-authority hourly values as potentially affected by near-real-time collection disruptions, reporting lags, subsequent corrections and differences between directly published BA-level observations and anomaly-handled aggregates (EIA, EIA-930 About). This source-level publication policy provides a reason to audit endpoint consistency before treating complete timestamp coverage as validated operational data. It does **not** establish that any one of these mechanisms caused the T21 discrepancy.

The hourly audit demonstrates a separate source-consistency risk. The bounded five-hour cross-endpoint discrepancy can be reproduced from same-run raw JSON, but the case is not evidence of a full-year error rate and its causal explanation remains open. This distinction between **detecting** an inconsistency and **correcting** it is essential for defensible modeling.

A further limitation is that annual OP nameplate is not an hourly availability series. Battery MW does not determine storage MWh or duration, and a plant-level BA assignment does not validate hourly interchange or network topology. Consequently the present evidence supports an inventory-validation case study but does not support empirical PyPSA dispatch, resource adequacy, generation mix, emissions or economic conclusions.

## 5. Conclusions

An exact-identity and source-audited comparison of 2024–2025 CISO annual generator records identifies a +6,895.8 MW net increase in reported OP nameplate, with batteries and solar accounting for 82.83% of that change. However, newly present records, earlier reported operating years and historically operating units changing status demonstrate why inventory growth must not be equated with newly commissioned or available capacity. A reproducible five-hour EIA-930 audit independently reveals a localized 2,271 MWh cross-endpoint inconsistency. These results motivate a fail-closed acceptance framework for integrating annual inventories and hourly data into power-system models. Future work requires verified hourly availability, interchange, storage energy constraints and boundary reconciliation before empirical dispatch can be evaluated.

## Data and code availability

Code, test contracts and derived audit documentation are maintained in a private research repository during manuscript preparation. EIA-860 and EIA-930 are publicly distributed by the U.S. Energy Information Administration; source URLs, retrieval provenance and SHA256 digests are documented in the project audit trail. A public reproducibility release and third-party redistribution/license review remain to be completed before submission. No claim is made that private artifacts are currently publicly accessible.

## References — verified foundational sources (additional related-work review pending)

1. U.S. Energy Information Administration. Form EIA-860 annual generator and plant data. https://www.eia.gov/electricity/data/eia860/
2. U.S. Energy Information Administration. EIA-930 hourly electric grid monitor data and API documentation. https://www.eia.gov/electricity/gridmonitor/ and https://www.eia.gov/opendata/
3. U.S. Energy Information Administration. EIA-930 data description, including the Data quality section (reporting lags, revisions and publication practices). https://www.eia.gov/electricity/930-content/about.html
4. Brown, T., Hörsch, J., & Schlachtberger, D. (2018). PyPSA: Python for Power System Analysis. *Journal of Open Research Software*, 6(1), 4. https://doi.org/10.5334/jors.188
5. Barnes, T., et al. (2022). OSeMOSYS Global, an open-source, open data global electricity system model generator. *Scientific Data*, 9, 623. https://doi.org/10.1038/s41597-022-01737-0
6. Developing reliable hourly electricity demand data through screening and imputation. (2020). *Scientific Data*. https://doi.org/10.1038/s41597-020-0483-x [Author list to be verified before final bibliography.]
7. Catalyst Cooperative. PUDL data dictionary: `core_eia860m__changelog_generators`. https://docs.catalyst.coop/pudl/en/stable/data_dictionaries/pudl_db.html
8. National Institute of Standards and Technology. (2023). *Generator Fleet Characteristics Model*. Technical Note 2246. https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.2246.pdf

**Before journal submission:** perform a systematic close-neighbor literature search (generator-inventory versioning and electricity-data validation); verify all citations and final journal formatting; embed and independently review the actual figures against archived bytes; check data redistribution rights; obtain coauthor review. The present primary-source and foundational references are not a complete literature review. Do not present this as a completed empirical PyPSA dispatch paper.


## Reproducibility and acceptance status (2026-11-12 audit addendum)

This section distinguishes **archived findings**, **verified execution evidence**, and **pending independent acceptance**. It is a reporting-status appendix, not a claim that new empirical analyses have been completed.

| Evidence layer | Current documented status | Scientific interpretation |
|---|---|---|
| Archived EIA-860 CISO OP counts and capacities (2024: 2,645 / 85,634.2 MW; 2025: 2,786 / 92,530.0 MW) | Archived result; original-workbook CI acceptance not yet verified | Report as archived findings pending original-workbook replay |
| Four-way OP inventory bridge (+6,339.3, −379.9, +862.4, +74.0 MW) | Archived result; independently coded reconciliation and row-level export; latest CI output not yet verified | Do not label independently reproduced until original-data receipts are inspected |
| Helms OA-to-OP and pre-2025 reported operating-year cohort | Archived case evidence; pending fresh row-level original-workbook verification | Status transition and first appearance are not synonymous with commissioning |
| EIA-930 cross-endpoint R02A audit | Verified GitHub Actions run 42921140978, job 130195976045, conclusion success; 13 tests passed; three raw audit files uploaded as artifact 13811587152 | Supports a narrowly scoped hourly endpoint-consistency finding, not empirical dispatch |
| PUDL pre-2025 cohort matching | Cohort and fixture safeguards exist; matching against the actual version-pinned PUDL data not yet verified | No independent longitudinal confirmation claimed |
| Empirical multi-year PyPSA dispatch | Blocked by data-admission requirements | No modeled dispatch, generation availability or dispatch-derived stress results claimed |

### Original-workbook acceptance protocol

The original EIA-860 ZIP archives must first pass pinned SHA-256 checks, then Plant/Generator workbook schema inspection, year-specific CISO extraction, independent OP count/MW reconciliation, four-way generator-identity bridge reconciliation, and re-aggregation of exported row-level changes. The workflow is designed to emit `official-data-acceptance-receipt.json` only after these checks pass. The presence of the workflow or source code **does not establish that the latest run succeeded**. Preserve the GitHub run ID, commit SHA, logs, manifest, reconciliation JSONs and generator-level CSV before changing this evidence status.

The scope of a successful acceptance receipt remains **CISO original-workbook OP inventory and capacity-bridge reconciliation only**. It does not independently certify historical balancing-authority membership, all non-OP records, commissioning dates, hourly generation availability, or empirical dispatch readiness.

### Interpretation guardrails for peer review

The +6,895.8 MW quantity is a difference in reported **OP nameplate inventory**. It is not a measure of newly constructed power plants, accredited capacity, dependable capacity, energy storage duration, or available dispatchable generation. The +1,053 MW Helms component is a reported OA-to-OP status transition for existing generators, not evidence of 2025 construction. The 29 records with reported operating years before 2025 are inventory entrants, not necessarily newly commissioned units or proven BA reassignment. The single-hour 2,271 MWh EIA-930 endpoint discrepancy identifies a consistency anomaly; a matching fuel-category value is not by itself causal attribution.

**Freeze rule:** Promote any archived EIA-860 numerical result to *independently reproduced* only when the official original-workbook workflow artifacts and their checksums are available for inspection and the corresponding reconciliation receipt reports success. Until then, retain the evidence qualifier in the abstract, tables, captions, and conclusions.


### Archived early-operating-year entrant cohort: descriptive breakdown (2026-11-12)

A row-level re-tabulation of the **archived** 29-record pre-2025 operating-year cohort (not an independent EIA-860 workbook extraction or a PUDL validation) yielded the following year-specific results:

| Reported operating year | Generator records | 2025 OP nameplate (MW) |
|---|---:|---:|
| 2012 | 1 | 0.0 |
| 2014 | 2 | 3.8 |
| 2018 | 1 | 2.3 |
| 2020 | 1 | 2.0 |
| 2021 | 5 | 7.2 |
| 2023 | 11 | 88.1 |
| 2024 | 8 | 34.7 |
| **Total** | **29** | **138.1** |

Twenty-three records have 2025 status OP, whereas six are non-OP (one OS and five SB). The technology-specific OP capacities are 70.7 MW batteries (five records), 33.2 MW solar PV (14 records), 30.0 MW onshore wind (one record), 2.8 MW landfill gas (two records), and 1.4 MW natural-gas internal-combustion generation (one record). The five petroleum-liquids records and one wood/wood-waste record have non-OP status and contribute zero OP capacity. Batteries, solar PV and onshore wind jointly account for 133.9 MW (96.96%) of this cohort's OP nameplate. These percentages describe the **selected historical-entrant cohort**, not all CISO capacity changes.

**Evidence qualifier:** This tabulation was calculated from `project_a_29_target_reconciliation_2026-11-12.csv`, which compares archived generator rows to a locally staged target list derived from the same historical cohort. Agreement between these files does not constitute independent source confirmation. The original EIA-860 2024/2025 workbook replay and real PUDL historical matching remain pending.


**Cohort concentration check (archived records, 2026-11-13).** Of the 29 earlier-operating-year entrants, 19 report operating years 2023 or 2024 (65.5% of records), accounting for 122.8 MW (88.9%) of the cohort's 138.1 MW OP nameplate. All 11 records dated 2023 are OP in the 2025 inventory, whereas only three of eight records dated 2024 are OP. The other five 2024 records have non-OP status; this concentration is descriptive and cannot establish a causal reporting lag, late BA assignment, or the date of physical commissioning. These statistics are recalculated from the archived 29-row reconciliation CSV, not from newly downloaded EIA/PUDL sources.

### Supplementary Table S1: archived pre-2025 operating-year entrants (2026-11-14)

The 29-record supplementary table is provided as a separate CSV evidence artifact, with columns `plant_id_eia`, `generator_id`, `reported_operating_year`, `reported_operating_month`, `status_2025`, `technology_2025`, `nameplate_2025_mw`, `op_capacity_delta_mw`, `interpretation`, and `evidence_tier`. The CSV has 29 data rows, of which 23 are OP, one OS, and five SB; its OP capacity delta sums to 138.1 MW. SHA-256 of the archived supplementary CSV: `d89aba3df44b74f25812383c8ae7c376f70e4b4efc4b952344fc128a8a5b17b1`.

**Suggested caption.** *Supplementary Table S1. Generator-level records first appearing in the 2025 archived CISO inventory despite a reported operating year before 2025.* The table records generator identifiers, operating-date fields, reported 2025 status and technology, nameplate capacity, and contribution to the change in OP inventory. The term *entrant* refers strictly to first appearance in the compared inventories; it does not imply 2025 construction or a verified BA reassignment. The table is derived from archived extracts and has **not** been independently reproduced against the official EIA-860 source workbooks. Its status and nameplate fields should not be interpreted as a certified 2025 commissioning record.

**Submission control.** The SHA-256 above identifies the specific local supplementary CSV. Before journal submission, deposit the CSV with the manuscript supplement or a versioned archival release, verify its hash against the deposited bytes, and replace this note with the permanent supplementary-data citation. Do not cite the local file as publicly accessible until it has actually been deposited.
