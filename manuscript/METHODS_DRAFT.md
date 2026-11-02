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


## Pre-specified analysis protocol (v0.3; pending empirical intake)

### Study-unit eligibility and coverage

The primary observational unit will be an hourly balancing-authority (BA) record within a defined calendar year. Before choosing the final sample, create a source inventory that distinguishes **reported demand**, net generation, interchange, and any balancing or adjustment fields; these variables are not interchangeable. For each BA–year, report expected and observed UTC timestamps, duplicated records, missing values, nonnumeric or negative readings, source revisions, and completeness after deduplication. The minimum acceptable coverage threshold must be registered **before** inspecting model performance; until then, no BA–year is declared eligible.

### Time alignment and leakage prevention

Parse source timestamps with explicit source-timezone and interval-end/interval-start conventions; convert to UTC before joining sources. Distinguish local daylight-saving transitions from actual missing UTC hours. Record whether reported hourly values represent instantaneous power, hourly mean power, or interval energy before converting units. No interpolation or forward filling may cross training/hold-out boundaries. If imputation is permitted, fit its parameters on training years only and report both imputed and complete-case sensitivity analyses.

### Comparability of model outputs and observations

Create a variable-level correspondence table linking each observed target to its modeled counterpart, geographic aggregation, unit, time resolution, and allowable tolerance. Validate only like-for-like quantities. In particular, observed BA demand is not a direct target for simulated shortage-proxy generation; the latter remains a scenario diagnostic unless an independently defined, comparable observed adequacy measure is available.

### Chronological validation and baselines

Reserve entire calendar years for validation, with all tuning, feature selection, harmonization thresholds and calibration performed using earlier years. Register the specific train/validation/test years after source coverage has been audited but before inspecting held-out prediction errors. Compare the calibrated PyPSA-based approach against at least a transparent seasonal/hour-of-week benchmark on targets where both methods are scientifically meaningful. Report sample sizes, bias, MAE and RMSE by BA and year; normalize metrics only when denominators and zero-handling are declared in advance.

### Sensitivity attribution

Use a frozen baseline dataset and model configuration. Change one harmonization or modeling decision at a time where identifiable, keeping the evaluation sample fixed for paired comparisons. Separately report the effect of changing the eligible sample itself. Do not interpret a difference in outcomes as caused by one preprocessing choice if capacity, topology, temporal coverage or other model inputs changed simultaneously.

### Uncertainty and claims

Where hourly serial dependence matters, avoid interpreting independent-hour bootstrap intervals as valid inferential uncertainty. If uncertainty intervals are reported, justify a time-block or year-level resampling scheme and its effective sample size. Numerical solver agreement, source-data consistency and predictive validation are three distinct claims, each requiring its own evidence. The study will not claim observed outage reduction, causal effects or generalizable forecasting skill from synthetic engineering tests.

### Release gate for empirical Results

Before replacing any Results placeholders, require: (1) recorded raw-input checksums and source versions; (2) explicit eligible BA–year inventory; (3) frozen geographic/technology crosswalk; (4) complete timestamp and energy-reconciliation audits; (5) solver diagnostics; (6) leakage-safe held-out evaluation; and (7) scripts that reproduce every reported figure and table. Failed checks must be documented rather than silently excluded.
