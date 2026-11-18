# Project A — Historical generator ID review (2023–2024)

Source: pinned PUDL `v2026.11.0`, `out_eia__yearly_generators.parquet`. Verified in GitHub Actions run https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44242038951. Fixed target list: `data/pudl/project_a_pudl_29_targets.csv`.

## Historical rows and 2025 target IDs at the same plant

| EIA plant | Historical IDs in **both** 2023 and 2024 | 2025 cohort target IDs | Exact overlap |
|---|---|---|---|
| 50535 | WGNS | MWD1 | None |
| 61446 | PV2 | BA2 | None |
| 63094 | SBAD1, SBAD2 | G100, G200, SOLAR | None |
| 65820 | OWS | OWB | None |

Historical annual generator records: **5 in 2023** and **5 in 2024** across these four plants. The target cohort contains **6 different generator IDs** at these plants, none matching the historical IDs. This does **not** establish that an ID was renamed, that two records refer to the same physical unit, or that a target generator was absent before 2025.

## High-priority independent review

1. Compare official **2023 and 2024 EIA-860 annual** generator records for each plant and all generator IDs above, preserving raw source filenames, reporting years, statuses, operation dates and SHA256 hashes.
2. Review official 2025 EIA-860 generator records for the six target IDs. The fixed target cohort lists reported operating years 2021–2024, so a 2025-only appearance in this PUDL annual table must **not** be interpreted as 2025 commissioning.
3. Do **not** infer `WGNS→MWD1`, `PV2→BA2`, `SBAD1/SBAD2→G100/G200/SOLAR`, or `OWS→OWB` without independent plant-level documentary evidence.
4. Review the remaining 23 historical unmatched targets separately: their plants have no generator records in the 2023/2024 PUDL annual table, which is a source-coverage limitation, not physical absence.
5. Treat EIA-860M monthly changelog data as a separate source, not an interchangeable annual snapshot.

## Gate

- Generator identity crosswalk verified: **false**
- Physical commissioning verified: **false**
- Empirical PyPSA dispatch approved: **false**

These observations are suitable for a descriptive data-quality/results appendix, not a commissioning or dispatch claim.
