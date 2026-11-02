# Dataset and model validation protocol (pre-registration draft)

## Phase 1: data intake

For every source record provider, download URL, license, retrieval date, SHA256, original unit, year, region definition, timezone, timestamp convention, missing intervals and revision history. Never silently substitute synthetic or annual demand for measured hourly electricity load.

## Phase 2: deterministic data gates

- Complete calendar-year hourly coverage: 8760 or 8784 unique UTC hourly timestamps, with documented daylight-saving handling.
- Nonnegative finite load MW; separately flag zero, missing and anomalous values.
- Hourly MW × 1 hour = MWh; annual totals reconciled against provider reports within predeclared tolerances.
- Region codes, technology mappings, and capacity nameplates have auditable sources.
- All scenario inputs must carry provenance, observation/synthetic flag, source year and units.

## Phase 3: model verification

Reproducible solver version, deterministic configuration, feasibility, nodal power balance, storage state equations (if used), objective decomposition and capacity constraints. Document whether topology is a copperplate approximation or a network model.

## Phase 4: validation

Train/calibrate on specified years, evaluate independent held-out years, report MAE/RMSE/bias and uncertainty intervals where observations support them. Avoid claiming real reliability performance from synthetic shortage generators.

## Phase 5: manuscript evidence

Every figure must be traceable to immutable input manifests, run configurations and outputs; results tables must cite validated run IDs and distinguish observed from simulated quantities.

## Initial decisions pending

Geographic scope, available hourly datasets, years, license terms, technology resolution, calibration targets, and journal scope.
