# R02a same-run EIA cross-endpoint evidence (2026-11-10)

**Evidence status: source-level discrepancy reproduced and raw-file integrity verified; causal explanation unresolved.**

- Actions run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42921140978
- Head commit: `ce649449fdc968ab4904ae9b3f8b3ea989b17cbd`
- Job `source-audit`: completed / success; **13 offline tests passed**.
- Artifact ID `13811587152`, `r02a-cross-endpoint-raw-audit`; GitHub artifact ZIP digest `sha256:fbbdfc76e4820c6e8fc6eaa6a998c1f2e3af1b28de8ae53a243fb1423321a727`; expires **2026-11-24T23:11:09Z**.
- Downloaded and independently opened ZIP. Contains `region_raw.json`, `fuel_raw.json`, `cross_endpoint_audit.json`.
- Independently checked each raw file's SHA256 against the hash recorded in `cross_endpoint_audit.json`: **both matched**.
- Parsed raw response row counts: **5 region rows and 40 fuel rows**.

| EIA hour-ending period | Region NG (MWh) | Signed fuel sum (MWh) | Fuel minus region (MWh) |
|---|---:|---:|---:|
| 2025-07-31T19 | 29677 | 29677 | 0 |
| 2025-07-31T20 | 29776 | 29775 | -1 |
| 2025-07-31T21 | 27732 | 30003 | **+2271** |
| 2025-07-31T22 | 30783 | 30783 | 0 |
| 2025-07-31T23 | 31641 | 31642 | +1 |

**Interpretation:** T21 discrepancy persists in a same-run, raw-hash-verified snapshot. Numerical equality to the T21 nuclear category (2271 MWh) does not prove nuclear omission or explain the upstream discrepancy. The independent CAISO load anomaly and broader source admissibility questions remain separate. No source correction, no empirical dispatch approval.

**Remaining gate:** source-definition/causal resolution or defensible exclusion policy, plus separate generation availability, interchange, storage, costs and boundary validation before empirical PyPSA dispatch. Retain raw evidence in durable *private* storage before the 14-day Actions artifact expires.
