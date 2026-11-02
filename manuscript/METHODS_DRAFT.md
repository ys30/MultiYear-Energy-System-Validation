# Methods — pre-results draft (v0.2)

## Study design

The study is designed as a retrospective, multi-year observational data and simulation analysis. Final geographic scope, included calendar years and technology resolution will be fixed before reporting model outcomes. The analysis separates (i) data validation, (ii) numerical model verification, and (iii) empirical out-of-sample validation.

## Data and provenance

Candidate hourly electricity-demand observations include U.S. EIA-930 balancing-authority records, subject to documented access, licensing, revisions, geographical coverage, and definition checks. Capacity and generation observations must be obtained and audited separately. Weather reanalysis may be used as explanatory covariates, not as a substitute for observed electrical demand. The 2020 five-continent LUT fixture in the predecessor engineering demonstration is an annual energy-service-demand input and is **not** part of the observed U.S. hourly-load validation sample.

For each dataset, record provider, source URI, access date, license, SHA256 checksum, observation period, spatial unit, variable definition, original unit, timezone, daylight-saving convention, missingness, and any revisions. An immutable manifest links raw files to all derived inputs.

## Temporal harmonization

All hourly observations are normalized to UTC with a documented timestamp convention. Each complete UTC calendar year contains 8,760 hours, or 8,784 in a leap year. Duplicated, missing, ambiguous and out-of-year timestamps are rejected or explicitly accounted for before annual aggregation. Hourly power in MW is converted to energy in MWh using the interval duration in hours; comparisons against reported annual energy totals use predeclared relative and absolute tolerances. Missing observations are not silently treated as zero.

## Spatial and technology harmonization

A versioned crosswalk maps source balancing authorities to the study regions and source technology labels to the modeling categories. Coverage and unmapped records are reported for each year. Regions with incomplete capacity coverage are excluded from calibrated adequacy comparisons or labeled as partial-coverage scenarios. Historical geographic boundary changes are explicitly flagged.

## PyPSA specification and solver verification

The baseline optimization will define buses, loads, generators, costs, availability, transmission and storage components according to audited input coverage. Simplifications (e.g., copperplate topology) will be labeled and held consistent across the comparison years. Solver version, convergence/termination status, objective components, hourly nodal balances, dispatch limits and storage state constraints (where relevant) will be checked automatically.

## Calibration and external validation

A chronological split will reserve one or more complete years for out-of-sample assessment. Calibration targets and admissible parameters will be registered before examining held-out outcomes. Model accuracy will be summarized using bias, MAE and RMSE on observed quantities that correspond to the modeled outputs. An optimization-derived shortage proxy is not treated as observed outages.

## Sensitivity and uncertainty

Prespecified comparisons will vary input-source selection, coverage thresholds, temporal aggregation, regional crosswalks, capacity assumptions and selected model simplifications, one factor or a documented factorial subset at a time. Report effect sizes and uncertainty intervals where justified; distinguish measurement uncertainty, modeling assumptions and numerical sensitivity.

## Reproducibility and research ethics

Raw third-party data will not be redistributed without permission. Code, manifests and nonrestricted derived results may be released separately after review. Manuscript tables and figures will include dataset versions, configuration IDs and verified workflow run identifiers.

## Items requiring final decisions

Study region, observed datasets, year range, transmission/storage treatment, calibration parameters, held-out years, validation metrics, sensitivity design and journal reporting requirements.
