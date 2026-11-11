# PUDL monthly changelog cross-check: execution gate

**Status (2026-11-10):** 29 EIA-860 historical-operating-year entrants have been extracted from the original 2024–2025 transition JSON and independently counted (23 OP, 1 OS, 5 SB; 138.1 MW OP). A matching CSV was generated from archived CI artifact 13295023796. **PUDL Parquet has not yet been downloaded or queried**; no matched/unmatched results may be claimed.

## Reproducible target selection

Input: private Actions artifact `ciso-eia860-fleet-transitions` from run 41772668659, file `fleet_transitions_2024_2025.json`.

Filter `changes` where `classification == "new_to_ciso_inventory"` and `int(current_operating_year_raw) < 2025`. Sort by integer Plant ID and Generator ID. The resulting target list contains 29 records and sums to 138.1 MW when counting `current_nameplate_mw` **only for current_status=OP**.

## PUDL source contract

- Dataset: Catalyst Cooperative PUDL `core_eia860m__changelog_generators`, from a **specific immutable release**; record version, exact Parquet URL, file SHA256, retrieval date, schema and row count before matching.
- The changelog records changes, **not monthly snapshots**. First changelog date is not necessarily a physical commissioning date.
- Use exact `plant_id_eia` and `generator_id` keys; do not fuzzy-match IDs.
- Validate `report_date` presence and key uniqueness in downloaded source.
- Do not assume that a missing changelog row means the generator did not exist.
- PUDL transforms EIA-860M; agreement with EIA-860 is a cross-release consistency check, not independent physical observation.

## Execution blocker and safe interpretation

The current execution environment cannot reach the PUDL remote data endpoint; an immutable Parquet URL and archive have not been established. The checked-in script is a **candidate** and must be schema-tested against the pinned release before claiming an executed result. No CI run has been launched for the PUDL check. Continue with an official immutable release and a small metadata/schema probe first; then run the 29-key join and archive the match output.

**Empirical dispatch remains blocked.**
