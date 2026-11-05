# R02 standardized EIA fuel observations — data contract

Module: `src/multiyear_energy_validation/normalized_fuel.py`.

The normalized table has one row per **UTC EIA hour label × fuel category** for CISO. The nine supported category codes are COL, GEO, NG, NUC, OIL, OTH, SUN, WAT and WND. Leap-year 2024 contains 8,784 expected UTC hour labels; 2025 contains 8,760. The `period_utc_eia` column retains the API's native hour label without silently shifting it to hour-start or hour-end.

`observed_generation_mwh` is numeric for reported values (including negative net generation), and empty for absent source rows. `observation_status` distinguishes `observed` and `not_reported`. `taxonomy_boundary_flag` identifies GEO hours before its first reported observation; it is not evidence of zero geothermal output. `availability_estimate` is always false: actual observed renewable generation is not the renewable potential required by R02 dispatch.

The writer generates CSV and adjacent SHA-256 provenance manifest with row counts, observed counts, missing counts, and source metadata supplied by the caller. It never imputes missing records. This module establishes the table contract; full-year export and artifact upload require a separate workflow and verification before claiming an archived dataset.

Existing exclusions remain: 2024-11-02T08 through 2024-11-03T07 lack EIA fuel/NG/TI data; 2025-12-16T09 marks first reported GEO; 2025-07-31T21 has a fuel-sum versus region-NG discrepancy. These are separate data-quality dimensions and must not be collapsed into a single completeness flag.
