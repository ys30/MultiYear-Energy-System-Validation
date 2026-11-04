# CISO pumped-storage status reclassification: 2024–2025

**Verified:** [EIA-860 cross-year CI run 41774268179](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41774268179), commit `891ad0ec`, success.

## Unit-level source records

| Plant ID | Generator ID | 2024 status | 2025 status | 2024 reported operating date | 2025 reported operating date | OP nameplate delta |
| --- | --- | --- | --- | --- | --- | ---: |
| 6100 | 1 | OA | OP | June 1984 | June 1984 | +351 MW |
| 6100 | 2 | OA | OP | June 1984 | June 1984 | +351 MW |
| 6100 | 3 | OA | OP | June 1984 | June 1984 | +351 MW |
| **Total** | | | | | | **+1,053 MW** |

All three records retain the same reported operating month and year across the two annual EIA-860 snapshots. The OP-only accounting delta arises from the **OA → OP status transition**, not an operating-year change.

**Do not call this new construction or 2025 commissioning.** Verify the official EIA-860 status-code dictionary before assigning a physical operational interpretation to OA. The records show the reported historical operating date, not independently validated commercial operation. OP nameplate is not dispatchable hourly capacity.

## Accounting implication

The fleet's 2024–2025 **+6,895.8 MW OP nameplate change** includes **+1,053.0 MW** from these three pumped-storage status transitions. The counterfactual arithmetic excluding this particular transition is **+5,842.8 MW**. This is a diagnostic decomposition, **not** an alternative official EIA-860 total or a construction estimate.

## Follow-up

- Check official EIA-860 OA/OP code definitions and plant-level identity.
- Investigate other OA→OP and OP→OA movements.
- Keep the status-change adjustment separate from new-to-inventory operating-year cohorts.
- Empirical hourly dispatch readiness remains false.
