# Paper A1 — E2 B1 PUDL identity baseline assessment

**Evidence date:** 2026-11-23. **Verified CI:** [run 45233024270](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/45233024270), pinned PUDL v2026.11.0 `out_eia__yearly_generators.parquet`.

## Verified facts

The annual generator parquet exposes 114 columns. The schema probe completed successfully and writes `e2_pudl_entity_schema_probe.json` to the run artifact. **No cross-vintage physical identity mapping has yet been established from this probe.** `canonical_identity_verified=false` is deliberate.

B0 is the already implemented exact-key baseline on `(plant_id_eia,generator_id)`; it measures record-key continuity, not physical identity. B1 is reserved for a documented PUDL entity-resolution output whose semantics and version can be independently verified. B2 requires official primary-source unit-level evidence and permits abstention.

## B1 implementation gates

1. Identify a version-pinned published PUDL generator entity table, entity identifier or source-to-entity mapping in official documentation and output catalog. Record exact URL and source version.
2. Inspect table grain and field semantics. Determine whether identifiers represent generator physical continuity across EIA IDs, only normalized records, or something else.
3. Test uniqueness and coverage by source year, plant and generator; check one-to-many and many-to-one relationships and cross-vintage joins.
4. Freeze a non-leaking baseline definition before independent adjudication. Do not let candidate mappings contaminate blinded reviewer judgments.
5. If no supported cross-ID physical mapping exists, mark B1 **not applicable / unavailable** rather than inventing a match. Report B0 and B2 separately.

## E2 status

The reproducible stratified review queue contains 158 source-year keys (eight strata); official evidence collection and independent adjudication have not occurred. No physical lineage or error prevalence is claimed. E4 dispatch remains gated.

## Priority

The next useful step is to inspect the PUDL published output catalog and entity-resolution documentation, then build a verified B1 extractor only if the actual schema supports it. In parallel, begin official EIA source collection for within-plant review cases.
