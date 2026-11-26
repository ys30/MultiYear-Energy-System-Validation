# E4 annual ERA5 acquisition milestone

Acquisition complete for January–December 2024 and 2025. This is an acquisition freeze, not final independent QA or resource-model admission.

Source: public ARCO ERA5 hourly 0.25-degree Zarr, as specified in paper_a1_e4_weather_probe.py. Variables: 100m U/V wind, 2m temperature, surface solar radiation downwards. Spatial weights pinned to run 45856946706; later-year operating renewable fleet coordinates, common across capacity scenarios within year.

| Year | Cells | Hours | Grid-hours | Scalar values |
|---|---:|---:|---:|---:|
| 2024 | 590 | 8784 | 5182560 | 20730240 |
| 2025 | 640 | 8760 | 5606400 | 22425600 |
| Total | | 17544 | 10788960 | 43155840 |

Pinned artifact runs:
- February pilot: 45872037214
- January, March, April: 45873772010
- May–July: 45877926960
- August–October: 45891450354
- November–December: 45895515819

Each monthly artifact contains raw_weather.csv and batch_manifest.json with SHA-256. Matrix artifact names use year and month, with pilot February zero-padded. Do not mix seasonal one-week artifacts into annual data. No re-fetch is needed while these artifacts remain available; long-term archival remains outstanding.

Independent QA through July: run 45891450299, 6272400 rows. Extended audit through October: run 45895515314 succeeded. Full audit with --require-full: run 45901610466 queued at time of writing. Do not mark full QA complete until manifest is checked for complete=true, empty missing_months and 10788960 rows.

No formal CF admitted. Small negative SSRD values preserved in raw source. Radiation interval semantics, wind temporal representation, turbine curve coverage and generation reporting scope remain to be checked. No universal time shift or fitted wind multiplier admitted. Annual LPs not executed.

Wind schema run 45896356314 confirmed predominant manufacturer/model, hub height in feet, turbine count and design wind speed in mph. Design wind speed is not rated wind speed. Rotor diameter and rated wind speed not present in inspected headers. Parameter coverage audit run 45900246129 queued. Predominant model is not necessarily every turbine in a generator record.

PR #2 remains unmerged.
