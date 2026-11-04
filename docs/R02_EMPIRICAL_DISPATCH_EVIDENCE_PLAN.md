# R02 empirical hourly dispatch: evidence acquisition and acceptance plan

**Status: blocked; no observed-data dispatch claim.** This plan follows completed R01–R01d audits. It is a prospective protocol, not results.

## Source-to-model contracts

| Input | Current evidence | Required acceptance test | Failure action |
| --- | --- | --- | --- |
| CISO load | EIA-930 hourly 2024/2025 BA demand audited (8784/8760 rows) | unique, gap-free UTC timestamps; MW/MWh and interval convention; negative and outlier audit; checksum and source timestamp | fail closed |
| Generator identities/nameplate | EIA-860 CISO 2024/2025 audited; OP nameplate 85,634.2 / 92,530.0 MW | reconcile year, plant ID, generator ID, status and technology; separate 42 status changes from new identities | fail closed |
| Renewable availability | **Missing validated hourly profiles** | hourly plant/technology alignment; 0 ≤ availability ≤ 1; documented curtailment treatment; independent source | block R02 |
| Thermal availability | **Missing validated hourly profiles** | outages/deratings or explicit, sensitivity-tested proxy; fuel/technology matching | block R02 |
| Thermal costs | **Missing validated defensible costs** | fuel, heat-rate, variable O&M, emissions treatment, source dates, units and sensitivity | block R02 |
| Storage energy and operation | **Missing complete energy-capacity and operational parameters** | MW vs MWh, duration, charge/discharge efficiencies, state of charge, boundary SOC, cyclic assumption | block R02 |
| CISO interchange and boundary | **Missing validated hourly treatment** | net imports/exports sign, balancing authority coverage, external generation, loss conventions; avoid double counting | block R02 |
| Solver and validation | synthetic 24h solver smoke only | model-year 8784/8760 snapshots, energy balance, infeasibility accounting, benchmark and independent holdout | block empirical claims |

## Ordered implementation

1. **R02a — observed load integrity**: machine-readable hourly quality report for both years, duplicate/gap detection, time convention and source manifest. This validates load only, not dispatch.
2. **R02b — interchange boundary**: reconcile CISO BA interchange with observed demand and document imports/exports; do not treat annual EIA-860 CISO nameplate as total system supply.
3. **R02c — technology-specific availability**: create source-backed profiles for solar, wind, hydro and thermal units, with a separate scenario path when only proxies are available.
4. **R02d — storage and operating costs**: distinguish battery MW and MWh; test SOC closure, efficiencies and cost sensitivity.
5. **R02e — model acceptance**: run a constrained model-year PyPSA solve, trace source→artifact→run→figure, compare independent observed metrics, report failures and sensitivity.

## Interpretation safeguards

- Annual EIA-860 OP status is not hourly availability.
- The 2024–2025 OP net delta +6,895.8 MW includes +862.4 MW from 42 matched-identity status changes; none of these 42 changed reported operating month/year. Do not infer new construction.
- The three pumped-storage OA→OP records (plant 6100, IDs 1–3) retain June 1984 as reported operating date. The +1,053 MW is an OP status-accounting contribution.
- Source-code labels OA, OP, OS, SB require official-codebook verification before attaching operational meaning.
- **Never represent a synthetic/proxy scenario as observed dispatch.** Do not publish manuscript drafts to this repository.
