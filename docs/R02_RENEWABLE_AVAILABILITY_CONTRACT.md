# R02 renewable availability — empirical input contract

R02 PyPSA requires independently estimated hourly **available generation**, not EIA-930 actual SUN/WND generation. Actual output may reflect curtailment, economic dispatch, outages and grid constraints; it cannot be assumed to equal weather-driven potential.

Candidate data must specify: UTC period, technology (solar/wind), installed operational capacity MW, hourly available MW, original source and source variable, time convention, capacity basis/source and physical or empirical estimation method. An eligible per-unit availability factor is `p_max_pu = available_mw / capacity_mw` with finite nonnegative availability no greater than installed capacity. Each modeled hour must be represented for each required technology; duplicate records are rejected.

The gate `renewable_availability_gate.py` explicitly rejects observed-generation variables and missing provenance. Passing this *schema* gate alone is not a claim of empirical validity: spatial aggregation, vintage, weather inputs, outage assumptions, capacity changes, curtailment validation, and time alignment still require independent review.

Potential data paths for later investigation: hourly weather-based irradiance and wind-speed models joined to verified installed plant capacity and locations; or an explicitly documented independent renewable-availability dataset. EIA-930 SUN/WND can serve as an observational comparison only, not as the potential series.

Status: **NO independently verified 2024–2025 solar/wind potential dataset has been ingested yet. R02 empirical dispatch remains blocked.**
