# Project A: pinned PUDL real-data acquisition (not yet executed)

## Source and release

Use the archived Catalyst Cooperative PUDL **v2026.11.0** release (2026-11-10), not `latest` or `nightly`. Published release: https://zenodo.org/records/24119965 ; release notes: https://docs.catalyst.coop/pudl/en/v2026.11.0/release_notes.html .

This release includes EIA-860M changelog fixes. Do not infer that an EIA-860M changelog is a complete monthly generator-presence panel. The changelog and annual generator tables answer different questions. For year-by-year presence, use `out_eia__yearly_generators` with explicit `report_date` and generator keys; for change events use the documented EIA-860M changelog, only after confirming its actual schema. Never relabel annual records as changelog events.

## Required provenance before acceptance

1. Record immutable release `v2026.11.0`, Zenodo record, exact downloaded filename and source URL, byte count, SHA-256, download UTC timestamp, and column schema.
2. Extract the **29 fixed (plant_id_eia, generator_id)** keys from `data/pudl/project_a_pudl_29_targets.csv`. Preserve generator IDs as strings.
3. Verify the selected table's meaning, its actual column names and date semantics before running any existing script. The current `scripts/pudl_pre2025_entrant_crosscheck.py` expects `plant_id_eia,generator_id,report_date` and interprets rows as *changelog events*; do not pass annual panel rows to it.
4. For annual tables, produce a separate annual-presence matrix with rows for each target and years 2023, 2024, 2025; distinguish no row from non-operating status, and flag duplicate (plant,generator,year) keys.
5. Save a machine-readable acceptance receipt with release, source hashes, counts, missing keys, and `pudl_matched` and `empirical_dispatch_approved` false until actual checks complete. Publish aggregate counts only after the real-source run passes.

## Scope limitations

PUDL EIA-860/EIA-860M transformations are not independent evidence of physical commissioning or BA transfers. PUDL changelog matches do not prove continuous monthly presence. EIA-930 hourly data and PyPSA dispatch remain separate evidence requirements.

## Local invocation for genuine changelog extracts only

```bash
sha256sum downloaded_pudl_changelog.csv
python scripts/pudl_pre2025_entrant_crosscheck.py \
  --targets data/pudl/project_a_pudl_29_targets.csv \
  --pudl downloaded_pudl_changelog.csv \
  --release v2026.11.0 \
  --sha256 REPLACE_WITH_OBSERVED_64_HEX_SHA256 \
  --output results/pudl_changelog_v2026.11.0.json
```

The example is **not evidence of a completed run**. Verify provenance and input semantics before execution.
