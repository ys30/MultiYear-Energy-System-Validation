# R02a: independently inspected historical EIA fuel CI log

**Evidence status:** verified archived CI log, **not** a fresh 2026-11-10 cross-endpoint API re-fetch.

- GitHub Actions run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41960929998
- Job ID: `127026855005` (`fuel-candidates`)
- Conclusion: `completed / success`
- Logged API response: `EIA_FUEL_CANDIDATES`, 40 rows, 8 categories for each of five hourly UTC labels.
- Execution: 2026-11-05 03:20 UTC (from job log)
- Fuel categories in every hour: `COL, NG, NUC, OIL, OTH, SUN, WAT, WND`
- Fuel sums below are **recomputed directly from the logged raw candidate rows**, including negative `OTH`.

| EIA UTC period | Signed fuel sum (MWh) | NUC (MWh) | OTH (MWh) | Historical region NG (MWh) | Difference (MWh) |
|---|---:|---:|---:|---:|---:|
| 2025-07-31T19 | 29,677 | 2,270 | -6,332 | 29,677 | 0 |
| 2025-07-31T20 | 29,775 | 2,271 | -5,870 | 29,776 | -1 |
| 2025-07-31T21 | 30,003 | 2,271 | -5,087 | 27,732 | +2,271 |
| 2025-07-31T22 | 30,783 | 2,273 | -3,415 | 30,783 | 0 |
| 2025-07-31T23 | 31,642 | 2,274 | -2,057 | 31,641 | +1 |

**Provenance distinction:** Fuel values and category counts above are directly verified against run `41960929998` job logs. Region NG values are from the earlier documented regional audit; the current run did not independently retrieve region-data. Therefore this is a historical cross-source comparison, **not** a verified same-run cross-endpoint snapshot.

**Interpretation:** The anomalous +2,271 MWh equals that hour's `NUC` value numerically; this does not establish the mechanism or authorize dropping nuclear from any source. `OTH` is signed and must not be clipped to zero. Fuel observations are not generation availability or validated dispatch inputs.

**Next gate:** obtain and inspect a successful `r02a-live-cross-endpoint.yml` run, including the two archived raw responses and their SHA256 values. Keep `empirical_dispatch_approved=false`.
