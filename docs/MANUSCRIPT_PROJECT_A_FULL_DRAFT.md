# Auditing Annual Generator-Fleet Transitions and Hourly Data Consistency for Reproducible Power-System Modeling: A 2024–2025 California ISO Case Study

**Manuscript draft v0.1 — 2026-11-10.** Research manuscript; not yet submission-ready. All numerical results below come from archived source and CI evidence. No empirical multi-year PyPSA dispatch is claimed.

## Abstract

Annual generator inventories and hourly balancing-authority observations are widely used to assemble power-system models, but their apparent completeness can obscure differences in reporting scope, status classification, temporal precision and source consistency. We present an auditable 2024–2025 case study for the California Independent System Operator (CISO) using annual U.S. Energy Information Administration (EIA) Form 860 generator and plant records and hourly EIA-930 observations. We construct an identity-matched, mutually exclusive accounting bridge for annual operable (OP) generator records, inspect reported operating-year cohorts and cross-check plant balancing-authority codes against original year-specific worksheets. Reported CISO OP nameplate increased from 85,634.2 MW in 2024 to 92,530.0 MW in 2025 (+6,895.8 MW, 8.05%). Newly present records contributed +6,339.3 MW; records absent in 2025, status transitions and nameplate revisions contributed −379.9, +862.4 and +74.0 MW, respectively. Batteries and solar photovoltaic accounted for 82.83% of the net OP nameplate change. However, three pumped-storage generators totaling 1,053 MW changed status from OA to OP while retaining reported June 1984 operating dates and CISO plant assignment in both years. Among 157 new-to-inventory records, 29 reported operating years before 2025. A targeted same-run EIA-930 audit also identified a 2,271 MWh disagreement between reported regional net generation and signed fuel-category sums for one hour. These findings show why annual inventory change and hourly source consistency must be separately validated before interpreting reported capacity as commissioning, availability or modeled dispatch. The contribution is an evidence-gated data-validation workflow, not an empirical generation-dispatch simulation.

**Keywords:** EIA-860; EIA-930; CISO; generator inventory; data provenance; power-system modeling; PyPSA; balancing authority.

## 1. Introduction

Reproducible electricity-system analysis depends on combining observations reported at different spatial, temporal and institutional resolutions. Annual generator records identify plants, generators, status and nameplate capacity; hourly balancing-authority series report operational quantities. A mechanically successful join between these sources does not establish that plant-level balancing-authority assignments match an operational network boundary, that annual status is hourly availability, or that reported operating dates identify an exact commissioning hour.

Open-source power-system tools such as PyPSA provide flexible multi-period simulation and optimization capabilities (Brown et al., 2018), while open-data model generators such as OSeMOSYS Global demonstrate that reproducible model construction is an established research direction (Barnes et al., 2022). Our novelty claim is therefore **not** the use of open data or the existence of a PyPSA workflow. It is the documented, identity-matched reconciliation of annual inventory changes with original plant-level BA evidence and an independent hourly cross-endpoint consistency check, with explicit limits on downstream inference.

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

Original Plant-sheet checks identify four plant IDs present with BA=CISO in both annual releases (six newly present generator records, 103.6 MW OP) and 16 plant IDs absent from the 2024 Plant worksheet but present in 2025 with BA=CISO (23 records, 34.5 MW OP). These findings distinguish two source-level pathways for first appearance without identifying their administrative or physical causes.

Three 351-MW generators at Helms Pumped Storage (Plant 6100) report operating dates of June 1984 in both years and status OA→OP. The plant reports BA=CISO in both annual Plant worksheets. The associated +1,053.0 MW OP change therefore reflects an annual status transition rather than verified 2025 construction or a plant-level BA transfer.

**Figure 2.** New-to-2025-CISO generator records grouped by reported operating year (2025 versus pre-2025), showing generator-record counts (128 versus 29) separately from OP nameplate MW (6,201.2 versus 138.1). Records and MW have different denominators; not all records are OP.

### 3.4 Targeted EIA-930 cross-endpoint inconsistency

For 2025-07-31T19–T23, regional net generation and signed fuel-category sums differ by 0, −1, +2,271, 0 and +1 MWh, respectively. The large difference is localized to T21 in this five-hour case. The T21 difference numerically matches the reported nuclear fuel category, but this equality alone does not establish nuclear omission or any particular upstream cause. No source correction is applied.

## 4. Discussion

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

**Before journal submission:** perform a systematic close-neighbor literature search (generator-inventory versioning and electricity-data validation); verify all citations and final journal formatting; embed and independently review the actual figures against archived bytes; check data redistribution rights; obtain coauthor review. The present primary-source and foundational references are not a complete literature review. Do not present this as a completed empirical PyPSA dispatch paper.
