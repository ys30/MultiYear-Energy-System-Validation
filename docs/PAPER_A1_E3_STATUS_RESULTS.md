# E3 precursor: national unmatched status decomposition

Verified CI: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/45478185009

Pinned PUDL v2026.11.0, 2023–2025, 4123 unmatched record-year comparisons, 25 grouped rows.

| operational_status | records | records with capacity | reported MW |
|---|---:|---:|---:|
| proposed | 2615 | 2615 | 266055.0 |
| existing | 1203 | 1203 | 15095.9 |
| retired | 287 | 287 | 9558.4 |
| Unknown | 18 | 0 | NA |
| Total | 4123 | 4105 | 290709.3 |

Proposed records contribute 91.52% of observed unmatched MW. Existing records contribute 5.19%. Excluding proposed and retired records reduces observed unmatched MW by 94.81%, but this is a scope sensitivity, not a measured error rate or a physical capacity change. Unknown capacity must not be interpreted as zero. Existing status is not equivalent to dispatch eligibility. No physical identity links are established by this decomposition.

E1 frozen; no changes to earlier results. Next: disaggregate existing status by operational_status_code and year/direction, reconcile to 1203 and 15095.9 MW, then evaluate explicit dispatch-eligibility scenarios. EIA-860M chronology remains outstanding.
