# R02a cross-endpoint acceptance record — updated 2026-11-10

**Scope:** EIA-930 CISO, raw hour-ending labels 2025-07-31T19–T23. Compare region-data NG against the **signed** sum of fuel-type-data. This is a source-consistency audit, **not** a physical energy balance or load correction.

## Independently verified same-run evidence

- Actions run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42921140978
- Job: 130195976045, `source-audit`, completed/success.
- Regression suite: **13 passed** (job log).
- Artifact: 13811587152, `r02a-cross-endpoint-raw-audit`, 3 files: `region_raw.json`, `fuel_raw.json`, `cross_endpoint_audit.json`.
- Artifact ZIP SHA256 reported by GitHub: `fbbdfc76e4820c6e8fc6eaa6a998c1f2e3af1b28de8ae53a243fb1423321a727`. This is the archive digest, **not** the individual raw-file digests.
- Downloaded archive was opened independently; SHA256 of each of the two raw files matched the corresponding hash in `cross_endpoint_audit.json`.
- Raw EIA response row counts: 5 region NG + 40 fuel rows; eight fuel categories per hour.
- Verified same-run values (MWh):

| Period | Region NG | Signed fuel sum | Fuel − region |
|---|---:|---:|---:|
| T19 | 29,677 | 29,677 | 0 |
| T20 | 29,776 | 29,775 | −1 |
| T21 | 27,732 | 30,003 | +2,271 |
| T22 | 30,783 | 30,783 | 0 |
| T23 | 31,641 | 31,642 | +1 |

The anomalous T21 difference was **reproduced in a fresh, same-run pair of endpoint responses**, and was not caused by joining separately retrieved historical snapshots. A numerical match with the T21 nuclear fuel value (2,271 MWh) **does not establish a nuclear omission mechanism**.

Full verification details: `docs/R02A_SAME_RUN_RAW_EVIDENCE_2026-11-10.md`. Tracking: https://github.com/ys30/MultiYear-Energy-System-Validation/issues/1#issuecomment-6782009300

## Research disposition

**Source discrepancy reproduced; cause unresolved.** No automatic correction of region NG, demand, or fuel values is permitted. The independent CAISO load comparison does not validate the isolated EIA demand trough. EIA endpoint semantics, upstream revision behavior, and the physical interpretation of signed OTH still require source-level explanation. The fuel-versus-NG check must not be presented as a generation–demand balance.

**R02 empirical dispatch remains BLOCKED** (`empirical_dispatch_approved = false`), additionally pending availability, interchange, storage, cost, and boundary validation. Passing this source-audit gate alone cannot authorize empirical dispatch.

## Evidence retention

The GitHub artifact expires **2026-11-24**. The three original files are now independently confirmed present in the private repository under `evidence/r02a/2026-11-10/` (`region_raw.json`, `fuel_raw.json`, `cross_endpoint_audit.json`). The preserved audit report contains the expected same-run five-hour differences and the original SHA256 manifest. This confirms durable version-controlled availability; the separate raw-byte hash verification was performed on the downloaded Actions artifact. Never commit credentials or secret-bearing query URLs.

## Status of acceptance items

1. Run, job, artifact and results: **verified**.
2. Raw response files and their SHA256 values: **verified**.
3. Five-hour completeness, signed categories, and discrepancy: **verified**.
4. Source revision / official endpoint semantic explanation: **open**.
5. Durable private raw evidence retention: **verified present in private GitHub repository**.
6. Empirical dispatch approval: **blocked**, independently of the source audit's technical success.
