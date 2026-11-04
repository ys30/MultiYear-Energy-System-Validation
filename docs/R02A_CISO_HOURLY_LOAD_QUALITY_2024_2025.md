# R02a — EIA-930 CISO observed hourly load quality, 2024–2025

**Evidence:** [successful full-year EIA candidate workflow 41780386655](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41780386655), commit `8f4e5c63`; all five year-matrix jobs succeeded. 2024 and 2025 job logs print `R02A_HOURLY_LOAD_QUALITY` and archive `r02a_hourly_load_quality.json` as a workflow artifact.

| Metric | 2024 | 2025 |
| --- | ---: | ---: |
| Hourly UTC observations | 8,784 | 8,760 |
| Annual load energy (MWh) | 224,030,258 | 224,023,764 |
| Mean (MW) | 25,504.3554 | 25,573.4890 |
| Median (MW) | 24,524 | 24,889 |
| Minimum (MW) | 14,794 | 11,819 |
| Minimum UTC hour | 2024-05-05 23:00 | 2025-07-31 20:00 |
| Maximum (MW) | 47,571 | 43,860 |
| Maximum UTC hour | 2024-09-06 01:00 | 2025-08-22 02:00 |
| P01 (MW) | 18,106.77 | 18,987.00 |
| P99 (MW) | 40,959.00 | 38,013.51 |
| Largest absolute adjacent-hour change (MW) | 4,136 | **18,067** |
| Minimum daily energy (MWh) | 458,587 | 468,240 |
| Maximum daily energy (MWh) | 905,965 | 851,522 |
| Zero-load hours | 0 | 0 |
| Complete hourly UTC grid | yes | yes |

## Interpretation and hold

**R02a structural validation succeeded:** complete UTC hourly grid, finite nonnegative load and consistent annual totals. **R02a anomaly investigation remains open:** 2025 maximum adjacent-hour change is 18,067 MW (4.37× 2024 maximum). This is a screening flag, not proof of an erroneous measurement or a physical grid event.

Before accepting 2025 for empirical PyPSA dispatch:
1. Locate the two UTC timestamps and original EIA API records defining the maximum ramp, including raw period, value, type, respondent, units and source manifest.
2. Check nearby hours for abrupt discontinuity, revisions, duplication or interval-boundary issues.
3. Cross-check the affected date against an independent CISO/EIA published demand series if available.
4. Document whether to retain, flag or sensitivity-test the observation. Do not silently impute or remove it.

**Empirical dispatch remains blocked** pending R02b–R02e availability, storage, cost and interchange evidence. This note reports input-data quality only; it is not a calibrated simulation or model validation.

## R02a anomaly localization — successful rerun 41864319914

The 2025 largest absolute adjacent-hour ramp is a **single-hour trough** at **2025-07-31 20:00 UTC**, not a sustained 18 GW demand transition. Observed EIA-930 normalized CISO load (MW):

| UTC hour | Demand (MW) |
| --- | ---: |
| 2025-07-31 17:00 | 30,767 |
| 18:00 | 30,296 |
| 19:00 | 29,881 |
| **20:00** | **11,819** |
| 21:00 | 29,886 |
| 22:00 | 30,724 |
| 23:00 | 31,862 |
| 2025-08-01 00:00 | 33,033 |

The drop from 19:00 to 20:00 was **−18,062 MW**; rebound from 20:00 to 21:00 was **+18,067 MW**. The two neighboring values differ by just **5 MW**. Their mean is **29,883.5 MW**, versus observed 11,819 MW (difference **−18,064.5 MW**). This strongly suggests a single-hour outlier requiring raw-record verification; it does **not** establish its cause or authorize replacement.

The comparable 2024 maximum ramp was **+4,136 MW** from 2024-09-09 15:00 UTC (31,870 MW) to 16:00 UTC (36,006 MW), amid an increasing multi-hour trajectory. Both 2024 and 2025 full-year jobs and research contract tests succeeded at [run 41864319914](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41864319914) and [run 41864320019](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41864320019).

**Next checks:** inspect the original EIA API response for period 2025-07-31T21 (hour-ending label), validate the raw 11,819 MWh value and any later EIA revisions, and compare against a separate CAISO demand publication. Preserve original observations and provenance. A sensitivity experiment can compare unchanged observed load to an explicitly labeled, *non-authoritative* neighbor-interpolated scenario; do not silently replace the input or claim a calibrated dispatch outcome.
