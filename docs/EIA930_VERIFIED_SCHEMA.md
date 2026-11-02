# EIA-930 CISO candidate: observed API schema evidence

Source: GitHub Actions run 41529332150 (2026-11-02), 24 hourly records requested for 2021-01-01.
Independent artifact re-audit: run 41543901000 (2026-11-02), successful.
Source run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41529332150
Audit run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41543901000

## Observed (not inferred)
- respondent: CISO (24/24)
- type: D (24/24)
- value-units: megawatthours (24/24)
- period samples: 2021-01-01T00, 2021-01-01T01, 2021-01-01T02
- fields: period, respondent, respondent-name, type, type-name, value, value-units
- 24 rows, 24 distinct period labels

## Interpretation gates
- Request code explicitly sends `frequency=hourly`; check EIA metadata and documentation to substantiate UTC interpretation.
- EIA-930 hourly interval-end convention must be independently substantiated before subtracting one hour from API period labels.
- Hourly MWh over exactly one hour corresponds numerically to mean MW. This does not establish that `type=D` is interchangeable with any other demand definition.
- No full-year completeness, geography mapping, or PyPSA calibration is established by the 24-row snapshot.
- Never use these observations as manuscript results until all gates are satisfied.

## Next empirical validation
Download an entire candidate BA-year with an adequate `max_rows` limit; retain the raw SHA256 manifest, check 8760/8784 hourly periods, missing/duplicates, physical plausibility, and independent data-definition references before producing Table 1.

## Full-year CISO 2021 observed period-label audit (2026-11-02)
- Workflow run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41545175223
- Requested labels: 2021-01-01T00 through 2021-12-31T23 inclusive; `frequency=hourly` in request code.
- API returned 8,759 rows, 8,759 distinct period labels, no duplicates or out-of-year labels.
- The only absent raw label relative to a 8,760-label calendar grid: **2021-11-07T06**.
- This coincides with the US autumn daylight-saving transition date, but causation is **not established**. Do not fill, interpolate, or silently discard this gap.
- Unit is `megawatthours` for all 8,759 rows; respondent CISO, series D.
- Research status: observed missing raw label, not a validated missing UTC interval. Confirm official EIA hourly period semantics and compare alternate EIA endpoint/frequency before using in annual results.

## Live EIA route metadata and DST probe (2026-11-02)
- Probe run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41548601632
- Live route metadata lists `hourly` alias `hourly (UTC)`, description `One data point for each hour in UTC time.`, format `YYYY-MM-DDTHH24`.
- Live route metadata lists `local-hourly` alias `hourly (Local Time Zone)`, description `One data point for each hour in local time.`, format includes timezone offset.
- Independent CISO D request for 2021-11-07 using `hourly` returned 23 labels, omitting `2021-11-07T06`.
- Equivalent `local-hourly` query returned HTTP 500. Workflow now correctly fails incomplete comparisons while retaining its diagnostic artifact.
- This supports UTC label interpretation for `hourly`, **not** a causal attribution of the absent label to DST. Investigate alternate local-hourly query boundaries and source data before imputation or manuscript results.
