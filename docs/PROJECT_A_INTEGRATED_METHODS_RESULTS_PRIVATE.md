# Project A — integrated Methods and Results draft (private; 2026-11-10)

**Manuscript type:** reproducible data validation and evidence-gated modeling methodology. **Status:** draft sections, not a completed manuscript. No calibrated empirical hourly PyPSA dispatch has been performed.

## 2. Methods

### 2.1 Study scope and authoritative sources

We constructed a two-year California Independent System Operator (CISO)-associated data-validation case study using 2024–2025 records. The source stack combined EIA-860 generator-level technology, nameplate and commissioning metadata; EIA-923 monthly plant–fuel net generation; EIA-930 balancing-authority-level hourly demand and reported generation by fuel; and NASA POWER gridded meteorological variables. Each source was assigned its native spatial entity, temporal resolution and evidentiary role. These were not treated as interchangeable: generator nameplate describes installed capacity, monthly net generation describes realized output, hourly balancing-authority demand describes aggregate load, and NASA POWER meteorology supplies a resource proxy rather than measured turbine output.

The pilot comprised three solar and three wind sites selected for weather-data and equipment-evidence screening. It was not designed to be representative of the full CISO fleet; selection and commissioning constraints were explicitly checked. In particular, a site commissioned after July 2025 cannot serve as an observed operating plant for that month.

### 2.2 Source contracts and temporal alignment

Validation was conducted before any model-parameter promotion. Checks covered source provenance, entity identifiers, generator vintage, missing-versus-zero semantics, and period-specific time alignment. Leap-year 2024 was handled with actual calendar-month lengths: monthly EIA-923 net generation G_{p,y,m} (MWh) was normalized to daily output g_{p,y,m}=G_{p,y,m}/d_{y,m} (MWh day^-1). NASA POWER hourly 10-m wind speed was aggregated to a monthly mean w_{p,y,m} (m s^-1). This comparison is descriptive; daily normalization does not correct for curtailment, plant outages, hub-height wind conditions or changes in operating capacity.

### 2.3 Wind resource–generation diagnostics

For each plant p and year y, the within-year association was Pearson r across 12 pairs (w_{p,y,m},g_{p,y,m}). For leave-one-month-out (LOMO) sensitivity, we recomputed r 12 times using the remaining 11 months, reporting the minimum and maximum. These extrema are **sensitivity ranges**, not confidence intervals.

For matched-calendar-month interannual contrasts, we defined Δw_{p,m}=w_{p,2025,m}-w_{p,2024,m} and Δg_{p,m}=g_{p,2025,m}-g_{p,2024,m}; Pearson r was calculated across the 12 paired contrasts. Matched-month LOMO excluded one month pair at a time (11 pairs per re-estimation). No p-values, causal effects, forecast skill, or spatial representativeness are inferred from these exploratory comparisons.

### 2.4 Evidence promotion and simulation-readiness decision

We implemented two separate evidence layers. The plant parameter registry starts engineering parameters as unknown and does not impute equipment values from generator nameplate or technology labels. An update can be recorded as a **scenario assumption** or as **documented plant-specific evidence**. Documented evidence requires a source title, absolute URL, directly identifiable locator, equipment applicability, effective year and reviewer. A recorded evidence item does not automatically approve physical conversion models or hourly dispatch.

The downstream empirical-dispatch readiness audit evaluates all plant engineering parameter slots and five system-level requirements: (1) independently validated plant-hour renewable availability, (2) generator marginal costs, (3) storage efficiency and state-of-charge constraints, (4) network and interchange constraints, and (5) independent hourly dispatch observations. Each slot is assigned **block** or **screen_only** under the current conservative baseline; no item is promoted to empirical-dispatch approval without separate full-system validation. A documented engineering value can be screen-only while hourly availability remains unknown. These decisions apply to **empirical hourly dispatch validation**, not to exploratory scenario modeling using transparently stated assumptions.

### 2.5 Reproducibility and figure auditing

GitHub Actions regenerates the data-derived outputs, runs source/parameter contract tests, creates the three-panel wind diagnostic, and independently reconciles plotted SVG coordinates against analytical JSON. The verified R02 run [42854166545](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42854166545) reported 21 successful plotted-value checks across three wind plants. Actual rendered layout inspection at manuscript size remains a separate acceptance criterion.

## 3. Results

### 3.1 Multi-source integration and evidence limitations

The workflow reconstructed a two-year source stack without conflating EIA-860 nameplate with generation or EIA-923 monthly plant-fuel output with hourly availability. Source audits exposed specific temporal and reporting limitations, including a 2025 CISO hourly demand anomaly and missing EIA-930 fuel coverage in a 2024 period. These anomalies were flagged rather than silently imputed as observations. The six-site pilot supports method verification and targeted physical plausibility checks, not system-wide representativeness.

### 3.2 Wind resource–generation association is comparison-design dependent

The Pearson correlation between monthly mean NASA POWER 10-m wind speed and daily-normalized EIA-923 monthly net generation varied by site and year. For plant 57484, r was 0.587 in 2024 and 0.330 in 2025; for 57514, 0.981 and 0.899; and for 7526, 0.977 and 0.981. Within-year LOMO sensitivity ranges were 0.499–0.662 and 0.206–0.441 (57484); 0.971–0.989 and 0.873–0.930 (57514); and 0.972–0.984 and 0.976–0.990 (7526), for 2024 and 2025 respectively.

In contrast, matched-calendar-month interannual differences yielded r=0.796, 0.813 and 0.796 for plants 57484, 57514 and 7526, respectively. The corresponding matched-month LOMO ranges were 0.737–0.858, 0.751–0.847 and 0.675–0.862. All single-month-omission correlations were positive, but these small-sample estimates remain descriptive. **Figure R02-W1** visualizes the three comparison designs; its SVG numeric audit passed, while final visual inspection remains pending.

### 3.3 Empirical hourly dispatch is withheld by evidence gates

The baseline registry included six pilot plants with 39 engineering parameter slots (three solar sites × seven parameters and three wind sites × six parameters). All 39 remained blocked as unknown or insufficiently evidenced, while five additional system-level empirical-dispatch gates were blocked. The machine-readable audit therefore reported **44 blocked gates, zero screen-only gates, and empirical_dispatch_approved=false**. This is an auditable inventory of current evidence gaps, **not** an attempted dispatch optimization or a failure rate for all CISO assets. These results were reproduced in successful [R02 CI run 42854166545](https://github.com/ys30/MultiYear-Energy-System-Validation/actions/runs/42854166545).

## 4. Discussion — framing to develop

The principal methodological distinction is between reproducible data assembly and justified parameter use. A pipeline may reproduce a source faithfully while still lacking the equipment, operational or network evidence necessary for empirical hourly dispatch. Temporal-contrast dependence in the wind case illustrates how apparently strong source agreement can vary with the comparison design. This work demonstrates explicit rejection of unsupported modeling claims; it does not demonstrate superior dispatch accuracy, cost or reliability.

**Remaining before submission:** independent literature comparison and novelty audit; source coverage table with auditable counts; consolidated figures and references; journal-size SVG visual inspection; limitations of six-site selection and only two years; independent review of whether all five system gates are necessary for the manuscript's precise empirical-validation claim.
