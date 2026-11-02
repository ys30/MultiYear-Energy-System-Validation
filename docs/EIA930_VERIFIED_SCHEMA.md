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
