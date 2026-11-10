# R02a — Official EIA-930 semantics and interpretation boundary (2026-11-10)

## Primary references

1. EIA Hourly Electric Grid Monitor, About and Data Element Descriptions: https://www.eia.gov/electricity/930-content/about.html
2. Official EIA-930 form instructions, archived OMB publication: https://www.reginfo.gov/public/do/DownloadDocument?objectID=126698001
3. EIA Open Data API overview: https://www.eia.gov/opendata/

## Confirmed meanings

- Region-data type **NG** is total net generation, not natural-gas generation; **NG** as a fueltype code in fuel-type-data means natural gas. These are distinct fields and must never be confused.
- EIA distinguishes demand **D**, total net generation **NG**, and net interchange **FLOW**. Net interchange sign conventions matter in any physical balance.
- The instructions allow **negative net generation** for net storage use. Fuel-category **OTH** means 'other' energy sources and can include confidentially masked generation. Thus the observed negative OTH must remain signed; neither dropping nor clipping it is justified.
- EIA's monitoring page identifies net generation by energy source as a separate reported element. A discrepancy between its source-category sum and reported total NG is an **endpoint/source consistency** problem, not evidence that demand should be edited.

## Empirical same-run finding

Actions run 42921140978, artifact 13811587152, 5 region NG rows and 40 fuel rows, both raw-file hashes checked against audit manifest. Signed fuel-minus-region differences for CISO 2025-07-31T19–T23: 0, −1, +2271, 0, +1 MWh. At T21 nuclear generation is 2271 MWh, exactly equal to the discrepancy.

**The equality is a hypothesis-generating coincidence, not causal proof.** Possible explanations (source-side classification/aggregation issue, revision, reporting artifact) have not been distinguished by the available records. Do not label this as 'nuclear omitted' without upstream confirmation. No fuel-category deletion or adjustment is authorized.

## Manuscript-ready restrained interpretation

> A same-retrieval comparison of EIA-930 CISO total net generation and the signed sum of generation by fuel type identified a localized 2,271 MWh discrepancy at the 2025-07-31T21 hour-ending label. The neighboring hourly discrepancies were 0, −1, 0, and +1 MWh. All five region records and 40 fuel records were preserved with raw-response SHA256 verification. Although the anomalous difference equals the reported nuclear contribution at that hour, the available evidence does not establish an upstream cause. We therefore flag this interval as an unresolved cross-endpoint inconsistency rather than correcting the source data or treating the fuel sum as an independently validated system balance.

## Remaining source questions

- Request source-side confirmation from EIA / reporting BA of whether region total NG and fuel-type totals are independently reported, derived, or revised on different schedules.
- Confirm whether specific category codes are suppressed/aggregated for this respondent/hour, and how negative OTH was reported.
- Retain private original artifact beyond GitHub Actions' 2026-11-24 expiry.
- Independently validate generation availability, storage, interchange, cost, and system boundaries before R02 empirical dispatch.

**Decision:** R02a discrepancy reproduced and integrity checked; causal attribution unresolved; empirical dispatch remains BLOCKED.
