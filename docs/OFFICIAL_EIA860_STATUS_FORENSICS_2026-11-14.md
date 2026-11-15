# Project A — Official EIA-860 status-transition forensics

Evidence: GitHub Actions [run 43665855260](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/43665855260), original EIA-860 2024/2025 CISO extracts, `Diagnose old-to-new status classes in official bridge`. These are observed **reporting-status transitions**, not necessarily physical construction, commissioning, retirement, or dispatch.

| 2024 status | 2025 status | Nonzero-delta generators | OP capacity delta (MW) |
|---|---|---:|---:|
| absent | OP | 38 | +214.7 |
| OP | absent | 2 | -31.0 |
| OP | OP (nameplate revision) | 21 | +74.0 |
| OA | OP | 12 | +1322.2 |
| OP | OA | 13 | -463.4 |
| OP | OS | 2 | -2.5 |
| OP | RE | 9 | -348.9 |
| OP | SB | 5 | -6.0 |
| OS | OP | 3 | +12.1 |
| P | OP | 3 | +1011.2 |
| T | OP | 2 | +1.6 |
| TS | OP | 23 | +354.8 |
| U | OP | 27 | +1448.4 |
| V | OP | 54 | +3308.6 |

The 214 nonzero-delta generator rows reproduce **+6895.8 MW** net OP capacity change. Original-workbook bridge: +214.7 new-to-inventory, -31.0 missing, +6638.1 status transitions, +74.0 revisions. Archived benchmark: +6339.3, -379.9, +862.4, +74.0. **The component definitions are not reconciled**, even though the net change matches.

The V→OP and U→OP groups jointly contribute +4757.0 MW, while OA→OP contributes +1322.2 MW (including Helms units 6100/1, 6100/2, 6100/3 at +351 MW each). The 29 archived entrants' identity/status/OP capacity check passed (138.1 MW), but operating year is not independently verified.

**Research interpretation gate:** No claim that +6339.3 MW is newly constructed capacity. No claim that +6638.1 MW is new physical commissioning. EIA status transitions, first appearance in a reporting extract, and operating-year evidence must remain distinct. Current `fleet_validated=false`, `ba_mapping_validated=false`, `empirical_dispatch_approved=false`.

**Next forensic requirement:** Compare generator keys and status encoding between the archived transition artifact and the two official extracted inventories, using a joined row-level table with old/new statuses, capacities, reporting sheets, and provenance. Identify exactly why archived OP counts exceed original-workbook OP counts by 224 (2024) and 234 (2025), and why bridge categories differ. Do not alter archived benchmarks merely to pass CI.
