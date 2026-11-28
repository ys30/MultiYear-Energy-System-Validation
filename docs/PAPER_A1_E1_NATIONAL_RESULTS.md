# Paper A1 — National E1 descriptive results (verified, 2026-11-22)

**Status:** Results from successful GitHub Actions run [45084692811](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/45084692811), commit `f207704`. Pinned source: PUDL `v2026.11.0`, `out_eia__yearly_generators.parquet`. This is a descriptive snapshot comparison, not a generator-identity adjudication or physical commissioning/retirement analysis.

## E1.1 — Annual exact-key census

| Year | Generator records | Distinct plants |
|---|---:|---:|
| 2023 | 33,446 | 15,067 |
| 2024 | 34,871 | 16,134 |
| 2025 | 36,585 | 17,350 |

Exact `(plant_id_eia, generator_id)` overlap: 33,216 in 2023–24 (230 earlier-only; 1,655 later-only); 34,609 in 2024–25 (262 earlier-only; 1,976 later-only). These are record-key comparisons, **not error rates**.

## E1.2 — Plant-context classification

| Pair | Side | Plant absent in other year | Plant present in other year | Total |
|---|---|---:|---:|---:|
| 2023–24 | Earlier only | 211 | 19 | 230 |
| 2023–24 | Later only | 1,455 | 200 | 1,655 |
| 2024–25 | Earlier only | 243 | 19 | 262 |
| 2024–25 | Later only | 1,799 | 177 | 1,976 |

The two plant-context labels describe record coverage; they do not establish physical generator lineage.

## E1.3 — Reported capacity on unmatched records

| Pair | Side | Plant absent (MW) | Plant present (MW) | Total (MW) |
|---|---|---:|---:|---:|
| 2023–24 | Earlier only | 10,106.6 | 715.8 | 10,822.4 |
| 2023–24 | Later only | 131,401.1 | 14,489.5 | 145,890.6 |
| 2024–25 | Earlier only | 13,088.1 | 1,695.5 | 14,783.6 |
| 2024–25 | Later only | 109,788.4 | 9,424.3 | 119,212.7 |

Reported nonnegative MW summed across records with available capacity. Capacity completeness differs by category; do not interpret totals as net installed capacity change, construction, retirement, or causal effects. Repeated annual comparisons may count the same physical asset more than once.

In the 2024–25 earlier-only category, within-plant differences account for 19/262 (7.3%) of records and 1,695.5/14,783.6 (11.5%) of reported MW. This descriptive disproportion is not consistent across every comparison direction.

Largest technologies by reported MW among later-only records:
- 2023–24: Solar Photovoltaic 67,748.0 MW (970 records); Batteries 42,951.5 MW (316 records).
- 2024–25: Solar Photovoltaic 42,841.7 MW (1,044 records); Batteries 26,645.6 MW (346 records).

These are **coverage differences in pinned PUDL snapshots**, not evidence that equivalent amounts were newly commissioned. They motivate stratified E2 adjudication and capacity-aware sensitivity analyses.

## Publication gates remaining

1. E2: compare PUDL entity-resolution outputs, conservative official-document identity evidence, and independently adjudicated samples. Do not label same-plant unmatched keys as identity errors.
2. E3: official annual/monthly vintage chronology and status inconsistencies, including Mesa Wind, with provenance.
3. E4: capacity/retirement/dispatch consequences only after defensible crosswalks and scenario definitions; report unresolved identities explicitly.
4. Validate missing-capacity handling, status composition, denominator choice, and source snapshot stability before final manuscript tables.

**Reproduction:** `.github/workflows/paper-a1-national-baseline.yml`; downloadable run artifact includes baseline, classification, MW-by-technology, and capacity summary outputs.
