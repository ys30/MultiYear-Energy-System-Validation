# CISO 2024–2025 generator identity transitions — verified CI result

**Provenance:** [GitHub Actions run 41771523133](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41771523133), job `compare` (126382077503), succeeded. The analysis uses official annual EIA-860 source archives, CISO plant BA code, and the `Operable` worksheet. It matches exact `plant_id + generator_id` pairs; full change-level JSON is retained as a private CI artifact.

## Results

| Mutually exclusive first-match classification | Count | OP nameplate change (MW) |
| --- | ---: | ---: |
| New to CISO inventory | 157 | +6,339.3 |
| Missing from CISO inventory | 16 | -379.9 |
| Status changed | 42 | +862.4 |
| Technology changed | 7 | 0.0 |
| Nameplate changed | 21 | +74.0 |
| Unchanged | 2,559 | 0.0 |
| **Total OP nameplate change** | | **+6,895.8** |

2024 accepted inventory: 2,645 records; 2025: 2,786 records. 2024 OP nameplate: 85,634.2 MW; 2025 OP nameplate: 92,530.0 MW. Net OP change = 6,895.8 MW, equal to the sum of classified contributions (capacity reconciliation passed).

**Classification precedence:** new/missing, then status, then technology, then capacity. A generator with both status and capacity changes is classified under status; thus the category contribution includes all associated OP MW changes, not just the isolated effect of the named attribute.

## Interpretation guardrails

- `new_to_ciso_inventory` does **not** necessarily mean newly commissioned; `missing_from_ciso_inventory` does **not** necessarily mean physically retired. Reconcile BA reassignment, reporting revisions, dates and source status before those claims.
- OP nameplate MW is not dispatchable hourly MW, annual MWh, dependable capacity or adequacy. Battery MW does not specify duration.
- Annual EIA-860 snapshots are not directly comparable to the EIA-930 hourly operating boundary without a documented BA/interchange reconciliation.
- This is a **verified input-data finding**, not an optimized PyPSA outcome. `empirical_dispatch_ready=false`.

## Next steps

1. Analyze the change-level JSON to separate battery/solar/thermal additions and status transitions, with both counts and capacity contributions.
2. Cross-check 2024/2025 plant BA assignments and generator operating dates; distinguish genuine commissioning from inventory membership.
3. Audit independent hourly renewable/thermal availability, storage duration and interchange before empirical optimization.
