# R02 | Wind resource–generation validation: 2025 evidence memo

**Status:** observed-generation descriptive analysis; **not** an empirical dispatch validation or an hourly availability model. This document is internal to the private research repository.

## Research question

Can publicly available NASA POWER 10-m wind speed describe seasonal changes in EIA-923 net generation at three commissioning-screened California wind plants? Do not conflate association with prediction, power-curve calibration, equipment performance, or causality.

## Data and audit trail

- NASA POWER hourly WS10M, UTC, 2025: 8,760 hourly values at each of plant IDs 57484, 57514, and 7526. Site coordinates derive from the EIA-860 spatial pilot.
- EIA-923 2025 official Page 1 plant/fuel monthly **net generation**, 12 monthly values per plant.
- EIA-860 2025 nameplate MW for July capacity-factor denominators. This is a plant-level capacity benchmark, not a validated hourly operating capacity.
- Source, extraction, year coverage and sample restrictions are implemented in `annual_wind_weather_generation.py`, `annual_wind_monthly_alignment.py`, `annual_wind_first_difference.py`, and their workflow tests.
- Excluded solar site 64210 was commissioned after the July 2025 pilot; it is not used for operating July validation.

## Verified findings

| Plant ID | July net generation (MWh) | July net CF | WS10M vs daily-normalized monthly generation, Pearson r (12 months) | Mean WS10M first-difference r (11 month-pairs) | Mean WS10M-cubed first-difference r |
|---|---:|---:|---:|---:|---:|
| 57484 | 57,419 | 0.408339 | 0.329758 | 0.584368 | 0.454332 |
| 57514 | 45,732 | 0.231604 | 0.899374 | 0.786494 | 0.830810 |
| 7526 | 130,033 | 0.581616 | 0.980682 | 0.891408 | 0.797127 |

July mean WS10M: 57484 = 2.739368 m/s, 57514 = 5.685000 m/s, 7526 = 5.627715 m/s. The 57514–7526 absolute difference is 0.057285 m/s while July net CF differs by 35.0012 percentage points. Two of the three July plant pairs have opposite WS10M and CF rankings.

Solano Wind (7526) has a July/mean-month net generation ratio of 2.027463 and summer/winter generation ratio of 4.606350; the latter is 1.971269 times the maximum among the two wind peers. Its June–August monthly mean WS10M values are 5.630097, 5.627715, and 5.203427 m/s, consistent with a summer wind-resource peak. This is an association, not an attribution.

## Interpretation and limits

1. Site-level heterogeneity is substantial: a single generic NASA POWER 10-m wind-speed-to-generation rule is **not validated** by this pilot.
2. Positive first-difference correlations at 57514 and 7526 indicate that associations survive a simple month-to-month change diagnostic; they do not remove all seasonal confounding.
3. Monthly net generation reflects operations, curtailment, outages, and wind resource. It is not turbine availability, hourly capacity factor, or renewable dispatch potential.
4. NASA POWER grid-point WS10M is not hub-height wind. Wind shear, local terrain, turbine power curves, turbine vintages, wake losses, and plant-specific operational conditions are not resolved.
5. Twelve monthly observations and eleven first differences per site are insufficient for strong inference or validated out-of-sample forecasting; no p-values or causal claims are presented.
6. EIA-923 Page 1 is aggregated at plant/fuel level; do not attribute generation to individual EIA-860 generator records without separate evidence.

## Publication-oriented next experiment

Pre-specify an independent-year 2024 replication at the same three wind plants: verify EIA-860 operating chronology and nameplate validity in 2024, retrieve official EIA-923 2024 monthly plant/fuel net generation and NASA POWER 2024 WS10M, then recompute the same level/difference correlations. Compare year-to-year stability **without fitting or calibrating on the evaluation year**. Record any plant ownership, generator composition, or capacity changes. A successful replication would strengthen a descriptive weather-resource finding but would still not authorize PyPSA hourly dispatch.

**Current release gate:** `hourly_availability_approved = false`; `empirical_dispatch_approved = false`.
