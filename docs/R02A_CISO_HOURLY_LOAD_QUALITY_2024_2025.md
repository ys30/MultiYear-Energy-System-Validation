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

## Automated isolated-hour screening (verified)

Successful full-year run [41868714187](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41868714187) and test run [41868750287](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41868750287) confirm:

- **2024: 0** hours flagged by the current isolated-hour screening rule.
- **2025: 1** hour flagged, **2025-07-31T20:00:00+00:00**, observed **11,819 MW**, preceding **29,881 MW**, following **29,886 MW**, neighbor mean **29,883.5 MW**, deviation **−18,064.5 MW (−60.45%)**.
- Screening rule: deviation from neighbor mean >=5,000 MW and >=25%, and neighbor disagreement <=max(1,000 MW, 5% of neighbor mean). This is a heuristic, **not a validated statistical error classifier**. Other outliers may exist.
- The original observation is preserved unchanged in the normalized data and annual totals. No imputation, removal, or empirical dispatch simulation is authorized by this flag.

**Remaining:** inspect raw provider record and revision history, corroborate against independent CAISO series, and quantify transparent sensitivity (annual energy and peak ramp) under an explicitly hypothetical interpolation. R02 empirical dispatch gate remains closed.

## Verified counterfactual sensitivity (CI run 41872654672)

The real-data full-year workflow completed successfully at [41872654672](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41872654672); unit tests passed at [41872676571](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41872676571).

| Year | Flagged hours | Observed annual MWh | Hypothetical annual MWh | Difference MWh | Observed maximum hourly ramp MW | Hypothetical maximum hourly ramp MW |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2024 | 0 | 224,030,258 | 224,030,258 | 0 | 4,136 | 4,136 |
| 2025 | 1 | 224,023,764 | 224,041,828.5 | +18,064.5 (+0.00806%) | 18,067 | 4,815 |

**Interpretation:** A single isolated observed hour dominates the 2025 maximum absolute hourly ramp. Replacing it *only for diagnostic sensitivity* changes the ramp maximum by −13,252 MW (−73.35%) while leaving annual energy nearly unchanged. The scenario is **not a verified EIA revision or a recommended correction**. Raw observations remain intact, and any operational flexibility inference must explicitly disclose the anomalous hour and show both scenarios. Independent raw-record provenance and CAISO corroboration are outstanding. R02 empirical dispatch readiness remains blocked.

## EIA API raw-row provenance (verified in CI 41874265410)

The full-year EIA candidate workflow [41874265410](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41874265410) succeeded. For the isolated hour **2025-07-31T20:00:00+00:00** (normalized hour start), the original downloaded EIA-930 CISO demand response has exactly **one** matching row with raw hour-ending period **2025-07-31T21**, raw value **\"11819\"**, and raw units **megawatthours**. The normalized value is **11,819 MW**, exactly matching the original one-hour MWh reading. The independent raw-row check is archived in the workflow artifact `r02a_raw_source_audit.json`.

This verifies the value was not introduced by the project's numeric normalization and the hour-ending-to-hour-start mapping is consistent with the stated contract. **It does not verify EIA's upstream measurement, revision history, or independent CAISO corroboration.** The code explicitly sets `source_is_independently_verified=false`.

No source rows were audited for 2024 because the isolated-hour screening rule flagged no hours. R02 remains blocked for empirical dispatch.

## Independent CAISO telemetry cross-check (verified CI 41875210484)

The official CAISO Today's Outlook historical 5-minute demand CSV for **2025-07-31** was fetched in the independent workflow [41875210484](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41875210484). For the **13:00–14:00 PDT** hour corresponding to EIA's **2025-07-31 20:00–21:00 UTC**, all twelve five-minute observations are present.

| PDT hour | CAISO 5-minute mean MW | Min MW | Max MW | Samples |
| --- | ---: | ---: | ---: | ---: |
| 12:00–13:00 | 24,143.75 | 23,580 | 24,690 | 12 |
| **13:00–14:00** | **25,604.1667** | **24,852** | **26,399** | **12** |
| 14:00–15:00 | 27,590.9167 | 26,511 | 28,660 | 12 |

The independent CAISO telemetry rises smoothly across these three hours, showing **no matching one-hour collapse** to the EIA-930 11,819 MW reading. The CAISO target-hour mean is **13,785.1667 MW higher** than the EIA observation, but the two series can have different measurement scope and definitions; this numerical difference is **not** itself an error estimate. The raw EIA API row was confirmed to contain 11,819 MWh, so the discrepancy is upstream of this project's normalization.

**Evidence classification:** externally corroborated *shape inconsistency*, not a confirmed EIA upstream error or corrected value. Preserve the original EIA row; keep the neighbor-interpolation sensitivity explicitly hypothetical. Check CAISO telemetry's geographic scope, EIA-930 demand definition and published revision history before any authoritative correction or model decision.

## Published source definitions and revision limitations (2026-11-04 review)

**EIA-930:** EIA defines balancing-authority demand as **metered net generation minus total net interchange**. Its public methodology explicitly cautions that pseudo-ties and dynamic scheduling can affect reported demand; EIA says hourly individual-BA observations are published as received, while some daily/regional aggregates receive anomaly handling. EIA also says BA submissions can be revised and historical anomalies corrected. Source: https://www.eia.gov/electricity/930-content/about.html

**CAISO Today's Outlook:** The demand trend is a **5-minute average**, and the page says it **excludes dispatchable pump loads and battery charging**. CAISO labels Today's Outlook informational, subject to change, and points to OASIS for official data. Source: https://www.caiso.com/todays-outlook

**Interpretation:** The 2025-07-31 13:00–14:00 PDT EIA one-hour trough is not supported by the independent CAISO telemetry shape. However, these published definitions prevent treating the 13,785.17 MW pointwise gap as a direct measurement error or using CAISO telemetry as an authoritative substitute. The raw EIA candidate was obtained from a live API, not a versioned 2025 historical snapshot; this single retrieval cannot establish whether EIA ever revised that hour.

**Evidence gates before correction:** (1) obtain a dated/versioned EIA historical record or explicit provider confirmation; (2) check CAISO OASIS demand and scope for the same UTC hour; (3) examine EIA CISO net generation and total interchange for the energy-balance identity and any companion anomaly; (4) preserve original data, exact retrieval timestamp, and separately named sensitivity scenario. R02 empirical dispatch remains blocked independently of this issue.

## EIA component-level anomaly corroboration (CI 41879038944)

Live EIA API response for CISO hourly `D`, `NG`, and `TI` succeeded: [CI 41879038944](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41879038944). The raw hour-ending label `2025-07-31T21` has D=11,819 MWh, NG=27,732 MWh, and TI=-315 MWh. Adjacent labels are `T20`: D=29,881, NG=29,776, TI=-1,059; `T22`: D=29,886, NG=30,783, TI=-413.

For a *diagnostic*, calculate `D - NG + TI` under the candidate relationship `D = NG - TI`. The residual is **-16,228 MWh** at T21 versus **-954 MWh** at T20 and **-1,310 MWh** at T22. These are *not* corrected values and should not be interpreted as proof of a valid balance identity: verify EIA's sign convention, data coverage, revisions, and any adjustment terms. The change in demand at T20→T21 (-18,062 MWh) is much larger than net generation (-2,044 MWh) or interchange (+744 MWh). This strengthens the evidence for an internally inconsistent source observation.

The CI now emits both candidate-sign residuals to prevent a sign convention from being silently assumed. Original demand remains untouched; model approval remains blocked.

## Executed two-sign energy-balance diagnostic (CI 41887202196)

The live EIA component workflow successfully executed the diagnostic module and emitted both candidate-sign residuals: [run 41887202196](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41887202196).

| Raw EIA hour label | D - NG + TI (MWh) | D - NG - TI (MWh) |
| --- | ---: | ---: |
| 2025-07-31T19 | -403 | 1,641 |
| 2025-07-31T20 | -954 | 1,164 |
| **2025-07-31T21** | **-16,228** | **-15,598** |
| 2025-07-31T22 | -1,310 | -484 |
| 2025-07-31T23 | -1,999 | 165 |

The anomaly is robust to these two *candidate* interchange sign conventions. Neither residual is certified as a complete balancing-authority accounting identity, and this test alone cannot isolate the cause to a particular EIA component. The independent CAISO telemetry does not exhibit the same collapse. Preserve raw EIA observations and flag the affected hour for source-quality sensitivity analysis; do not silently replace it.

**Next evidence gate:** check whether EIA's current API value is unchanged in an independently dated snapshot or official historical revision; obtain a documented complete accounting relationship and assess whether an additional balancing term can explain the outlier. Do not conflate the source anomaly with R02 dispatch-model readiness.
