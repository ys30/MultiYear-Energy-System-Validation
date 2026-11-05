# R02 six-site weather evidence and empirical-dispatch boundary (2026-11-05)

## Verified execution

GitHub Actions [six-site July 2025 acquisition](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42129655022) and [six-site pairwise diagnostics](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42131365929) both completed successfully. The six EIA-860 CISO OP plant locations yielded 744 hourly NASA POWER observations per plant (4,464 site-hours). Files, checksums and manifests are stored as CI artifacts, with a 30-day retention period.

Selected solar plant IDs: 57695, 64210, 57373. Selected wind plant IDs: 7526, 57514, 57484. The pilot covers only 5.7493% of 2025 solar and 11.9327% of 2025 wind nameplate MW; it is **not regionally representative**.

## Matched-hour correlations (July 2025)

| Technology | Plant pair | Raw Pearson r | Hour-of-day anomaly Pearson r | Mean absolute hourly difference |
|---|---|---:|---:|---:|
| Solar GHI | 57695 / 64210 | 0.996199 | 0.490867 | 21.156976 W/m² |
| Solar GHI | 57695 / 57373 | 0.978774 | 0.168048 | 49.743159 W/m² |
| Solar GHI | 64210 / 57373 | 0.987664 | 0.175829 | 36.375645 W/m² |
| Wind 10 m speed | 7526 / 57514 | 0.038992 | 0.044112 | 1.843548 m/s |
| Wind 10 m speed | 7526 / 57484 | 0.513617 | 0.009477 | 2.906465 m/s |
| Wind 10 m speed | 57514 / 57484 | -0.023178 | 0.164569 | 3.263266 m/s |

Anomalies subtract each site's **own July UTC-hour-of-day mean**, not a physically computed clear-sky irradiance. Common solar geometry, satellite/reanalysis resolution, temporal autocorrelation, seasonal effects, and within-grid heterogeneity remain. Pairwise correlations are descriptive; no confidence intervals or regional inference are claimed.

The earlier solar-pair odd/even held-out day check yielded r=0.431303 (even days) and r=0.499938 (odd days) for all-hour anomalies, and r=0.424256 and r=0.491487 for daylight anomalies. This check does not remove synoptic autocorrelation.

## Sampling-design tradeoff (2025; 50 plants per technology)

| Technology | Capacity-first: MW coverage / occupied 1-degree cell coverage | Spatial-stratified: MW coverage / occupied cell coverage |
|---|---|---|
| Solar | 49.3722% / 40.0% | 32.7708% / 100% |
| Wind | 87.2184% / 66.6667% | 84.4807% / 100% |

These are **asset coverage** diagnostics, not weather representativeness tests. The six-site weather pilot has much lower coverage than either 50-site design.

## Scientific interpretation

The high raw solar GHI correlation (0.979–0.996) largely reflects a shared diurnal signal. Removing mean hour-of-day patterns yields substantially smaller correlations (0.168–0.491), so raw GHI correlation alone is unsafe for selecting spatially interchangeable weather sites. Three wind-site anomaly correlations (0.009–0.165) likewise indicate limited synchrony in this pilot. These observations **do not** establish CAISO-wide solar/wind output diversity or any economic-dispatch finding.

## Explicit boundary before PyPSA empirical R02

**BLOCKED**. NASA POWER `ALLSKY_SFC_SW_DWN` and `WS10M` are weather-resource inputs, not independently verified available generation. Do not map GHI linearly to solar p_max_pu or 10 m wind speed directly to turbine output and label the result empirical. The existing `renewable_availability_gate.py` enforces provenance and rejects observed EIA-930 SUN/WND generation as potential. Passing that schema gate alone does not validate a physical conversion.

To unblock empirical dispatch:
1. Validate plant-level PV irradiance-to-AC potential using appropriate geometry, panel assumptions, temperature, inverter clipping, plant vintage and independent benchmark(s); document uncertainty.
2. Validate wind speed extrapolation from 10 m to hub height, turbine power curves, cut-in/rated/cut-out, air density, losses and independent benchmarks. A 10 m wind series alone is insufficient.
3. Expand spatial/temporal sample, check source resolution and aggregation errors, and provide 2024–2025 full-hour potential for the modeled capacity.
4. Independently document thermal variable costs, storage energy/power/efficiency/SOC, and intertie/boundary assumptions before claiming an empirical dispatch result.

No new dispatch, generation, reliability or transition-impact estimates are claimed in this note. Keep manuscript drafts private; this document records reproducible engineering evidence only.
