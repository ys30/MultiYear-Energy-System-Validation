# Project A — 29-target source reconciliation and CI status (2026-11-10)

## Independently rerun in the local execution environment

Read archived GitHub Actions ZIP `github-actions-artifact-13295023796.zip`, member `fleet_transitions_2024_2025.json`; read checked-in cohort CSV `data/pudl/project_a_pudl_29_targets.csv`. Filter transition records to `classification == new_to_ciso_inventory` and reported operating year < 2025. Match exact string keys `(plant_id, generator_id)`.

**Observed:** 29 filtered source rows, 29 CSV rows, zero absent CSV keys, zero absent source keys, zero status differences, zero operating-year differences, zero OP nameplate capacity differences. CSV OP capacity 138.1 MW. The source ZIP is from previously successful fleet workflow run 41772668659 (artifact 13295023796).

**CI status:** GitHub connector `fetch_commit_workflow_runs` for workflow commit `bd80bac333c43f52c71e23c7726bb92b861035a0` returned an empty list. This action filters to pull-request-triggered runs, so empty does **not** prove that no push workflow ran. It also cannot establish a passing CI result. The new PUDL fixture tests have **not** been independently verified as passing in CI.

**PUDL status:** Zenodo network access attempted and failed due to DNS resolution. No PUDL v2026.11.0 Parquet bytes, hash, schema, matched counts or monthly-history conclusions were obtained. Do not treat EIA-860 cohort reconciliation as independent PUDL evidence.

**Research status:** Empirical PyPSA dispatch remains blocked; annual inventory bridge and EIA-930 cross-endpoint evidence remain unchanged.
