# Project A — manuscript claim-to-evidence audit and submission decision

**Date:** 2026-11-10. **Scope:** existing verified outputs; no new model run. This is an internal research quality-control document, not a claim of submission readiness.

| Manuscript claim | Primary evidence | Permitted wording | Prohibited inference |
|---|---|---|---|
| 2024/2025 CISO hourly demand coverage (8784/8760) | `PYPSA_LOAD_ONLY_BASELINE.md` and audited EIA-930 normalization | complete normalized timestamp grids | anomaly-free measured load |
| OP capacity +6895.8 MW | EIA-860 identity-matched transition artifact; `CISO_2024_2025_FLEET_ACCOUNTING_BRIDGE.md` | net change in reported OP nameplate inventory | 6895.8 MW newly commissioned |
| Batteries +3862.2 MW, PV +1849.4 MW | `EIA860_CISO_TECHNOLOGY_DECOMPOSITION_2024_2025.md` | 82.83% of net OP inventory increase | 82.83% of electricity generation |
| 128/29 entrant cohort records | `EIA860_CISO_OPERATING_YEAR_COHORTS_2024_2025.md`, unit-level JSON | reported operating year, 6201.2/138.1 MW OP | confirmed commissioning or project counts |
| Historical entrants plant classification 4/16 | `EIA860_PRE2025_ENTRANTS_PLANT_BA_CROSSWALK.md` and original Plant sheets | already-CISO plants vs absent from earlier Plant worksheet | proven BA reassignment for absent plants |
| Pumped storage +1053 MW | `EIA860_CISO_STATUS_TRANSITIONS_2024_2025.md` and Plant crosswalk | three 1984 units OA→OP at same CISO plant | newly built pumped hydro |
| 2025 EIA-860 final annual release | `EIA860_2025_FINAL_RELEASE_VERIFICATION.md` | final annual EIA-860 source, archive hashes recorded | no later revisions possible |
| EIA-930 T21 +2271 MWh inconsistency | `R02A_SAME_RUN_RAW_EVIDENCE_2026-11-10.md` and private raw evidence | targeted source discrepancy | proven omitted nuclear or year-wide prevalence |
| PyPSA 24-hour synthetic smoke test | repo README / test artifacts | solver path works with synthetic generator | validated CISO dispatch |

## Cross-table arithmetic acceptance

- 2025 − 2024 OP MW: 92,530.0 − 85,634.2 = **6,895.8**.
- Change-class bridge: 6,339.3 − 379.9 + 862.4 + 74.0 = **6,895.8**.
- Battery + solar: 3,862.2 + 1,849.4 = **5,711.6 MW**, or **82.83%** of net OP change.
- Entrants: 128 + 29 = **157**; 6,201.2 + 138.1 = **6,339.3 MW OP**.
- Historical entrants: 6 + 23 = **29** records; 103.6 + 34.5 = **138.1 MW OP**.
- Pumped storage: 3 × 351 = **1,053 MW**; 1984 operating dates, annual BA=CISO both years.

## Figure audit

**Figure 1:** technology-specific net OP MW changes. Retain negative values, include 2024–2025, CISO, EIA-860 annual, OP nameplate and source in caption. State that 82.83% denominator is **net change**, not 2025 total capacity.

**Figure 2:** two reported operating-year cohorts for newly present generator records: 128 vs 29 records and 6201.2 vs 138.1 MW OP. If plotted on separate axes/panels, label each unit and avoid implying all records are OP. Do not claim BA membership is displayed unless included.

**Supplement (optional):** R02a T19–T23 targeted discrepancy, signed fuel sum vs regional net generation; no causal label and no extrapolation.

## Manuscript scope decision

**Defensible near-term paper:** a narrowly framed **data provenance and fleet-accounting validation case study** for 2024–2025 CISO. It can report observed demand coverage, generator-inventory transition decomposition and a targeted source-consistency counterexample.

**Not yet defensible:** a paper whose principal result is **multi-year empirical PyPSA dispatch, reliability, energy transition impacts, emissions or economic optimization**. A solver smoke test does not close those gates.

**Pre-submission essentials:** (1) full Methods, Abstract, Introduction, and Conclusions integrated into one manuscript; (2) source and license statements and reproducible figure generation; (3) verified scholarly literature and journal fit; (4) explicit study limitation that EIA-860 OP nameplate is not hourly available power; (5) independent check of figures and captions against archived data.

**Decision:** keep empirical dispatch fail-closed. Freeze the current two-figure, two-table inventory-validation story rather than proliferating exploratory appendices.
