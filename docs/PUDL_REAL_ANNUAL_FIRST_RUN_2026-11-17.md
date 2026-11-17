# Project A — first real PUDL annual extraction (2026-11-17)

GitHub Actions run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44022893767
Artifact: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/44022893767/artifacts/14301681495
Code commit: a97cbb8d1a2b510d17e285c13dbd8f2519cb959f

Pinned query: `s3://pudl.catalyst.coop/v2026.11.0/out_eia__yearly_generators.parquet` (anonymous S3, us-west-2, path-style addressing).

Actual CI log: `query_success=true`; `matched_rows=29`; `matched_rows_by_year={"2023":0,"2024":0,"2025":29}`.
Extracted CSV SHA256: `cdb1367ec15b21bbe430c0c96470cf8786c81450c789cbe8d9036cc07530b5de`.
The remote full Parquet SHA256 has **not** been independently verified. The full-source 2023–2025 year coverage has **not** been verified. These 29 are *matched annual rows*, not 29 independently verified physical additions. This extract has not been compared with EIA-860M changelog or EIA-930 hourly output.

## Next acceptance steps
1. Independently query annual source `SELECT year(report_date), count(*) ... GROUP BY 1` for 2023–2025 and verify annual coverage and schema. Avoid mistaking zero cohort matches for absent annual source years.
2. Independently cross-check 29 row keys and their 2025 dates against fixed target file; inspect `operational_status` and `operating_date` semantics as available.
3. Preserve a source snapshot checksum or explicit S3 object version/ETag metadata and record query code commit.
4. Only after (1)–(3), label the PUDL annual-presence audit complete. Do not infer commissioning, physical BA transfer, or dispatch approval.

Evidence scope: authentic PUDL versioned remote query executed successfully; **annual coverage audit remains incomplete**.
