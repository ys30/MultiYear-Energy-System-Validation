# R02 standardized EIA fuel observations — data contract

Module: `src/multiyear_energy_validation/normalized_fuel.py`.

The normalized table has one row per **UTC EIA hour label × fuel category** for CISO. The nine supported category codes are COL, GEO, NG, NUC, OIL, OTH, SUN, WAT and WND. Leap-year 2024 contains 8,784 expected UTC hour labels; 2025 contains 8,760. The `period_utc_eia` column retains the API's native hour label without silently shifting it to hour-start or hour-end.

`observed_generation_mwh` is numeric for reported values (including negative net generation), and empty for absent source rows. `observation_status` distinguishes `observed` and `not_reported`. `taxonomy_boundary_flag` identifies GEO hours before its first reported observation; it is not evidence of zero geothermal output. `availability_estimate` is always false: actual observed renewable generation is not the renewable potential required by R02 dispatch.

The writer generates CSV and adjacent SHA-256 provenance manifest with row counts, observed counts, missing counts, and source metadata supplied by the caller. It never imputes missing records. This module establishes the table contract; full-year export and artifact upload require a separate workflow and verification before claiming an archived dataset.

Existing exclusions remain: 2024-11-02T08 through 2024-11-03T07 lack EIA fuel/NG/TI data; 2025-12-16T09 marks first reported GEO; 2025-07-31T21 has a fuel-sum versus region-NG discrepancy. These are separate data-quality dimensions and must not be collapsed into a single completeness flag.

## Verified full-year artifact export

[Successful GitHub Actions run 42078909965](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42078909965) produced normalized 2024 and 2025 CSVs and adjacent JSON manifests as the private run artifact `r02-ciso-eia-fuel-2024-2025` (retention: 30 days).

| Year | Normalized cells | Observed rows | Not-reported cells | Whole missing UTC hours | CSV SHA-256 |
| --- | ---: | ---: | ---: | ---: | --- |
| 2024 | 79,056 | 70,067 | 8,989 | 24 | `45e57e2b9bd6ac7a9eccf0dca0e35a915882fa09270cdcd8127f667441bdfd21` |
| 2025 | 78,840 | 70,455 | 8,385 | 0 | `52b1b4b468e1c24041b4d72cd5af148c51119ae5f750324760fe6ed5bd3b98c9` |

The 2025 unreported cells correspond to GEO being absent before its reporting introduction; they do **not** establish zero geothermal production. The 2024 missing hours affect fuel generation and regional NG/TI, while demand remains observed.

The `r02_export_gate.py` verifier checks CSV SHA-256, unique hour/fuel keys, observed/missing semantics and manifest row counts. Passing these integrity checks does not grant empirical PyPSA dispatch approval.
