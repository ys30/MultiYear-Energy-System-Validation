# R02 plant-to-weather spatial mapping: evidence requirements

The July 2025 NASA POWER three-site pilot succeeded with 744 UTC hours per site and zero missing GHI/wind values. Verified means: Central Valley GHI 347.537 W/m2, 10m wind 2.423 m/s; Southern California 345.322 W/m2, 2.635 m/s; Northern California 343.689 W/m2, 3.638 m/s. See [successful workflow 42106910056](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42106910056).

**Do not** assign equal weights to these three sites and call the result CAISO renewable potential. They are illustrative geographic points, not verified operational solar/wind generator locations or capacity weights.

Next: independently retrieve the relevant EIA-860 2024/2025 generator-level records, validate plant ID, generator ID, coordinates, technology, OP status, reporting year and MW capacity. Separately verify CAISO balancing authority membership; a plant in California is not automatically in CISO. The `plant_weather_mapping_gate.py` module enforces these input conditions and rejects unverified records. Once independently validated, derive weather-resource weights by technology and plant capacity, document sampling and interpolation uncertainty, and only then compute a physical renewable-availability model.

The 2025 July weather data are not the full 2024–2025 weather history. 10m wind is not 100m hub-height wind. No dispatch results are supported yet.
