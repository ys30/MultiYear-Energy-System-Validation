# Project A — Real PUDL annual generator coverage findings

## Source and reproducibility

- PUDL release: `v2026.11.0`.
- Source: `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/v2026.11.0/out_eia__yearly_generators.parquet`.
- Exact annual export CSV SHA256: `762e6712d00171e921bab9c235dcb6aa4caad15ccd273d7f8cf68cd1a5f51561`.
- Fixed 29-target CSV SHA256: `01a92f10e13401d185f9a6f1a07b2244eba212237174772519bc0a8338d93b5f`.
- GitHub Actions run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44222689632
- Artifact ID: `14391327986` (retention-limited; contains provenance, coverage receipt and 87-row evidence matrix).

## Observed annual source coverage

| Report year | PUDL annual generator rows | Exact target generator records | Target generator keys at plants with any record | Target generator keys at plants without a record |
|---|---:|---:|---:|---:|
| 2023 | 33,446 | 0 | 6 | 23 |
| 2024 | 34,871 | 0 | 6 | 23 |
| 2025 | 36,585 | 29 | 29 | 0 |

The 29 target generator keys occur at 20 distinct plants in the 2025 annual table. In each of 2023 and 2024, only 4 of those plants have annual generator records, accounting for 6 target keys whose generator ID does not match a record. This is **source-record coverage**, not proof of construction or commissioning.

## Interpretation boundaries

1. A missing PUDL annual generator row **does not** prove that the physical generator did not exist or was not operating.
2. PUDL annual tables, official EIA-860 reporting-year data, EIA-860M monthly data, and historical commissioning evidence must not be conflated.
3. Some target records are not in 2025 OP status; no commissioning year is inferred from the 2025 inventory.
4. These findings do **not** approve empirical PyPSA dispatch, establish generator commissioning, or resolve the EIA-930 generation-by-fuel discrepancy.

## Next independent checks

- Retrieve official EIA-860 annual source records for 2023 and 2024 and compare reporting-year cohort and generator status.
- For the six generator keys at four plants present in both earlier years, inspect alternative generator identifiers and annual generator rows **without fuzzy auto-matching**.
- For the remaining 23 keys, audit plant coverage and source-year boundaries before interpreting absence.
- Preserve original raw records and checksums; use the 87-row matrix only as descriptive evidence until independent cross-validation.

## Reproduction

Run the `Project A PUDL annual coverage diagnostics` workflow on the research branch; it exports the fixed-version annual source, computes the CSV SHA256, runs the fail-closed audit, and uploads the EIA-860-linked 87-row evidence matrix. The release is pinned, but reproducibility also requires the exported CSV checksum above to remain unchanged.

**Project status:** annual source coverage diagnostics complete; empirical dispatch not approved.
