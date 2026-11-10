# Figure R02-W1 — candidate freeze and acceptance record (private)

**Candidate source commit:** `b61cf714`  
**Verified full workflow:** [R02 six-site extended physical weather #42851314978](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42851314978) — **success**.  
**Research Data Contracts:** passed on the same commit.  
**Archived workflow artifact:** `r02-six-site-extended-weather-2025`, artifact ID `13779223503` (available when checked).  
**Figure filename inside outputs:** `wind_2024_2025_three_panel.svg`.

## Acceptance status

| Criterion | Evidence | Status |
|---|---|---|
| Analysis provenance | NASA POWER WS10M, EIA-923 observed monthly plant-fuel generation, correct 2024/2025 calendar-day normalization | Verified in pipeline |
| 2024/2025 year encoding | Open versus filled markers, dashed versus solid ranges, explicit legend | Automated tests passed |
| Panel A | Two annual within-year Pearson estimates per plant, 12 months per estimate | Automated tests passed |
| Panel B | Full-sample dots over 11-month leave-one-out sensitivity ranges | Automated tests passed |
| Panel C | Matched-calendar-month 2025–2024 Pearson estimate with 11-pair leave-one-out range | Automated tests passed |
| Label/whisker overlap | Numeric labels positioned above Panel C sensitivity upper whiskers | Geometric regression test passed |
| SVG syntax | XML parses and required labels are present | Automated tests passed |
| Actual rendering at journal size | Open the artifact SVG, visually inspect at full size and reduced two-column width | **Pending manual visual inspection** |
| Data-to-label audit | Independent SVG/XML-to-JSON audit: 21 plotted-value checks for 3 plants; run #42851314978 | **Passed** |
| Submission-ready freeze | Requires pending visual check above and manuscript cross-references | **Not yet approved** |

## Figure interpretation

The three panels present different descriptive estimands and should not be treated as interchangeable evidence: within-year monthly correlation (A), leave-one-month-out sensitivity of that correlation (B), and matched-month 2025-minus-2024 correlation (C). The whiskers in B and C are **sensitivity ranges, not confidence intervals**. Sample sizes are small (12 observations or paired contrasts, 11 per omission). NASA POWER 10-m wind speed is not turbine hub-height wind; maintenance, curtailment, availability and changing operating capacity remain uncontrolled.

## Verified matched-month results

| Plant ID | Full matched-month r | Leave-one-out min | Leave-one-out max |
|---|---:|---:|---:|
| 57484 | 0.796281 | 0.737020 | 0.857708 |
| 57514 | 0.813280 | 0.751134 | 0.846581 |
| 7526 | 0.796318 | 0.675153 | 0.862247 |

The values above were obtained from successful R02 run #42752870880 and are reproduced by the current workflow. They are not out-of-sample forecasting metrics and do not authorize empirical hourly PyPSA dispatch.

## Manuscript integration

Use the private `docs/R02_WIND_2024_2025_MANUSCRIPT_RESULTS_PRIVATE.md` for proposed Results and Figure R02-W1 caption. Keep this empirical wind-resource diagnostic separate from any uncalibrated hourly dispatch or claims of system-wide reliability.

**Decision:** **candidate freeze only**; do not label the SVG journal-final until actual render inspection and manuscript cross-references have passed.
