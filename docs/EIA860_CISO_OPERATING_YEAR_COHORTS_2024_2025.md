# CISO EIA-860 2024–2025: reported operating-year cohorts of new inventory records

**Verified:** [CI run 41772668659](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41772668659), job 126385736695, commit 3a450382 (success). The unit-level JSON artifact is available in the workflow for 30 days.

## Reconciled new-to-CISO inventory

| Technology | 2025 reported operating year: units | 2025 reported operating year: OP MW | Pre-2025 reported operating year: units | Pre-2025 reported operating year: OP MW |
| --- | ---: | ---: | ---: | ---: |
| Batteries | 58 | 4,318.0 | 5 | 70.7 |
| Solar Photovoltaic | 57 | 1,826.8 | 14 | 33.2 |
| Other technologies | 14 | 56.4 | 9 | 34.2 |
| **Total** | **129** | **6,201.2** | **28** | **138.1** |

The cohorts reconcile to **157 records** and **6,339.3 MW** of OP capacity newly present in the CISO annual inventory. The 2025 reported operating-year cohort accounts for approximately **97.8%** of this OP capacity.

**Interpretation:** A reported operating year of 2025 is supporting evidence, not independent confirmation of commissioning or CISO BA assignment. These are generator records and nameplate MW, not projects, delivered energy, storage duration, or verified hourly capacity.

## Distinguish inventory additions from net growth

- New-to-inventory OP contribution: **+6,339.3 MW**.
- Missing-from-inventory OP contribution: **−379.9 MW**.
- OP status-change contribution: **+862.4 MW**.
- Nameplate revisions: **+74.0 MW**.
- Net CISO OP nameplate change: **+6,895.8 MW**.

The technology-specific net change in Batteries (**+3,862.2 MW**) and Solar Photovoltaic (**+1,849.4 MW**) must not be confused with the new-to-inventory gross contribution (**4,388.7 MW** and **1,860.0 MW**, respectively).

## Next validation gates

1. Verify the original year-specific EIA-860 operating month/year fields and status-code definitions.
2. Inspect the three pumped-storage OA→OP records (+1,053 MW), including original operating year and any revised BA mapping.
3. Validate historical-year units entering CISO against plant BA assignment and generator IDs.
4. Keep empirical hourly PyPSA dispatch gated on availability, interchange, costs and storage duration/efficiency data.

**Empirical dispatch ready:** false. This document is a verified inventory accounting result, not an operational adequacy claim.
