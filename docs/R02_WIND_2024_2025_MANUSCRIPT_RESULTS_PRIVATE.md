# R02 wind resource–generation comparison: manuscript-ready results (private)

**Status:** exploratory empirical evidence; 2024–2025 source and workflow checks passed. This is not a calibrated PyPSA dispatch or an out-of-sample wind generation forecast.

## Data and comparison design

Three CISO-associated wind plants (EIA plant IDs 57484, 57514, and 7526) were matched to NASA POWER 10-m hourly wind-speed estimates and EIA-923 Page 1 observed monthly plant-fuel net generation in 2024 and 2025. Hourly meteorological coverage is 8,784 hours per plant in leap-year 2024 and 8,760 hours per plant in 2025. Monthly net generation was divided by the correct number of calendar days before calculating Pearson correlations against monthly mean wind speed. There are 12 monthly observations per plant-year. The analysis uses EIA-860 generator-level operating-year and year-end nameplate data for capacity context, **not** validated monthly operational capacity or turbine availability.

Three descriptive diagnostics were applied: (i) within-year Pearson correlations across 12 months; (ii) leave-one-calendar-month-out sensitivity (12 re-estimations per plant-year, each based on 11 months); and (iii) matched-calendar-month interannual contrasts, correlating the 12 differences in monthly mean wind speed (2025 minus 2024) with the corresponding differences in daily-normalized generation.

## Verified results

| Plant | 2024 within-year r | 2025 within-year r | 2024 leave-one-out r range | 2025 leave-one-out r range | Matched-month interannual difference r |
|:--|--:|--:|:--|:--|--:|
| 57484 | 0.587061 | 0.329758 | 0.499175–0.661963 | 0.205950–0.441450 | 0.796281 |
| 57514 | 0.981182 | 0.899374 | 0.971263–0.988995 | 0.872632–0.930080 | 0.813280 |
| 7526 | 0.976504 | 0.980682 | 0.971836–0.984308 | 0.975966–0.989623 | 0.796318 |


### Matched-month leave-one-out robustness (new verified diagnostic)

For each plant, the 12 matched-calendar-month year-over-year contrasts were recomputed 12 times after excluding one calendar month (11 contrasts per re-estimation). These are **sensitivity ranges, not confidence intervals**.

| Plant | Full matched-month interannual r | Leave-one-month-out minimum r | Maximum r |
|:--|--:|--:|--:|
| 57484 | 0.796281 | 0.737020 | 0.857708 |
| 57514 | 0.813280 | 0.751134 | 0.846581 |
| 7526 | 0.796318 | 0.675153 | 0.862247 |

The positive associations persist under all single-month omissions, but Plant 7526 has the broadest sensitivity interval. These estimates derive from the successful R02 CI run **42752870880**; they are descriptive and based on only two years.

**Additional manuscript Results sentence:** *Across the three plants, correlations based on matched-calendar-month interannual contrasts remained positive after omitting any one calendar month (r ranges: 0.737–0.858, 0.751–0.847, and 0.675–0.862 for Plants 57484, 57514, and 7526, respectively). The broader range for Plant 7526 indicates greater sensitivity to the choice of included months; these leave-one-out ranges should not be interpreted as confidence intervals.*

### Proposed Results text

*Monthly wind-resource–generation associations varied substantially among the three plants. The Pearson correlation between monthly mean 10-m wind speed and observed daily-normalized monthly generation was 0.587 in 2024 and 0.330 in 2025 for Plant 57484, compared with 0.981 and 0.899 for Plant 57514 and 0.977 and 0.981 for Plant 7526. Leave-one-month-out sensitivity analyses showed that the high correlations for Plant 7526 persisted regardless of which month was omitted (r = 0.972–0.984 in 2024; r = 0.976–0.990 in 2025). However, matched-calendar-month interannual contrasts yielded more similar correlations across plants (r = 0.796–0.813), suggesting that conclusions about between-plant heterogeneity depend on the temporal contrast being analyzed. These exploratory associations do not establish causality, operational availability, or out-of-sample predictive performance.*

### Proposed figure caption

**Figure R02-W1.** Descriptive wind-resource–generation associations for three wind plants in 2024–2025. **(A)** Within-year Pearson correlations between NASA POWER monthly mean 10-m wind speed and EIA-923 observed monthly plant-fuel net generation normalized by calendar days (12 monthly observations per plant-year). **(B)** Range of Pearson correlations after removing each calendar month in turn (12 estimates per plant-year, each using 11 observations). **(C)** Pearson correlation between matched-calendar-month differences (2025 minus 2024) in wind speed and daily-normalized generation (12 month pairs per plant), with whiskers showing the range after leaving out one matched month (11 pairs per estimate). Whiskers in panels B and C are sensitivity ranges, not statistical confidence intervals. Colors distinguish plant IDs. All analyses are descriptive and do not constitute a calibrated wind-power model or forecast validation.

## Interpretation boundaries and open checks

1. NASA POWER WS10M is a gridded 10-m meteorological estimate, not turbine hub-height wind or observed plant output.
2. EIA-923 Page 1 plant-fuel net generation is not necessarily attributable to a single EIA-860 generator record. Year-end EIA-860 nameplate is not a month-by-month operational denominator. Plant 7526 includes an 85.5-MW generator with a May 2024 operating date; year-end capacity matches 2025 but partial-year operational context matters.
3. Leave-one-month-out is a robustness diagnostic, not out-of-sample validation; removing one month does not eliminate shared seasonal structure.
4. Matched-month interannual contrasts reduce fixed calendar-month seasonality but cannot control maintenance, curtailment, outages, capacity availability, or other year-specific confounding. Two years yield only 12 paired monthly differences per plant.
5. **Do not authorize empirical R02 hourly PyPSA dispatch** without independently validated hourly renewable availability, generation and operating constraints.
6. Verify figure appearance and typography by opening the generated SVG artifact before journal submission. CI confirms generation and basic content, not human visual quality.

## Reproduction

Workflow: `.github/workflows/r02-six-site-extended-weather.yml`.

Artifacts: `outputs/spatial_weather_merged_2025/wind_2024_2025_comparison.json`, `wind_2024_2025_leave_one_month_out.json`, `wind_2024_2025_matched_month_contrasts.json`, and `wind_2024_2025_three_panel.svg`.

Evidence source: CI run 42747028898 (success), preceded by independent 2024 weather-generation and 2024 EIA-860 capacity audits.
