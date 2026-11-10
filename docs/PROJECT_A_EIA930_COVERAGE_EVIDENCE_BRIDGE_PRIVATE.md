# Project A — EIA-930 coverage evidence bridge: source status (private)

## Verified source records available in this repository

- [R02a hourly demand quality](R02A_CISO_HOURLY_LOAD_QUALITY_2024_2025.md) reports 8,784 complete UTC demand hours for 2024 and 8,760 for 2025; historical workflow [41780386655](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41780386655).
- [R02 fuel annual audit](R02_FUEL_ANNUAL_AUDIT_2024_2025.md) reports 8,760 of 8,784 UTC fuel reporting hours for 2024 and 8,760 of 8,760 for 2025. The 2024 missing fuel block is 2024-11-02T08 through 2024-11-03T07 UTC.
- Demand anomaly: normalized **hour-start 2025-07-31T20:00 UTC**, raw EIA **hour-ending label 2025-07-31T21**. The value 11,819 MWh (one-hour mean 11,819 MW) is present in the original API response. These are two labels for the **same** hour, not two different anomalies.
- Independent CAISO 5-minute telemetry does not show the same one-hour demand collapse. Different source definitions prohibit treating the numerical gap as a direct error correction. The source observation remains preserved; hypothetical neighbor interpolation is sensitivity-only.
- 2025 GEO fuel category first reports at EIA hour label 2025-12-16T09; earlier absence must not be interpreted as zero.

## Coverage denominators

| Series | Year | Expected UTC hours | Audited reported hours | Missing hours | Interpretation |
|---|---:|---:|---:|---:|---|
| CISO demand | 2024 | 8,784 | 8,784 | 0 | Structurally complete; anomaly-free not established |
| CISO demand | 2025 | 8,760 | 8,760 | 0 | Structurally complete; one isolated hour flagged |
| CISO fuel hourly labels | 2024 | 8,784 | 8,760 | 24 | Incomplete; no silent zero filling |
| CISO fuel hourly labels | 2025 | 8,760 | 8,760 | 0 | Hour-label coverage only; category taxonomy still shifts |

## Evidence and integration boundary

The newly tested `paper_eia930_coverage_contract.py` validates **structured coverage audit dictionaries**, not the Markdown table above. This note preserves the verified historical sources, but **does not yet make the paper manifest automatically reproduce these historical coverage numbers**. That requires a workflow to retrieve the versioned annual EIA source records, regenerate demand/fuel coverage JSONs, and pass those JSONs into the paper manifest. A typed source/provenance bridge should distinguish historical results from same-run results. Do not hardcode these historical numbers as if they had been computed by the latest R02 run.

## Recommended manuscript phrasing

*Demand-series structural completeness and fuel-series completeness were evaluated separately. CISO demand records covered all 8,784 UTC hours in 2024 and all 8,760 in 2025, whereas 2024 fuel-type reporting covered 8,760 of 8,784 hours. One 2025 demand observation was flagged at 20:00 UTC on July 31 (raw EIA hour-ending label T21); independent telemetry and component checks supported an inconsistency in its temporal pattern, but did not establish an authoritative replacement. Accordingly, source values were retained, and hypothetical adjustments were restricted to explicitly labeled sensitivity analysis. The separate empirical-dispatch readiness audit remained closed.*

These are **historically verified source findings**; they are not new measurements from the 2026-11-10 manuscript-manifest CI.
