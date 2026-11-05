# R02 historical weather-resource acquisition decision (2024–2025)

**Primary candidate: ERA5 hourly single levels** (Copernicus Climate Data Store): https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels

ERA5 offers 2024–2025 hourly historical meteorology including 100-metre U/V wind components and surface solar radiation downwards. For radiation, accumulated J/m² must be aligned to the correct accumulation interval before conversion to average W/m²; never interpret raw accumulated energy as instantaneous irradiance. Wind speed at 100 m is sqrt(u100² + v100²), but wind power still needs turbine power curves, density, plant location/capacity and losses. Solar generation potential needs a PV performance model, irradiance decomposition/geometry as applicable, module orientation and losses. Regional CISO aggregation requires verified plant coordinates and capacity weights.

**Solar cross-validation candidate: NSRDB** https://developer.nlr.gov/docs/solar/nsrdb/ — includes historical satellite-derived GHI/DNI/DHI, with a documented 2025 GOES product. Availability and licensing/credential constraints must be checked at extraction time.

**Not suitable as a direct 2024–2025 weather series: original WIND Toolkit** https://catalog.data.gov/dataset/wind-integration-national-dataset-wind-toolkit — historical model years 2007–2014. It may inform methodology or long-run climatology but must not be labeled contemporaneous 2024/2025 observations.

The initial `weather_resource_gate.py` checks time basis, coordinates, units, hourly coverage, irradiance interval documentation and 100m wind components. This is a **schema/quality gate only**, not a retrieval or a physically calibrated renewable-potential model. No CDS credentials or 2024–2025 weather series have yet been obtained in the workflow. Avoid treating EIA-930 actual SUN/WND generation as potential.

Acquisition order: (1) select representative plant or capacity-weighted sites from independently validated capacity/location data; (2) request bounded ERA5 sample for two UTC days including solar/wind variables; (3) validate radiation time convention and hourly coverage; (4) extend to 2024–2025; (5) calculate and calibrate technology-specific potential against actual EIA observations with curtailment caveats; (6) only then revisit R02 dispatch gate.
