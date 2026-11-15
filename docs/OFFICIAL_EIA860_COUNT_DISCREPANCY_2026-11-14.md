# Project A: unresolved EIA-860 OP count discrepancy

**Evidence source:** [GitHub Actions run 43660115660](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/43660115660), `official-eia860-archive-integrity` job, step `Independently reconcile original-workbook OP inventory`. Run SHA `45f659d97927586e21d8d033f5c38d5d52a3ef1b`.

The run verified the pinned official ZIP hashes, inspected workbook schemas, and extracted 2024/2025 CISO staging CSVs. The original workbook extraction reported 3,563/3,691 CISO generator records (all statuses) in 2024/2025, respectively.

| Metric | 2024 | 2025 |
|---|---:|---:|
| Official-extract rows with status exactly OP | 2,421 | 2,552 |
| Archived pinned 'OP count' benchmark | 2,645 | 2,786 |
| Difference (official minus archived) | -224 | -234 |
| Official-extract OP nameplate MW | 85,634.2 | 92,530.0 |
| Archived OP nameplate MW | 85,634.2 | 92,530.0 |
| OP nameplate discrepancy MW | 0.0 | 0.0 |
| Official-extract OP records with 0.0 MW | 0 | 0 |

**Verified:** OP nameplate totals and net OP capacity change (+6,895.8 MW) agree exactly to one decimal place. Both official OP generator counts **do not** agree with the archived benchmark. All extracted OP records are from the `Operable` sheet. **The observed count discrepancy cannot be explained by zero-MW OP rows** in the official staging extracts.

**Not yet established:** whether archived counts refer to a different population/denominator, reflect an alternative reporting snapshot, or contain a data-generation defect. Capacity equality does not prove generator-level membership equality. Do not change pinned counts, reclassify statuses, or claim official count reconciliation until a row-key audit resolves these differences.

## Next forensic checks

1. Recover the archived generator-level input and its definition of `OP count` for both years.
2. Compare unique `(plant_id_eia, generator_id)` identity sets, statuses, and nameplate values between archived and original-workbook staging data.
3. Report exact keys responsible for the 224/234 count differences; classify causes based on evidence only.
4. Re-run the four-way capacity bridge, Helms check, and 29-entrant checks once the count denominator is reconciled.
5. Keep `fleet_validated`, `ba_mapping_validated`, and `empirical_dispatch_approved` false pending independent evidence.

**Evidence tier:** GitHub CI logs from actual official input, *partial validation only*. Not a successful official-data acceptance receipt.
