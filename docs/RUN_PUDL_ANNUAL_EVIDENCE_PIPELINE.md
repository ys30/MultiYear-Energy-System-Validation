# Running the annual PUDL evidence pipeline

This pipeline is **not** a data downloader and is **not** a commissioning or empirical-dispatch certification. Obtain an authorized annual generator export from a fixed PUDL release. The source must be an **annual generator table**, not an EIA-860M changelog.

Required CSV columns: `plant_id_eia,generator_id,report_date`. The file must contain 2023, 2024 and 2025 records, with unique generator/year keys. Preserve original source URL, immutable release, extraction SQL, retrieval date and file checksum in a private provenance note. A targeted-only subset cannot establish overall annual-source coverage.

```bash
sha256sum /secure/path/annual_generators.csv
python scripts/run_pudl_annual_evidence_pipeline.py \
  --annual-csv /secure/path/annual_generators.csv \
  --targets data/pudl/project_a_pudl_29_targets.csv \
  --release v2026.11.0 \
  --sha256 REPLACE_WITH_INDEPENDENTLY_RECORDED_SHA256 \
  --out-dir /secure/path/project_a_pudl_evidence
```

Outputs: `pudl_annual_coverage.json` and `pudl_eia860_87_row_evidence_matrix.json`. Both remain descriptive. Review unmatched plant/generator keys and source-wide year counts before attributing any difference to commissioning, BA reassignment, or record migration.

**Status as of 2026-11-17:** source export not available in this PR; no real-data matrix executed. Do not publish source-wide coverage or dispatch conclusions from unit-test fixtures.
