# Project A — PUDL annual coverage acceptance (2026-11-17)

## Verified
- PR #2 branch CI run 44032567544 completed successfully.
- Job 133867730533 ran `python -m pytest -q tests/test_audit_pudl_annual_coverage.py`.
- Log reports **3 passed in 0.08s**.
- Research data contracts run 44032567569 also completed successfully.

## Not yet verified
- No real pinned PUDL annual export has been audited by this new program.
- No causal explanation for 2023/2024 target nonmatches is established.
- No commissioning, dispatch, reliability, emissions or cost claim is authorized.

## Reproduce against a real export
1. Obtain the annual generator export for a fixed PUDL release. Preserve the exact source URL, release ID, retrieval timestamp, schema and SHA256.
2. Ensure CSV columns: `plant_id_eia,generator_id,report_date` and one row per generator/year.
3. Run:

```bash
sha256sum annual_generators.csv
python scripts/audit_pudl_annual_coverage.py \
  --annual-csv annual_generators.csv \
  --targets data/pudl/project_a_pudl_29_targets.csv \
  --release <immutable-release-id> \
  --sha256 <64-character-source-sha256> \
  --output artifacts/pudl_annual_coverage.json
```

4. Examine `source_rows_by_year`, `target_exact_matches_by_year`, and `target_plant_matches_by_year`. Zero exact matches does **not** imply that assets were physically absent.
5. Independently compare unmatched plant/generator keys with original EIA-860 Plant and Generator workbooks and EIA-860M change records before attributing any commissioning or BA assignment mechanism.

## Review gate
Keep PR #2 as draft until real-source provenance, coverage scope and the annual diagnostic receipt are independently reviewed. Do not merge solely on fixture-test success.
