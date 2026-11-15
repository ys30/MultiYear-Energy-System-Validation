# Project A — CISO 2024–2025 fleet change: accounting bridge and interpretation (2026-11-10)

**Scope:** Annual EIA-860 CISO plant-BA operable (OP) generator inventory. This is a synthesis of previously verified CI outputs, **not a new experiment** and not empirical PyPSA dispatch.

## Capacity bridge (MW)

| Mutually exclusive first-match generator-record class | OP nameplate change (MW) |
|---|---:|
| New to 2025 CISO inventory | +6,339.3 |
| Missing from 2025 CISO inventory | −379.9 |
| Present in both years; status changed | +862.4 |
| Present in both years; nameplate changed | +74.0 |
| Present in both years; technology changed | 0.0 |
| **Net OP change** | **+6,895.8** |

**Arithmetic check:** 6,339.3 − 379.9 + 862.4 + 74.0 + 0.0 = 6,895.8 MW. Starting 2024 OP capacity 85,634.2 MW; ending 2025 OP capacity 92,530.0 MW; difference 6,895.8 MW (about **8.05%** of the 2024 OP nameplate). This bridge is based on **first-match mutually exclusive categories**; it must not be interpreted as physical capacity construction/retirement.

## Technology decomposition and denominator discipline

| Technology | Net OP change (MW) | Share of overall net OP change |
|---|---:|---:|
| Batteries | +3,862.2 | 56.01% |
| Solar photovoltaic | +1,849.4 | 26.82% |
| Pumped hydro storage | +1,053.0 | 15.27% |
| Other technologies combined | +131.2 | 1.90% |
| **Total** | **+6,895.8** | **100%** |

Batteries plus solar contributed **+5,711.6 MW**, approximately **82.83%** of the *net inventory change*. These percentages do **not** describe energy generation, total installed capacity mix, reliability contribution, or firm capacity. Because positive and negative technology contributions offset, shares of a net difference can exceed 100% in other samples; do not interpret these as a conventional composition share.

## Newly present records by reported operating year

| Reported operating-year cohort | Records | OP nameplate (MW) |
|---|---:|---:|
| 2025 | 128 | 6,201.2 |
| Before 2025 | 29 | 138.1 |
| **Total new-to-inventory** | **157** | **6,339.3** |

**Record-count correction:** Direct inspection of the archived per-generator transitions (artifact 13295023796) confirms 128/29 records rather than the previously documented 129/28; the capacity split is unchanged.\n\nThe 2025 reported-operating-year cohort represents **97.82%** of the OP MW newly present in the annual CISO inventory. This supports prioritizing commissioning-date verification for the large cohort but **does not establish independent commissioning, ownership, or BA assignment**.

**Critical counterexample:** The +1,053.0 MW pumped-storage technology change was caused by three generator records transitioning **OA→OP** in the annual inventory. This is not evidence of 1,053 MW of newly built pumped storage. Similarly, new-to-inventory batteries (4,388.7 MW) exceed the net battery increase (+3,862.2 MW); gross new inventory and net change must not be conflated.

## Why the inventory bridge cannot be a PyPSA dispatch result

EIA-860 OP nameplate is an annual record, not hourly available generation. The source does not by itself establish renewable profiles, thermal availability, battery energy (MWh), storage efficiency, plant BA changes, imports/exports, operating costs, or an electrical operating boundary. The R02a EIA-930 cross-endpoint anomaly is an additional source-consistency warning, not a correction to the EIA-860 fleet. Therefore **empirical_dispatch_approved = false**.

## Manuscript-ready Results paragraph

> Reconciliation of annual EIA-860 CISO Operable-sheet generator inventories identified 2,645 accepted records across OP/OA/OS/SB statuses in 2024 and 2,786 in 2025 (strict OP counts: 2,421 and 2,552). Their reported OP nameplate capacity increased from 85,634.2 to 92,530.0 MW, a net gain of 6,895.8 MW (8.05%). A mutually exclusive record-level accounting bridge attributed +6,339.3 MW to units newly present in the CISO inventory, −379.9 MW to records no longer present, +862.4 MW to status transitions, and +74.0 MW to nameplate revisions. Batteries (+3,862.2 MW) and solar photovoltaic (+1,849.4 MW) together accounted for 82.83% of the net change. However, these are changes in annual reported inventory, not verified commissioning or operational availability: notably, the +1,053.0 MW pumped-storage increase arose from three OA-to-OP status transitions rather than documented new construction.

## Evidence and next falsification checks

- [Technology decomposition](EIA860_CISO_TECHNOLOGY_DECOMPOSITION_2024_2025.md) — CI run 41771789078.
- [Operating-year cohorts](EIA860_CISO_OPERATING_YEAR_COHORTS_2024_2025.md) — CI run 41772668659.
- [Status transitions](EIA860_CISO_STATUS_TRANSITIONS_2024_2025.md) — CI run 41772065717.
- **Priority 1:** verify the three pumped-storage records' original operating month/year, plant BA code and 2024/2025 status definitions.
- **Priority 2:** examine 29 historical-operating-year records newly present in 2025 for BA reassignment versus delayed reporting.
- **Priority 3:** retrieve battery energy capacity and storage duration, distinguish MW from MWh.
- **Priority 4:** independently establish hourly availability, interchange and boundary before any empirical optimization.

**Research status:** validated annual inventory accounting; causal interpretation and empirical dispatch still gated.


## Independent original-workbook acceptance (2026-11-14)

[GitHub Actions run 43669441900](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/43669441900) (commit `d30f20095072f506dc5b09539e4eec0917b92944`) passed all three jobs, including independent EIA-860 ZIP integrity, Operable-sheet all-status row counts, strict OP MW totals, the four mutually exclusive capacity components, Helms OA→OP evidence and 29 entrant identity/status/capacity checks. A machine-readable acceptance receipt was emitted. The old 224/234 count discrepancy was a **denominator-labeling error**, not missing OP capacity. The earlier bridge mismatch was caused by including Proposed/Retired worksheets in an independent identity join instead of restricting to Operable.

This acceptance does **not** independently establish the 29 entrants' operating years, PUDL matching, historical BA boundaries, hourly availability, or empirical dispatch. Keep `fleet_validated=false`, `ba_mapping_validated=false`, `empirical_dispatch_approved=false` until their separate evidence gates pass.
