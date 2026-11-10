# Project A — manuscript integration draft: R02a (2026-11-10)

**Status:** Manuscript text proposal, not a claim that the full paper is updated or ready for submission. All empirical numbers trace to same-run EIA-930 audit Actions run [42921140978](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42921140978), artifact 13811587152, with independent raw-file hash checks. This analysis is distinct from the blocked R02 dispatch experiment.

## Methods — Cross-endpoint data consistency

We extracted five consecutive EIA-930 hourly records for the California Independent System Operator (CISO), using the original hour-ending labels 2025-07-31T19–T23. For each hour, we compared the total net generation reported by the EIA region-data endpoint (series type `NG`) against the algebraic sum of all fuel-type-data records for the same respondent and hour. In this context `NG` as a region-data *type* denotes total net generation, whereas `NG` as a *fuel code* denotes natural gas; these variables were not conflated. All fuel-type values, including negative `OTH`, were retained with their original signs. We rejected missing or duplicate periods, inconsistent fuel-category coverage, and non-finite values rather than imputing or silently dropping records. Raw endpoint responses were archived together with an audit manifest containing SHA256 digests; the two raw-file digests were independently checked against the manifest. The five-hour window is a targeted diagnostic and does not establish the frequency of such inconsistencies in the complete series.

## Results — Localized cross-endpoint discrepancy

The same-retrieval audit contained five total-generation observations and 40 fuel-category observations (eight categories per hour). For the hour ending 2025-07-31T21, the fuel-type sum was 30,003 MWh while region-level total net generation was 27,732 MWh, a positive difference of 2,271 MWh. Differences in the two preceding and two following hours were 0, −1, 0, and +1 MWh, respectively. The anomalous difference numerically equals the nuclear fuel-category observation at T21 (2,271 MWh), but the two source responses alone cannot establish whether the cause was an omitted category, an upstream reporting issue, a revision mismatch, or another mechanism. The result is therefore classified as an **unresolved source inconsistency**, not a reconciled generation total.

### Table R02a. Same-run endpoint comparison

| Hour-ending label (2025-07-31) | Region NG (MWh) | Signed fuel sum (MWh) | Fuel minus region (MWh) |
|---|---:|---:|---:|
| T19 | 29,677 | 29,677 | 0 |
| T20 | 29,776 | 29,775 | −1 |
| T21 | 27,732 | 30,003 | +2,271 |
| T22 | 30,783 | 30,783 | 0 |
| T23 | 31,641 | 31,642 | +1 |

**Table note:** The comparison concerns two generation-related source representations; it is not a generation-demand balance. No original EIA observation was corrected.

## Discussion — Implications for reproducible energy-system models

This case illustrates why agreement on time labels and respondent identifiers does not guarantee internal consistency across source endpoints. The large single-hour discrepancy would be hidden by an ingestion workflow that silently equated the fuel sum with reported total generation, clipped negative categories, or interpolated the discrepant observation. Its proximity to otherwise near-zero differences makes the hour a useful stress test for data-quality gates, but not evidence of a particular upstream failure mode. The coincidence with the nuclear category warrants investigation rather than causal labeling.

The source discrepancy must also be distinguished from a separate demand-series anomaly. A fuel-total versus region-total generation mismatch does not, by itself, prove that a demand observation is wrong or provide a justified replacement for it. Independent CAISO load evidence raised concern about the demand trough at the same hour, but the targeted five-hour audit is not a calibrated reconciliation of demand, interchange, storage, and generation.

We therefore preserve original source records and isolate this hour in diagnostic and sensitivity analyses. We do **not** promote interpolated values to corrected observations, and we do **not** use this audit to authorize empirical PyPSA dispatch. That authorization additionally requires validated availability, interchange, storage, cost, and boundary assumptions. This separation of ingestion reproducibility, source consistency, and physical model validity is the methodological contribution of the case study.

## Figure recommendation (no new experiments required)

**Figure R02a:** A five-hour diverging bar plot of signed fuel-minus-region differences (MWh), with a zero reference line and T21 highlighted. An inset or second panel can show the two source series, but the main axis must not imply that the 2,271 MWh difference is a measured physical imbalance. A table is preferable if the manuscript already has many figures.

## Limitations and outstanding checks

1. This is a **targeted five-hour diagnostic**, not a population-wide prevalence estimate.
2. EIA's source-level aggregation and revision mechanism for this respondent/hour has **not** been confirmed; do not claim a nuclear omission.
3. Independent external load evidence and generation consistency address different quantities.
4. The archived Actions artifact is scheduled to expire 2026-11-24 and must be preserved in approved durable private storage.
5. R02 empirical dispatch remains **BLOCKED**; no performance or policy conclusions can be drawn from a non-executed dispatch experiment.

## References / provenance

- EIA Hourly Electric Grid Monitor: https://www.eia.gov/electricity/930-content/about.html
- EIA Open Data API: https://www.eia.gov/opendata/
- Same-run evidence: `docs/R02A_SAME_RUN_RAW_EVIDENCE_2026-11-10.md`
- Semantics review: `docs/R02A_EIA_OFFICIAL_SEMANTICS_2026-11-10.md`
- Audit acceptance: `docs/R02A_CROSS_ENDPOINT_ACCEPTANCE.md`
