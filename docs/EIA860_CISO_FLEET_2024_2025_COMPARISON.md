# CISO EIA-860 fleet comparison: 2024 vs 2025

**Evidence class:** audited annual generator inventory, not dispatch or adequacy. Source: successful private [EIA-860 intake run 41743257455](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41743257455), jobs `inventory (2024)` (126289789873) and `inventory (2025)` (126289789475). Values are parsed from `EIA860_CISO_FLEET_AUDIT` and `COMBINED_OBSERVED_LOAD_ASSETS` log records; full raw manifests and source hashes reside in private workflow artifacts.

| Audit quantity | 2024 | 2025 | 2025 minus 2024 |
| --- | ---: | ---: | ---: |
| Accepted CISO operable-sheet rows (all statuses) | 2,645 | 2,786 | +141 |
| OP-status total nameplate MW | 85,634.2 | 92,530.0 | +6,895.8 |
| OP nonbattery candidate count | 2,202 | 2,275 | +73 |
| OP nonbattery nameplate MW | 73,977.1 | 77,010.7 | +3,033.6 |
| OP battery candidate count | 219 | 277 | +58 |
| OP battery nameplate MW | 11,657.1 | 15,519.3 | +3,862.2 |
| Unmatched plant rows | 2 | 1 | -1 |
| Observed annual demand MWh | 224,030,258 | 224,023,764 | -6,494 |
| Observed hourly snapshots | 8,784 | 8,760 | -24 |

Battery nameplate power increased **33.13%**; its 3,862.2 MW increase accounts for **56.01%** of the 6,895.8 MW increase in OP total nameplate. This is a comparison of two annual inventory snapshots, **not** a matched-generator additions/retirements decomposition. Battery MW is power, not stored energy (MWh) or firm deliverable capacity.

## Interpretation and next acceptance gates

- EIA-860 plant `Balancing Authority Code=CISO` is a screening boundary; verify plant assignments and interchange treatment against the EIA-930 CISO operating boundary before supply-demand claims.
- `OP` is a source status code; it does not guarantee 8,760/8,784-hour availability. Keep `OA`, `OS`, `SB` excluded from OP dispatch candidates unless a documented policy changes.
- Check raw generator ID matches across years to separate additions, retirements, status transitions, capacity edits, and BA reassignment; aggregate differences alone cannot identify causes.
- Audit battery charge/discharge ratings, energy duration, and operating dates independently. No implicit 4-hour assumption.
- Independently validate renewable hourly availability, thermal availability/costs, storage initial state/efficiency and imports/exports. Only then change the fail-closed dispatch readiness gate.
- Preserve the 2024 calibration / 2025 held-out split. Do not infer emissions, reliability, adequacy, or dispatch from this table.

**Run outcome:** both annual jobs succeeded and both combined load-asset manifests explicitly reported `optimized=false` and `empirical_dispatch_ready=false`.
