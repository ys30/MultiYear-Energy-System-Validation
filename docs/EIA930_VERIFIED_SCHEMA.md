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

## Resolved local-hourly request syntax (2026-11-02)
- Successful probe: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41548821393
- `local-hourly` **requires offset-bearing start/end query labels** in this observed API behavior. Unzoned query returned HTTP 500, while offset-bearing requests succeeded.
- On the 2021-11-07 Pacific fall-back day, local CISO demand response returned 25 labels including both `2021-11-07T01-07` and `2021-11-07T01-08` (distinct offsets).
- UTC `hourly` response for that date returned 23 labels, omitting `2021-11-07T06`.
- A 2021-11-06 local query bounded `00-07` to `23-07` returned 23 labels; **do not interpret this as a missing hour** without checking API boundary semantics.
- Next validation must compare offset-converted UTC instants and values between frequency representations, including cross-day boundaries. No interpolation or full-year acceptance yet.

## Five-year CISO raw-label coverage (2026-11-02)
Source: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41570393968 (all five matrix jobs completed successfully).

| Year | Observed labels | Expected labels | Missing labels | Raw grid complete | Model input approved |
| --- | ---: | ---: | --- | --- | --- |
| 2021 | 8759 | 8760 | 2021-11-07T06 | no | no |
| 2022 | 8760 | 8760 | none | yes | no |
| 2023 | 8760 | 8760 | none | yes | no |
| 2024 | 8784 | 8784 | none | yes | no |
| 2025 | 8760 | 8760 | none | yes | no |

Total 43,823 observed of 43,824 expected raw UTC hour labels; one missing. No duplicate or unexpected labels reported in any of the five years. **These are raw-label audits, not final certified MW demand, hourly interval-start semantics, or PyPSA-ready input.** Do not silently impute the missing hour. Prioritize source-semantic validation and normalized UTC boundary checks on 2022–2025 while investigating 2021 separately.

## Exact null-demand observations (verified 2026-11-03)

Source: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41575917559 . All five year-specific jobs completed successfully. All ten invalid demand observations have `value: null` in the EIA API response, with expected respondent CISO, type D and units megawatthours. These are **source-returned null values**, not proven physical sensor outages.

| Year | Null-value period labels (UTC hourly API) | Other missing period labels | Raw candidate eligible for semantic review |
| --- | --- | --- | --- |
| 2021 | 2021-08-29T06; 2021-08-29T17; 2021-08-30T16; 2021-08-31T09; 2021-08-31T14 | 2021-11-07T06 | no |
| 2022 | 2022-01-05T10; 2022-05-17T18; 2022-06-13T18 | none | no |
| 2023 | 2023-10-31T21; 2023-11-14T20 | none | no |
| 2024 | none | none | yes, raw checks only |
| 2025 | none | none | yes, raw checks only |

Across 2021–2025, 43,813 of 43,824 expected hourly labels have a valid numeric demand observation. The 11 unavailable observations comprise 10 returned null values and one absent raw label. No interpolation, silent deletion, or model-input approval was performed. A successful CI run indicates the audit executed, **not** that the scientific acceptance gate passed. Before PyPSA ingestion, verify period interval semantics and year boundaries independently.

## UTC interval-boundary hypothesis results (2026-11-03)

Verified GitHub Actions run: https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/41665296840 . For all five CISO years, raw API period labels span Jan 1 00 through Dec 31 23 (with the previously documented 2021 missing label). Under the interval-start hypothesis all labels map inside the named year; under interval-end interpretation the Jan 1 00 label maps to Dec 31 23 of the previous year.

| Year | Interval-start labels inside year | Interval-end labels inside year | Interval-end labels outside year |
| --- | ---: | ---: | ---: |
| 2021 | 8759 | 8758 | 1 |
| 2022 | 8760 | 8759 | 1 |
| 2023 | 8760 | 8759 | 1 |
| 2024 | 8784 | 8783 | 1 |
| 2025 | 8760 | 8759 | 1 |

**Important:** boundary consistency does not independently establish EIA's interval convention. The normalization helper currently requires explicit interval-end confirmation; do not invoke it on the live hourly data based only on these observations. Before using any year in PyPSA, obtain documented interval semantics, verify the proper year-edge query window, and validate the resulting contiguous UTC index. No year is approved for model ingestion by this check.

## Official interval semantics confirmed (2026-11-03)

EIA's own EIA-930 About page https://www.eia.gov/electricity/930-content/about.html states that hourly values are time-weighted hourly averages and are published using **hour ending** time reporting. The EIA-930 instructions https://omb.report/icr/202112-1905-001/doc/117324000 likewise require reporting hourly integrated values by hour ending time with UTC timestamps. The API's `hourly` frequency is UTC; API metadata gives `megawatthours` as the value unit. Thus the interval-start UTC timestamp for each API record is the labeled UTC time minus one hour; one-hour MWh becomes one-hour mean MW numerically.

**Critical correction to earlier candidate coverage:** previous yearly queries used raw period labels `YYYY-01-01T00` through `YYYY-12-31T23`. They cover the *hour-ending label year*, NOT the complete interval-start calendar year. For a model calendar year Y, request `Y-01-01T01` through `(Y+1)-01-01T00` inclusive. Consequently the previous 2024/2025 raw-label completeness cannot by itself establish a full 2024/2025 model-year series. The first raw label of each prior query belongs to the previous model year and the next year's Jan 1 00 raw label is needed. Existing 2021-2023 source nulls and absent labels remain independently observed but must be re-audited against the corrected model-year window.

Do not treat source publication's mention of aggregate imputation as permission to impute individual BA demand: EIA explicitly notes hourly individual BA data are published as received. No historical numerical result has yet been approved for PyPSA.
